#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charmed operator for the OAI RAN Distributed Unit (DU) for K8s."""

import json
import logging
from ipaddress import IPv4Address
from subprocess import check_output
from typing import List, Optional

from charms.kubernetes_charm_libraries.v0.multus import (  # type: ignore[import]
    KubernetesMultusCharmLib,
    NetworkAnnotation,
    NetworkAttachmentDefinition,
)
from charms.loki_k8s.v1.loki_push_api import LogForwarder  # type: ignore[import]
from charms.oai_ran_cu_k8s.v0.fiveg_f1 import F1Requires  # type: ignore[import]
from charms.observability_libs.v1.kubernetes_service_patch import (  # type: ignore[import]
    KubernetesServicePatch,
)
from jinja2 import Environment, FileSystemLoader
from lightkube.models.core_v1 import ServicePort
from lightkube.models.meta_v1 import ObjectMeta
from ops import (
    ActiveStatus,
    BlockedStatus,
    CollectStatusEvent,
    EventBase,
    EventSource,
    WaitingStatus,
)
from ops.charm import CharmBase, CharmEvents
from ops.main import main
from ops.pebble import Layer

from charm_config import CharmConfig, CharmConfigInvalidError, CNIType
from oai_ran_du_k8s import DUSecurityContext, DUUSBVolume

logger = logging.getLogger(__name__)

BASE_CONFIG_PATH = "/tmp/conf"
CONFIG_FILE_NAME = "du.conf"
F1_RELATION_NAME = "fiveg_f1"
LOGGING_RELATION_NAME = "logging"
WORKLOAD_VERSION_FILE_NAME = "/etc/workload-version"


class NadConfigChangedEvent(EventBase):
    """Event triggered when an existing network attachment definition is changed."""


class KubernetesMultusCharmEvents(CharmEvents):
    """Kubernetes Multus Charm Events."""

    nad_config_changed = EventSource(NadConfigChangedEvent)


class OAIRANDUOperator(CharmBase):
    """Main class to describe Juju event handling for the OAI RAN DU operator for K8s."""

    on = KubernetesMultusCharmEvents()  # type: ignore

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.collect_unit_status, self._on_collect_unit_status)
        if not self.unit.is_leader():
            return
        self._container_name = self._service_name = "du"
        self._container = self.unit.get_container(self._container_name)
        self._f1_requirer = F1Requires(self, F1_RELATION_NAME)
        self._logging = LogForwarder(charm=self, relation_name=LOGGING_RELATION_NAME)
        self._du_security_context = DUSecurityContext(
            namespace=self.model.name,
            statefulset_name=self.app.name,
            container_name=self._container_name,
        )
        self._usb_volume = DUUSBVolume(
            namespace=self.model.name,
            statefulset_name=self.app.name,
            unit_name=self.unit.name,
            container_name=self._container_name,
        )
        try:
            self._charm_config: CharmConfig = CharmConfig.from_charm(charm=self)
        except CharmConfigInvalidError:
            return
        self._kubernetes_multus = KubernetesMultusCharmLib(
            charm=self,
            container_name=self._container_name,
            cap_net_admin=True,
            network_annotations_func=self._generate_network_annotations,
            network_attachment_definitions_func=self._network_attachment_definitions_from_config,
            refresh_event=self.on.nad_config_changed,
            privileged=True,
        )
        self._service_patcher = KubernetesServicePatch(
            charm=self,
            ports=[
                ServicePort(name="f1c", port=38472, protocol="SCTP"),
                ServicePort(name="f1u", port=self._charm_config.f1_port, protocol="UDP"),
            ],
        )

        self.framework.observe(self.on.update_status, self._configure)
        self.framework.observe(self.on.config_changed, self._configure)
        self.framework.observe(self.on.du_pebble_ready, self._configure)
        self.framework.observe(self._f1_requirer.on.fiveg_f1_provider_available, self._configure)

    def _on_collect_unit_status(self, event: CollectStatusEvent):  # noqa C901
        """Check the unit status and set to Unit when CollectStatusEvent is fired.

        Set the workload version if present in workload
        Args:
            event: CollectStatusEvent
        """
        if not self.unit.is_leader():
            # NOTE: In cases where leader status is lost before the charm is
            # finished processing all teardown events, this prevents teardown
            # event code from running. Luckily, for this charm, none of the
            # teardown code is necessary to perform if we're removing the
            # charm.
            event.add_status(BlockedStatus("Scaling is not implemented for this charm"))
            logger.info("Scaling is not implemented for this charm")
            return
        try:
            self._charm_config: CharmConfig = CharmConfig.from_charm(charm=self)  # type: ignore[no-redef]  # noqa: E501
        except CharmConfigInvalidError as exc:
            event.add_status(BlockedStatus(exc.msg))
            return
        if not self._kubernetes_multus.multus_is_available():
            event.add_status(BlockedStatus("Multus is not installed or enabled"))
            logger.info("Multus is not installed or enabled")
            return
        if not self._kubernetes_multus.is_ready():
            event.add_status(WaitingStatus("Waiting for Multus to be ready"))
            logger.info("Waiting for Multus to be ready")
            return
        if not self._du_security_context.is_privileged():
            event.add_status(WaitingStatus("Waiting for statefulset to be patched"))
            logger.info("Waiting for statefulset to be patched")
            return
        if not self._charm_config.simulation_mode and not self._usb_volume.is_mounted():
            event.add_status(WaitingStatus("Waiting for USB device to be mounted"))
            logger.info("Waiting for USB device to be mounted")
            return
        if not self._relation_created(F1_RELATION_NAME):
            event.add_status(BlockedStatus("Waiting for F1 relation to be created"))
            logger.info("Waiting for F1 relation to be created")
            return
        if not self._container.can_connect():
            event.add_status(WaitingStatus("Waiting for container to be ready"))
            logger.info("Waiting for container to be ready")
            return
        if not _get_pod_ip():
            event.add_status(WaitingStatus("Waiting for Pod IP address to be available"))
            logger.info("Waiting for Pod IP address to be available")
            return
        self.unit.set_workload_version(self._get_workload_version())
        if not self._container.exists(path=BASE_CONFIG_PATH):
            event.add_status(WaitingStatus("Waiting for storage to be attached"))
            logger.info("Waiting for storage to be attached")
            return
        if not self._f1_requirer.f1_ip_address or not self._f1_requirer.f1_port:
            event.add_status(WaitingStatus("Waiting for F1 information"))
            logger.info("Waiting for F1 information")
            return
        event.add_status(ActiveStatus())

    def _configure(self, _) -> None:  # noqa C901
        try:
            self._charm_config: CharmConfig = CharmConfig.from_charm(  # type: ignore[no-redef]  # noqa: E501
                charm=self
            )
        except CharmConfigInvalidError:
            return
        if not self._kubernetes_multus.multus_is_available():
            return
        self.on.nad_config_changed.emit()
        if not self._kubernetes_multus.is_ready():
            return
        if not self._du_security_context.is_privileged():
            self._du_security_context.set_privileged()
        if not self._charm_config.simulation_mode and not self._usb_volume.is_mounted():
            self._usb_volume.mount()
        if not self._relation_created(F1_RELATION_NAME):
            return
        if not self._container.can_connect():
            return
        if not _get_pod_ip():
            return
        if not self._container.exists(path=BASE_CONFIG_PATH):
            return
        if not self._f1_requirer.f1_ip_address or not self._f1_requirer.f1_port:
            return

        du_config = self._generate_du_config()
        if service_restart_required := self._is_du_config_up_to_date(du_config):
            self._write_config_file(content=du_config)
        self._configure_pebble(restart=service_restart_required)

        self._update_fiveg_f1_relation_data()

    def _relation_created(self, relation_name: str) -> bool:
        """Return whether a given Juju relation was created.

        Args:
            relation_name (str): Relation name

        Returns:
            bool: Whether the relation was created.
        """
        return bool(self.model.relations.get(relation_name))

    def _generate_du_config(self) -> str:
        return _render_config_file(
            gnb_name=self._gnb_name,
            du_f1_interface_name=self._charm_config.f1_interface_name,
            du_f1_ip_address=str(self._charm_config.f1_ip_address).split("/")[0],
            du_f1_port=self._charm_config.f1_port,
            cu_f1_ip_address=self._f1_requirer.f1_ip_address,
            cu_f1_port=self._f1_requirer.f1_port,
            mcc=self._charm_config.mcc,
            mnc=self._charm_config.mnc,
            sst=self._charm_config.sst,
            tac=self._charm_config.tac,
            simulation_mode=self._charm_config.simulation_mode,
        ).rstrip()

    def _generate_network_annotations(self) -> List[NetworkAnnotation]:
        """Generate a list of NetworkAnnotations to be used by CU's StatefulSet.

        Returns:
            List[NetworkAnnotation]: List of NetworkAnnotations
        """
        return [
            NetworkAnnotation(
                name=f"{self._charm_config.f1_interface_name}-du-net",
                interface=self._charm_config.f1_interface_name,
            ),
        ]

    def _get_f1_nad_config(self) -> dict:
        f1_nad_config = {
            "cniVersion": "0.3.1",
            "ipam": {
                "type": "static",
                "addresses": [
                    {
                        "address": self._charm_config.f1_ip_address,
                    }
                ],
            },
            "capabilities": {"mac": True},
        }
        cni_type = self._charm_config.cni_type
        if cni_type == CNIType.macvlan:
            f1_nad_config.update(
                {
                    "type": "macvlan",
                    "master": self._charm_config.f1_interface_name,
                }
            )
        elif cni_type == CNIType.bridge:
            f1_nad_config.update({"type": "bridge", "bridge": "f1-br"})
        return f1_nad_config

    def _network_attachment_definitions_from_config(self) -> list[NetworkAttachmentDefinition]:
        """Return list of Multus NetworkAttachmentDefinitions to be created based on config."""
        f1_nad_config = self._get_f1_nad_config()
        return [
            NetworkAttachmentDefinition(
                metadata=ObjectMeta(name=f"{self._charm_config.f1_interface_name}-du-net"),
                spec={"config": json.dumps(f1_nad_config)},
            ),
        ]

    def _is_du_config_up_to_date(self, content: str) -> bool:
        """Decide whether config update is required by checking existence and config content.

        Args:
            content (str): desired config file content

        Returns:
            True if config update is required else False
        """
        if not self._config_file_content_matches(content=content):
            return True
        return False

    def _config_file_content_matches(self, content: str) -> bool:
        if not self._container.exists(path=f"{BASE_CONFIG_PATH}/{CONFIG_FILE_NAME}"):
            return False
        existing_content = self._container.pull(path=f"{BASE_CONFIG_PATH}/{CONFIG_FILE_NAME}")
        if existing_content.read() != content:
            return False
        return True

    def _write_config_file(self, content: str) -> None:
        self._container.push(source=content, path=f"{BASE_CONFIG_PATH}/{CONFIG_FILE_NAME}")
        logger.info("Config file written")

    def _configure_pebble(self, restart=False) -> None:
        """Configure the Pebble layer.

        Args:
            restart (bool): Whether to restart the DU container.
        """
        plan = self._container.get_plan()
        if plan.services != self._du_pebble_layer.services:
            self._container.add_layer(self._container_name, self._du_pebble_layer, combine=True)
            self._container.replan()
            logger.info("New layer added: %s", self._du_pebble_layer)
        if restart:
            self._container.restart(self._service_name)
            logger.info("Restarted container %s", self._service_name)
            return
        self._container.replan()

    def _update_fiveg_f1_relation_data(self) -> None:
        """Publish F1 interface information in the `fiveg_f1` relation data bag."""
        if not self.unit.is_leader():
            return
        fiveg_f1_relations = self.model.relations.get(F1_RELATION_NAME)
        if not fiveg_f1_relations:
            logger.info("No %s relations found.", F1_RELATION_NAME)
            return
        self._f1_requirer.set_f1_information(port=self._charm_config.f1_port)

    @property
    def _gnb_name(self) -> str:
        """The gNB's name contains the model name and the app name.

        Returns:
            str: the gNB's name.
        """
        return f"{self.model.name}-{self.app.name}-du"

    @property
    def _du_pebble_layer(self) -> Layer:
        """Return pebble layer for the du container.

        Returns:
            Layer: Pebble Layer
        """
        return Layer(
            {
                "services": {
                    self._service_name: {
                        "override": "replace",
                        "startup": "enabled",
                        "command": self._du_startup_command,
                        "environment": self._du_environment_variables,
                    },
                },
            }
        )

    @property
    def _du_startup_command(self) -> str:
        rfsim_switch = ""
        if self._charm_config.simulation_mode:
            rfsim_switch = "--rfsim"
        return f"/opt/oai-gnb/bin/nr-softmodem -O {BASE_CONFIG_PATH}/{CONFIG_FILE_NAME} --sa {rfsim_switch}"  # noqa: E501

    @property
    def _du_environment_variables(self) -> dict:
        return {
            "TZ": "UTC",
        }

    def _get_workload_version(self) -> str:
        """Return the workload version.

        Checks for the presence of /etc/workload-version file
        and if present, returns the contents of that file. If
        the file is not present, an empty string is returned.

        Returns:
            string: A human-readable string representing the version of the workload
        """
        if self._container.exists(path=WORKLOAD_VERSION_FILE_NAME):
            version_file_content = self._container.pull(path=WORKLOAD_VERSION_FILE_NAME).read()
            return version_file_content
        return ""


def _render_config_file(
    *,
    gnb_name: str,
    du_f1_interface_name: str,
    du_f1_ip_address: str,
    du_f1_port: int,
    cu_f1_ip_address: str,
    cu_f1_port: int,
    mcc: str,
    mnc: str,
    sst: int,
    tac: int,
    simulation_mode: bool,
) -> str:
    """Render DU config file based on parameters.

    Args:
        gnb_name: The name of the gNodeB
        du_f1_interface_name: Name of the network interface used for F1 traffic
        du_f1_ip_address: IPv4 address of the network interface used for F1 traffic
        du_f1_port: Number of the port used by the DU for F1 traffic
        cu_f1_ip_address: IPv4 address of the CU's F1 interface
        cu_f1_port: Number of the port used by the CU for F1 traffic
        mcc: Mobile Country Code
        mnc: Mobile Network Code
        sst: Slice Selection Type
        tac: Tracking Area Code
        simulation_mode: Run DU in simulation mode

    Returns:
        str: Rendered DU configuration file
    """
    jinja2_env = Environment(loader=FileSystemLoader("src/templates"))
    template = jinja2_env.get_template(f"{CONFIG_FILE_NAME}.j2")
    return template.render(
        gnb_name=gnb_name,
        du_f1_interface_name=du_f1_interface_name,
        du_f1_ip_address=du_f1_ip_address,
        du_f1_port=du_f1_port,
        cu_f1_ip_address=cu_f1_ip_address,
        cu_f1_port=cu_f1_port,
        mcc=mcc,
        mnc=mnc,
        sst=sst,
        tac=tac,
        simulation_mode=simulation_mode,
    )


def _get_pod_ip() -> Optional[str]:
    """Return the pod IP using juju client.

    Returns:
        str: The pod IP.
    """
    ip_address = check_output(["unit-get", "private-address"])
    return str(IPv4Address(ip_address.decode().strip())) if ip_address else None


if __name__ == "__main__":  # pragma: nocover
    main(OAIRANDUOperator)

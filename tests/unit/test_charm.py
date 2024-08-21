#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
import json
from unittest.mock import call, patch

import pytest
from charm import OAIRANDUOperator
from ops import testing
from ops.model import ActiveStatus, BlockedStatus, WaitingStatus

MULTUS_LIB = "charms.kubernetes_charm_libraries.v0.multus.KubernetesMultusCharmLib"
MULTUS_K8S_CLIENT = "charms.kubernetes_charm_libraries.v0.multus.KubernetesClient"
F1_LIB = "charms.oai_ran_cu_k8s.v0.fiveg_f1.F1Requires"
NAMESPACE = "whatever"
WORKLOAD_CONTAINER_NAME = "du"


class TestCharm:
    patcher_k8s_service_patch = patch("charm.KubernetesServicePatch")
    patcher_check_output = patch("charm.check_output")
    patcher_security_context = patch("charm.DUSecurityContext")
    patcher_du_usb_volume = patch("charm.DUUSBVolume")
    patcher_multus_ready = patch(f"{MULTUS_LIB}.is_ready")
    patcher_multus_available = patch(f"{MULTUS_LIB}.multus_is_available")
    patcher_f1_set_information = patch(f"{F1_LIB}.set_f1_information")
    patcher_multus_statefulset_patch = patch(f"{MULTUS_K8S_CLIENT}.statefulset_is_patched")
    patcher_lightkube_client = patch("lightkube.core.client.GenericSyncClient")

    @pytest.fixture()
    def setUp(self):
        self.mock_k8s_service_patch = TestCharm.patcher_k8s_service_patch.start()
        self.mock_check_output = TestCharm.patcher_check_output.start()
        self.mock_security_context = TestCharm.patcher_security_context.start().return_value
        self.mock_du_usb_volume = TestCharm.patcher_du_usb_volume.start().return_value
        self.mock_multus_ready = TestCharm.patcher_multus_ready.start()
        self.mock_multus_available = TestCharm.patcher_multus_available.start()
        self.mock_multus_statefulset_patch = TestCharm.patcher_multus_statefulset_patch.start()
        self.mock_f1_set_information = TestCharm.patcher_f1_set_information.start()
        self.mock_lightkube_client = TestCharm.patcher_lightkube_client.start()

    def tearDown(self) -> None:
        patch.stopall()

    @pytest.fixture(autouse=True)
    def harness(self, setUp, request):
        self.mock_multus_ready.return_value = True
        self.mock_multus_available.return_value = True
        self.harness = testing.Harness(OAIRANDUOperator)
        self.harness.set_model_name(name=NAMESPACE)
        self.harness.set_leader(is_leader=True)
        self.harness.set_can_connect(container=WORKLOAD_CONTAINER_NAME, val=True)
        self.harness.begin()
        yield self.harness
        self.harness.cleanup()
        request.addfinalizer(self.tearDown)

    def test_given_unit_is_not_leader_when_evaluate_status_then_status_is_blocked(self):
        self.mock_security_context.configure_mock(
            **{
                "is_privileged.return_value": True,
            },
        )
        self.mock_du_usb_volume.configure_mock(
            **{
                "is_mounted.return_value": True,
            },
        )

        self.harness.set_leader(is_leader=False)

        self.harness.evaluate_status()

        assert self.harness.charm.unit.status == BlockedStatus(
            "Scaling is not implemented for this charm"
        )

    @pytest.mark.parametrize(
        "config_param,value",
        [
            pytest.param("f1-interface-name", "", id="empty_f1_interface_name"),
            pytest.param("f1-ip-address", "", id="empty_f1_ip-address"),
            pytest.param("f1-ip-address", "5.5.5/3", id="invalid_f1_ip-address"),
            pytest.param("f1-port", int(), id="empty_f1_port"),
            pytest.param("mcc", "", id="empty_mcc"),
            pytest.param("mnc", "", id="empty_mnc"),
            pytest.param("sst", int(), id="empty_sst"),
            pytest.param("tac", int(), id="empty_tac"),
        ],
    )
    def test_given_invalid_config_when_config_changed_then_status_is_blocked(
        self, config_param, value
    ):
        self.harness.update_config(key_values={config_param: value})
        self.harness.evaluate_status()

        assert self.harness.charm.unit.status == BlockedStatus(
            f"The following configurations are not valid: ['{config_param}']"
        )

    def test_given_macvlan_cni_type_when_network_attachment_definitions_from_config_is_called_then_interface_type_is_macvlan(  # noqa: E501
        self,
    ):
        self.harness.disable_hooks()
        self.harness.update_config(
            key_values={
                "cni-type": "macvlan",
                "f1-interface-name": "du-f1",
            }
        )
        self.harness.evaluate_status()
        nad = self.harness.charm._network_attachment_definitions_from_config()
        config_f1 = json.loads(nad[0].spec["config"])  # type: ignore
        assert config_f1["type"] == "macvlan"
        assert config_f1["master"] == "du-f1"

    def test_given_default_config_when_network_attachment_definitions_from_config_is_called_then_interfaces_type_is_bridge(  # noqa: E501
        self,
    ):
        self.harness.disable_hooks()
        self.harness.update_config(key_values={})
        self.harness.evaluate_status()
        nad = self.harness.charm._network_attachment_definitions_from_config()
        assert nad[0].spec
        config_f1 = json.loads(nad[0].spec["config"])
        assert config_f1["type"] == "bridge"

    def test_given_multus_disabled_when_collect_status_then_status_is_blocked(self):
        self.prepare_workload_for_configuration()
        self.mock_multus_available.return_value = False
        self.harness.evaluate_status()

        assert self.harness.model.unit.status == BlockedStatus(
            "Multus is not installed or enabled"
        )

    def test_given_multus_not_configured_when_collect_status_then_status_is_waiting(
        self,
    ):
        self.prepare_workload_for_configuration()
        self.mock_multus_ready.return_value = False
        self.harness.evaluate_status()

        assert self.harness.model.unit.status == WaitingStatus("Waiting for Multus to be ready")

    def test_given_charm_is_configured_and_running_when_f1_relation_is_added_then_f1_port_is_published(  # noqa: E501
        self,
    ):
        self.mock_du_usb_volume.configure_mock(
            **{
                "is_mounted.return_value": True,
            },
        )
        self.mock_security_context.configure_mock(
            **{
                "is_privileged.return_value": True,
            },
        )
        self.mock_check_output.return_value = b"1.1.1.1"
        self.harness.add_storage("config", attach=True)
        self.set_f1_relation_data()
        self.mock_f1_set_information.assert_called_once_with(
            port=2153,
        )

    def test_given_charm_is_active_when_config_changed_then_updated_f1_port_is_published(  # noqa: E501
        self,
    ):
        self.mock_du_usb_volume.configure_mock(
            **{
                "is_mounted.return_value": True,
            },
        )
        self.mock_security_context.configure_mock(
            **{
                "is_privileged.return_value": True,
            },
        )
        self.mock_check_output.return_value = b"1.1.1.1"
        self.harness.add_storage("config", attach=True)
        self.set_f1_relation_data()
        self.harness.update_config(key_values={"f1-port": 3522})
        self.harness.evaluate_status()
        self.mock_f1_set_information.assert_has_calls(
            [
                call(port=2153),
                call(port=3522),
            ]
        )

    def test_given_usb_volume_not_mounted_when_evaluate_status_then_status_is_waiting(self):
        self.mock_du_usb_volume.configure_mock(
            **{
                "is_mounted.return_value": False,
            },
        )
        self.harness.set_leader(is_leader=True)

        self.harness.evaluate_status()

        assert self.harness.charm.unit.status == WaitingStatus(
            "Waiting for USB device to be mounted"
        )

    def test_given_f1_relation_not_created_when_evaluate_status_then_status_is_blocked(self):
        self.mock_du_usb_volume.configure_mock(
            **{
                "is_mounted.return_value": True,
            },
        )
        self.mock_security_context.configure_mock(
            **{
                "is_privileged.return_value": True,
            },
        )
        self.harness.set_leader(is_leader=True)

        self.harness.evaluate_status()

        assert self.harness.charm.unit.status == BlockedStatus(
            "Waiting for F1 relation to be created"
        )

    def test_given_workload_container_cant_be_connected_to_when_evaluate_status_then_status_is_waiting(  # noqa: E501
        self,
    ):
        self.mock_du_usb_volume.configure_mock(
            **{
                "is_mounted.return_value": True,
            },
        )
        self.mock_security_context.configure_mock(
            **{
                "is_privileged.return_value": True,
            },
        )
        self.create_f1_relation()
        self.harness.set_can_connect(container=WORKLOAD_CONTAINER_NAME, val=False)

        self.harness.evaluate_status()

        assert self.harness.charm.unit.status == WaitingStatus("Waiting for container to be ready")

    def test_given_pod_ip_is_not_available_when_evaluate_status_then_status_is_waiting(  # noqa: E501
        self,
    ):
        self.mock_du_usb_volume.configure_mock(
            **{
                "is_mounted.return_value": True,
            },
        )
        self.mock_security_context.configure_mock(
            **{
                "is_privileged.return_value": True,
            },
        )
        self.mock_check_output.return_value = b""
        self.create_f1_relation()

        self.harness.evaluate_status()

        assert self.harness.charm.unit.status == WaitingStatus(
            "Waiting for Pod IP address to be available"
        )

    def test_given_charm_statefulset_is_not_patched_when_evaluate_status_then_status_is_waiting(
        self,
    ):
        self.mock_du_usb_volume.configure_mock(
            **{
                "is_mounted.return_value": False,
            },
        )
        self.mock_security_context.configure_mock(
            **{
                "is_privileged.return_value": False,
            },
        )

        self.harness.evaluate_status()

        assert self.harness.charm.unit.status == WaitingStatus(
            "Waiting for statefulset to be patched"
        )

    def test_given_storage_is_not_attached_when_evaluate_status_then_status_is_waiting(self):
        self.mock_du_usb_volume.configure_mock(
            **{
                "is_mounted.return_value": True,
            },
        )
        self.mock_security_context.configure_mock(
            **{
                "is_privileged.return_value": True,
            },
        )
        self.mock_check_output.return_value = b"1.1.1.1"
        self.create_f1_relation()

        self.harness.evaluate_status()

        assert self.harness.charm.unit.status == WaitingStatus(
            "Waiting for storage to be attached"
        )

    def test_given_f1_information_is_not_available_when_evaluate_status_then_status_is_waiting(
        self,
    ):
        self.mock_du_usb_volume.configure_mock(
            **{
                "is_mounted.return_value": True,
            },
        )
        self.mock_security_context.configure_mock(
            **{
                "is_privileged.return_value": True,
            },
        )
        self.mock_check_output.return_value = b"1.1.1.1"
        self.harness.add_storage("config", attach=True)
        self.create_f1_relation()

        self.harness.evaluate_status()

        assert self.harness.charm.unit.status == WaitingStatus("Waiting for F1 information")

    def test_given_all_status_check_are_ok_when_evaluate_status_then_status_is_active(self):
        self.mock_du_usb_volume.configure_mock(
            **{
                "is_mounted.return_value": True,
            },
        )
        self.mock_security_context.configure_mock(
            **{
                "is_privileged.return_value": True,
            },
        )
        self.mock_check_output.return_value = b"1.1.1.1"
        self.harness.add_storage("config", attach=True)
        self.set_f1_relation_data()

        self.harness.evaluate_status()

        assert self.harness.charm.unit.status == ActiveStatus()

    def test_given_statefulset_is_not_patched_when_config_changed_then_usb_is_mounted_and_privileged_context_is_set(  # noqa: E501
        self,
    ):
        self.mock_du_usb_volume.configure_mock(
            **{
                "is_mounted.return_value": False,
            },
        )
        self.mock_security_context.configure_mock(
            **{
                "is_privileged.return_value": False,
            },
        )

        self.harness.update_config(key_values={})

        self.mock_security_context.set_privileged.assert_called_once()
        self.mock_du_usb_volume.mount.assert_called_once()

    def test_given_statefulset_is_not_patched_when_simulation_mode_config_changed_to_true_then_privileged_context_is_set_but_usb_is_not_mounted(  # noqa: E501
        self,
    ):
        self.mock_du_usb_volume.configure_mock(
            **{
                "is_mounted.return_value": False,
            },
        )
        self.mock_security_context.configure_mock(
            **{
                "is_privileged.return_value": False,
            },
        )

        self.harness.update_config(key_values={"simulation-mode": True})

        self.mock_security_context.set_privileged.assert_called_once()
        self.mock_du_usb_volume.mount.assert_not_called()

    def test_given_statefulset_is_patched_when_config_changed_then_usb_is_not_mounted_and_privileged_context_is_not_set(  # noqa: E501
        self,
    ):
        self.prepare_workload_for_configuration()

        self.harness.update_config(key_values={})

        self.mock_security_context.set_privileged.assert_not_called()
        self.mock_du_usb_volume.mount.assert_not_called()

    def test_given_workload_is_ready_to_be_configured_when_config_changed_then_cu_config_file_is_generated_and_pushed_to_the_workload_container(  # noqa: E501
        self,
    ):
        root = self.harness.get_filesystem_root(WORKLOAD_CONTAINER_NAME)
        self.prepare_workload_for_configuration()

        self.harness.update_config(key_values={})

        with open("tests/unit/resources/expected_config.conf") as expected_config_file:
            expected_config = expected_config_file.read()
        assert (root / "tmp/conf/du.conf").read_text() == expected_config.strip()

    def test_given_workload_is_ready_to_be_configured_when_simulation_mode_config_changed_to_true_then_cu_config_file_contains_rfsimulator_config(  # noqa: E501
        self,
    ):
        root = self.harness.get_filesystem_root(WORKLOAD_CONTAINER_NAME)
        self.prepare_workload_for_configuration()

        self.harness.update_config(key_values={"simulation-mode": True})

        with open("tests/unit/resources/expected_rfsim_mode_config.conf") as expected_config_file:
            expected_config = expected_config_file.read()
        assert (root / "tmp/conf/du.conf").read_text() == expected_config.strip()

    def test_given_cu_config_file_is_up_to_date_when_config_changed_then_cu_config_file_is_not_pushed_to_the_workload_container(  # noqa: E501
        self,
    ):
        self.prepare_workload_for_configuration()
        root = self.harness.get_filesystem_root(WORKLOAD_CONTAINER_NAME)
        (root / "tmp/conf/cu.conf").write_text(
            self._read_file("tests/unit/resources/expected_config.conf").strip()
        )
        config_modification_time = (root / "tmp/conf/du.conf").stat().st_mtime

        self.harness.update_config(key_values={})

        assert (root / "tmp/conf/du.conf").stat().st_mtime == config_modification_time

    def test_given_charm_configuration_is_done_when_config_changed_then_pebble_layer_is_created(
        self,
    ):
        expected_pebble_plan = {
            "services": {
                "du": {
                    "override": "replace",
                    "startup": "enabled",
                    "command": "/opt/oai-gnb/bin/nr-softmodem -O /tmp/conf/du.conf --sa ",
                    "environment": {
                        "TZ": "UTC",
                    },
                },
            },
        }
        self.prepare_workload_for_configuration()
        root = self.harness.get_filesystem_root(WORKLOAD_CONTAINER_NAME)
        (root / "tmp/conf/du.conf").write_text(
            self._read_file("tests/unit/resources/expected_config.conf").strip()
        )

        self.harness.update_config(key_values={})

        updated_plan = self.harness.get_container_pebble_plan(WORKLOAD_CONTAINER_NAME).to_dict()
        assert expected_pebble_plan == updated_plan

    def test_given_charm_configuration_is_done_when_simulation_mode_config_changed_to_true_then_service_startup_command_container_rfsim_flag(  # noqa: E501
        self,
    ):
        expected_pebble_plan = {
            "services": {
                "du": {
                    "override": "replace",
                    "startup": "enabled",
                    "command": "/opt/oai-gnb/bin/nr-softmodem -O /tmp/conf/du.conf --sa --rfsim",
                    "environment": {
                        "TZ": "UTC",
                    },
                },
            },
        }
        self.prepare_workload_for_configuration()
        root = self.harness.get_filesystem_root(WORKLOAD_CONTAINER_NAME)
        (root / "tmp/conf/du.conf").write_text(
            self._read_file("tests/unit/resources/expected_config.conf").strip()
        )

        self.harness.update_config(key_values={"simulation-mode": True})

        updated_plan = self.harness.get_container_pebble_plan(WORKLOAD_CONTAINER_NAME).to_dict()
        assert expected_pebble_plan == updated_plan

    def create_f1_relation(self) -> int:
        """Create a relation between the DU and the CU.

        Returns:
            int: ID of the created relation
        """
        amf_relation_id = self.harness.add_relation(relation_name="fiveg_f1", remote_app="cu")  # type: ignore[attr-defined]  # noqa: E501
        self.harness.add_relation_unit(relation_id=amf_relation_id, remote_unit_name="cu/0")  # type: ignore[attr-defined]  # noqa: E501
        return amf_relation_id

    def set_f1_relation_data(self) -> int:
        """Create the `fiveg_f1` relation, set the relation data and return its ID.

        Returns:
            int: ID of the created relation
        """
        fiveg_f1_relation_id = self.create_f1_relation()
        self.harness.update_relation_data(  # type: ignore[attr-defined]
            relation_id=fiveg_f1_relation_id,
            app_or_unit="cu",
            key_values={
                "f1_ip_address": "4.3.2.1",
                "f1_port": "2153",
            },
        )
        return fiveg_f1_relation_id

    def prepare_workload_for_configuration(self):
        self.mock_du_usb_volume.configure_mock(
            **{
                "is_mounted.return_value": True,
            },
        )
        self.mock_security_context.configure_mock(
            **{
                "is_privileged.return_value": True,
            },
        )
        self.mock_check_output.return_value = b"1.2.3.4"
        self.harness.add_storage("config", attach=True)
        self.set_f1_relation_data()

    @staticmethod
    def _read_file(path: str) -> str:
        """Read a file and returns as a string.

        Args:
            path (str): path to the file.

        Returns:
            str: content of the file.
        """
        with open(path, "r") as f:
            content = f.read()
        return content

#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Module used to set a privileged context for Kubernetes Statefulset containers."""

import logging
from typing import Iterable

from lightkube import Client
from lightkube.core.exceptions import ApiError
from lightkube.models.apps_v1 import StatefulSetSpec
from lightkube.models.core_v1 import Container, HostPathVolumeSource, Volume, VolumeMount
from lightkube.resources.apps_v1 import StatefulSet

logger = logging.getLogger(__name__)


class OAIDUK8sError(Exception):
    """K8sPrivilegedError."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DUSecurityContext:
    """Class used to update Kubernetes Statefulset to run containers in privileged context."""

    def __init__(
        self,
        namespace: str,
        statefulset_name: str,
        container_name: str,
    ):
        self.k8s_client = Client()
        self.statefulset_name = statefulset_name
        self.container_name = container_name
        self.namespace = namespace

    def is_privileged(self) -> bool:
        """Check whether the container in the Statefulset runs in privileged context.

        Returns:
            bool: True if the container is privileged, otherwise False
        """
        try:
            statefulset = self.k8s_client.get(
                res=StatefulSet,
                name=self.statefulset_name,
                namespace=self.namespace,
            )
            container = next(
                filter(
                    lambda ctr: ctr.name == self.container_name,
                    statefulset.spec.template.spec.containers,  # type: ignore[union-attr]
                )
            )
            if not container.securityContext.privileged:
                return False
        except ApiError:
            raise OAIDUK8sError(f"Could not get statefulset {self.statefulset_name}")
        except StopIteration:
            raise OAIDUK8sError(f"Could not get container {self.container_name}")
        return True

    def set_privileged(self) -> None:
        """Patch the Statefulset to run container in privileged context."""
        try:
            statefulset = self.k8s_client.get(
                res=StatefulSet,
                name=self.statefulset_name,
                namespace=self.namespace,
            )
            container = next(
                filter(
                    lambda ctr: ctr.name == self.container_name,
                    statefulset.spec.template.spec.containers,  # type: ignore[union-attr]
                )
            )
            container.securityContext.privileged = True
            self.k8s_client.replace(obj=statefulset)
            logger.info("Container %s patched", self.container_name)
        except ApiError:
            raise OAIDUK8sError(f"Could not get statefulset {self.statefulset_name}")
        except StopIteration:
            raise OAIDUK8sError(f"Could not get container {self.container_name}")


class DUUSBVolume:
    """Class used to mount USB device to the DU container."""

    USB_MOUNT_PATH = "/dev/bus/usb"

    def __init__(
        self,
        namespace: str,
        statefulset_name: str,
        unit_name: str,
        container_name: str,
    ):
        self.k8s_client = Client()
        self.statefulset_name = statefulset_name
        self.unit_name = unit_name
        self.container_name = container_name
        self.namespace = namespace
        self.k8s_client = Client()
        self.usb_volume = Volume(
            name="usb",
            hostPath=HostPathVolumeSource(path=self.USB_MOUNT_PATH, type=""),
        )
        self.usb_volumemount = VolumeMount(
            name=self.usb_volume.name,
            mountPath=self.USB_MOUNT_PATH,
        )

    def is_mounted(self) -> bool:
        """Check whether the USB volume is mounted."""
        return self._container_is_patched() and self._statefulset_is_patched()

    def _container_is_patched(self) -> bool:
        try:
            statefulset = self.k8s_client.get(
                res=StatefulSet, name=self.statefulset_name, namespace=self.namespace
            )
        except ApiError as e:
            if e.status.reason == "Unauthorized":
                logger.debug("kube-apiserver not ready yet")
            else:
                raise OAIDUK8sError(f"Container `{self.container_name}` not found")
            logger.info("Container `%s` not found", self.container_name)
            return False
        pod_has_usb_volumemount = self._pod_has_usb_volumemount(
            usb_volumemount=self.usb_volumemount,
            containers=statefulset.spec.template.spec.containers,  # type: ignore[union-attr]
            container_name=self.container_name,
        )
        logger.info(
            "Container `%s` has USB volume mounted: %s",
            self.container_name,
            pod_has_usb_volumemount,
        )
        return pod_has_usb_volumemount

    def _statefulset_is_patched(self) -> bool:
        try:
            statefulset = self.k8s_client.get(
                res=StatefulSet, name=self.statefulset_name, namespace=self.namespace
            )
        except ApiError as e:
            if e.status.reason == "Unauthorized":
                logger.debug("kube-apiserver not ready yet")
            else:
                raise OAIDUK8sError(f"Could not get statefulset `{self.statefulset_name}`")
            logger.info("Statefulset `%s` not found", self.statefulset_name)
            return False

        statefulset_has_usb_volume = self._statefulset_has_usb_volume(
            statefulset_spec=statefulset.spec,  # type: ignore[arg-type]
            usb_volume=self.usb_volume,
        )
        logger.info(
            "Statefulset `%s` has USB volume: %s",
            self.statefulset_name,
            statefulset_has_usb_volume,
        )
        return statefulset_has_usb_volume

    @staticmethod
    def _statefulset_has_usb_volume(
        statefulset_spec: StatefulSetSpec,
        usb_volume: Volume,
    ) -> bool:
        if not statefulset_spec.template.spec:
            logger.info("Statefulset has no template spec")
            return False
        if not statefulset_spec.template.spec.volumes:
            logger.info("Statefulset has no volumes")
            return False
        return usb_volume in statefulset_spec.template.spec.volumes

    @classmethod
    def _get_container(cls, container_name: str, containers: Iterable[Container]) -> Container:
        try:
            return next(filter(lambda ctr: ctr.name == container_name, containers))
        except StopIteration:
            raise OAIDUK8sError(f"Container `{container_name}` not found")

    def _pod_has_usb_volumemount(
        self,
        containers: Iterable[Container],
        container_name: str,
        usb_volumemount: VolumeMount,
    ) -> bool:
        container = self._get_container(container_name=container_name, containers=containers)
        if not container.volumeMounts:
            return False
        return usb_volumemount in container.volumeMounts

    def mount(self) -> None:
        """Mount USB volume."""
        try:
            statefulset = self.k8s_client.get(
                res=StatefulSet, name=self.statefulset_name, namespace=self.namespace
            )
        except ApiError:
            raise OAIDUK8sError(f"Could not get statefulset `{self.statefulset_name}`")

        containers: Iterable[Container] = statefulset.spec.template.spec.containers  # type: ignore[union-attr]
        container = self._get_container(container_name=self.container_name, containers=containers)
        if not container.volumeMounts:
            container.volumeMounts = [self.usb_volumemount]
        else:
            container.volumeMounts.append(self.usb_volumemount)
        if not statefulset.spec.template.spec.volumes:  # type: ignore[union-attr]
            statefulset.spec.template.spec.volumes = [self.usb_volume]  # type: ignore[union-attr]
        else:
            statefulset.spec.template.spec.volumes.append(self.usb_volume)  # type: ignore[union-attr]
        try:
            self.k8s_client.replace(obj=statefulset)
        except ApiError:
            raise OAIDUK8sError(f"Could not replace statefulset `{self.statefulset_name}`")
        logger.info("Replaced `%s` statefulset", self.statefulset_name)

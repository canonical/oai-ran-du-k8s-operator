#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Module used to set a privileged context for Kubernetes Statefulset containers."""

import logging

from lightkube import Client
from lightkube.core.exceptions import ApiError
from lightkube.resources.apps_v1 import StatefulSet

logger = logging.getLogger(__name__)


class K8sPrivilegedError(Exception):
    """K8sPrivilegedError."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class K8sPrivileged:
    """Class used to update Kubernetes Statefulset to run containers in privileged context."""

    def __init__(
        self,
        namespace: str,
        statefulset_name: str,
    ):
        self.k8s_client = Client()
        self.statefulset_name = statefulset_name
        self.namespace = namespace

    def is_patched(self, container_name: str) -> bool:
        """Check whether the container in the Statefulset runs in privileged context.

        Args:
            container_name (str): Name of the container to check

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
                    lambda ctr: ctr.name == container_name,
                    statefulset.spec.template.spec.containers,  # type: ignore[union-attr]
                )
            )
            if not container.securityContext.privileged:
                return False
        except ApiError:
            raise K8sPrivilegedError(f"Could not get statefulset {self.statefulset_name}")
        except StopIteration:
            raise K8sPrivilegedError(f"Could not get container {container_name}")
        return True

    def patch_statefulset(self, container_name: str) -> None:
        """Patch the Statefulset to run container in privileged context.

        Args:
            container_name (str): Name of the container to check
        """
        try:
            statefulset = self.k8s_client.get(
                res=StatefulSet,
                name=self.statefulset_name,
                namespace=self.namespace,
            )
            container = next(
                filter(
                    lambda ctr: ctr.name == container_name,
                    statefulset.spec.template.spec.containers,  # type: ignore[union-attr]
                )
            )
            container.securityContext.privileged = True
            self.k8s_client.replace(obj=statefulset)
            logger.info("Container %s patched", container_name)
        except ApiError:
            raise K8sPrivilegedError(f"Could not get statefulset {self.statefulset_name}")
        except StopIteration:
            raise K8sPrivilegedError(f"Could not get container {container_name}")

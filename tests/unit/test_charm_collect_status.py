#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import tempfile

import pytest
from ops import testing
from ops.model import ActiveStatus, BlockedStatus, WaitingStatus

from tests.unit.fixtures import F1_PROVIDER_DATA, DUFixtures


class TestCharmCollectStatus(DUFixtures):
    def test_given_unit_is_not_leader_when_collect_status_then_status_is_blocked(self):
        state_in = testing.State(
            leader=False,
        )

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == BlockedStatus("Scaling is not implemented for this charm")

    @pytest.mark.parametrize(
        "config_param,value",
        [
            pytest.param("f1-interface-name", "", id="empty_f1_interface_name"),
            pytest.param("f1-ip-address", "", id="empty_f1_ip-address"),
            pytest.param("f1-ip-address", "5.5.5/3", id="invalid_f1_ip-address"),
            pytest.param("f1-port", int(), id="empty_f1_port"),
        ],
    )
    def test_given_invalid_config_when_collect_status_then_status_is_blocked(
        self, config_param, value
    ):
        state_in = testing.State(
            leader=True,
            config={config_param: value},
        )

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == BlockedStatus(
            f"The following configurations are not valid: ['{config_param}']"
        )

    def test_given_multus_not_available_when_collect_status_then_status_is_blocked(self):
        self.mock_k8s_multus.multus_is_available.return_value = False
        state_in = testing.State(
            leader=True,
        )

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == BlockedStatus("Multus is not installed or enabled")

    def test_given_multus_not_configured_when_collect_status_then_status_is_waiting(
        self,
    ):
        self.mock_k8s_multus.multus_is_available.return_value = True
        self.mock_k8s_multus.is_ready.return_value = False
        state_in = testing.State(
            leader=True,
        )

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == WaitingStatus("Waiting for Multus to be ready")

    def test_given_not_privileged_when_collect_status_then_status_is_waiting(self):
        self.mock_k8s_multus.multus_is_available.return_value = True
        self.mock_k8s_multus.is_ready.return_value = True
        self.mock_du_security_context.is_privileged.return_value = False
        state_in = testing.State(
            leader=True,
        )

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == WaitingStatus("Waiting for statefulset to be patched")

    def test_given_usb_volume_not_mounted_when_collect_status_then_status_is_waiting(self):
        self.mock_k8s_multus.multus_is_available.return_value = True
        self.mock_k8s_multus.is_ready.return_value = True
        self.mock_du_security_context.is_privileged.return_value = True
        self.mock_du_usb_volume.is_mounted.return_value = False
        state_in = testing.State(
            leader=True,
        )

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == WaitingStatus("Waiting for USB device to be mounted")

    def test_given_f1_relation_not_created_when_collect_status_then_status_is_blocked(self):
        self.mock_k8s_multus.multus_is_available.return_value = True
        self.mock_k8s_multus.is_ready.return_value = True
        self.mock_du_security_context.is_privileged.return_value = True
        self.mock_du_usb_volume.is_mounted.return_value = True
        state_in = testing.State(
            leader=True,
        )

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == BlockedStatus("Waiting for F1 relation to be created")

    def test_given_cant_connect_to_container_when_collect_status_then_status_is_waiting(self):
        self.mock_k8s_multus.multus_is_available.return_value = True
        self.mock_k8s_multus.is_ready.return_value = True
        self.mock_du_security_context.is_privileged.return_value = True
        self.mock_du_usb_volume.is_mounted.return_value = True
        f1_relation = testing.Relation(
            endpoint="fiveg_f1",
            interface="fiveg_f1",
        )
        container = testing.Container(
            name="du",
            can_connect=False,
        )
        state_in = testing.State(
            leader=True,
            relations=[f1_relation],
            containers=[container],
        )

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == WaitingStatus("Waiting for container to be ready")

    def test_given_pod_address_not_available_when_collect_status_then_status_is_waiting(self):
        self.mock_k8s_multus.multus_is_available.return_value = True
        self.mock_k8s_multus.is_ready.return_value = True
        self.mock_du_security_context.is_privileged.return_value = True
        self.mock_du_usb_volume.is_mounted.return_value = True
        self.mock_check_output.return_value = b""
        f1_relation = testing.Relation(
            endpoint="fiveg_f1",
            interface="fiveg_f1",
        )
        container = testing.Container(
            name="du",
            can_connect=True,
        )
        state_in = testing.State(
            leader=True,
            relations=[f1_relation],
            containers=[container],
        )

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == WaitingStatus("Waiting for Pod IP address to be available")

    def test_given_config_file_doesnt_exist_when_collect_status_then_status_is_waiting(self):
        self.mock_k8s_multus.multus_is_available.return_value = True
        self.mock_k8s_multus.is_ready.return_value = True
        self.mock_du_security_context.is_privileged.return_value = True
        self.mock_du_usb_volume.is_mounted.return_value = True
        self.mock_check_output.return_value = b"1.2.3.4"
        f1_relation = testing.Relation(
            endpoint="fiveg_f1",
            interface="fiveg_f1",
        )
        container = testing.Container(
            name="du",
            can_connect=True,
        )
        state_in = testing.State(
            leader=True,
            relations=[f1_relation],
            containers=[container],
        )

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == WaitingStatus("Waiting for storage to be attached")

    def test_given_f1_info_unavailable_when_collect_status_then_status_is_waiting(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_k8s_multus.multus_is_available.return_value = True
            self.mock_k8s_multus.is_ready.return_value = True
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_check_output.return_value = b"1.2.3.4"
            self.mock_f1_get_remote_data.return_value = None
            f1_relation = testing.Relation(
                endpoint="fiveg_f1",
                interface="fiveg_f1",
            )
            config_mount = testing.Mount(
                source=temp_dir,
                location="/tmp/conf",
            )
            container = testing.Container(
                name="du",
                can_connect=True,
                mounts={
                    "config": config_mount,
                },
            )
            state_in = testing.State(
                leader=True,
                relations=[f1_relation],
                containers=[container],
            )

            state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

            assert state_out.unit_status == WaitingStatus("Waiting for F1 information")

    def test_given_all_prerequisites_met_when_collect_status_then_status_is_active(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_k8s_multus.multus_is_available.return_value = True
            self.mock_k8s_multus.is_ready.return_value = True
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_check_output.return_value = b"1.2.3.4"
            self.mock_f1_get_remote_data.return_value = F1_PROVIDER_DATA
            f1_relation = testing.Relation(
                endpoint="fiveg_f1",
                interface="fiveg_f1",
            )
            config_mount = testing.Mount(
                source=temp_dir,
                location="/tmp/conf",
            )
            container = testing.Container(
                name="du",
                can_connect=True,
                mounts={
                    "config": config_mount,
                },
            )
            state_in = testing.State(
                leader=True,
                relations=[f1_relation],
                containers=[container],
            )

            state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

            assert state_out.unit_status == ActiveStatus()

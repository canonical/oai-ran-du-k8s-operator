#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import tempfile

import pytest
from ops import testing
from ops.model import ActiveStatus, BlockedStatus, WaitingStatus

from tests.unit.fixtures import F1_PROVIDER_DATA, DUFixtures

SAMPLE_CONFIG = {
    "center-frequency": "3600",
    "bandwidth": 20,
    "frequency-band": 78,
    "sub-carrier-spacing": 15,
}


class TestCharmCollectStatus(DUFixtures):
    def test_given_unit_is_not_leader_when_collect_status_then_status_is_blocked(self):
        state_in = testing.State(
            leader=False,
            config=SAMPLE_CONFIG,
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
    def test_given_invalid_f1_config_when_collect_status_then_status_is_blocked(
        self, config_param, value
    ):
        state_in = testing.State(
            leader=True,
            config={**SAMPLE_CONFIG, config_param: value},
        )

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == BlockedStatus(
            f"The following configurations are not valid: ['{config_param}']"
        )

    @pytest.mark.parametrize(
        "config_param,value",
        [
            pytest.param("center-frequency", "", id="empty_center_frequency"),
            pytest.param("center-frequency", "invalid", id="string_center_frequency"),
            pytest.param("center-frequency", "409", id="too_small_center_frequency"),
            pytest.param("center-frequency", "7126", id="too_big_center_frequency"),
        ],
    )
    def test_given_invalid_center_frequency_when_collect_status_then_status_is_blocked(
        self, config_param, value
    ):
        state_in = testing.State(
            leader=True,
            config={**SAMPLE_CONFIG, config_param: value},
        )
        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)
        assert state_out.unit_status == BlockedStatus(
            f"The following configurations are not valid: ['{config_param}']"
        )

    @pytest.mark.parametrize(
        "config_param,value",
        [
            pytest.param("bandwidth", int(), id="empty_bandwidth"),
            pytest.param("bandwidth", 73, id="not_allowed_bandwidth"),
            pytest.param("bandwidth", 0, id="zero_bandwidth"),
            pytest.param("bandwidth", -1, id="negative_bandwidth"),
        ],
    )
    def test_given_invalid_bandwidth_when_collect_status_then_status_is_blocked(
        self, config_param, value
    ):
        state_in = testing.State(
            leader=True,
            config={**SAMPLE_CONFIG, config_param: value},
        )
        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)
        assert state_out.unit_status == BlockedStatus(
            f"The following configurations are not valid:"
            f" ['{config_param}', 'center-frequency', 'sub-carrier-spacing']"
        )

    @pytest.mark.parametrize(
        "config_param,value",
        [
            pytest.param("frequency-band", int(), id="empty_frequency_band"),
            pytest.param("frequency-band", 0, id="zero_frequency_band"),
            pytest.param("frequency-band", -1, id="negatibe_frequency_band"),
            pytest.param("frequency-band", 120, id="too_high_frequency_band"),
        ],
    )
    def test_given_invalid_frequency_band_when_collect_status_then_status_is_blocked(
        self, config_param, value
    ):
        state_in = testing.State(
            leader=True,
            config={**SAMPLE_CONFIG, config_param: value},
        )
        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)
        assert state_out.unit_status == BlockedStatus(
            f"The following configurations are not valid: "
            f"['center-frequency', '{config_param}', 'sub-carrier-spacing']"
        )

    @pytest.mark.parametrize(
        "config_param,value",
        [
            pytest.param("sub-carrier-spacing", int(), id="empty_sub_carrier_spacing"),
            pytest.param("sub-carrier-spacing", 7, id="too_low_sub_carrier_spacing"),
            pytest.param("sub-carrier-spacing", -1, id="negative_sub_carrier_spacing"),
            pytest.param("sub-carrier-spacing", 240, id="too_large_sub_carrier_spacing"),
        ],
    )
    def test_given_invalid_sub_carrier_spacing_when_collect_status_then_status_is_blocked(
        self, config_param, value
    ):
        state_in = testing.State(
            leader=True,
            config={**SAMPLE_CONFIG, config_param: value},
        )
        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)
        assert state_out.unit_status == BlockedStatus(
            f"The following configurations are not valid: ['{config_param}']"
        )

    def test_given_multus_not_available_when_collect_status_then_status_is_blocked(self):
        self.mock_k8s_multus.multus_is_available.return_value = False
        state_in = testing.State(
            leader=True,
            config=SAMPLE_CONFIG,
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
            config=SAMPLE_CONFIG,
        )

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == WaitingStatus("Waiting for Multus to be ready")

    def test_given_not_privileged_when_collect_status_then_status_is_waiting(self):
        self.mock_k8s_multus.multus_is_available.return_value = True
        self.mock_k8s_multus.is_ready.return_value = True
        self.mock_du_security_context.is_privileged.return_value = False
        state_in = testing.State(
            leader=True,
            config=SAMPLE_CONFIG,
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
            config=SAMPLE_CONFIG,
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
            config=SAMPLE_CONFIG,
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
            config=SAMPLE_CONFIG,
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
            config=SAMPLE_CONFIG,
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
            config=SAMPLE_CONFIG,
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
                config=SAMPLE_CONFIG,
            )

            state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

            assert state_out.unit_status == WaitingStatus("Waiting for F1 information")

    @pytest.mark.parametrize(
        "frequency_band,center_frequency,sub_carrier_spacing,bandwidth",
        [
            pytest.param(34, "2020.21", 15, 5, id="minimum_valid_frequency_band"),
            pytest.param(77, "3500.002", 15, 30, id="midrange_valid_frequency_band"),
            pytest.param(102, "6000", 60, 40, id="maximum_valid_frequency_band"),
        ],
    )
    def test_given_all_prerequisites_met_when_collect_status_then_status_is_active(
        self, frequency_band, center_frequency, sub_carrier_spacing, bandwidth
    ):
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
                config={
                    "frequency-band": frequency_band,
                    "center-frequency": center_frequency,
                    "sub-carrier-spacing": sub_carrier_spacing,
                    "bandwidth": bandwidth,
                },
            )

            state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

            assert state_out.unit_status == ActiveStatus()

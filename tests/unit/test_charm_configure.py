#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import os
import tempfile
from ipaddress import IPv4Address

import pytest
from charms.oai_ran_cu_k8s.v0.fiveg_f1 import PLMNConfig, ProviderAppData
from charms.oai_ran_du_k8s.v0.fiveg_rfsim import LIBAPI
from ops import testing
from ops.pebble import Layer

from tests.unit.fixtures import F1_PROVIDER_DATA, F1_PROVIDER_DATA_WITH_SD, DUFixtures

F1_PROVIDER_DATA_MULTIPLE_PLMNS = ProviderAppData(
    f1_ip_address=IPv4Address("1.2.3.4"),
    f1_port=1234,
    tac=12,
    plmns=[
        PLMNConfig(mcc="999", mnc="99", sst=12),
        PLMNConfig(mcc="001", mnc="01", sst=1, sd=164),
    ],
)
SAMPLE_CONFIG = {
    "bandwidth": 20,
    "frequency-band": 77,
    "sub-carrier-spacing": 15,
    "center-frequency": "3500",
}
INVALID_FIVEG_RFSIM_API_VERSION = str(LIBAPI + 1)


class TestCharmConfigure(DUFixtures):
    def test_given_statefulset_is_not_patched_when_configure_then_usb_is_mounted_and_privileged_context_is_set(  # noqa: E501
        self,
    ):
        self.mock_du_security_context.is_privileged.return_value = False
        self.mock_du_usb_volume.is_mounted.return_value = False
        container = testing.Container(
            name="du",
            can_connect=True,
        )
        state_in = testing.State(
            leader=True,
            containers=[container],
            config=SAMPLE_CONFIG,
        )

        self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

        self.mock_du_security_context.set_privileged.assert_called_once()
        self.mock_du_usb_volume.mount.assert_called_once()

    def test_given_simulation_mode_when_configure_then_privileged_context_is_set_but_usb_is_not_mounted(  # noqa: E501
        self,
    ):
        self.mock_du_security_context.is_privileged.return_value = False
        self.mock_du_usb_volume.is_mounted.return_value = False
        container = testing.Container(
            name="du",
            can_connect=True,
        )
        state_in = testing.State(
            leader=True,
            containers=[container],
            config={**SAMPLE_CONFIG, "simulation-mode": True},
        )

        self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

        self.mock_du_security_context.set_privileged.assert_called_once()
        self.mock_du_usb_volume.mount.assert_not_called()

    def test_given_statefulset_is_patched_when_configure_then_usb_is_not_mounted_and_privileged_context_is_not_set(  # noqa: E501
        self,
    ):
        self.mock_du_security_context.is_privileged.return_value = True
        self.mock_du_usb_volume.is_mounted.return_value = True
        container = testing.Container(
            name="du",
            can_connect=True,
        )
        state_in = testing.State(
            leader=True,
            containers=[container],
            config=SAMPLE_CONFIG,
        )

        self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

        self.mock_du_security_context.set_privileged.assert_not_called()
        self.mock_du_usb_volume.mount.assert_not_called()

    @pytest.mark.parametrize(
        "f1_provider_data,config_file",
        [
            pytest.param(
                F1_PROVIDER_DATA, "tests/unit/resources/expected_config.conf", id="single_plmn"
            ),
            pytest.param(
                F1_PROVIDER_DATA_MULTIPLE_PLMNS,
                "tests/unit/resources/expected_multiple_plmns_config.conf",
                id="two_plmns",
            ),
        ],
    )
    def test_given_workload_is_ready_to_be_configured_when_configure_then_cu_config_file_is_generated_and_pushed_to_the_workload_container(  # noqa: E501
        self, f1_provider_data, config_file
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_get_remote_data.return_value = f1_provider_data
            self.mock_check_output.return_value = b"1.2.3.4"
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
                model=testing.Model(name="whatever"),
                config=SAMPLE_CONFIG,
            )

            self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

            with open(config_file) as expected_config_file:
                expected_config = expected_config_file.read()

            with open(f"{temp_dir}/du.conf") as generated_config_file:
                generated_config = generated_config_file.read()

            assert generated_config.strip() == expected_config.strip()

    def test_given_rf_simulator_mode_when_configure_then_du_config_file_contains_rfsimulator_config(  # noqa: E501
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_get_remote_data.return_value = F1_PROVIDER_DATA
            self.mock_check_output.return_value = b"1.2.3.4"
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
                model=testing.Model(name="whatever"),
                config={**SAMPLE_CONFIG, "simulation-mode": True},
            )

            self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

            with open(
                "tests/unit/resources/expected_rfsim_mode_config.conf"
            ) as expected_config_file:
                expected_config = expected_config_file.read()

            with open(f"{temp_dir}/du.conf") as generated_config_file:
                generated_config = generated_config_file.read()

            assert generated_config.strip() == expected_config.strip()

    def test_given_mimo_mode_when_configure_then_du_config_file_contains_mimo_config(  # noqa: E501
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_get_remote_data.return_value = F1_PROVIDER_DATA
            self.mock_check_output.return_value = b"1.2.3.4"
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
                model=testing.Model(name="whatever"),
                config={**SAMPLE_CONFIG, "use-mimo": True},
            )

            self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

            with open("tests/unit/resources/expected_mimo_config.conf") as expected_config_file:
                expected_config = expected_config_file.read()

            with open(f"{temp_dir}/du.conf") as generated_config_file:
                generated_config = generated_config_file.read()

            assert generated_config.strip() == expected_config.strip()

    def test_given_cu_config_file_is_up_to_date_when_configure_then_cu_config_file_is_not_pushed_to_the_workload_container(  # noqa: E501
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_get_remote_data.return_value = F1_PROVIDER_DATA
            self.mock_check_output.return_value = b"1.2.3.4"
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
                model=testing.Model(name="whatever"),
                config=SAMPLE_CONFIG,
            )
            with open("tests/unit/resources/expected_config.conf") as expected_config_file:
                expected_config = expected_config_file.read().strip()
            with open(f"{temp_dir}/du.conf", "w") as generated_config_file:
                generated_config_file.write(expected_config)
            config_modification_time = os.stat(temp_dir + "/du.conf").st_mtime

            self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

            assert os.stat(temp_dir + "/du.conf").st_mtime == config_modification_time

    def test_given_can_connect_when_configure_then_pebble_layer_is_created(
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_get_remote_data.return_value = F1_PROVIDER_DATA
            self.mock_check_output.return_value = b"1.2.3.4"
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
                model=testing.Model(name="whatever"),
                config=SAMPLE_CONFIG,
            )

            state_out = self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

            container = state_out.get_container("du")
            assert container.layers == {
                "du": Layer(
                    {
                        "services": {
                            "du": {
                                "startup": "enabled",
                                "override": "replace",
                                "command": "/opt/oai-gnb/bin/nr-softmodem -O /tmp/conf/du.conf --continuous-tx ",  # noqa: E501
                                "environment": {"TZ": "UTC"},
                            }
                        }
                    }
                )
            }

    @pytest.mark.parametrize(
        "simulation_mode,three_quarter_sampling,rfsim_flag,three_quarter_sampling_flag",
        [
            pytest.param(
                True, False, "--rfsim", "", id="simulation mode without three quarter sampling"
            ),
            pytest.param(
                False, True, "", "-E ", id="three quarter sampling enabled, simulation mode off"
            ),
            pytest.param(
                True, True, "--rfsim", "-E ", id="simulation mode with three quarter sampling"
            ),
        ],
    )
    def test_given_simulation_mode_three_quarter_sampling_configurations_when_configure_then_service_startup_command_container_includes_correct_flags(  # noqa: E501
        self, simulation_mode, three_quarter_sampling, rfsim_flag, three_quarter_sampling_flag
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_get_remote_data.return_value = F1_PROVIDER_DATA
            self.mock_check_output.return_value = b"1.2.3.4"
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
                model=testing.Model(name="whatever"),
                config={
                    **SAMPLE_CONFIG,
                    "simulation-mode": simulation_mode,
                    "use-three-quarter-sampling": three_quarter_sampling,
                },
            )

            state_out = self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

            container = state_out.get_container("du")
            assert container.layers == {
                "du": Layer(
                    {
                        "services": {
                            "du": {
                                "startup": "enabled",
                                "override": "replace",
                                "command": f"/opt/oai-gnb/bin/nr-softmodem -O /tmp/conf/du.conf {three_quarter_sampling_flag}--continuous-tx {rfsim_flag}",  # noqa: E501
                                "environment": {"TZ": "UTC"},
                            }
                        }
                    }
                )
            }

    def test_given_charm_is_configured_and_running_when_f1_relation_is_added_then_f1_port_is_published(  # noqa: E501
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_get_remote_data.return_value = F1_PROVIDER_DATA
            self.mock_check_output.return_value = b"1.2.3.4"
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
                model=testing.Model(name="whatever"),
                config={**SAMPLE_CONFIG, "simulation-mode": True},
            )

            self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

            self.mock_f1_set_information.assert_called_once_with(port=2152)

    def test_given_charm_is_configured_rfsim_address_is_not_available_and_f1_provider_data_is_available_when_rfsim_relation_is_joined_then_rfsim_information_is_not_published(  # noqa: E501
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_get_remote_data.return_value = F1_PROVIDER_DATA
            self.mock_check_output.return_value = None
            f1_relation = testing.Relation(
                endpoint="fiveg_f1",
                interface="fiveg_f1",
            )
            rfsim_relation = testing.Relation(
                endpoint="fiveg_rfsim",
                interface="fiveg_rfsim",
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
                relations=[f1_relation, rfsim_relation],
                containers=[container],
                model=testing.Model(name="whatever"),
                config={**SAMPLE_CONFIG, "simulation-mode": True},
            )

            self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

            self.mock_rfsim_set_information.assert_not_called()

    def test_given_charm_is_configured_running_and_f1_provider_data_is_not_available_when_rfsim_relation_is_joined_then_rfsim_information_is_not_published(  # noqa: E501
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_get_remote_data.return_value = None
            self.mock_check_output.return_value = b"1.2.3.4"
            f1_relation = testing.Relation(
                endpoint="fiveg_f1",
                interface="fiveg_f1",
            )
            rfsim_relation = testing.Relation(
                endpoint="fiveg_rfsim",
                interface="fiveg_rfsim",
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
                relations=[f1_relation, rfsim_relation],
                containers=[container],
                model=testing.Model(name="whatever"),
                config={**SAMPLE_CONFIG, "simulation-mode": True},
            )

            self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

            self.mock_rfsim_set_information.assert_not_called()

    def test_given_charm_is_configured_running_and_f1_provider_data_includes_multiple_plmns_when_rfsim_relation_is_joined_then_rfsim_information_is_published_with_first_plmn_info(  # noqa: E501
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_get_remote_data.return_value = F1_PROVIDER_DATA_MULTIPLE_PLMNS
            self.mock_check_output.return_value = b"1.2.3.4"
            f1_relation = testing.Relation(
                endpoint="fiveg_f1",
                interface="fiveg_f1",
            )
            rfsim_relation = testing.Relation(
                endpoint="fiveg_rfsim",
                interface="fiveg_rfsim",
                remote_app_data={"version": str(LIBAPI)},
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
                relations=[f1_relation, rfsim_relation],
                containers=[container],
                model=testing.Model(name="whatever"),
                config={**SAMPLE_CONFIG, "simulation-mode": True},
            )

            self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

            self.mock_rfsim_set_information.assert_called_once_with(
                rfsim_address="1.2.3.4",
                sst=12,
                sd=None,
                band=77,
                dl_freq=3499545000,
                carrier_bandwidth=106,
                numerology=0,
                start_subcarrier=525,
            )

    def test_given_charm_is_configured_running_and_f1_relation_is_not_created_when_rfsim_relation_is_joined_then_rfsim_information_is_not_published(  # noqa: E501
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_check_output.return_value = b"1.2.3.4"
            rfsim_relation = testing.Relation(
                endpoint="fiveg_rfsim",
                interface="fiveg_rfsim",
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
                relations=[rfsim_relation],
                containers=[container],
                model=testing.Model(name="whatever"),
                config={**SAMPLE_CONFIG, "simulation-mode": True},
            )

            self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

            self.mock_rfsim_set_information.assert_not_called()

    def test_given_charm_is_configured_running_and_f1_provider_data_is_available_with_sd_when_rfsim_relation_is_joined_then_rfsim_information_is_published_including_sd(  # noqa: E501
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_get_remote_data.return_value = F1_PROVIDER_DATA_WITH_SD
            self.mock_check_output.return_value = b"1.2.3.4"
            f1_relation = testing.Relation(
                endpoint="fiveg_f1",
                interface="fiveg_f1",
            )
            rfsim_relation = testing.Relation(
                endpoint="fiveg_rfsim",
                interface="fiveg_rfsim",
                remote_app_data={"version": str(LIBAPI)},
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
                relations=[f1_relation, rfsim_relation],
                containers=[container],
                model=testing.Model(name="whatever"),
                config={**SAMPLE_CONFIG, "simulation-mode": True},
            )

            self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

            self.mock_rfsim_set_information.assert_called_once_with(
                rfsim_address="1.2.3.4",
                sst=1,
                sd=1,
                band=77,
                dl_freq=3499545000,
                carrier_bandwidth=106,
                numerology=0,
                start_subcarrier=525,
            )

    def test_given_charm_is_configured_running_and_f1_provider_data_is_available_with_sd_when_rfsim_relation_joins_and_requirer_uses_different_api_version_then_rfsim_information_is_not_published(  # noqa: E501
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_get_remote_data.return_value = F1_PROVIDER_DATA_WITH_SD
            self.mock_check_output.return_value = b"1.2.3.4"
            f1_relation = testing.Relation(
                endpoint="fiveg_f1",
                interface="fiveg_f1",
            )
            rfsim_relation = testing.Relation(
                endpoint="fiveg_rfsim",
                interface="fiveg_rfsim",
                remote_app_data={"version": INVALID_FIVEG_RFSIM_API_VERSION},
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
                relations=[f1_relation, rfsim_relation],
                containers=[container],
                model=testing.Model(name="whatever"),
                config={**SAMPLE_CONFIG, "simulation-mode": True},
            )
            self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

            self.mock_rfsim_set_information.assert_not_called()

    def test_given_charm_is_configured_running_and_f1_provider_data_is_available_with_sd_when_rfsim_relation_joins_and_requirer_uses_different_api_version_then_relevant_error_message_is_logged(  # noqa: E501
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_get_remote_data.return_value = F1_PROVIDER_DATA_WITH_SD
            self.mock_check_output.return_value = b"1.2.3.4"
            f1_relation = testing.Relation(
                endpoint="fiveg_f1",
                interface="fiveg_f1",
            )
            rfsim_relation = testing.Relation(
                endpoint="fiveg_rfsim",
                interface="fiveg_rfsim",
                remote_app_data={"version": INVALID_FIVEG_RFSIM_API_VERSION},
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
                relations=[f1_relation, rfsim_relation],
                containers=[container],
                model=testing.Model(name="whatever"),
                config={**SAMPLE_CONFIG, "simulation-mode": True},
            )
            self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

            assert (
                testing.JujuLogLine(
                    level="ERROR",
                    message="Can't establish communication over the `fiveg_rfsim` "
                    "interface due to version mismatch!",
                )
                in self.ctx.juju_log
            )

    def test_given_f1_provider_information_is_no_available_when_pebble_ready_then_config_file_is_not_written(  # noqa: E501
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_get_remote_data.return_value = None
            self.mock_check_output.return_value = b"1.2.3.4"
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
                model=testing.Model(name="whatever"),
                config=SAMPLE_CONFIG,
            )

            self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

            assert not os.path.exists(f"{temp_dir}/du.conf")


class TestCharmDUConfigParams(DUFixtures):
    @pytest.mark.parametrize(
        "frequency_band,center_frequency,sub_carrier_spacing,bandwidth",
        [
            pytest.param(34, "2020.21", 15, 50, id="invalid_bandwidth"),
            pytest.param(27, "3500.002", 15, 30, id="invalid_frequency_band"),
            pytest.param(102, "1000", 60, 40, id="invalid_center_frequency"),
            pytest.param(102, "1000", 80, 40, id="invalid_subcarrier_spacing"),
        ],
    )
    def test_given_invalid_du_config_params_when_config_changed_then_config_file_is_not_written(
        self, frequency_band, center_frequency, sub_carrier_spacing, bandwidth
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_get_remote_data.return_value = None
            self.mock_check_output.return_value = b"1.2.3.4"
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
                model=testing.Model(name="whatever"),
                config={
                    "frequency-band": frequency_band,
                    "center-frequency": center_frequency,
                    "sub-carrier-spacing": sub_carrier_spacing,
                    "bandwidth": bandwidth,
                },
            )

            self.ctx.run(self.ctx.on.pebble_ready(container), state_in)

            assert not os.path.exists(f"{temp_dir}/du.conf")

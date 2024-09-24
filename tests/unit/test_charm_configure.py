#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.


import os
import tempfile

import scenario
from ops.pebble import Layer

from tests.unit.fixtures import DUFixtures


class TestCharmConfigure(DUFixtures):
    def test_given_statefulset_is_not_patched_when_configure_then_usb_is_mounted_and_privileged_context_is_set(  # noqa: E501
        self,
    ):
        self.mock_du_security_context.is_privileged.return_value = False
        self.mock_du_usb_volume.is_mounted.return_value = False
        container = scenario.Container(
            name="du",
            can_connect=True,
        )
        state_in = scenario.State(
            leader=True,
            containers=[container],
        )

        self.ctx.run(container.pebble_ready_event, state_in)

        self.mock_du_security_context.set_privileged.assert_called_once()
        self.mock_du_usb_volume.mount.assert_called_once()

    def test_given_simulation_mode_when_configure_then_privileged_context_is_set_but_usb_is_not_mounted(  # noqa: E501
        self,
    ):
        self.mock_du_security_context.is_privileged.return_value = False
        self.mock_du_usb_volume.is_mounted.return_value = False
        container = scenario.Container(
            name="du",
            can_connect=True,
        )
        state_in = scenario.State(
            leader=True,
            containers=[container],
            config={"simulation-mode": True},
        )

        self.ctx.run(container.pebble_ready_event, state_in)

        self.mock_du_security_context.set_privileged.assert_called_once()
        self.mock_du_usb_volume.mount.assert_not_called()

    def test_given_statefulset_is_patched_when_configure_then_usb_is_not_mounted_and_privileged_context_is_not_set(  # noqa: E501
        self,
    ):
        self.mock_du_security_context.is_privileged.return_value = True
        self.mock_du_usb_volume.is_mounted.return_value = True
        container = scenario.Container(
            name="du",
            can_connect=True,
        )
        state_in = scenario.State(
            leader=True,
            containers=[container],
        )

        self.ctx.run(container.pebble_ready_event, state_in)

        self.mock_du_security_context.set_privileged.assert_not_called()
        self.mock_du_usb_volume.mount.assert_not_called()

    def test_given_workload_is_ready_to_be_configured_when_configure_then_cu_config_file_is_generated_and_pushed_to_the_workload_container(  # noqa: E501
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_requires_f1_ip_address.return_value = "4.3.2.1"
            self.mock_f1_requires_f1_port.return_value = 2152
            self.mock_check_output.return_value = b"1.2.3.4"
            f1_relation = scenario.Relation(
                endpoint="fiveg_f1",
                interface="fiveg_f1",
            )
            config_mount = scenario.Mount(
                src=temp_dir,
                location="/tmp/conf",
            )
            container = scenario.Container(
                name="du",
                can_connect=True,
                mounts={
                    "config": config_mount,
                },
            )
            state_in = scenario.State(
                leader=True,
                relations=[f1_relation],
                containers=[container],
                model=scenario.Model(name="whatever"),
            )

            self.ctx.run(container.pebble_ready_event, state_in)

            with open("tests/unit/resources/expected_config.conf") as expected_config_file:
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
            self.mock_f1_requires_f1_ip_address.return_value = "4.3.2.1"
            self.mock_f1_requires_f1_port.return_value = 2152
            self.mock_check_output.return_value = b"1.2.3.4"
            f1_relation = scenario.Relation(
                endpoint="fiveg_f1",
                interface="fiveg_f1",
            )
            config_mount = scenario.Mount(
                src=temp_dir,
                location="/tmp/conf",
            )
            container = scenario.Container(
                name="du",
                can_connect=True,
                mounts={
                    "config": config_mount,
                },
            )
            state_in = scenario.State(
                leader=True,
                relations=[f1_relation],
                containers=[container],
                model=scenario.Model(name="whatever"),
                config={"simulation-mode": True},
            )

            self.ctx.run(container.pebble_ready_event, state_in)

            with open(
                "tests/unit/resources/expected_rfsim_mode_config.conf"
            ) as expected_config_file:
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
            self.mock_f1_requires_f1_ip_address.return_value = "4.3.2.1"
            self.mock_f1_requires_f1_port.return_value = 2152
            self.mock_check_output.return_value = b"1.2.3.4"
            f1_relation = scenario.Relation(
                endpoint="fiveg_f1",
                interface="fiveg_f1",
            )
            config_mount = scenario.Mount(
                src=temp_dir,
                location="/tmp/conf",
            )
            container = scenario.Container(
                name="du",
                can_connect=True,
                mounts={
                    "config": config_mount,
                },
            )
            state_in = scenario.State(
                leader=True,
                relations=[f1_relation],
                containers=[container],
                model=scenario.Model(name="whatever"),
            )
            with open("tests/unit/resources/expected_config.conf") as expected_config_file:
                expected_config = expected_config_file.read()
            with open(f"{temp_dir}/du.conf", "w") as generated_config_file:
                generated_config_file.write(expected_config)
            config_modification_time = os.stat(temp_dir + "/du.conf").st_mtime

            self.ctx.run(container.pebble_ready_event, state_in)

            assert os.stat(temp_dir + "/du.conf").st_mtime == config_modification_time

    def test_given_can_connect_when_configure_then_pebble_layer_is_created(
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_requires_f1_ip_address.return_value = "4.3.2.1"
            self.mock_f1_requires_f1_port.return_value = 2152
            self.mock_check_output.return_value = b"1.2.3.4"
            f1_relation = scenario.Relation(
                endpoint="fiveg_f1",
                interface="fiveg_f1",
            )
            config_mount = scenario.Mount(
                src=temp_dir,
                location="/tmp/conf",
            )
            container = scenario.Container(
                name="du",
                can_connect=True,
                mounts={
                    "config": config_mount,
                },
            )
            state_in = scenario.State(
                leader=True,
                relations=[f1_relation],
                containers=[container],
                model=scenario.Model(name="whatever"),
            )

            state_out = self.ctx.run(container.pebble_ready_event, state_in)

            assert state_out.containers[0].layers == {
                "du": Layer(
                    {
                        "services": {
                            "du": {
                                "startup": "enabled",
                                "override": "replace",
                                "command": "/opt/oai-gnb/bin/nr-softmodem -O /tmp/conf/du.conf -E --sa ",  # noqa: E501
                                "environment": {"TZ": "UTC"},
                            }
                        }
                    }
                )
            }

    def test_given_simulation_mode_when_configure_then_service_startup_command_container_rfsim_flag(  # noqa: E501
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_requires_f1_ip_address.return_value = "4.3.2.1"
            self.mock_f1_requires_f1_port.return_value = 2152
            self.mock_check_output.return_value = b"1.2.3.4"
            f1_relation = scenario.Relation(
                endpoint="fiveg_f1",
                interface="fiveg_f1",
            )
            config_mount = scenario.Mount(
                src=temp_dir,
                location="/tmp/conf",
            )
            container = scenario.Container(
                name="du",
                can_connect=True,
                mounts={
                    "config": config_mount,
                },
            )
            state_in = scenario.State(
                leader=True,
                relations=[f1_relation],
                containers=[container],
                model=scenario.Model(name="whatever"),
                config={"simulation-mode": True},
            )

            state_out = self.ctx.run(container.pebble_ready_event, state_in)

            assert state_out.containers[0].layers == {
                "du": Layer(
                    {
                        "services": {
                            "du": {
                                "startup": "enabled",
                                "override": "replace",
                                "command": "/opt/oai-gnb/bin/nr-softmodem -O /tmp/conf/du.conf -E --sa --rfsim",  # noqa: E501
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
            self.mock_f1_requires_f1_ip_address.return_value = "4.3.2.1"
            self.mock_f1_requires_f1_port.return_value = 2152
            self.mock_check_output.return_value = b"1.2.3.4"
            f1_relation = scenario.Relation(
                endpoint="fiveg_f1",
                interface="fiveg_f1",
            )
            config_mount = scenario.Mount(
                src=temp_dir,
                location="/tmp/conf",
            )
            container = scenario.Container(
                name="du",
                can_connect=True,
                mounts={
                    "config": config_mount,
                },
            )
            state_in = scenario.State(
                leader=True,
                relations=[f1_relation],
                containers=[container],
                model=scenario.Model(name="whatever"),
                config={"simulation-mode": True},
            )

            self.ctx.run(container.pebble_ready_event, state_in)

            self.mock_f1_set_information.assert_called_once_with(port=2152)

    def test_given_charm_is_configured_and_running_when_rfsim_relation_is_joined_then_rfsim_information_is_published(  # noqa: E501
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_du_usb_volume.is_mounted.return_value = True
            self.mock_f1_requires_f1_ip_address.return_value = "4.3.2.1"
            self.mock_f1_requires_f1_port.return_value = 2153
            self.mock_check_output.return_value = b"1.2.3.4"
            f1_relation = scenario.Relation(
                endpoint="fiveg_f1",
                interface="fiveg_f1",
            )
            rfsim_relation = scenario.Relation(
                endpoint="fiveg_rfsim",
                interface="fiveg_rfsim",
            )
            config_mount = scenario.Mount(
                src=temp_dir,
                location="/tmp/conf",
            )
            container = scenario.Container(
                name="du",
                can_connect=True,
                mounts={
                    "config": config_mount,
                },
            )
            state_in = scenario.State(
                leader=True,
                relations=[f1_relation, rfsim_relation],
                containers=[container],
                model=scenario.Model(name="whatever"),
                config={"simulation-mode": True},
            )

            self.ctx.run(container.pebble_ready_event, state_in)

            self.mock_rfsim_set_information.assert_called_once_with("1.2.3.4")

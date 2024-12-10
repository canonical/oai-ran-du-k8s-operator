# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.


import tempfile

from ops import testing
from ops.pebble import Layer, ServiceStatus

from tests.unit.fixtures import F1_PROVIDER_DATA_WITH_SD, DUFixtures


class TestCharmFivegRFSIMRelationChanged(DUFixtures):
    def test_given_f1_relation_exists_service_not_running_when_fiveg_rfsim_relation_changed_then_rfsim_information_is_not_in_relation_databag(  # noqa: E501
        self,
    ):
        f1_relation = testing.Relation(endpoint="fiveg_f1", interface="fiveg_f1")
        fiveg_rfsim_relation = testing.Relation(endpoint="fiveg_rfsim", interface="fiveg_rfsim")
        container = testing.Container(name="du", can_connect=True)
        state_in = testing.State(
            leader=True,
            containers=[container],
            relations=[fiveg_rfsim_relation, f1_relation],
        )
        self.mock_check_output.return_value = b"1.2.3.4"

        state_out = self.ctx.run(self.ctx.on.relation_changed(fiveg_rfsim_relation), state_in)

        relation = state_out.get_relation(fiveg_rfsim_relation.id)
        assert relation.local_app_data == {}

    def test_given_given_service_is_running_and_f1_relation_joined_and_remote_network_information_exists_when_fiveg_rfsim_relation_changed_then_rfsim_information_is_in_relation_databag(  # noqa: E501
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
            fiveg_rfsim_relation = testing.Relation(
                endpoint="fiveg_rfsim",
                interface="fiveg_rfsim",
                local_app_data={"rfsim_address": "1.2.3.4", "sst": "1", "sd": "1"},
            )
            config_mount = testing.Mount(
                source=temp_dir,
                location="/tmp/conf",
            )
            container = testing.Container(
                name="du",
                can_connect=True,
                layers={
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
                },
                service_statuses={"du": ServiceStatus.ACTIVE},
                mounts={
                    "config": config_mount,
                },
            )
            state_in = testing.State(
                leader=True,
                relations=[f1_relation, fiveg_rfsim_relation],
                containers=[container],
                model=testing.Model(name="whatever"),
                config={"simulation-mode": True},
            )

            state_out = self.ctx.run(self.ctx.on.relation_changed(fiveg_rfsim_relation), state_in)
            relation = state_out.get_relation(fiveg_rfsim_relation.id)
            assert relation.local_app_data == {"rfsim_address": "1.2.3.4", "sst": "1", "sd": "1"}

    def test_given_given_service_is_running_and_f1_relation_does_not_exist_when_fiveg_rfsim_relation_changed_then_rfsim_information_is_not_in_relation_databag(  # noqa: E501
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.mock_du_security_context.is_privileged.return_value = True
            self.mock_check_output.return_value = b"1.2.3.4"
            fiveg_rfsim_relation = testing.Relation(
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
                layers={
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
                },
                service_statuses={"du": ServiceStatus.ACTIVE},
                mounts={
                    "config": config_mount,
                },
            )
            state_in = testing.State(
                leader=True,
                relations=[fiveg_rfsim_relation],
                containers=[container],
                model=testing.Model(name="whatever"),
                config={"simulation-mode": True},
            )

            state_out = self.ctx.run(self.ctx.on.relation_changed(fiveg_rfsim_relation), state_in)
            relation = state_out.get_relation(fiveg_rfsim_relation.id)
            assert relation.local_app_data == {}

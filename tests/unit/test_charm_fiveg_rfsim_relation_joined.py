# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.


import tempfile

import scenario
from ops.pebble import Layer, ServiceStatus

from tests.unit.fixtures import DUFixtures


class TestCharmFivegRFSIMRelationJoined(DUFixtures):
    def test_given_service_not_running_when_fiveg_rfsim_relation_joined_then_rfsim_information_is_not_in_relation_databag(  # noqa: E501
        self,
    ):
        fiveg_rfsim_relation = scenario.Relation(endpoint="fiveg_rfsim", interface="fiveg_rfsim")
        container = scenario.Container(name="du", can_connect=True)
        state_in = scenario.State(
            leader=True,
            containers=[container],
            relations=[fiveg_rfsim_relation],
        )
        self.mock_check_output.return_value = b"1.2.3.4"
        self.mock_k8s_service_patch.get_ip.return_value = "1.2.3.4"

        state_out = self.ctx.run(fiveg_rfsim_relation.joined_event, state_in)

        assert state_out.relations[0].local_app_data == {}

    def test_given_given_service_is_running_when_fiveg_rfsim_relation_joined_then_rfsim_information_is_in_relation_databag(  # noqa: E501
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
            fiveg_rfsim_relation = scenario.Relation(
                endpoint="fiveg_rfsim",
                interface="fiveg_rfsim",
                local_app_data={"rfsim_address": "1.2.3.4"},
            )
            config_mount = scenario.Mount(
                src=temp_dir,
                location="/tmp/conf",
            )
            container = scenario.Container(
                name="du",
                can_connect=True,
                layers={
                    "du": Layer(
                        {
                            "services": {
                                "du": {
                                    "startup": "enabled",
                                    "override": "replace",
                                    "command": "/opt/oai-gnb/bin/nr-softmodem -O /tmp/conf/du.conf -E --sa ",  # noqa: E501
                                    # noqa: E501
                                    "environment": {"TZ": "UTC"},
                                }
                            }
                        }
                    )
                },
                service_status={"du": ServiceStatus.ACTIVE},
                mounts={
                    "config": config_mount,
                },
            )
            state_in = scenario.State(
                leader=True,
                relations=[f1_relation, fiveg_rfsim_relation],
                containers=[container],
                model=scenario.Model(name="whatever"),
                config={"simulation-mode": True},
            )
            self.mock_rfsim_set_information.return_value = "1.2.3.4"

            state_out = self.ctx.run(fiveg_rfsim_relation.joined_event, state_in)

            assert state_out.relations[1].local_app_data == {"rfsim_address": "1.2.3.4"}

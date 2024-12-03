# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.


import pytest
from ops import testing

from tests.unit.lib.charms.oai_ran_du.v0.test_charms.test_requirer_charm.src.charm import (
    DummyFivegRFSIMRequires,
)

VALID_RFSIM_ADDRESS = "192.168.70.130"
VALID_SST = "1"
VALID_SD = "1"


class TestFivegRFSIMRequires:
    @pytest.fixture(autouse=True)
    def context(self):
        self.ctx = testing.Context(
            charm_type=DummyFivegRFSIMRequires,
            meta={
                "name": "rfsim-requirer-charm",
                "requires": {"fiveg_rfsim": {"interface": "fiveg_rfsim"}},
            },
            actions={
                "get-rfsim-information": {
                    "params": {
                        "expected_rfsim_address": {"type": "string"},
                        "expected_sst": {"type": "integer"},
                        "expected_sd": {"type": "integer"},
                    }
                },
                "get-rfsim-information-invalid": {"params": {}},
            },
        )

    def test_given_rfsim_information_in_relation_data_when_get_rfsim_information_is_called_then_information_is_returned(  # noqa: E501
        self,
    ):
        fiveg_rfsim_relation = testing.Relation(
            endpoint="fiveg_rfsim",
            interface="fiveg_rfsim",
            remote_app_data={
                "rfsim_address": VALID_RFSIM_ADDRESS,
                "sst": VALID_SST,
                "sd": VALID_SD,
            },
        )
        state_in = testing.State(
            leader=True,
            relations=[fiveg_rfsim_relation],
        )
        params = {
            "expected_rfsim_address": VALID_RFSIM_ADDRESS,
            "expected_sst": int(VALID_SST),
            "expected_sd": int(VALID_SD),
        }
        self.ctx.run(self.ctx.on.action("get-rfsim-information", params=params), state_in)

    @pytest.mark.parametrize(
        "remote_data",
        [
            pytest.param(
                {
                    "rfsim_address": "1111",
                    "sst": VALID_SST,
                    "sd": VALID_SD,
                },
                id="invalid_rfsim_address",
            ),
            pytest.param(
                {
                    "rfsim_address": VALID_RFSIM_ADDRESS,
                    "sst": "",
                    "sd": VALID_SD,
                },
                id="empty_sst",
            ),
        ],
    )
    def test_given_invalid_remote_databag_when_get_rfsim_information_is_called_then_none_is_retrieved(  # noqa: E501
        self, remote_data
    ):
        fiveg_rfsim_relation = testing.Relation(
            endpoint="fiveg_rfsim",
            interface="fiveg_rfsim",
            remote_app_data=remote_data,
        )
        state_in = testing.State(
            leader=True,
            relations=[fiveg_rfsim_relation],
        )
        self.ctx.run(self.ctx.on.action("get-rfsim-information-invalid", params={}), state_in)

    def test_given_rfsim_relation_does_not_exist_when_get_rfsim_information_then_none_is_retrieved(
        self,
    ):  # noqa: E501
        state_in = testing.State(relations=[], leader=True)

        self.ctx.run(self.ctx.on.action("get-rfsim-information-invalid", params={}), state_in)

    def test_given_charm_is_not_leader_when_get_rfsim_information_then_none_is_retrieved(self):
        state_in = testing.State(relations=[], leader=False)

        self.ctx.run(self.ctx.on.action("get-rfsim-information-invalid", params={}), state_in)

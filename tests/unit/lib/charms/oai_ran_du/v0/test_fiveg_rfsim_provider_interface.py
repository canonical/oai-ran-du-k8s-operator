# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest
from ops import testing

from tests.unit.lib.charms.oai_ran_du.v0.test_charms.test_provider_charm.src.charm import (
    DummyFivegRFSIMProviderCharm,
)

VALID_RFSIM_ADDRESS = "192.168.70.130"
VALID_SST = "1"
VALID_SD = "1"


class TestFivegRFSIMProvides:
    @pytest.fixture(autouse=True)
    def context(self):
        self.ctx = testing.Context(
            charm_type=DummyFivegRFSIMProviderCharm,
            meta={
                "name": "rfsim-provider-charm",
                "provides": {"fiveg_rfsim": {"interface": "fiveg_rfsim"}},
            },
            actions={
                "set-rfsim-information": {
                    "params": {
                        "rfsim_address": {"type": "string"},
                        "sst": {"type": "string"},
                        "sd": {"type": "string"},
                    }
                },
                "set-rfsim-information-as-string": {
                    "params": {
                        "rfsim_address": {"type": "string"},
                        "sst": {"type": "string"},
                        "sd": {"type": "string"},
                    }
                },
            },
        )

    def test_given_valid_rfsim_interface_data_when_set_rfsim_information_then_rfsim_address_is_pushed_to_the_relation_databag(  # noqa: E501
        self,
    ):
        fiveg_rfsim_relation = testing.Relation(
            endpoint="fiveg_rfsim",
            interface="fiveg_rfsim",
        )
        state_in = testing.State(
            relations=[fiveg_rfsim_relation],
            leader=True,
        )
        params = {
            "rfsim_address": VALID_RFSIM_ADDRESS,
            "sst": VALID_SST,
            "sd": VALID_SD,
        }

        state_out = self.ctx.run(
            self.ctx.on.action("set-rfsim-information", params=params), state_in
        )

        relation = state_out.get_relation(fiveg_rfsim_relation.id)
        assert relation.local_app_data["rfsim_address"] == VALID_RFSIM_ADDRESS
        assert relation.local_app_data["sst"] == VALID_SST
        assert relation.local_app_data["sd"] == VALID_SD

    def test_given_no_sd_when_set_rfsim_information_then_rfsim_data_is_pushed_to_the_relation_databag_without_sd(  # noqa: E501
        self,
    ):
        fiveg_rfsim_relation = testing.Relation(
            endpoint="fiveg_rfsim",
            interface="fiveg_rfsim",
        )
        state_in = testing.State(
            relations=[fiveg_rfsim_relation],
            leader=True,
        )
        params = {
            "rfsim_address": VALID_RFSIM_ADDRESS,
            "sst": VALID_SST,
        }

        state_out = self.ctx.run(
            self.ctx.on.action("set-rfsim-information", params=params), state_in
        )

        relation = state_out.get_relation(fiveg_rfsim_relation.id)
        assert relation.local_app_data["rfsim_address"] == VALID_RFSIM_ADDRESS
        assert relation.local_app_data["sst"] == VALID_SST
        assert relation.local_app_data.get("sd") is None

    @pytest.mark.parametrize(
        "rfsim_address",
        [
            pytest.param("1111", id="invalid_rfsim_address"),
            pytest.param("", id="empty_rfsim_address"),
        ],
    )
    def test_given_invalid_rfsim_address_when_set_rfsim_information_then_error_is_raised(
        self, rfsim_address
    ):
        fiveg_rfsim_relation = testing.Relation(
            endpoint="fiveg_rfsim",
            interface="fiveg_rfsim",
        )
        state_in = testing.State(
            relations=[fiveg_rfsim_relation],
            leader=True,
        )
        params = {
            "rfsim_address": rfsim_address,
            "sst": VALID_SST,
            "sd": VALID_SD,
        }

        with pytest.raises(Exception) as e:
            self.ctx.run(self.ctx.on.action("set-rfsim-information", params=params), state_in)

        assert "Invalid relation data" in str(e.value)

    @pytest.mark.parametrize(
        "sst,sd",
        [
            pytest.param(VALID_SST, "-1", id="too_small_sd"),
            pytest.param(VALID_SST, "16777216", id="too_large_sd"),
            pytest.param("-1", VALID_SD, id="too_small_sst"),
            pytest.param("256", VALID_SD, id="too_large_sst"),
        ],
    )
    def test_given_invalid_sst_and_sd_when_set_rfsim_information_then_error_is_raised(
        self, sst, sd
    ):
        fiveg_rfsim_relation = testing.Relation(
            endpoint="fiveg_rfsim",
            interface="fiveg_rfsim",
        )
        state_in = testing.State(
            relations=[fiveg_rfsim_relation],
            leader=True,
        )
        params = {
            "rfsim_address": VALID_RFSIM_ADDRESS,
            "sst": sst,
            "sd": sd,
        }

        with pytest.raises(Exception) as e:
            self.ctx.run(self.ctx.on.action("set-rfsim-information", params=params), state_in)

        assert "Invalid relation data" in str(e.value)

    def test_given_unit_is_not_leader_when_fiveg_rfsim_relation_joined_then_data_is_not_in_application_databag(  # noqa: E501
        self,
    ):
        fiveg_rfsim_relation = testing.Relation(
            endpoint="fiveg_rfsim",
            interface="fiveg_rfsim",
        )
        state_in = testing.State(
            leader=False,
            relations=[fiveg_rfsim_relation],
        )
        params = {
            "rfsim_address": VALID_RFSIM_ADDRESS,
            "sst": VALID_SST,
            "sd": VALID_SD,
        }

        with pytest.raises(Exception) as e:
            self.ctx.run(self.ctx.on.action("set-rfsim-information", params=params), state_in)

        assert "Unit must be leader" in str(e.value)

    def test_given_rfsim_relation_does_not_exist_when_set_rfsim_information_then_error_is_raised(  # noqa: E501
        self,
    ):
        state_in = testing.State(relations=[], leader=True)
        params = {
            "rfsim_address": VALID_RFSIM_ADDRESS,
            "sst": VALID_SST,
            "sd": VALID_SD,
        }

        with pytest.raises(Exception) as e:
            self.ctx.run(self.ctx.on.action("set-rfsim-information", params=params), state_in)

        assert "Relation fiveg_rfsim not created yet." in str(e.value)

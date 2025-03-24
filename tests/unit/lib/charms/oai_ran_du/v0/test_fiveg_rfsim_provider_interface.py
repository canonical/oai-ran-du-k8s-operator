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
VALID_BAND = "78"
VALID_DL_FREQ = "4059090000"
VALID_CARRIER_BANDWIDTH = "106"
VALID_NUMEROLOGY = "1"
VALID_START_SUBCARRIER = "541"


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
                        "band": {"type": "string"},
                        "dl_freq": {"type": "string"},
                        "carrier_bandwidth": {"type": "string"},
                        "numerology": {"type": "string"},
                        "start_subcarrier": {"type": "string"},
                    }
                },
                "set-rfsim-information-as-string": {
                    "params": {
                        "rfsim_address": {"type": "string"},
                        "sst": {"type": "string"},
                        "sd": {"type": "string"},
                        "band": {"type": "string"},
                        "dl_freq": {"type": "string"},
                        "carrier_bandwidth": {"type": "string"},
                        "numerology": {"type": "string"},
                        "start_subcarrier": {"type": "string"},
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
            "band": VALID_BAND,
            "dl_freq": VALID_DL_FREQ,
            "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
            "numerology": VALID_NUMEROLOGY,
            "start_subcarrier": VALID_START_SUBCARRIER,
        }

        state_out = self.ctx.run(
            self.ctx.on.action("set-rfsim-information", params=params), state_in
        )

        relation = state_out.get_relation(fiveg_rfsim_relation.id)
        assert relation.local_app_data["rfsim_address"] == VALID_RFSIM_ADDRESS
        assert relation.local_app_data["sst"] == VALID_SST
        assert relation.local_app_data["sd"] == VALID_SD
        assert relation.local_app_data["band"] == VALID_BAND
        assert relation.local_app_data["dl_freq"] == VALID_DL_FREQ
        assert relation.local_app_data["carrier_bandwidth"] == VALID_CARRIER_BANDWIDTH
        assert relation.local_app_data["numerology"] == VALID_NUMEROLOGY
        assert relation.local_app_data["start_subcarrier"] == VALID_START_SUBCARRIER

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
            "band": VALID_BAND,
            "dl_freq": VALID_DL_FREQ,
            "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
            "numerology": VALID_NUMEROLOGY,
            "start_subcarrier": VALID_START_SUBCARRIER,
        }

        state_out = self.ctx.run(
            self.ctx.on.action("set-rfsim-information", params=params), state_in
        )

        relation = state_out.get_relation(fiveg_rfsim_relation.id)
        assert relation.local_app_data["rfsim_address"] == VALID_RFSIM_ADDRESS
        assert relation.local_app_data["sst"] == VALID_SST
        assert relation.local_app_data.get("sd") is None
        assert relation.local_app_data["band"] == VALID_BAND
        assert relation.local_app_data["dl_freq"] == VALID_DL_FREQ
        assert relation.local_app_data["carrier_bandwidth"] == VALID_CARRIER_BANDWIDTH
        assert relation.local_app_data["numerology"] == VALID_NUMEROLOGY
        assert relation.local_app_data["start_subcarrier"] == VALID_START_SUBCARRIER

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
            "band": VALID_BAND,
            "dl_freq": VALID_DL_FREQ,
            "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
            "numerology": VALID_NUMEROLOGY,
            "start_subcarrier": VALID_START_SUBCARRIER,
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
            "band": VALID_BAND,
            "dl_freq": VALID_DL_FREQ,
            "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
            "numerology": VALID_NUMEROLOGY,
            "start_subcarrier": VALID_START_SUBCARRIER,
        }

        with pytest.raises(Exception) as e:
            self.ctx.run(self.ctx.on.action("set-rfsim-information", params=params), state_in)

        assert "Invalid relation data" in str(e.value)

    @pytest.mark.parametrize(
        "band",
        [
            pytest.param("-1", id="rf_band_negative_numer"),
            pytest.param("0", id="rf_band_is_0"),
        ],
    )
    def test_given_invalid_rf_band_when_set_rfsim_information_then_error_is_raised(self, band):
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
            "band": band,
            "dl_freq": VALID_DL_FREQ,
            "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
            "numerology": VALID_NUMEROLOGY,
            "start_subcarrier": VALID_START_SUBCARRIER,
        }

        with pytest.raises(Exception) as e:
            self.ctx.run(self.ctx.on.action("set-rfsim-information", params=params), state_in)

        assert "Invalid relation data" in str(e.value)

    @pytest.mark.parametrize(
        "dl_freq",
        [
            pytest.param("-1", id="dl_freq_negative_numer"),
            pytest.param("0", id="dl_freq_is_0"),
            pytest.param("1234567", id="dl_freq_below_410_mhz"),
        ],
    )
    def test_given_invalid_dl_freq_when_set_rfsim_information_then_error_is_raised(self, dl_freq):
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
            "band": VALID_BAND,
            "dl_freq": dl_freq,
            "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
            "numerology": VALID_NUMEROLOGY,
            "start_subcarrier": VALID_START_SUBCARRIER,
        }

        with pytest.raises(Exception) as e:
            self.ctx.run(self.ctx.on.action("set-rfsim-information", params=params), state_in)

        assert "Invalid relation data" in str(e.value)

    @pytest.mark.parametrize(
        "carrier_bandwidth",
        [
            pytest.param("-1", id="carrier_bandwidth_negative_numer"),
            pytest.param("10", id="carrier_bandwidth_below_11"),
            pytest.param("274", id="carrier_bandwidth_above_273"),
        ],
    )
    def test_given_invalid_carrier_bandwidth_when_set_rfsim_information_then_error_is_raised(
        self, carrier_bandwidth
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
            "band": VALID_BAND,
            "dl_freq": VALID_DL_FREQ,
            "carrier_bandwidth": carrier_bandwidth,
            "numerology": VALID_NUMEROLOGY,
            "start_subcarrier": VALID_START_SUBCARRIER,
        }

        with pytest.raises(Exception) as e:
            self.ctx.run(self.ctx.on.action("set-rfsim-information", params=params), state_in)

        assert "Invalid relation data" in str(e.value)

    @pytest.mark.parametrize(
        "numerology",
        [
            pytest.param("-1", id="numerology_negative_numer"),
            pytest.param("7", id="numerology_above_6"),
        ],
    )
    def test_given_invalid_numerology_when_set_rfsim_information_then_error_is_raised(
        self, numerology
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
            "band": VALID_BAND,
            "dl_freq": VALID_DL_FREQ,
            "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
            "numerology": numerology,
            "start_subcarrier": VALID_START_SUBCARRIER,
        }

        with pytest.raises(Exception) as e:
            self.ctx.run(self.ctx.on.action("set-rfsim-information", params=params), state_in)

        assert "Invalid relation data" in str(e.value)

    def test_given_invalid_start_subcarrier_when_set_rfsim_information_then_error_is_raised(self):
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
            "band": VALID_BAND,
            "dl_freq": VALID_DL_FREQ,
            "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
            "numerology": VALID_NUMEROLOGY,
            "start_subcarrier": "-1",
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
            "band": VALID_BAND,
            "dl_freq": VALID_DL_FREQ,
            "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
            "numerology": VALID_NUMEROLOGY,
            "start_subcarrier": VALID_START_SUBCARRIER,
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
            "band": VALID_BAND,
            "dl_freq": VALID_DL_FREQ,
            "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
            "numerology": VALID_NUMEROLOGY,
            "start_subcarrier": VALID_START_SUBCARRIER,
        }

        with pytest.raises(Exception) as e:
            self.ctx.run(self.ctx.on.action("set-rfsim-information", params=params), state_in)

        assert "Relation fiveg_rfsim not created yet." in str(e.value)

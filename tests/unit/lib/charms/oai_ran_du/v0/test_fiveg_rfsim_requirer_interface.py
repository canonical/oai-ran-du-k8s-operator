# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.


import pytest
from ops import testing

from tests.unit.lib.charms.oai_ran_du.v0.test_charms.test_requirer_charm.src.charm import (
    DummyFivegRFSIMRequires,
)

VALID_INTERFACE_VERSION = "0"
VALID_RFSIM_ADDRESS = "192.168.70.130"
VALID_SST = "1"
VALID_SD = "1"
VALID_BAND = "78"
VALID_DL_FREQ = "4059090000"
VALID_CARRIER_BANDWIDTH = "106"
VALID_NUMEROLOGY = "1"
VALID_START_SUBCARRIER = "541"


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
                        "expected_version": {"type": "integer"},
                        "expected_rfsim_address": {"type": "string"},
                        "expected_sst": {"type": "integer"},
                        "expected_sd": {"type": "integer"},
                        "expected_band": {"type": "integer"},
                        "expected_dl_freq": {"type": "integer"},
                        "expected_carrier_bandwidth": {"type": "integer"},
                        "expected_numerology": {"type": "integer"},
                        "expected_start_subcarrier": {"type": "integer"},
                    }
                },
                "get-rfsim-information-invalid": {"params": {}},
            },
        )

    @pytest.mark.parametrize(
        "remote_data,expected_version,expected_rfsim_address,expected_sst,expected_sd,expected_band,expected_dl_freq,expected_carrier_bandwidth,expected_numerology,expected_start_subcarrier",
        [
            pytest.param(
                {
                    "version": VALID_INTERFACE_VERSION,
                    "rfsim_address": VALID_RFSIM_ADDRESS,
                    "sst": VALID_SST,
                    "sd": VALID_SD,
                    "band": VALID_BAND,
                    "dl_freq": VALID_DL_FREQ,
                    "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
                    "numerology": VALID_NUMEROLOGY,
                    "start_subcarrier": VALID_START_SUBCARRIER,
                },
                int(VALID_INTERFACE_VERSION),
                VALID_RFSIM_ADDRESS,
                int(VALID_SST),
                int(VALID_SD),
                int(VALID_BAND),
                int(VALID_DL_FREQ),
                int(VALID_CARRIER_BANDWIDTH),
                int(VALID_NUMEROLOGY),
                int(VALID_START_SUBCARRIER),
                id="all_attributes_are_available",
            ),
            pytest.param(
                {
                    "version": VALID_INTERFACE_VERSION,
                    "rfsim_address": VALID_RFSIM_ADDRESS,
                    "sst": VALID_SST,
                    "band": VALID_BAND,
                    "dl_freq": VALID_DL_FREQ,
                    "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
                    "numerology": VALID_NUMEROLOGY,
                    "start_subcarrier": VALID_START_SUBCARRIER,
                },
                int(VALID_INTERFACE_VERSION),
                VALID_RFSIM_ADDRESS,
                int(VALID_SST),
                int(),
                int(VALID_BAND),
                int(VALID_DL_FREQ),
                int(VALID_CARRIER_BANDWIDTH),
                int(VALID_NUMEROLOGY),
                int(VALID_START_SUBCARRIER),
                id="empty_sd",
            ),
        ],
    )
    def test_given_valid_rfsim_information_in_relation_data_when_get_rfsim_information_is_called_then_information_is_returned(  # noqa: E501
        self,
        remote_data,
        expected_version,
        expected_rfsim_address,
        expected_sst,
        expected_sd,
        expected_band,
        expected_dl_freq,
        expected_carrier_bandwidth,
        expected_numerology,
        expected_start_subcarrier,
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
        params = {
            "expected_version": expected_version,
            "expected_rfsim_address": expected_rfsim_address,
            "expected_sst": expected_sst,
            "expected_sd": expected_sd,
            "expected_band": expected_band,
            "expected_dl_freq": expected_dl_freq,
            "expected_carrier_bandwidth": expected_carrier_bandwidth,
            "expected_numerology": expected_numerology,
            "expected_start_subcarrier": expected_start_subcarrier,
        }
        self.ctx.run(self.ctx.on.action("get-rfsim-information", params=params), state_in)

    @pytest.mark.parametrize(
        "remote_data",
        [
            pytest.param(
                {
                    "version": "-1",
                    "rfsim_address": "1111",
                    "sst": VALID_SST,
                    "sd": VALID_SD,
                    "band": VALID_BAND,
                    "dl_freq": VALID_DL_FREQ,
                    "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
                    "numerology": VALID_NUMEROLOGY,
                    "start_subcarrier": VALID_START_SUBCARRIER,
                },
                id="invalid_interface_version",
            ),
            pytest.param(
                {
                    "version": VALID_INTERFACE_VERSION,
                    "rfsim_address": "1111",
                    "sst": VALID_SST,
                    "sd": VALID_SD,
                    "band": VALID_BAND,
                    "dl_freq": VALID_DL_FREQ,
                    "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
                    "numerology": VALID_NUMEROLOGY,
                    "start_subcarrier": VALID_START_SUBCARRIER,
                },
                id="invalid_rfsim_address",
            ),
            pytest.param(
                {
                    "version": VALID_INTERFACE_VERSION,
                    "rfsim_address": VALID_RFSIM_ADDRESS,
                    "sst": "",
                    "sd": VALID_SD,
                    "band": VALID_BAND,
                    "dl_freq": VALID_DL_FREQ,
                    "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
                    "numerology": VALID_NUMEROLOGY,
                    "start_subcarrier": VALID_START_SUBCARRIER,
                },
                id="empty_sst",
            ),
            pytest.param(
                {
                    "version": VALID_INTERFACE_VERSION,
                    "rfsim_address": VALID_RFSIM_ADDRESS,
                    "sst": VALID_SST,
                    "sd": VALID_SD,
                    "band": "-1",
                    "dl_freq": VALID_DL_FREQ,
                    "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
                    "numerology": VALID_NUMEROLOGY,
                    "start_subcarrier": VALID_START_SUBCARRIER,
                },
                id="invalid_band",
            ),
            pytest.param(
                {
                    "version": VALID_INTERFACE_VERSION,
                    "rfsim_address": VALID_RFSIM_ADDRESS,
                    "sst": VALID_SST,
                    "sd": VALID_SD,
                    "band": VALID_BAND,
                    "dl_freq": "-1",
                    "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
                    "numerology": VALID_NUMEROLOGY,
                    "start_subcarrier": VALID_START_SUBCARRIER,
                },
                id="invalid_dl_freq",
            ),
            pytest.param(
                {
                    "version": VALID_INTERFACE_VERSION,
                    "rfsim_address": VALID_RFSIM_ADDRESS,
                    "sst": VALID_SST,
                    "sd": VALID_SD,
                    "band": VALID_BAND,
                    "dl_freq": VALID_DL_FREQ,
                    "carrier_bandwidth": "274",
                    "numerology": VALID_NUMEROLOGY,
                    "start_subcarrier": VALID_START_SUBCARRIER,
                },
                id="invalid_carrier_bandwidth",
            ),
            pytest.param(
                {
                    "version": VALID_INTERFACE_VERSION,
                    "rfsim_address": VALID_RFSIM_ADDRESS,
                    "sst": VALID_SST,
                    "sd": VALID_SD,
                    "band": VALID_BAND,
                    "dl_freq": VALID_DL_FREQ,
                    "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
                    "numerology": "7",
                    "start_subcarrier": VALID_START_SUBCARRIER,
                },
                id="invalid_numerology",
            ),
            pytest.param(
                {
                    "version": VALID_INTERFACE_VERSION,
                    "rfsim_address": VALID_RFSIM_ADDRESS,
                    "sst": VALID_SST,
                    "sd": VALID_SD,
                    "band": VALID_BAND,
                    "dl_freq": VALID_DL_FREQ,
                    "carrier_bandwidth": VALID_CARRIER_BANDWIDTH,
                    "numerology": VALID_NUMEROLOGY,
                    "start_subcarrier": "-1",
                },
                id="invalid_start_subcarrier",
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

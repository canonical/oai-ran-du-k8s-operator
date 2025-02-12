# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
import pytest

from src.du_parameters.frequency import GSCN, Frequency
from src.du_parameters.initial_bwp import (
    CalculateBWPLocationBandwidthError,
    calculate_initial_bwp,
    get_total_prbs_from_scs,
)


class TestGetTotalPRBs:
    @pytest.mark.parametrize(
        "scs,expected_prbs",
        [
            (Frequency.from_khz(15), 275),
            (Frequency.from_khz(30), 137),
            (Frequency.from_khz(60), 69),
            (Frequency.from_khz(120), 33),
        ],
    )
    def test_get_total_prbs_from_scs_when_valid_inputs_given_then_return_expected_results(
        self, scs, expected_prbs
    ):
        assert get_total_prbs_from_scs(scs) == expected_prbs

    @pytest.mark.parametrize(
        "scs",
        [
            "invalid",
            None,
            3.43,
            23232,
        ],
    )
    def test_get_total_prbs_from_scs_when_invalid_type_inputs_given_then_raise_type_error(
        self, scs
    ):
        with pytest.raises(TypeError, match="SCS must be a Frequency object"):
            get_total_prbs_from_scs(scs)

    def test_get_total_prbs_from_scs_when_unsupported_value_given_then_raise_value_error(self):
        invalid_scs = Frequency.from_khz(10)
        with pytest.raises(ValueError, match="SCS value 10000 is not supported"):
            get_total_prbs_from_scs(invalid_scs)


class TestCalculateInitialBWP:
    @pytest.mark.parametrize(
        "carrier_bandwidth,scs,expected_bwp",
        [
            (1, Frequency.from_khz(15), 0),
            (2, Frequency.from_khz(15), 275),
            (3, Frequency.from_khz(30), 274),
            (1, Frequency.from_khz(60), 0),
            (4, Frequency.from_khz(120), 99),
        ],
    )
    def test_calculate_initial_bwp_when_valid_inputs_given_then_return_expected_results(
        self, carrier_bandwidth, scs, expected_bwp
    ):
        assert calculate_initial_bwp(carrier_bandwidth, scs) == expected_bwp

    @pytest.mark.parametrize(
        "carrier_bandwidth",
        [
            "invalid",
            None,
            4.23,
        ],
    )
    def test_calculate_initial_bwp_when_invalid_type_carrier_bandwidth_given_then_raise_type_error(
        self, carrier_bandwidth
    ):
        with pytest.raises(TypeError) as e:
            calculate_initial_bwp(carrier_bandwidth, Frequency.from_khz(15))
        assert "Carrier bandwidth must be an integer" in str(e.value)

    @pytest.mark.parametrize(
        "scs",
        [
            "invalid",
            None,
            4.23,
            GSCN(23),
        ],
    )
    def test_calculate_initial_bwp_when_invalid_type_scs_given_then_raise_type_error(self, scs):
        with pytest.raises(TypeError, match="SCS must be a Frequency object"):
            calculate_initial_bwp(1, scs)

    def test_calculate_initial_bwp__when_unsupported_carrier_bandwidth_value_given_then_raise_value_error(  # noqa: E501
        self,
    ):
        with pytest.raises(ValueError) as e:
            calculate_initial_bwp(0, Frequency.from_khz(15))
        assert "Carrier bandwidth must be greater than 0" in str(e.value)

    def test_calculate_initial_bwp_when_get_total_prb_calculation_fails_then_raise_calculate_bwp_location_bandwidth_error(  # noqa: E501
        self,
    ):  # noqa: E501
        with pytest.raises(
            CalculateBWPLocationBandwidthError,
            match="Error calculating total PRBs: SCS value 10000 is not supported",
        ):
            calculate_initial_bwp(2, Frequency.from_khz(10))

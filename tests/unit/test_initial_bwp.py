# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
import pytest

from src.du_parameters.initial_bwp import (
    get_initial_bwp,
)


class TestCalculateInitialBWP:
    @pytest.mark.parametrize(
        "carrier_bandwidth,expected_bwp",
        [(1, 0), (2, 275), (3, 550), (1, 0), (106, 28875), (50, 13475)],
    )
    def test_calculate_initial_bwp_when_valid_inputs_given_then_return_expected_results(
        self, carrier_bandwidth, expected_bwp
    ):
        assert get_initial_bwp(carrier_bandwidth) == expected_bwp

    @pytest.mark.parametrize(
        "carrier_bandwidth, error_type, error_message",
        [
            ("invalid", TypeError, "'<=' not supported between instances of 'str' and 'int'"),
            (None, TypeError, "'<=' not supported between instances of 'NoneType' and 'int'"),
        ],
    )
    def test_calculate_initial_bwp_when_invalid_type_carrier_bandwidth_given_then_it_raises_error(
        self, carrier_bandwidth, error_type, error_message
    ):
        with pytest.raises(error_type) as e:
            get_initial_bwp(carrier_bandwidth)
        assert error_message in str(e.value)

    def test_calculate_initial_bwp_when_unsupported_carrier_bandwidth_value_given_then_raise_value_error(  # noqa: E501
        self,
    ):
        with pytest.raises(ValueError) as e:
            get_initial_bwp(0)
        assert "Carrier bandwidth must be greater than 0" in str(e.value)

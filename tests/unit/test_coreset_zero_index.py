# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest

from du_parameters import Frequency
from du_parameters.coreset_zero_index import (
    TABLE_13_1,
    TABLE_13_4,
    TABLE_13_6,
    CoresetZeroConfigurationIndexError,
    _get_coreset_zero_config_search_space,
    get_coreset_zero_configuration_index,
)


class TestCoresetZeroConfigurationIndex:
    @pytest.mark.parametrize(
        "band,subcarrier_spacing,expected_search_space",
        [
            (38, Frequency.from_khz(15), TABLE_13_1),
            (50, Frequency.from_khz(30), TABLE_13_4),
            (77, Frequency.from_khz(15), TABLE_13_1),
            (78, Frequency.from_khz(30), TABLE_13_4),
            (79, Frequency.from_khz(30), TABLE_13_6),
            (101, Frequency.from_khz(15), TABLE_13_1),
        ],
    )
    def test_get_coreset_zero_config_search_space_when_valid_rf_config_is_given_then_correct_search_space_is_returned(  # noqa: E501
        self, band, subcarrier_spacing, expected_search_space
    ):
        assert (
            _get_coreset_zero_config_search_space(band, subcarrier_spacing)
            == expected_search_space
        )

    @pytest.mark.parametrize(
        "band,bandwidth,subcarrier_spacing,offset_to_point_a,expected_index",
        [
            (38, 132, Frequency.from_khz(15), 61, 12),
            (50, 78, Frequency.from_khz(30), 61, 10),
            (77, 216, Frequency.from_khz(15), 99, 12),
            (78, 24, Frequency.from_khz(30), 6, 0),
            (79, 106, Frequency.from_khz(30), 71, 4),
            (101, 52, Frequency.from_khz(15), 15, 6),
        ],
    )
    def test_get_coreset_zero_configuration_index_when_valid_rf_config_is_given_then_correct_configuration_index_is_returned(  # noqa: E501
        self, band, bandwidth, subcarrier_spacing, offset_to_point_a, expected_index
    ):
        assert (
            get_coreset_zero_configuration_index(
                band, bandwidth, subcarrier_spacing, offset_to_point_a
            )
            == expected_index
        )

    @pytest.mark.parametrize(
        "band,bandwidth,subcarrier_spacing,offset_to_point_a",
        [
            pytest.param(38, 132, Frequency.from_khz(15), 21, id="No matching offset"),
            pytest.param(78, 20, Frequency.from_khz(15), 6, id="No matching CORESET bandwidth"),
        ],
    )
    def test_get_coreset_zero_configuration_index_when_invalid_rf_config_is_given_then_correct_exception_is_raised(  # noqa: E501
        self, band, bandwidth, subcarrier_spacing, offset_to_point_a
    ):
        with pytest.raises(CoresetZeroConfigurationIndexError):
            get_coreset_zero_configuration_index(
                band, bandwidth, subcarrier_spacing, offset_to_point_a
            )

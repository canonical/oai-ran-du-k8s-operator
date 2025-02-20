#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest

from src.du_parameters.dl_absolute_freq_point_a import (
    CONFIG_CONSTANT_TWO,
    DLAbsoluteFrequencyPointAError,
    get_dl_absolute_frequency_point_a,
)
from src.du_parameters.frequency import ARFCN, Frequency


class TestDLAbsoluteFrequencyPointA:
    @pytest.mark.parametrize(
        "center_freq, bandwidth, subcarrier_spacing, expected_arfcn_value",
        [
            (
                Frequency.from_mhz(1000),
                Frequency.from_mhz("20.43"),
                Frequency.from_khz(15),
                197958,
            ),
            (Frequency.from_mhz("700.3"), Frequency.from_mhz(10), Frequency.from_khz(15), 139059),
            (Frequency.from_mhz(4060), Frequency.from_mhz(40), Frequency.from_khz(30), 669334),
            (Frequency.from_mhz(3925), Frequency.from_mhz(20), Frequency.from_khz(15), 661000),
            (Frequency.from_mhz(25000), Frequency.from_mhz(20), Frequency.from_khz(60), 2029000),
            (
                Frequency.from_mhz("24000.523"),
                Frequency.from_mhz(20),
                Frequency.from_khz(30),
                1999368,
            ),
        ],
    )
    def test_get_dl_absolute_frequency_point_a_when_valid_inputs_given_then_return_expected_values(  # noqa: E501
        self, center_freq, bandwidth, subcarrier_spacing, expected_arfcn_value
    ):
        result = get_dl_absolute_frequency_point_a(center_freq, bandwidth, subcarrier_spacing)
        assert isinstance(result, ARFCN)
        assert result._channel == expected_arfcn_value

    @pytest.mark.parametrize(
        "center_freq, bandwidth, sub_carrier_spacing, expected_lowest_freq",
        [
            (
                Frequency.from_mhz(1000),
                Frequency.from_mhz("20.43"),
                Frequency.from_khz(30),
                Frequency.from_khz(989790),
            ),
            (
                Frequency.from_mhz("700.3"),
                Frequency.from_mhz(10),
                Frequency.from_khz(30),
                Frequency.from_khz(695310),
            ),
            (
                Frequency.from_mhz(3500),
                Frequency.from_mhz(100),
                Frequency.from_khz(30),
                Frequency.from_mhz(3450),
            ),
            (
                Frequency.from_mhz(3925),
                Frequency.from_mhz(20),
                Frequency.from_khz(30),
                Frequency.from_mhz(3915),
            ),
        ],
    )
    def test_get_dl_absolute_frequency_point_a_when_valid_inputs_given_then_get_aligned_lowest_freq_calculation(  # noqa: E501
        self, center_freq, bandwidth, sub_carrier_spacing, expected_lowest_freq
    ):
        actual_lowest_freq = center_freq - (bandwidth / CONFIG_CONSTANT_TWO)
        aligned_lowes_freq = round(actual_lowest_freq / sub_carrier_spacing) * sub_carrier_spacing
        assert expected_lowest_freq == aligned_lowes_freq
        result = get_dl_absolute_frequency_point_a(center_freq, bandwidth, sub_carrier_spacing)
        assert isinstance(result, ARFCN)

    @pytest.mark.parametrize(
        "center_freq, bandwidth, sub_carrier_spacing, expected_exception, expected_msg",
        [
            (
                "invalid",
                Frequency.from_mhz(20),
                Frequency.from_khz(30),
                DLAbsoluteFrequencyPointAError,
                "Unsupported type for subtraction: <class 'str'>",
            ),
            (
                Frequency.from_mhz(1000),
                "20",
                Frequency.from_khz(30),
                DLAbsoluteFrequencyPointAError,
                "unsupported operand type(s) for /: 'str' and 'decimal.Decimal'",
            ),
            (
                None,
                Frequency.from_mhz(20),
                Frequency.from_khz(30),
                DLAbsoluteFrequencyPointAError,
                "Unsupported type for subtraction: <class 'NoneType'>",
            ),
        ],
    )
    def test_get_dl_absolute_frequency_point_a_when_invalid_inputs_given_then_raise_error(
        self, center_freq, bandwidth, sub_carrier_spacing, expected_exception, expected_msg
    ):
        with pytest.raises(expected_exception) as err:
            get_dl_absolute_frequency_point_a(center_freq, bandwidth, sub_carrier_spacing)
        assert expected_msg in str(err.value)

    @pytest.mark.parametrize(
        "center_freq, bandwidth, sub_carrier_spacing, expected_exception, expected_msg",
        [
            (
                Frequency.from_mhz(392533333),
                Frequency.from_mhz(20),
                Frequency.from_khz(30),
                DLAbsoluteFrequencyPointAError,
                "No frequency range found for frequency 392533323000000",
            ),
            (
                Frequency.from_mhz(-1000),
                Frequency.from_mhz(50),
                Frequency.from_khz(30),
                DLAbsoluteFrequencyPointAError,
                "No frequency range found for frequency -1025010000",
            ),
            (
                None,
                Frequency.from_mhz(20),
                Frequency.from_khz(30),
                DLAbsoluteFrequencyPointAError,
                "Unsupported type for subtraction: <class 'NoneType'>",
            ),
            (
                "24000.523",
                Frequency.from_mhz(20),
                Frequency.from_khz(30),
                DLAbsoluteFrequencyPointAError,
                "No frequency range found for frequency -9990000",
            ),
        ],
    )
    def test_get_dl_absolute_frequency_point_a_when_invalid_values_provided_then_dl_absolute_frequency_point_a_error_raised(  # noqa: E501
        self, center_freq, bandwidth, sub_carrier_spacing, expected_exception, expected_msg
    ):
        with pytest.raises(expected_exception) as err:
            get_dl_absolute_frequency_point_a(center_freq, bandwidth, sub_carrier_spacing)
        assert expected_msg in str(err.value)

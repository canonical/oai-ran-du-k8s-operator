#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import decimal
import pytest

from src.du_parameters.dl_absolute_freq_point_a import (
    CONFIG_CONSTANT_TWO,
    DLAbsoluteFrequencyPointAError,
    get_dl_absolute_frequency_point_a,
)
from src.du_parameters.frequency import ARFCN, Frequency


class TestDLAbsoluteFrequencyPointA:
    @pytest.mark.parametrize(
        "center_freq, bandwidth, expected_arfcn_value",
        [
            (Frequency.from_mhz(1000), Frequency.from_mhz("20.43"), 197957),
            (Frequency.from_mhz("700.3"), Frequency.from_mhz(10), 139060),
            (Frequency.from_mhz(3500), Frequency.from_mhz(100), 630000),
            (Frequency.from_mhz(3925), Frequency.from_mhz(20), 661000),
            (Frequency.from_mhz(25000), Frequency.from_mhz(20), 2029000),
            (Frequency.from_mhz("24000.523"), Frequency.from_mhz(20), 1999368),
        ],
    )
    def test_get_dl_absolute_frequency_point_a_when_valid_inputs_given_then_return_expected_values(  # noqa: E501
        self, center_freq, bandwidth, expected_arfcn_value
    ):
        result = get_dl_absolute_frequency_point_a(center_freq, bandwidth)
        assert isinstance(result, ARFCN)
        assert result._channel == expected_arfcn_value

    @pytest.mark.parametrize(
        "center_freq, bandwidth, expected_lowest_freq",
        [
            (
                Frequency.from_mhz(1000),
                Frequency.from_mhz("20.43"),
                Frequency(str(989784999.9999999681676854379)),
            ),
            (
                Frequency.from_mhz("700.3"),
                Frequency.from_mhz(10),
                Frequency(str(695299999.9999999545252649114)),
            ),
            (Frequency.from_mhz(3500), Frequency.from_mhz(100), Frequency.from_mhz(3450)),
            (Frequency.from_mhz(3925), Frequency.from_mhz(20), Frequency.from_mhz(3915)),
        ],
    )
    def test_get_dl_absolute_frequency_point_a_when_valid_inputs_given_then_get_expected_lowest_freq_calculation(  # noqa: E501
        self, center_freq, bandwidth, expected_lowest_freq
    ):
        actual_lowest_freq = center_freq - (bandwidth / CONFIG_CONSTANT_TWO)
        assert actual_lowest_freq == expected_lowest_freq
        result = get_dl_absolute_frequency_point_a(center_freq, bandwidth)
        assert isinstance(result, ARFCN)

    @pytest.mark.parametrize(
        "center_freq, bandwidth, expected_exception, expected_msg",
        [
            (
                "invalid",
                Frequency.from_mhz(20),
                DLAbsoluteFrequencyPointAError,
                "Unsupported type for subtraction: <class 'str'>",
            ),
            (
                Frequency.from_mhz(1000),
                "20",
                DLAbsoluteFrequencyPointAError,
                "unsupported operand type(s) for /: 'str' and 'decimal.Decimal'",
            ),
            (
                None,
                Frequency.from_mhz(20),
                DLAbsoluteFrequencyPointAError,
                "Unsupported type for subtraction: <class 'NoneType'>",
            ),
        ],
    )
    def test_get_dl_absolute_frequency_point_a_when_invalid_inputs_given_then_raise_error(
        self, center_freq, bandwidth, expected_exception, expected_msg
    ):
        with pytest.raises(expected_exception) as err:
            get_dl_absolute_frequency_point_a(center_freq, bandwidth)
        assert expected_msg in str(err.value)


    @pytest.mark.parametrize(
        "center_freq, bandwidth, expected_exception, expected_msg",
        [
            (
                Frequency.from_mhz(392533333),
                Frequency.from_mhz(20),
                DLAbsoluteFrequencyPointAError,
                "No frequency range found for frequency 392533323000000",
            ),
            (
                Frequency.from_mhz(-1000),
                Frequency.from_mhz(50),
                DLAbsoluteFrequencyPointAError,
                "No frequency range found for frequency -1025000000",
            ),
            (
                None,
                Frequency.from_mhz(20),
                DLAbsoluteFrequencyPointAError,
                "Unsupported type for subtraction: <class 'NoneType'>",
            ),
            (
                "24000.523",
                Frequency.from_mhz(20),
                DLAbsoluteFrequencyPointAError,
                "No frequency range found for frequency -9975999.477",
            ),
        ],
    )
    def test_get_dl_absolute_frequency_point_a_when_invalid_values_provided_then_dl_absolute_frequency_point_a_error_raised(  # noqa: E501
        self, center_freq, bandwidth, expected_exception, expected_msg
    ):
        with pytest.raises(expected_exception) as err:
            get_dl_absolute_frequency_point_a(center_freq, bandwidth)
        assert expected_msg in str(err.value)

#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import decimal
from unittest.mock import patch

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
            (Frequency.from_mhz(1000), Frequency.from_mhz("20.43"), 123456),
            (Frequency.from_mhz("700.3"), Frequency.from_mhz(10), 654321),
            (Frequency.from_mhz(3500), Frequency.from_mhz(100), 987654),
            (Frequency.from_mhz(3925), Frequency.from_mhz(20), 661000),
        ],
    )
    def test_get_dl_absolute_frequency_point_a_when_arfcn_from_frequency_is_mocked_then_return_value_of_arfcn_object_macthes_expected_value(  # noqa: E501
        self, center_freq, bandwidth, expected_arfcn_value
    ):
        with patch.object(
            ARFCN,
            "from_frequency",
            return_value=ARFCN(expected_arfcn_value),
        ):
            result = get_dl_absolute_frequency_point_a(center_freq, bandwidth)
            assert isinstance(result, ARFCN)
            assert result._channel == expected_arfcn_value

    @pytest.mark.parametrize(
        "center_freq, bandwidth, expected_arfcn_value",
        [
            (Frequency.from_mhz(1000), Frequency.from_mhz("20.43"), 123456),
            (Frequency.from_mhz("700.3"), Frequency.from_mhz(10), 654321),
            (Frequency.from_mhz(3500), Frequency.from_mhz(100), 987654),
            (Frequency.from_mhz(3925), Frequency.from_mhz(20), 661000),
        ],
    )
    def test_get_dl_absolute_frequency_point_a_when_when_arfcn_from_frequency_is_mocked_then_lowest_frequency_passed_to_arfcn_calculation_is_correct(  # noqa: E501
        self, center_freq, bandwidth, expected_arfcn_value
    ):
        expected_lowest_freq = center_freq - (bandwidth / CONFIG_CONSTANT_TWO)
        with patch.object(
            ARFCN, "from_frequency", return_value=ARFCN(expected_arfcn_value)
        ) as mock_from_frequency:
            result = get_dl_absolute_frequency_point_a(center_freq, bandwidth)
            mock_from_frequency.assert_called_once_with(expected_lowest_freq)
            assert result._channel == expected_arfcn_value

    @pytest.mark.parametrize(
        "center_freq, bandwidth, expected_exception, expected_msg",
        [
            (
                "invalid",
                Frequency.from_mhz(20),
                DLAbsoluteFrequencyPointAError,
                "decimal.ConversionSyntax",
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
        with patch.object(
            ARFCN,
            "from_frequency",
        ):
            with pytest.raises(expected_exception) as err:
                get_dl_absolute_frequency_point_a(center_freq, bandwidth)
            assert expected_msg in str(err.value)

    def test_get_dl_absolute_frequency_point_a_when_decimal_invalid_operation_error_raised_then_handle_and_raise_dl_absolute_frequency_point_a_error(  # noqa: E501
        self,
    ):  # noqa: E501
        with patch.object(
            ARFCN,
            "from_frequency",
            side_effect=decimal.InvalidOperation("Invalid decimal operation"),
        ):
            center_freq = Frequency.from_mhz(1000)
            bandwidth = Frequency.from_mhz(20)
            with pytest.raises(
                DLAbsoluteFrequencyPointAError,
                match="Error calculating downlink absolute frequency Point A.*Invalid decimal operation",  # noqa: E501
            ):
                get_dl_absolute_frequency_point_a(center_freq, bandwidth)

    @pytest.mark.parametrize(
        "center_freq, bandwidth, expected_value",
        [
            (Frequency.from_mhz(3925), Frequency.from_mhz(20), 661000),
            (Frequency.from_mhz(1000), Frequency.from_mhz(50), 195000),
            (Frequency.from_mhz(25000), Frequency.from_mhz(20), 2029000),
            (Frequency.from_mhz("24000.523"), Frequency.from_mhz(20), 1999368),
        ],
    )
    def test_get_dl_absolute_frequency_point_a_when_valid_values_provided_and_no_mock_used_then_get_expected_values(  # noqa: E501
        self, center_freq, bandwidth, expected_value
    ):
        result = get_dl_absolute_frequency_point_a(center_freq, bandwidth)
        assert result == ARFCN(expected_value)

    @pytest.mark.parametrize(
        "center_freq, bandwidth, expected_exception, expected_msg",
        [
            (
                Frequency.from_mhz(392533333),
                Frequency.from_mhz(20),
                DLAbsoluteFrequencyPointAError,
                "Frequency 392533323000000 is out of supported range.",
            ),
            (
                Frequency.from_mhz(-1000),
                Frequency.from_mhz(50),
                DLAbsoluteFrequencyPointAError,
                "Frequency -1025000000 is out of supported range.",
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
                "Frequency -9975999.477 is out of supported range",
            ),
        ],
    )
    def test_get_dl_absolute_frequency_point_a_when_invalid_values_provided_then_dl_absolute_frequency_point_a_error_raised(  # noqa: E501
        self, center_freq, bandwidth, expected_exception, expected_msg
    ):
        with pytest.raises(expected_exception) as err:
            get_dl_absolute_frequency_point_a(center_freq, bandwidth)
        assert expected_msg in str(err.value)

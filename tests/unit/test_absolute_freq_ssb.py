#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import MagicMock, patch

import pytest

from src.du_parameters.absolute_freq_ssb import (
    AbsoluteFrequencySSBError,
    get_absolute_frequency_ssb,
)
from src.du_parameters.frequency import ARFCN, GSCN, Frequency, GetRangeFromFrequencyError


def test_get_absolute_frequency_ssb_when_valid_input_given_then_return_expected_result():
    mock_center_freq = MagicMock(spec=Frequency)
    mock_gscn = MagicMock(spec=GSCN)
    mock_adjusted_frequency = MagicMock(spec=Frequency)
    mock_arfcn = MagicMock(spec=ARFCN)

    with (
        patch.object(GSCN, "from_frequency", return_value=mock_gscn) as mock_from_frequency,
        patch.object(
            GSCN, "to_frequency", return_value=mock_adjusted_frequency
        ) as mock_to_frequency,
        patch.object(
            ARFCN, "from_frequency", return_value=mock_arfcn
        ) as mock_from_frequency_arfcn,
    ):
        result = get_absolute_frequency_ssb(mock_center_freq)
        assert result == mock_arfcn
        mock_from_frequency.assert_called_once_with(mock_center_freq)
        mock_to_frequency.assert_called_once_with(mock_gscn)
        mock_from_frequency_arfcn.assert_called_once_with(mock_adjusted_frequency)


@pytest.mark.parametrize(
    "invalid_freq, expected_error",
    [
        (-1222, GetRangeFromFrequencyError),
        ("invalid", GetRangeFromFrequencyError),
        (None, GetRangeFromFrequencyError),
    ],
)
def test_get_absolute_frequency_ssb_when_input_with_invalid_type_given_then_raise_exception(  # noqa: E501
    invalid_freq, expected_error
):
    invalid_center_freq = invalid_freq
    with pytest.raises(expected_error):
        get_absolute_frequency_ssb(invalid_center_freq)


def test_get_absolute_frequency_ssb_when_value_error_raised_during_freq_to_gcsn_conversion_then_raise_exception():  # noqa: E501
    mock_center_freq = MagicMock(spec=Frequency)

    with (
        patch.object(
            GSCN, "from_frequency", side_effect=ValueError("Invalid GSCN")
        ) as mock_from_frequency,
    ):
        with pytest.raises(AbsoluteFrequencySSBError, match=r"GSCN"):
            get_absolute_frequency_ssb(mock_center_freq)

        mock_from_frequency.assert_called_once_with(mock_center_freq)

@pytest.mark.parametrize(
    "center_freq, expected_result",
    [
        (3925, 661632),
        (4000, 666624),
        (20, 4030),
        (1000, 200030),
        (25000, 2029052),
    ],
)
def test_get_absolute_frequency_ssb_when_center_frequency_given_then_return_expected_result(center_freq, expected_result):
    result = get_absolute_frequency_ssb(Frequency.from_mhz(center_freq))
    assert result == ARFCN(expected_result)

@pytest.mark.parametrize(
    "center_freq, expected_error_message",
    [
        (0, "Value of N: -0.125 is out of supported range (1-2499)"),
        (99999, "Value of N: 4383.618055555555555555555556 is out of supported range (0-4383)"),
    ],
)
def test_get_absolute_frequency_ssb_when_n_is_out_of_range_then_raise_error(center_freq, expected_error_message):
    with pytest.raises(AbsoluteFrequencySSBError) as err:
        get_absolute_frequency_ssb(Frequency.from_mhz(center_freq))
    assert expected_error_message in str(err.value)

@pytest.mark.parametrize(
    "invalid_freq, expected_error",
    [
        (-1e10, GetRangeFromFrequencyError),  # Extremely large negative value
        (1e10, GetRangeFromFrequencyError),  # Extremely large positive value
        (complex(1, 1), TypeError),  # Complex number
    ],
)
def test_get_absolute_frequency_ssb_when_extreme_invalid_values_given_then_raise_error(invalid_freq, expected_error):
    with pytest.raises(expected_error):
        get_absolute_frequency_ssb(Frequency.from_mhz(invalid_freq))
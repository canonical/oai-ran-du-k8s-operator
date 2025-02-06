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
    mock_frequency = MagicMock(spec=Frequency)
    mock_gscn = MagicMock(spec=GSCN)
    mock_adjusted_frequency = MagicMock(spec=Frequency)
    mock_arfcn = MagicMock(spec=ARFCN)

    with (
        patch.object(Frequency, "from_mhz", return_value=mock_frequency) as mock_from_mhz,
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
        mock_from_mhz.assert_called_once_with(str(mock_center_freq))
        mock_from_frequency.assert_called_once_with(mock_frequency)
        mock_to_frequency.assert_called_once_with(mock_gscn)
        mock_from_frequency_arfcn.assert_called_once_with(mock_adjusted_frequency)


@pytest.mark.parametrize(
    "invalid_freq, expected_error",
    [
        (-1222, GetRangeFromFrequencyError),
        ("invalid", AbsoluteFrequencySSBError),
        (None, AbsoluteFrequencySSBError),
    ],
)
def test_get_absolute_frequency_ssb_when_input_with_invalid_type_given_then_raise_exception(  # noqa: E501
    invalid_freq, expected_error
):
    invalid_center_freq = invalid_freq
    with pytest.raises(expected_error):
        get_absolute_frequency_ssb(invalid_center_freq)


def test_get_absolute_frequency_ssb_when_value_error_raised_during_frequency_conversion_then_raise_exception():  # noqa: E501
    mock_center_freq = MagicMock(spec=Frequency)
    with patch.object(
        Frequency,
        "from_mhz",
        side_effect=ValueError("Invalid frequency"),
    ) as mock_from_mhz:
        with pytest.raises(
            AbsoluteFrequencySSBError,
            match=r"Error calculating absolute frequency for SSB with center_freq",
        ):
            get_absolute_frequency_ssb(mock_center_freq)

        mock_from_mhz.assert_called_once_with(str(mock_center_freq))


def test_get_absolute_frequency_ssb_when_value_error_raised_during_freq_to_gcsn_conversion_then_raise_exception():  # noqa: E501
    mock_center_freq = MagicMock(spec=Frequency)
    mock_frequency = MagicMock(spec=Frequency)

    with (
        patch.object(Frequency, "from_mhz", return_value=mock_frequency) as mock_from_mhz,
        patch.object(
            GSCN, "from_frequency", side_effect=ValueError("Invalid GSCN")
        ) as mock_from_frequency,
    ):
        with pytest.raises(AbsoluteFrequencySSBError, match=r"GSCN"):
            get_absolute_frequency_ssb(mock_center_freq)

        mock_from_mhz.assert_called_once_with(str(mock_center_freq))
        mock_from_frequency.assert_called_once_with(mock_frequency)

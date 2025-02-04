#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import MagicMock, patch

import pytest

from src.du_parameters.absolute_freq_ssb import get_absolute_frequency_ssb


@pytest.mark.parametrize(
    "center_freq, expected_result",
    [
        (3500.0, 12345),  # Valid
        (700.0, 6789),  # Valid
    ],
)
@patch("src.du_parameters.absolute_freq_ssb.Frequency")
@patch("src.du_parameters.absolute_freq_ssb.get_config_for_frequency")
@patch("src.du_parameters.absolute_freq_ssb.GSCN")
@patch("src.du_parameters.absolute_freq_ssb.ARFCN")
def test_get_absolute_frequency_ssb_when_valid_center_freq_then_result_is_expected(
    mock_arfcn, mock_gscn, mock_get_config, mock_frequency, center_freq, expected_result
):
    mock_frequency.from_mhz.return_value = MagicMock()
    mock_config = MagicMock()
    mock_get_config.return_value = mock_config

    mock_gscn.freq_to_gcsn.return_value = 123
    mock_gscn.gscn_to_freq.return_value = 3550.0
    mock_arfcn.freq_to_arfcn.return_value = expected_result

    result = get_absolute_frequency_ssb(center_freq)
    assert result == expected_result
    mock_frequency.from_mhz.assert_called_once_with(center_freq)
    mock_get_config.assert_called_once_with(mock_frequency.from_mhz.return_value)
    mock_gscn.freq_to_gcsn.assert_called_once_with(mock_frequency.from_mhz.return_value)
    mock_gscn.gscn_to_freq.assert_called_once_with(mock_config, 123)
    mock_arfcn.freq_to_arfcn.assert_called_once_with(mock_gscn.gscn_to_freq.return_value)


@pytest.mark.parametrize(
    "center_freq, expected_result",
    [
        (-500.0, None),  # Invalid
        (0, None),  # Invalid
        ("string", None),  # Invalid
    ],
)
@patch("src.du_parameters.absolute_freq_ssb.Frequency")
@patch("src.du_parameters.absolute_freq_ssb.get_config_for_frequency")
@patch("src.du_parameters.absolute_freq_ssb.GSCN")
@patch("src.du_parameters.absolute_freq_ssb.ARFCN")
def test_get_absolute_frequency_ssb_when_invalid_center_freq_then_expected_result_is_returned(
    mock_arfcn, mock_gscn, mock_get_config, mock_frequency, center_freq, expected_result
):
    mock_frequency.from_mhz.return_value = MagicMock()
    mock_config = MagicMock()
    mock_get_config.return_value = mock_config

    mock_gscn.freq_to_gcsn.return_value = 123
    mock_gscn.gscn_to_freq.return_value = 3550.0
    mock_arfcn.freq_to_arfcn.return_value = expected_result

    result = get_absolute_frequency_ssb(center_freq)
    assert result == expected_result

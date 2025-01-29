#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import patch

import pytest

from src.du_parameters.absolute_frequency_ssb import get_absolute_frequency_ssb
from src.du_parameters.ssb import HighFrequencySSB, LowFrequencySSB, MidFrequencySSB

# A random test frequency
TEST_FREQUENCY = 24300


class TestGetAbsoluteFrequencySSB:
    @pytest.mark.parametrize(
        "frequency, gscn, gscn_to_freq, frequency_class",
        [
            (24250, 9432, 24249, HighFrequencySSB),
            # Value of N: -0.004629629629730684 is out of supported range (0-4383).
            (99999, 232324, 99890, HighFrequencySSB),
            # Value of N: 4383.618055555555 is out of supported range (0-4383).
            (0, 4, 0, LowFrequencySSB),
            # Value of N: -0.12500000000000003 is out of supported range (1-2499).
            (2999, 4, 2998, LowFrequencySSB),
            # Value of N: 2499.0416666666665 is out of supported range (1-2499)
            (24249, 9233, 24199, MidFrequencySSB),
            # Value of N: 14756.25 is out of supported range (0-14756)
        ],
    )
    @patch("src.du_parameters.absolute_frequency_ssb.get_frequency_instance")
    def test_get_arfcn_when_valid_input_provided_but_n_is_out_of_supported_range_then_none_is_returned(  # noqa E501
        self, mock_get_frequency_instance, frequency, gscn, gscn_to_freq, frequency_class
    ):
        mock_get_frequency_instance.freq_to_gscn.return_value = gscn
        mock_get_frequency_instance.gscn_to_freq.return_value = gscn_to_freq

        result = get_absolute_frequency_ssb(frequency)
        assert result is None

    @pytest.mark.parametrize(
        "frequency",
        [
            None,
            "invalid",
            [123],
            {"value": 123},
        ],
    )
    def test_get_arfcn_when_invalid_type_inputs_given_then_return_none(self, frequency):
        result = get_absolute_frequency_ssb(frequency)
        assert result is None

    @pytest.mark.parametrize(
        "frequency, expected",
        [
            (25251.5, 2033084),
            (9.99, 1950),
        ],
    )
    def test_get_arfcn_when_float_inputs_provided_then_return_arfcn(self, frequency, expected):
        result = get_absolute_frequency_ssb(frequency)
        assert result == expected

    @pytest.mark.parametrize(
        "frequency, expected",
        [
            (HighFrequencySSB.RANGE[0], None),
            (HighFrequencySSB.RANGE[1], None),
            (LowFrequencySSB.RANGE[0], None),
            (LowFrequencySSB.RANGE[1], 600000),
            (MidFrequencySSB.RANGE[0], 600000),
            (MidFrequencySSB.RANGE[1], None),
        ],
    )
    def test_get_arfcn_when_boundary_frequencies_provided_then_return_arfcn(
        self, frequency, expected
    ):
        result = get_absolute_frequency_ssb(frequency)
        assert result == expected

    @patch("src.du_parameters.absolute_frequency_ssb.get_frequency_instance")
    def test_get_arfcn_when_freq_to_gscn_calculation_fails_then_return_none(
        self, mock_get_frequency_instance
    ):
        mock_get_frequency_instance.freq_to_gscn.return_value = None
        result = get_absolute_frequency_ssb(TEST_FREQUENCY)
        assert result is None

    @patch("src.du_parameters.absolute_frequency_ssb.get_frequency_instance")
    def test_get_arfcn_when_gscn_to_freq_calculation_fails_then_returns_none(
        self, mock_get_frequency_instance
    ):
        mock_get_frequency_instance.gscn_to_freq.return_value = None

        result = get_absolute_frequency_ssb(TEST_FREQUENCY)
        assert result is None

    @pytest.mark.parametrize(
        "frequency",
        [
            -10,  # Below MIN_N
            250000,  # Above HighFrequency.MAX_N
        ],
    )
    def test_get_arfcn_when_out_of_range_frequencies_provided_then_return_none(self, frequency):
        result = get_absolute_frequency_ssb(frequency)
        assert result is None

    @pytest.mark.parametrize(
        "exception", [TypeError("Unexpected error"), ValueError("Invalid value")]
    )
    @patch("src.du_parameters.absolute_frequency_ssb.get_frequency_instance")
    def test_get_arfcn_when_different_exceptions_occur_then_return_none(
        self, mock_get_frequency_instance, exception
    ):
        mock_get_frequency_instance.side_effect = exception
        result = get_absolute_frequency_ssb(TEST_FREQUENCY)
        assert result is None

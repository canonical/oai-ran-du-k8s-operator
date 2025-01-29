#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest

from src.du_parameters.afrcn import HIGH, LOW, MID, freq_to_arfcn


class TestARFCN:
    def test_freq_to_arfcn_when_low_frequency_is_given_then_arfcn_is_returned_as_integer(self):
        # Frequency in low range
        frequency = 1000
        expected_arfcn = LOW.arfcn_offset + ((frequency - LOW.freq_offset) / LOW.freq_grid)
        assert freq_to_arfcn(frequency) == int(expected_arfcn)

    def test_freq_to_arfcn_when_mid_frequency_is_given_then_arfcn_is_returned_as_integer(self):
        # Frequency in mid range
        frequency = 10000
        expected_arfcn = MID.arfcn_offset + ((frequency - MID.freq_offset) / MID.freq_grid)
        assert freq_to_arfcn(frequency) == int(expected_arfcn)

    def test_freq_to_arfcn_when_high_frequency_is_given_then_arfcn_is_returned_as_integer(self):
        # Frequency in high range
        frequency = 50000
        expected_arfcn = HIGH.arfcn_offset + ((frequency - HIGH.freq_offset) / HIGH.freq_grid)
        assert freq_to_arfcn(frequency) == int(expected_arfcn)

    def test_freq_to_arfcn_when_too_low_frequency_is_given_then_value_error_is_raised(self):
        with pytest.raises(ValueError) as exc_info:
            freq_to_arfcn(-1)
        assert "Frequency -1 is out of supported range." in str(exc_info.value)

    def test_freq_to_arfcn_when_too_high_frequency_is_given_then_value_error_is_raised(self):
        with pytest.raises(ValueError) as exc_info:
            freq_to_arfcn(2016668)
        assert "Frequency 2016668 is out of supported range." in str(exc_info.value)

    def test_freq_to_arfcn_when_non_numeric_input_is_given_then_type_error_is_raised(self):
        with pytest.raises(TypeError) as exc_info:
            freq_to_arfcn("not_a_number")  # type: ignore
        assert "Frequency not_a_number is not a numeric value." in str(exc_info.value)

    def test_freq_to_arfcn_when_freq_grid_is_zero_then_value_error_is_raised(self):
        custom_range = LOW
        # Set freq_grid to zero for testing
        custom_range.freq_grid = 0
        with pytest.raises(ValueError) as exc_info:
            freq_to_arfcn(custom_range.lower + 1)
        assert "FREQ_GRID cannot be zero." in str(exc_info.value)
        # Reset to the initial value not to have side effects
        custom_range.freq_grid = 0.005

#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from decimal import Decimal

import pytest

from src.du_parameters.afrcn import HIGH, LOW, MID, freq_to_arfcn

MHZ = 1000000  # HZ


class TestARFCN:
    def test_freq_to_arfcn_when_low_frequency_is_given_then_arfcn_is_returned_as_integer(self):
        # Frequency in low range
        frequency = 1000000000  # HZ
        expected_arfcn = Decimal(LOW.arfcn_offset) + (
            (frequency - Decimal(LOW.freq_offset)) / Decimal(LOW.freq_grid)
        )  # noqa: E501
        assert freq_to_arfcn(frequency) == int(expected_arfcn)

    def test_freq_to_arfcn_when_mid_frequency_is_given_then_arfcn_is_returned_as_integer(self):
        # Frequency in mid range
        frequency = 10000 * MHZ
        expected_arfcn = MID.arfcn_offset + ((frequency - MID.freq_offset) / MID.freq_grid)
        assert freq_to_arfcn(frequency) == int(expected_arfcn)

    def test_freq_to_arfcn_when_high_frequency_is_given_then_arfcn_is_returned_as_integer(self):
        # Frequency in high range
        frequency = 50000 * MHZ
        expected_arfcn = HIGH.arfcn_offset + ((frequency - HIGH.freq_offset) / HIGH.freq_grid)
        assert freq_to_arfcn(frequency) == int(expected_arfcn)

    def test_freq_to_arfcn_when_too_low_frequency_is_given_then_value_error_is_raised(self):
        with pytest.raises(ValueError) as exc_info:
            freq_to_arfcn(-1)
        assert "Frequency -1 is out of supported range." in str(exc_info.value)

    def test_freq_to_arfcn_when_too_high_frequency_is_given_then_value_error_is_raised(self):
        with pytest.raises(ValueError) as exc_info:
            freq_to_arfcn(2016668 * MHZ)
        assert "Frequency 2016668000000 is out of supported range." in str(exc_info.value)

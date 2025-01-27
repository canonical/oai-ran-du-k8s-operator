#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import MagicMock, patch

import pytest

from src.du_parameters.absolute_frequency_ssb import get_absolute_frequency_ssb
from src.du_parameters.gscn_arfcn import HighFrequency, LowFrequency, MidFrequency

# A random test frequency
TEST_FREQUENCY = 24300


class TestGetAbsoluteFrequencySSB:
    def setup_method(self):
        self.get_frequency_instance_patch = patch(
            "src.du_parameters.absolute_frequency_ssb.get_frequency_instance"
        )
        self.mock_get_frequency_instance = self.get_frequency_instance_patch.start()
        self.mock_frequency_instance = MagicMock()

        self.mock_frequency_instance.freq_to_gscn.return_value = 0
        self.mock_frequency_instance.gscn_to_freq.return_value = 0
        self.mock_frequency_instance.freq_to_arfcn.return_value = 0
        self.mock_get_frequency_instance.return_value = self.mock_frequency_instance

    def teardown_method(self):
        patch.stopall()

    @pytest.mark.parametrize(
        "frequency, gscn, arfcn, gscn_to_freq, frequency_class",
        [
            (24250, 9432, None, 24249, HighFrequency),
            # Value of N: -0.004629629629730684 is out of supported range (0-4383).
            (99999, 232324, None, 99890, HighFrequency),
            # Value of N: 4383.618055555555 is out of supported range (0-4383).
            (0, 4, None, 0, LowFrequency),
            # Value of N: -0.12500000000000003 is out of supported range (1-2499).
            (2999, 4, None, 2998, LowFrequency),
            # Value of N: 2499.0416666666665 is out of supported range (1-2499)
            (24249, 9233, None, 24199, MidFrequency),
            # Value of N: 14756.25 is out of supported range (0-14756)
        ],
    )
    def test_get_arfcn_when_valid_input_provided_but_n_is_out_of_supported_range_then_none_is_returned(  # noqa E501
        self, frequency, gscn, arfcn, gscn_to_freq, frequency_class
    ):
        self.mock_frequency_instance.freq_to_gscn.return_value = gscn
        self.mock_frequency_instance.gscn_to_freq.return_value = gscn_to_freq
        self.mock_frequency_instance.freq_to_arfcn.return_value = arfcn

        result = get_absolute_frequency_ssb(frequency)
        assert result == arfcn

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
            (24250.5, None),
            (0.01, None),
        ],
    )
    def test_get_arfcn_when_float_inputs_provided_then_return_arfcn(self, frequency, expected):
        result = get_absolute_frequency_ssb(frequency)
        assert result is None

    @pytest.mark.parametrize(
        "frequency, expected",
        [
            (HighFrequency.RANGE[0], None),
            (HighFrequency.RANGE[1], None),
            (LowFrequency.RANGE[0], None),
            (LowFrequency.RANGE[1], None),
            (MidFrequency.RANGE[0], None),
            (MidFrequency.RANGE[1], None),
        ],
    )
    def test_get_arfcn_when_boundary_frequencies_provided_then_return_arfcn(
        self, frequency, expected
    ):
        result = get_absolute_frequency_ssb(frequency)
        assert result == expected

    def test_get_arfcn_when_freq_to_gscn_calculation_fails_then_return_none(
        self,
    ):
        self.mock_frequency_instance.freq_to_gscn.return_value = None
        self.mock_get_frequency_instance.return_value = self.mock_frequency_instance
        result = get_absolute_frequency_ssb(TEST_FREQUENCY)
        assert result is None

    def test_get_arfcn_when_gscn_to_freq_calculation_fails_then_returns_none(
        self,
    ):
        self.mock_frequency_instance.gscn_to_freq.return_value = None
        self.mock_get_frequency_instance.return_value = self.mock_frequency_instance

        result = get_absolute_frequency_ssb(TEST_FREQUENCY)
        assert result is None

    def test_get_arfcn_when_frequency_set_failure_then_return_none(
        self,
    ):
        self.mock_frequency_instance.gscn_to_freq.return_value = 24290  # Random value
        self.mock_frequency_instance.freq_to_gscn.return_value = 9444  # Random value
        type(self.mock_frequency_instance).frequency = MagicMock(
            side_effect=ValueError("invalid frequency value")
        )
        self.mock_get_frequency_instance.return_value = self.mock_frequency_instance
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
    def test_get_arfcn_when_different_exceptions_occur_then_return_none(self, exception):
        self.mock_get_frequency_instance.side_effect = exception
        result = get_absolute_frequency_ssb(TEST_FREQUENCY)
        assert result is None

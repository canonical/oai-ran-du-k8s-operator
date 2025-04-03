#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.


import pytest

from src.du_parameters import (
    ARFCN,
    AbsoluteFrequencySSBError,
    Frequency,
    get_absolute_frequency_ssb,
)


class TestAbsoluteFrequencySSB:
    @pytest.mark.parametrize(
        "invalid_freq, expected_error, error_message",
        [
            (-1222, AbsoluteFrequencySSBError, "Expected Frequency, got int"),
            (
                "invalid",
                AbsoluteFrequencySSBError,
                "Expected Frequency, got str",
            ),
            (
                None,
                AbsoluteFrequencySSBError,
                "Expected Frequency, got NoneType",
            ),
            (
                Frequency.from_mhz(100099991111212),
                AbsoluteFrequencySSBError,
                "No frequency range found for frequency 100099991111212000000",
            ),
        ],
    )
    def test_get_absolute_frequency_ssb_when_input_with_invalid_type_given_then_raise_exception(  # noqa: E501
        self, invalid_freq, expected_error, error_message
    ):
        invalid_center_freq = invalid_freq
        with pytest.raises(expected_error) as e:
            get_absolute_frequency_ssb(invalid_center_freq)
        assert error_message in str(e.value)

    @pytest.mark.parametrize(
        "center_freq, expected_result",
        [
            (3925, 661632),
            (4000, 666624),
            (20, 4110),
            (1000, 199950),
            (25000, 2029052),
            (4900, 726432),
        ],
    )
    def test_get_absolute_frequency_ssb_when_center_frequency_given_then_return_expected_result(
        self, center_freq, expected_result
    ):
        result = get_absolute_frequency_ssb(Frequency.from_mhz(center_freq))
        assert result == ARFCN(expected_result)

    @pytest.mark.parametrize(
        "center_freq, expected_error_message",
        [
            (0, "Value of N: -0.125 is out of supported range (1-2499)"),
            (
                99999,
                "Value of N: 4383.618055555555555555555556 is out of supported range (0-4383)",  # noqa: E501
            ),
        ],
    )
    def test_get_absolute_frequency_ssb_when_n_is_out_of_range_then_raise_error(
        self, center_freq, expected_error_message
    ):
        with pytest.raises(AbsoluteFrequencySSBError) as err:
            get_absolute_frequency_ssb(Frequency.from_mhz(center_freq))
        assert expected_error_message in str(err.value)

    @pytest.mark.parametrize(
        "invalid_freq, expected_error, error_message",
        [
            (
                -1e10,  # Extremely large negative value
                AbsoluteFrequencySSBError,
                "No frequency range found for frequency -10000000000000000",
            ),
            (
                1e10,  # Extremely large positive value
                AbsoluteFrequencySSBError,
                "No frequency range found for frequency 10000000000000000",
            ),
            (
                complex(1, 1),  # Complex number
                TypeError,
                "conversion from complex to Decimal is not supported",
            ),
        ],
    )
    def test_get_absolute_frequency_ssb_when_extreme_invalid_values_given_then_raise_error(
        self, invalid_freq, expected_error, error_message
    ):
        with pytest.raises(expected_error) as err:
            get_absolute_frequency_ssb(Frequency.from_mhz(invalid_freq))
        assert error_message in str(err.value)

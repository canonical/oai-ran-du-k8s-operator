#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.


import pytest

from src.du_parameters import (
    Frequency,
    GuardBandError,
    get_carrier_bandwidth,
    get_minimum_guard_band,
)


class TestGetCarrierBandwidth:
    @pytest.mark.parametrize(
        "bandwidth, subcarrier_spacing, expected_bandwidth",
        [
            (Frequency.from_mhz(10), Frequency.from_khz(15), 52),
            (Frequency.from_mhz(50), Frequency.from_khz(30), 133),
            (Frequency.from_mhz(5), Frequency.from_khz(15), 25),
            (Frequency.from_mhz(100), Frequency.from_khz(60), 135),
            (Frequency.from_mhz(20), Frequency.from_khz(15), 106),
        ],
    )
    def test_carrier_bandwidth_when_valid_inputs_given_then_return_expected_result(
        self, bandwidth, subcarrier_spacing, expected_bandwidth
    ):
        result = get_carrier_bandwidth(bandwidth, subcarrier_spacing)
        assert result == expected_bandwidth

    @pytest.mark.parametrize(
        "bandwidth, subcarrier_spacing",
        [
            (Frequency.from_mhz(-1), Frequency.from_khz(30)),
            (Frequency.from_mhz(10), Frequency.from_khz(-15)),
        ],
    )
    def test_carrier_bandwidth_when_negative_input_values_given_then_raise_error(
        self, bandwidth, subcarrier_spacing
    ):
        with pytest.raises(
            ValueError, match="Both bandwidth and subcarrier spacing must be greater than 0"
        ):
            get_carrier_bandwidth(bandwidth, subcarrier_spacing)

    @pytest.mark.parametrize(
        "bandwidth, subcarrier_spacing",
        [
            ("10MHz", Frequency.from_khz(15)),
            (Frequency.from_mhz(20), "30kHz"),
        ],
    )
    def test_carrier_bandwidth_when_string_inputs_given_then_raise_error(
        self, bandwidth, subcarrier_spacing
    ):
        with pytest.raises(
            TypeError, match="'<=' not supported between instances of 'str' and 'Frequency'"
        ):
            get_carrier_bandwidth(bandwidth, subcarrier_spacing)

    def test_carrier_bandwidth_when_none_inputs_are_given_then_raise_error(self):
        with pytest.raises(
            TypeError, match="'<=' not supported between instances of 'NoneType' and 'Frequency'"
        ):
            get_carrier_bandwidth(None, None)  # type: ignore


class TestGetMinimumGuardBand:
    @pytest.mark.parametrize(
        "scs, bandwidth, expected_guard_band",
        [
            (Frequency.from_khz(15), Frequency.from_mhz(10), Frequency.from_khz("312.5")),
            (Frequency.from_khz(60), Frequency.from_mhz(40), Frequency.from_khz(1610)),
        ],
    )
    def test_guard_band_when_valid_inputs_given_then_return_expected_results(
        self, scs, bandwidth, expected_guard_band
    ):
        result = get_minimum_guard_band(scs, bandwidth)
        assert result == expected_guard_band

    @pytest.mark.parametrize(
        "scs, bandwidth",
        [
            (Frequency.from_khz(15), Frequency.from_mhz(105)),
            (Frequency.from_khz(60), Frequency.from_mhz(500)),
        ],
    )
    def test_guard_band_when_unsupported_guard_band_or_scs_is_provided_then_raise_error(
        self, scs, bandwidth
    ):
        with pytest.raises(
            GuardBandError,
            match=f"No guard band found for bandwidth={bandwidth} and SCS={scs}",
        ):
            get_minimum_guard_band(scs, bandwidth)

    @pytest.mark.parametrize(
        "scs, bandwidth, expected_error_message",
        [
            (Frequency.from_khz(0), Frequency.from_mhz(10), r"No guard band found for SCS=0"),
            (
                Frequency.from_khz(100),
                Frequency.from_mhz(20),
                r"No guard band found for SCS=100000",
            ),
        ],
    )
    def test_guard_band_when_invalid_scs_values_given_then_raise_error(
        self, scs, bandwidth, expected_error_message
    ):
        with pytest.raises(GuardBandError, match=expected_error_message):
            get_minimum_guard_band(scs, bandwidth)

    @pytest.mark.parametrize(
        "scs, bandwidth",
        [
            ("15kHz", Frequency.from_mhz(10)),
            (Frequency.from_khz(15), "20MHz"),
            (None, None),
        ],
    )
    def test_guard_band_when_invalid_type_inputs_given_then_raise_error(self, scs, bandwidth):
        with pytest.raises(GuardBandError, match="No guard band found"):
            get_minimum_guard_band(scs, bandwidth)

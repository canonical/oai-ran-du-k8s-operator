# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from decimal import Decimal

import pytest

from src.du_parameters.frequency import (
    ARFCN,
    GSCN,
    HIGH_FREQUENCY,
    LOW_FREQUENCY,
    MID_FREQUENCY,
    Frequency,
    get_config_for_frequency,
)


@pytest.mark.parametrize(
    "from_khz, from_mhz, expected_repr",
    [
        (1000, 1.0, "Frequency(1000000)"),
        (2000, 2.0, "Frequency(2000000)"),
        (500, 0.5, "Frequency(500000)"),
    ],
)
def test_frequency_instantiation_when_khz_or_mhz_values_are_given_then_return_in_hz(
    from_khz, from_mhz, expected_repr
):
    freq1 = Frequency.from_khz(from_khz)
    freq2 = Frequency.from_mhz(from_mhz)
    assert freq1 == freq2
    assert isinstance(freq1, Frequency)
    assert repr(freq1) == expected_repr


@pytest.mark.parametrize(
    "freq1_khz, freq2_khz, expected_khz",
    [
        (500, 500, 1000),
        (1000, 2000, 3000),
        (0, 1500, 1500),
    ],
)
def test_frequency_addition_when_khz_inputs_given_then_return_in_khz(
    freq1_khz, freq2_khz, expected_khz
):
    freq1 = Frequency.from_khz(freq1_khz)
    freq2 = Frequency.from_khz(freq2_khz)
    total = freq1 + freq2
    assert total == Frequency.from_khz(expected_khz)
    assert isinstance(total, Frequency)


@pytest.mark.parametrize(
    "freq1_mhz, freq2_khz, expected_hz",
    [
        (500, 500, 500500000),
        (1000, 2000, 1002000000),
        (10, 1500, 11500000),
    ],
)
def test_frequency_addition_when_mixed_inputs_given_then_return_in_hz(
    freq1_mhz, freq2_khz, expected_hz
):
    freq1 = Frequency.from_mhz(freq1_mhz)
    freq2 = Frequency.from_khz(freq2_khz)
    total = freq1 + freq2
    assert total == Frequency(expected_hz)
    assert isinstance(total, Frequency)


@pytest.mark.parametrize("invalid_input", ["invalid", None])
def test_frequency_addition_when_invalid_inputs_given_then_raise_type_error(invalid_input):
    freq1 = Frequency.from_khz(500)
    with pytest.raises(TypeError):
        _ = freq1 + invalid_input


@pytest.mark.parametrize(
    "freq1_mhz, freq2_khz, expected_hz",
    [
        (2.0, 500, Decimal("1500000")),
        (1.0, 500, Decimal("500000")),
    ],
)
def test_frequency_subtraction_when_mhz_and_khz_inputs_given_then_return_output_in_hz(
    freq1_mhz, freq2_khz, expected_hz
):
    freq1 = Frequency.from_mhz(freq1_mhz)
    freq2 = Frequency.from_khz(freq2_khz)
    result = freq1 - freq2
    assert result == Frequency(expected_hz)


@pytest.mark.parametrize("invalid_input", ["invalid", None])
def test_frequency_subtraction_when_invalid_inputs_given_then_raise_error(invalid_input):
    freq1 = Frequency.from_mhz(2.0)
    with pytest.raises(TypeError):
        _ = freq1 - invalid_input


@pytest.mark.parametrize(
    "freq, expected_config_name",
    [
        (0.0001, "LowFrequency"),
        (2999.000, "LowFrequency"),
        (3000, "MidFrequency"),
        (24249.999, "MidFrequency"),
        (24250, "HighFrequency"),
        (99999.999, "HighFrequency"),
    ],
)
def test_get_config_for_frequency_when_valid_frequencies_given_then_return_expected_config_range(
    freq, expected_config_name
):
    config = get_config_for_frequency(freq)
    assert config.name == expected_config_name  # type: ignore


@pytest.mark.parametrize(
    "freq_hz, expected_arfcn",
    [
        (Frequency.from_mhz(3924.48), 661632),
        (Frequency.from_mhz(3000), 600000),
    ],
)
def test_freq_to_arfcn_when_freq_is_given_in_mhz_then_arfcn_is_returned(freq_hz, expected_arfcn):
    assert ARFCN.freq_to_arfcn(freq_hz) == expected_arfcn


@pytest.mark.parametrize("invalid_freq_mhz", [150000, -1])
def test_freq_to_arfcn_when_invalid_inputs_given_then_raise_value_error(invalid_freq_mhz):
    with pytest.raises(ValueError):
        ARFCN.freq_to_arfcn(invalid_freq_mhz)


@pytest.mark.parametrize(
    "frequency_mhz, expected_gscn",
    [
        (100, 25248),
        (3000, 7499),
        (4000, 8193),
        (24000, 22082),
        (50000, 23746),
        (99090, 26587),
        (3925, 8141),
    ],
)
def test_freq_to_gscn_when_valid_inputs_given_then_return_expected_gcsn(
    frequency_mhz, expected_gscn
):
    gscn = GSCN.freq_to_gcsn(frequency_mhz)
    assert isinstance(gscn, int)
    assert gscn == expected_gscn


@pytest.mark.parametrize("frequency", [24250, 0, 24249, 99999, 2999])
def test_freq_to_gscn_when_n_is_out_of_range_then_raise_value_error(frequency):
    with pytest.raises(ValueError) as err:
        GSCN.freq_to_gcsn(frequency)
    assert "is out of supported range" in str(err.value)


@pytest.mark.parametrize(
    "frequency_band, gscn, expected_freq",
    [
        (LOW_FREQUENCY, 25248, Decimal("99950000")),
        (MID_FREQUENCY, 8193, Decimal("3999360000")),
        (MID_FREQUENCY, 8141, Decimal("3924480000")),
        (HIGH_FREQUENCY, 26587, Decimal("99089760000")),
    ],
)
def test_gscn_to_freq_when_valid_inputs_given_then_return_expected_frequency(
    frequency_band, gscn, expected_freq
):
    freq = GSCN.gscn_to_freq(frequency_band, gscn)
    assert isinstance(freq, Decimal)
    assert freq == expected_freq


@pytest.mark.parametrize(
    "frequency_band, gscn",
    [
        (LOW_FREQUENCY, -248),
        (MID_FREQUENCY, 93),
        (MID_FREQUENCY, 8140001),
        (HIGH_FREQUENCY, -34),
    ],
)
def test_gscn_to_freq_when_invalid_inputs_given_then_raise_value_error(frequency_band, gscn):
    with pytest.raises(ValueError) as err:
        GSCN.gscn_to_freq(frequency_band, gscn)
    assert "Invalid GSCN or frequency range." in str(err.value)

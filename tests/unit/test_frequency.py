# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
import decimal
from builtins import isinstance

import pytest

from src.du_parameters.frequency import (
    ARFCN,
    GSCN,
    HIGH_FREQUENCY,
    LOW_FREQUENCY,
    MID_FREQUENCY,
    Frequency,
    GetRangeFromFrequencyError,
    GetRangeFromGSCNError,
    get_range_from_frequency,
    get_range_from_gscn,
)


class TestFrequency:
    @pytest.mark.parametrize(
        "from_khz, from_mhz, expected_repr",
        [
            (1000, "1.0", "Frequency(1000000)"),
            (2000, "2.0", "Frequency(2000000)"),
            (500, "0.5", "Frequency(500000)"),
            (0, "0.0", "Frequency(0)"),
            (100000000, "100000.0", "Frequency(100000000000)"),
        ],
    )
    def test_frequency_instantiation_when_khz_or_mhz_values_are_given_then_return_expected_value(
        self, from_khz, from_mhz, expected_repr
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
            (10**7, 10**7, 2 * 10**7),
        ],
    )
    def test_frequency_addition_when_khz_inputs_given_then_result_is_expected_value(
        self, freq1_khz, freq2_khz, expected_khz
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
    def test_frequency_addition_when_mixed_inputs_given_then_result_is_expected_value(
        self, freq1_mhz, freq2_khz, expected_hz
    ):
        freq1 = Frequency.from_mhz(freq1_mhz)
        freq2 = Frequency.from_khz(freq2_khz)
        total = freq1 + freq2
        assert total == Frequency(expected_hz)
        assert isinstance(total, Frequency)

    @pytest.mark.parametrize("invalid_input", ["invalid", "wrong"])
    def test_frequency_addition_when_invalid_inputs_given_then_raise_error(self, invalid_input):
        freq1 = Frequency.from_khz(500)
        with pytest.raises(NotImplementedError):
            _ = freq1 + invalid_input

    @pytest.mark.parametrize(
        "freq1_mhz, freq2_khz, expected_hz",
        [
            ("2.0", 500, "1500000"),
            ("1.0", 500, "500000"),
            ("1.0", 0, "1000000"),
            ("5.0", "1.0", "4999000.0"),
        ],
    )
    def test_frequency_subtraction_when_mhz_and_khz_inputs_given_then_return_expected_output(  # noqa: E501
        self, freq1_mhz, freq2_khz, expected_hz
    ):
        freq1 = Frequency.from_mhz(freq1_mhz)
        freq2 = Frequency.from_khz(freq2_khz)
        result = freq1 - freq2
        assert result == Frequency(expected_hz)

    @pytest.mark.parametrize("invalid_input", ["invalid", "wrong"])
    def test_frequency_subtraction_when_invalid_inputs_given_then_raise_error(self, invalid_input):
        freq1 = Frequency.from_mhz("2.0")
        with pytest.raises(NotImplementedError):
            _ = freq1 - invalid_input

    @pytest.mark.parametrize(
        "freq1_mhz, freq2_mhz, expected",
        [
            ("1.0", "2.0", True),
            ("2.0", "1.0", False),
            ("2.0", "2.0", False),
        ],
    )
    def test_frequency_comparison_when_valid_inputs_are_given_then_return_expected_results(
        self, freq1_mhz, freq2_mhz, expected
    ):
        freq1 = Frequency.from_mhz(freq1_mhz)
        freq2 = Frequency.from_mhz(freq2_mhz)
        assert (freq1 < freq2) == expected

    def test_frequency_add_operation_when_float_type_input_is_given_then_raise_error(self):
        freq = Frequency.from_mhz(3000)
        with pytest.raises(TypeError):
            freq + 1.5

    def test_frequency_subtract_operation_when_unsupported_type_is_given_then_raise_error(self):
        freq = Frequency.from_mhz(3000)
        with pytest.raises(NotImplementedError):
            freq - "invalid"

    def test_frequency_divide_operation_when_unsupported_type_is_given_then_raise_error(self):
        freq = Frequency.from_mhz(3000)
        with pytest.raises(NotImplementedError):
            freq / [1, 2]

    def test_frequency_subtraction_when_big_value_is_extracted_from_small_value_then_return_negative_result(  # noqa: E501
        self,
    ):
        freq1 = Frequency.from_mhz(1000)
        freq2 = Frequency.from_mhz(3000)
        result = freq1 - freq2
        assert result == Frequency(-2000000000)


class TestGetRangeFromFrequency:
    @pytest.mark.parametrize(
        "freq, expected_config_name",
        [
            ("0.0001", "LowFrequency"),
            ("2999.000", "LowFrequency"),
            (3000, "MidFrequency"),
            ("24249.999", "MidFrequency"),
            (24250, "HighFrequency"),
            ("99999.999", "HighFrequency"),
        ],
    )
    def test_get_range_from_frequency_when_valid_frequencies_given_then_return_expected_config_range(  # noqa: E501
        self, freq, expected_config_name
    ):
        config = get_range_from_frequency(Frequency.from_mhz(freq))
        assert config.name == expected_config_name  # type: ignore[argument]

    @pytest.mark.parametrize(
        "invalid_freq, expected_error",
        [
            (-1, GetRangeFromFrequencyError),
            ("invalid", decimal.InvalidOperation),
            (None, TypeError),
        ],
    )
    def test_get_range_from_frequency_when_invalid_inputs_given_then_raise_error(
        self, invalid_freq, expected_error
    ):
        with pytest.raises(expected_error):
            _ = get_range_from_frequency(Frequency.from_mhz(invalid_freq))


class TestARFCN:
    @pytest.mark.parametrize(
        "freq_hz, expected_arfcn",
        [
            (Frequency.from_mhz("3924.48"), 661632),
            (Frequency.from_khz(3000), 600),
            (Frequency.from_mhz(0), 0),
        ],
    )
    def test_arfcn_from_frequency_when_freq_is_given_in_mhz_then_arfcn_is_returned(
        self, freq_hz, expected_arfcn
    ):
        assert ARFCN.from_frequency(freq_hz) == expected_arfcn

    @pytest.mark.parametrize(
        "invalid_freq_mhz, expected_error",
        [
            (Frequency.from_mhz(150000), ValueError),
            (Frequency.from_mhz(-1), ValueError),
            ("invalid", TypeError),
            (-100, TypeError),
            (None, TypeError),
        ],
    )
    def test_arfcn_from_frequency_when_invalid_inputs_given_then_raise_value_error(
        self, invalid_freq_mhz, expected_error
    ):
        with pytest.raises(expected_error):
            ARFCN.from_frequency(invalid_freq_mhz)

    @pytest.mark.parametrize(
        "channel, expected_error",
        [
            (-1, ValueError),
            (3279166, ValueError),
        ],
    )
    def test_arfcn_when_values_given_lower_than_min_upper_than_max_then_raise_error(
        self, channel, expected_error
    ):
        with pytest.raises(expected_error):
            ARFCN(channel)

    def test_arfcn_addition_when_incompatible_type_is_given_then_raise_error(self):
        arfcn = ARFCN(100)
        with pytest.raises(NotImplementedError):
            arfcn + "invalid"

    def test_arfcn_addition_when_compatible_types_are_given_then_return_expected_result(self):
        arfcn1 = ARFCN(100)
        arfcn2 = ARFCN(50)
        result = arfcn1 + arfcn2
        assert result._channel == 150


class TestGSCN:
    @pytest.mark.parametrize(
        "frequency_mhz, expected_gscn",
        [
            (100, GSCN(250)),
            (2000, GSCN(5000)),
            (3000, GSCN(7499)),
            (4000, GSCN(8193)),
            (24000, GSCN(22082)),
            (50000, GSCN(23746)),
            (99090, GSCN(26587)),
            (3925, GSCN(8141)),
            (2, GSCN(5)),
        ],
    )
    def test_gscn_from_frequency_when_valid_inputs_given_then_return_expected_gcsn(
        self, frequency_mhz, expected_gscn
    ):
        gscn = GSCN.from_frequency(Frequency.from_mhz(frequency_mhz))
        assert isinstance(gscn, GSCN)
        assert gscn == expected_gscn

    @pytest.mark.parametrize("frequency_mhz", [24250, 0, 24249, 99999, 2999])
    def test_gscn_from_frequency_when_n_is_out_of_range_then_raise_value_error(
        self, frequency_mhz
    ):
        with pytest.raises(ValueError) as err:
            GSCN.from_frequency(Frequency.from_mhz(frequency_mhz))
        assert "is out of supported range" in str(err.value)

    @pytest.mark.parametrize("frequency_mhz", [-1, 99999999999])
    def test_gscn_from_frequency_when_n_is_out_of_range_then_raise_range_error(
        self, frequency_mhz
    ):
        with pytest.raises(ValueError) as err:
            GSCN.from_frequency(Frequency.from_mhz(frequency_mhz))
        assert (
            f"No frequency range found for frequency " f"{Frequency.from_mhz(frequency_mhz)}"
        ) in str(err.value)

    @pytest.mark.parametrize(
        "gscn, expected_freq",
        [
            (25248, Frequency("75951840000")),
            (8193, Frequency("3999360000")),
            (8141, Frequency("3924480000")),
            (26587, Frequency("99089760000")),
            (26639, Frequency("99988320000")),
            (200, Frequency("80550000")),
        ],
    )
    def test_gscn_to_freq_when_valid_inputs_given_then_return_expected_frequency(
        self, gscn, expected_freq
    ):
        freq = GSCN.to_frequency(GSCN(gscn))
        assert isinstance(freq, Frequency)
        assert freq == expected_freq

    @pytest.mark.parametrize(
        "gscn, expected_error",
        [
            (-248, ValueError),
            (8140001, ValueError),
            (-34, ValueError),
            ("invalid", TypeError),
            (None, TypeError),
        ],
    )
    def test_gscn_to_freq_when_invalid_inputs_given_then_raise_error(self, gscn, expected_error):
        with pytest.raises(expected_error):
            GSCN.to_frequency(GSCN(gscn))

    def test_gscn_equality_when_valid_inputs_given_then_return_expected_result(self):
        gscn1 = GSCN(1000)
        gscn2 = GSCN(1000)
        gscn3 = GSCN(2000)
        assert gscn1 == gscn2
        assert gscn1 != gscn3

    @pytest.mark.parametrize(
        "channel, expected_error, error_message",
        [
            (-10, ValueError, "GSCN must be between 0 and 26639, got -10 instead"),
            (8140001, ValueError, "GSCN must be between 0 and 26639, got 8140001 instead"),
            ("invalid", TypeError, "Channel must be an integer"),
        ],
    )
    def test_gscn_initialization_when_invalid_input_given_then_raise_error(
        self, channel, expected_error, error_message
    ):
        with pytest.raises(expected_error) as err:
            GSCN(channel)
        assert error_message in str(err.value)

    def test_gscn_addition_when_other_type_is_invalid_then_raise_error(self):
        gscn = GSCN(100)
        with pytest.raises(NotImplementedError) as err:
            gscn + [1, 2, 3]
        assert "Unsupported type for addition: list" in str(err.value)


class TestGetRangeFromGSCN:
    @pytest.mark.parametrize(
        "gscn_input, expected_output",
        [
            (GSCN(2), LOW_FREQUENCY),
            (GSCN(7498), LOW_FREQUENCY),
            (GSCN(1000), LOW_FREQUENCY),
            (GSCN(2900), LOW_FREQUENCY),
            (GSCN(7499), MID_FREQUENCY),
            (GSCN(22255), MID_FREQUENCY),
            (GSCN(15000), MID_FREQUENCY),
            (GSCN(22256), HIGH_FREQUENCY),
            (GSCN(26639), HIGH_FREQUENCY),
            (GSCN(25000), HIGH_FREQUENCY),
        ],
    )
    def test_get_range_from_gscn_when_valid_input_given_then_return_expected_result(
        self, gscn_input, expected_output
    ):
        assert get_range_from_gscn(gscn_input) == expected_output

    @pytest.mark.parametrize(
        "invalid_gscn_input, exception_type, exception_message",
        [
            (GSCN(1), GetRangeFromGSCNError, "is out of supported range"),
            (None, TypeError, "Expected GSCN, got NoneType"),
            ("invalid", TypeError, "Expected GSCN, got str"),
        ],
    )
    def test_get_range_from_gscn_when_invalid_inputs_given_then_raise_error(
        self, invalid_gscn_input, exception_type, exception_message
    ):
        with pytest.raises(exception_type) as excinfo:
            get_range_from_gscn(invalid_gscn_input)
        assert exception_message in str(excinfo.value)

#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import patch

import pytest

from src.du_parameters.afrcn import freq_to_arfcn
from src.du_parameters.ssb import (
    BaseSSB,
    HighFrequencySSB,
    LowFrequencySSB,
    MidFrequencySSB,
    get_absolute_frequency_ssb,
    get_frequency_instance,
)

MHZ = 1000000  # HZ
# A random test frequency
TEST_FREQUENCY = 24300 * MHZ


class TestBaseSSB:
    def test_base_frequency_when_called_directly_then_raise_not_implemented_error(self):
        with pytest.raises(NotImplementedError) as err:
            BaseSSB(1000 * MHZ)
        assert "BaseFrequency cannot be instantiated directly." in str(err.value)

    def test_child_class_when_range_is_defined_then_subclass_is_instantiated(self):
        class ValidFrequency(BaseSSB):
            RANGE = (2 * MHZ, 300 * MHZ)

            def some_required_method(self):
                return "Implemented"

        instance = ValidFrequency(2 * MHZ)
        assert isinstance(instance, ValidFrequency)

    def test_child_class_when_range_is_missing_then_raise_error(self):
        class ValidFrequency(BaseSSB):
            def some_required_method(self):
                return "Implemented"

        with pytest.raises(ValueError) as err:
            ValidFrequency(1 * MHZ)
        assert "Frequency 1000000 is out of range for ValidFrequency." in str(err.value)

    def test_child_class_when_child_class_is_unimplemented_then_raise_error(self):
        class IncompleteFrequency(BaseSSB):
            pass

        with pytest.raises(ValueError) as err:
            IncompleteFrequency(1000 * MHZ)
        assert "Frequency 1000000000 is out of range for IncompleteFrequency." in str(err.value)

    def test_child_class_when_child_class_is_defined_with_inverted_range_then_raise_error(self):
        class InvertedRangeFrequency(BaseSSB):
            RANGE = (3000 * MHZ, 1000 * MHZ)

        with pytest.raises(ValueError) as err:
            InvertedRangeFrequency(2000 * MHZ)
        assert "Frequency 2000000000 is out of range for InvertedRangeFrequency." in str(err.value)

    @pytest.mark.parametrize(
        "frequency",
        [
            -1 * MHZ,
            3000 * MHZ,
        ],
    )
    def test_child_class_when_invalid_initial_input_then_raises_error(self, frequency):
        with pytest.raises(ValueError) as err:
            LowFrequencySSB(frequency)
        assert f"Frequency {frequency} is out of range for LowFrequencySSB." in str(err.value)

    @pytest.mark.parametrize(
        "frequency",
        [
            -0.00000001 * MHZ,
        ],
    )
    def test_child_class_when_float_initial_input_then_raises_error(self, frequency):
        with pytest.raises(TypeError) as err:
            LowFrequencySSB(frequency)
        assert "Frequency -0.01 is not a numeric value." in str(err.value)

    @pytest.mark.parametrize(
        "frequency",
        [
            "2332323",
            "some-value",
            None,
        ],
    )
    def test_child_class_when_non_numeric_input_provided_then_raises_error(self, frequency):
        with pytest.raises(TypeError) as err:
            LowFrequencySSB(frequency)
        assert f"Frequency {frequency} is not a numeric value." in str(err.value)

    def test_base_class_enforcing_an_abstract_method_when_child_class_instance_called_with_enforced_method_then_method_is_available(  # noqa E501
        self,
    ):
        class ConcreteFrequency(BaseSSB):
            RANGE = (0, 300 * MHZ)

            def some_required_method(self):
                return "Implemented"

        freq = ConcreteFrequency(200)
        assert freq.some_required_method() == "Implemented"


class TestLowFrequencySSB:
    @pytest.mark.parametrize(
        "frequency",
        [
            -232 * MHZ,
            int(-0.0001 * MHZ),
            -1 * MHZ,
            3000 * MHZ,
            3001 * MHZ,
            5000 * MHZ,
        ],
    )
    def test_low_frequency_instance_when_invalid_value_provided_then_raise_value_error(
        self, frequency
    ):
        with pytest.raises(ValueError) as err:
            instance = LowFrequencySSB(frequency)
            assert instance is None
        assert f"Frequency {frequency} is out of range for LowFrequencySSB." in str(err.value)

    @pytest.mark.parametrize(
        "frequency",
        [
            0,
            int(0.333 * MHZ),
            100 * MHZ,
            1000 * MHZ,
            2000 * MHZ,
            int(2999.9999 * MHZ),
        ],
    )
    def test_low_frequency_instance_when_valid_value_provided_then_instance_is_instantiated(
        self, frequency
    ):
        instance = LowFrequencySSB(frequency)
        assert isinstance(instance, LowFrequencySSB)

    def test_low_frequency_instance_when_freq_to_gcsn_is_called_then_gcsn_returned(self):
        instance = LowFrequencySSB(2000 * MHZ)
        assert instance.freq_to_gscn() == 4999

    @pytest.mark.parametrize(
        "frequency",
        [
            2999 * MHZ,
            int(2998.999 * MHZ),
        ],
    )
    def test_low_frequency_instance_when_freq_to_gcsn_is_called_then_n_is_out_of_supported_range(
        self, frequency
    ):
        with pytest.raises(ValueError):
            instance = LowFrequencySSB(frequency)
            instance.freq_to_gscn()

    def test_low_frequency_instance_when_gcsn_to_freq_is_called_then_freq_is_returned(self):
        instance = LowFrequencySSB(2000 * MHZ)
        assert instance.gscn_to_freq(4999) == 1999.75 * MHZ

    def test_low_frequency_when_freq_to_arfcn_is_called_then_arfcn_is_returned(self):
        assert freq_to_arfcn(int(1999.75 * MHZ)) == 399950


class TestMidFrequencySSB:
    @pytest.mark.parametrize(
        "frequency",
        [
            int(999.999 * MHZ),
            24250 * MHZ,
            30000 * MHZ,
            24251 * MHZ,
            2900 * MHZ,
            1000000000,  # HZ
        ],
    )
    def test_mid_frequency_instance_when_invalid_value_provided_then_raise_value_error(
        self, frequency
    ):
        with pytest.raises(ValueError) as err:
            instance = MidFrequencySSB(frequency)
            assert instance is None
        assert f"Frequency {frequency} is out of range for MidFrequencySSB." in str(err.value)

    @pytest.mark.parametrize(
        "frequency",
        [
            3000000000,  # HZ
            3001 * MHZ,
            int(24249.999 * MHZ),
            24000 * MHZ,
            3900 * MHZ,
        ],
    )
    def test_mid_frequency_instance_when_valid_value_provided_then_instance_is_instantiated(
        self, frequency
    ):
        instance = MidFrequencySSB(frequency)
        assert isinstance(instance, MidFrequencySSB)

    @pytest.mark.parametrize(
        "frequency",
        [
            int(24249.9999 * MHZ),
            24249 * MHZ,
            int(24248.999 * MHZ),
        ],
    )
    def test_mid_frequency_instance_when_freq_to_gcsn_is_called_then_n_is_out_of_supported_range(
        self, frequency
    ):
        with pytest.raises(ValueError):
            instance = MidFrequencySSB(frequency)
            instance.freq_to_gscn()

    def test_mid_frequency_instance_when_freq_to_gcsn_is_called_then_gcsn_returned(self):
        instance = MidFrequencySSB(3925 * MHZ)
        assert instance.freq_to_gscn() == 8141

    def test_mid_frequency_instance_when_gcsn_to_freq_is_called_then_freq_is_returned(self):
        instance = MidFrequencySSB(3925 * MHZ)
        assert instance.gscn_to_freq(8141) == 3924.48 * MHZ

    def test_mid_frequency_when_freq_to_arfcn_is_called_then_arfcn_is_returned(self):
        assert freq_to_arfcn(int(3924.48 * MHZ)) == 661632


class TestHighFrequencySSB:
    @pytest.mark.parametrize(
        "frequency",
        [
            int(24249.9999 * MHZ),
            24000000000,  # HZ
            1000 * MHZ,
            100000 * MHZ,
            int(100000.0001 * MHZ),
            200000000000,  # HZ
        ],
    )
    def test_high_frequency_instance_when_invalid_value_provided_then_raise_value_error(
        self, frequency
    ):
        with pytest.raises(ValueError) as err:
            instance = HighFrequencySSB(frequency)
            assert instance is None
        assert f"Frequency {frequency} is out of range for HighFrequencySSB." in str(err.value)

    @pytest.mark.parametrize(
        "frequency",
        [
            24250000000,  # HZ
            int(99999.999 * MHZ),
            80000 * MHZ,
            int(24250.001 * MHZ),
            24251 * MHZ,
            30000 * MHZ,
        ],
    )
    def test_high_frequency_instance_when_valid_value_provided_then_instance_is_instantiated(
        self, frequency
    ):
        instance = HighFrequencySSB(frequency)
        assert isinstance(instance, HighFrequencySSB)

    def test_high_frequency_instance_when_freq_to_gcsn_is_called_then_gcsn_returned(self):
        instance = HighFrequencySSB(50000 * MHZ)
        assert instance.freq_to_gscn() == 23746

    @pytest.mark.parametrize(
        "frequency",
        [
            99990 * MHZ,
            99991 * MHZ,
            int(99999.999 * MHZ),
        ],
    )
    def test_high_frequency_instance_when_freq_to_gcsn_is_called_then_n_is_out_of_supported_range(
        self, frequency
    ):
        with pytest.raises(ValueError):
            instance = HighFrequencySSB(frequency)
            instance.freq_to_gscn()

    def test_high_frequency_instance_when_gcsn_to_freq_is_called_then_freq_is_returned(self):
        instance = HighFrequencySSB(50000 * MHZ)
        assert instance.gscn_to_freq(23746) == 49997.28 * MHZ

    def test_high_frequency_instance_when_freq_to_arfcn_is_called_then_arfcn_is_returned(self):
        assert freq_to_arfcn(50000 * MHZ) == 2445833


class TestGetFrequencyInstance:
    @pytest.mark.parametrize(
        "frequency, expected_cls",
        [
            (int(0), LowFrequencySSB),
            (int(1500000000), LowFrequencySSB),
            (int(2999999000), LowFrequencySSB),
            (int(3000000000), MidFrequencySSB),
            (5000000000, MidFrequencySSB),
            (24249990000, MidFrequencySSB),
            (24250000000, HighFrequencySSB),
            (50000000000, HighFrequencySSB),
            (99999990000, HighFrequencySSB),
        ],
    )
    def test_get_frequency_instance_when_valid_ranges_provided_then_instance_returned(
        self, frequency, expected_cls
    ):
        instance = get_frequency_instance(frequency)
        assert isinstance(instance, expected_cls)
        assert int(instance.frequency) == frequency

    @pytest.mark.parametrize(
        "frequency",
        [
            -100,
            -1000000,
            150000000000,
            100000000000,
        ],
    )
    def test_get_frequency_instance_when_invalid_ranges_provided_then_error_raised(
        self, frequency
    ):
        with pytest.raises(ValueError) as err:
            get_frequency_instance(frequency)
        assert f"Frequency {frequency} is out of supported range." in str(err.value)

    @pytest.mark.parametrize(
        "frequency",
        [
            "some-value",
            "-2",
        ],
    )
    def test_get_frequency_instance_when_invalid_input_types_provided_then_error_raised(
        self, frequency
    ):
        with pytest.raises(TypeError) as err:
            get_frequency_instance(frequency)
        assert f"Frequency {frequency} is not a numeric value." in str(err.value)

    def test_get_frequency_instance_when_input_is_none_then_error_raised(self):
        with pytest.raises(TypeError) as err:
            get_frequency_instance(None)  # type: ignore
        assert "Frequency None is not a numeric value." in str(err.value)


class TestGetAbsoluteFrequencySSB:
    @pytest.mark.parametrize(
        "frequency, gscn, gscn_to_freq, frequency_class",
        [
            (24250 * MHZ, 9432, 24249 * MHZ, HighFrequencySSB),
            # Value of N: -0.004629629629730684 is out of supported range (0-4383).
            (99999 * MHZ, 232324, 99890 * MHZ, HighFrequencySSB),
            # Value of N: 4383.618055555555 is out of supported range (0-4383).
            (0 * MHZ, 4, 0 * MHZ, LowFrequencySSB),
            # Value of N: -0.12500000000000003 is out of supported range (1-2499).
            (2999 * MHZ, 4, 2998 * MHZ, LowFrequencySSB),
            # Value of N: 2499.0416666666665 is out of supported range (1-2499)
            (24249 * MHZ, 9233, 24199 * MHZ, MidFrequencySSB),
            # Value of N: 14756.25 is out of supported range (0-14756)
        ],
    )
    @patch("src.du_parameters.ssb.get_frequency_instance")
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
            (int(HighFrequencySSB.RANGE[0]), None),
            (int(HighFrequencySSB.RANGE[1]), None),
            (int(LowFrequencySSB.RANGE[0]), None),
            (int(LowFrequencySSB.RANGE[1]), 600000),
            (int(MidFrequencySSB.RANGE[0]), 600000),
            (int(MidFrequencySSB.RANGE[1]), None),
        ],
    )
    def test_get_arfcn_when_boundary_frequencies_provided_then_return_arfcn(
        self, frequency, expected
    ):
        result = get_absolute_frequency_ssb(frequency)
        assert result == expected

    @patch("src.du_parameters.ssb.get_frequency_instance")
    def test_get_arfcn_when_freq_to_gscn_calculation_fails_then_return_none(
        self, mock_get_frequency_instance
    ):
        mock_get_frequency_instance.freq_to_gscn.return_value = None
        result = get_absolute_frequency_ssb(TEST_FREQUENCY)
        assert result is None

    @patch("src.du_parameters.ssb.get_frequency_instance")
    def test_get_arfcn_when_gscn_to_freq_calculation_fails_then_returns_none(
        self, mock_get_frequency_instance
    ):
        mock_get_frequency_instance.gscn_to_freq.return_value = None

        result = get_absolute_frequency_ssb(TEST_FREQUENCY)
        assert result is None

    @pytest.mark.parametrize(
        "frequency",
        [
            -10 * MHZ,  # Below MIN_N
            250000 * MHZ,  # Above HighFrequency.MAX_N
        ],
    )
    def test_get_arfcn_when_out_of_range_frequencies_provided_then_return_none(self, frequency):
        result = get_absolute_frequency_ssb(frequency)
        assert result is None

    @pytest.mark.parametrize(
        "exception", [TypeError("Unexpected error"), ValueError("Invalid value")]
    )
    @patch("src.du_parameters.ssb.get_frequency_instance")
    def test_get_arfcn_when_different_exceptions_occur_then_return_none(
        self, mock_get_frequency_instance, exception
    ):
        mock_get_frequency_instance.side_effect = exception
        result = get_absolute_frequency_ssb(TEST_FREQUENCY)
        assert result is None

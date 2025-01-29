#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest

from src.du_parameters.afrcn import freq_to_arfcn
from src.du_parameters.ssb import (
    BaseSSB,
    HighFrequencySSB,
    LowFrequencySSB,
    MidFrequencySSB,
    get_frequency_instance,
)


class TestBaseSSB:
    def test_base_frequency_when_called_directly_then_raise_not_implemented_error(self):
        with pytest.raises(NotImplementedError) as err:
            BaseSSB(1000)
        assert "BaseFrequency cannot be instantiated directly." in str(err.value)

    def test_child_class_when_range_is_defined_then_subclass_is_instantiated(self):
        class ValidFrequency(BaseSSB):
            RANGE = (2, 300)

            def some_required_method(self):
                return "Implemented"

        instance = ValidFrequency(2)
        assert isinstance(instance, ValidFrequency)

    def test_child_class_when_range_is_missing_then_raise_error(self):
        class ValidFrequency(BaseSSB):
            def some_required_method(self):
                return "Implemented"

        with pytest.raises(ValueError) as err:
            ValidFrequency(1)
        assert "Frequency 1 is out of range for ValidFrequency." in str(err.value)

    def test_child_class_when_child_class_is_unimplemented_then_raise_error(self):
        class IncompleteFrequency(BaseSSB):
            pass

        with pytest.raises(ValueError) as err:
            IncompleteFrequency(1000)
        assert "Frequency 1000 is out of range for IncompleteFrequency." in str(err.value)

    def test_child_class_when_child_class_is_defined_with_inverted_range_then_raise_error(self):
        class InvertedRangeFrequency(BaseSSB):
            RANGE = (3000, 1000)

        with pytest.raises(ValueError) as err:
            InvertedRangeFrequency(2000)
        assert "Frequency 2000 is out of range for InvertedRangeFrequency." in str(err.value)

    @pytest.mark.parametrize(
        "frequency",
        [
            -0.0001,
            -1,
            3000,
        ],
    )
    def test_child_class_when_invalid_initial_input_then_raises_error(self, frequency):
        with pytest.raises(ValueError) as err:
            LowFrequencySSB(frequency)
        assert f"Frequency {frequency} is out of range for LowFrequencySSB." in str(err.value)

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
            RANGE = (0, 300)

            def some_required_method(self):
                return "Implemented"

        freq = ConcreteFrequency(200)
        assert freq.some_required_method() == "Implemented"


class TestLowFrequencySSB:
    @pytest.mark.parametrize(
        "frequency",
        [
            -232,
            -0.0001,
            -1,
            3000,
            3001,
            5000,
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
            0.333,
            100,
            1000,
            2000,
            2999.9999,
        ],
    )
    def test_low_frequency_instance_when_valid_value_provided_then_instance_is_instantiated(
        self, frequency
    ):
        instance = LowFrequencySSB(frequency)
        assert isinstance(instance, LowFrequencySSB)

    def test_low_frequency_instance_when_freq_to_gcsn_is_called_then_gcsn_returned(self):
        instance = LowFrequencySSB(2000)
        assert instance.freq_to_gscn() == 4999

    @pytest.mark.parametrize(
        "frequency",
        [
            2999,
            2998.999,
        ],
    )
    def test_low_frequency_instance_when_freq_to_gcsn_is_called_then_n_is_out_of_supported_range(
        self, frequency
    ):
        with pytest.raises(ValueError):
            instance = LowFrequencySSB(frequency)
            instance.freq_to_gscn()

    def test_low_frequency_instance_when_gcsn_to_freq_is_called_then_freq_is_returned(self):
        instance = LowFrequencySSB(2000)
        assert instance.gscn_to_freq(4999) == 1999.75

    def test_low_frequency_when_freq_to_arfcn_is_called_then_arfcn_is_returned(self):
        assert freq_to_arfcn(1999.75) == 399950


class TestMidFrequencySSB:
    @pytest.mark.parametrize(
        "frequency",
        [
            2999.999,
            24250,
            30000,
            24251,
            2900,
            1000,
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
            3000,
            3001,
            24249.999,
            24000,
            3900,
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
            24249.9999,
            24249,
            24248.999,
        ],
    )
    def test_mid_frequency_instance_when_freq_to_gcsn_is_called_then_n_is_out_of_supported_range(
        self, frequency
    ):
        with pytest.raises(ValueError):
            instance = MidFrequencySSB(frequency)
            instance.freq_to_gscn()

    def test_mid_frequency_instance_when_freq_to_gcsn_is_called_then_gcsn_returned(self):
        instance = MidFrequencySSB(3925)
        assert instance.freq_to_gscn() == 8141

    def test_mid_frequency_instance_when_gcsn_to_freq_is_called_then_freq_is_returned(self):
        instance = MidFrequencySSB(3925)
        assert instance.gscn_to_freq(8141) == 3924.48

    def test_mid_frequency_when_freq_to_arfcn_is_called_then_arfcn_is_returned(self):
        assert freq_to_arfcn(3924.48) == 661632


class TestHighFrequencySSB:
    @pytest.mark.parametrize(
        "frequency",
        [
            24249.9999,
            24000,
            1000,
            100000,
            100000.0001,
            200000,
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
            24250,
            99999.999,
            80000,
            24250.001,
            24251,
            30000,
        ],
    )
    def test_high_frequency_instance_when_valid_value_provided_then_instance_is_instantiated(
        self, frequency
    ):
        instance = HighFrequencySSB(frequency)
        assert isinstance(instance, HighFrequencySSB)

    def test_high_frequency_instance_when_freq_to_gcsn_is_called_then_gcsn_returned(self):
        instance = HighFrequencySSB(50000)
        assert instance.freq_to_gscn() == 23746

    @pytest.mark.parametrize(
        "frequency",
        [
            99990,
            99991,
            99999.999,
        ],
    )
    def test_high_frequency_instance_when_freq_to_gcsn_is_called_then_n_is_out_of_supported_range(
        self, frequency
    ):
        with pytest.raises(ValueError):
            instance = HighFrequencySSB(frequency)
            instance.freq_to_gscn()

    def test_high_frequency_instance_when_gcsn_to_freq_is_called_then_freq_is_returned(self):
        instance = HighFrequencySSB(50000)
        assert instance.gscn_to_freq(23746) == 49997.28

    def test_high_frequency_instance_when_freq_to_arfcn_is_called_then_arfcn_is_returned(self):
        assert freq_to_arfcn(50000) == 2445833


class TestGetFrequencyInstance:
    @pytest.mark.parametrize(
        "frequency, expected_cls",
        [
            (0, LowFrequencySSB),
            (1500, LowFrequencySSB),
            (2999.999, LowFrequencySSB),
            (3000, MidFrequencySSB),
            (5000, MidFrequencySSB),
            (24249.99, MidFrequencySSB),
            (24250, HighFrequencySSB),
            (50000, HighFrequencySSB),
            (99999.99, HighFrequencySSB),
        ],
    )
    def test_get_frequency_instance_when_valid_ranges_provided_then_instance_returned(
        self, frequency, expected_cls
    ):
        instance = get_frequency_instance(frequency)
        assert isinstance(instance, expected_cls)
        assert instance.frequency == frequency

    @pytest.mark.parametrize(
        "frequency",
        [
            -0.0001,
            -1,
            150000,
            100000,
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

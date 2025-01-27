#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest

from src.du_parameters.gscn_arfcn import (
    BaseFrequency,
    HighFrequency,
    LowFrequency,
    MidFrequency,
    get_frequency_instance,
)


class TestBaseFrequency:
    def test_base_frequency_when_called_directly_then_raise_not_implemented_error(self):
        with pytest.raises(NotImplementedError) as err:
            BaseFrequency(1000)
        assert "BaseFrequency cannot be instantiated directly." in str(err.value)

    def test_child_class_when_range_is_defined_then_subclass_is_instantiated(self):
        class ValidFrequency(BaseFrequency):
            RANGE = (2, 300)

            def some_required_method(self):
                return "Implemented"

        instance = ValidFrequency(2)
        assert isinstance(instance, ValidFrequency)

    def test_child_class_when_range_is_missing_then_raise_error(self):
        class ValidFrequency(BaseFrequency):
            def some_required_method(self):
                return "Implemented"

        with pytest.raises(ValueError) as err:
            ValidFrequency(1)
        assert "Frequency 1 is out of range for ValidFrequency." in str(err.value)

    def test_child_class_when_child_class_is_unimplemented_then_raise_error(self):
        class IncompleteFrequency(BaseFrequency):
            pass

        with pytest.raises(ValueError) as err:
            IncompleteFrequency(1000)
        assert "Frequency 1000 is out of range for IncompleteFrequency." in str(err.value)

    def test_child_class_when_child_class_is_defined_with_inverted_range_then_raise_error(self):
        class InvertedRangeFrequency(BaseFrequency):
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
            LowFrequency(frequency)
        assert f"Frequency {frequency} is out of range for LowFrequency." in str(err.value)

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
            LowFrequency(frequency)
        assert f"Frequency {frequency} is not a numeric value." in str(err.value)

    def test_base_class_enforcing_an_abstract_method_when_child_class_instance_called_with_enforced_method_then_method_is_available(  # noqa E501
        self,
    ):
        class ConcreteFrequency(BaseFrequency):
            RANGE = (0, 300)

            def some_required_method(self):
                return "Implemented"

        freq = ConcreteFrequency(200)
        assert freq.some_required_method() == "Implemented"


class TestLowFrequency:
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
            instance = LowFrequency(frequency)
            assert instance is None
        assert f"Frequency {frequency} is out of range for LowFrequency." in str(err.value)

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
        instance = LowFrequency(frequency)
        assert isinstance(instance, LowFrequency)

    def test_low_frequency_instance_when_freq_to_gcsn_is_called_then_gcsn_returned(self):
        instance = LowFrequency(2000)
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
            instance = LowFrequency(frequency)
            instance.freq_to_gscn()

    def test_low_frequency_instance_when_gcsn_to_freq_is_called_then_freq_is_returned(self):
        instance = LowFrequency(2000)
        assert instance.gscn_to_freq(4999) == 1999.75

    def test_low_frequency_instance_when_freq_to_arfcn_is_called_then_arfcn_is_returned(self):
        instance = LowFrequency(1999.75)
        assert instance.freq_to_arfcn() == 399950


class TestMidFrequency:
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
            instance = MidFrequency(frequency)
            assert instance is None
        assert f"Frequency {frequency} is out of range for MidFrequency." in str(err.value)

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
        instance = MidFrequency(frequency)
        assert isinstance(instance, MidFrequency)

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
            instance = MidFrequency(frequency)
            instance.freq_to_gscn()

    def test_mid_frequency_instance_when_freq_to_gcsn_is_called_then_gcsn_returned(self):
        instance = MidFrequency(3925)
        assert instance.freq_to_gscn() == 8141

    def test_mid_frequency_instance_when_gcsn_to_freq_is_called_then_freq_is_returned(self):
        instance = MidFrequency(3925)
        assert instance.gscn_to_freq(8141) == 3924.48

    def test_mid_frequency_instance_when_freq_to_arfcn_is_called_then_arfcn_is_returned(self):
        instance = MidFrequency(3924.48)
        assert instance.freq_to_arfcn() == 661632


class TestHighFrequency:
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
            instance = HighFrequency(frequency)
            assert instance is None
        assert f"Frequency {frequency} is out of range for HighFrequency." in str(err.value)

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
        instance = HighFrequency(frequency)
        assert isinstance(instance, HighFrequency)

    def test_high_frequency_instance_when_freq_to_gcsn_is_called_then_gcsn_returned(self):
        instance = HighFrequency(50000)
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
            instance = HighFrequency(frequency)
            instance.freq_to_gscn()

    def test_high_frequency_instance_when_gcsn_to_freq_is_called_then_freq_is_returned(self):
        instance = HighFrequency(50000)
        assert instance.gscn_to_freq(23746) == 49997.28

    def test_high_frequency_instance_when_freq_to_arfcn_is_called_then_arfcn_is_returned(self):
        instance = HighFrequency(50000)
        assert instance.freq_to_arfcn() == 2445833


class TestGetFrequencyInstance:
    @pytest.mark.parametrize(
        "frequency, expected_cls",
        [
            (0, LowFrequency),
            (1500, LowFrequency),
            (2999.999, LowFrequency),
            (3000, MidFrequency),
            (5000, MidFrequency),
            (24249.99, MidFrequency),
            (24250, HighFrequency),
            (50000, HighFrequency),
            (99999.99, HighFrequency),
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
        assert "Frequency cannot be None." in str(err.value)

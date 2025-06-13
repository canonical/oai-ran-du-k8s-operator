import pytest
from pydantic import ValidationError

from src.charm_config import DUConfig


class TestFrequencyBandValidation:
    @pytest.mark.parametrize(
        "frequency_band, center_frequency",
        [
            (48, "3590.33"),
            (77, "3500"),
            (38, "2590.5"),
            (90, "2530"),
        ],
    )
    def test_frequency_band_validation_when_valid_values_given_then_return_expected_results(
        self, frequency_band, center_frequency
    ):
        config = {
            "f1-port": 8080,
            "frequency-band": frequency_band,
            "bandwidth": 20,
            "sub-carrier-spacing": 15,
            "center-frequency": center_frequency,
        }
        assert DUConfig(**config).frequency_band == frequency_band

    @pytest.mark.parametrize(
        "frequency_band",
        [
            103,
            33,
            500,
        ],
    )
    def test_frequency_band_validation_when_invalid_values_given_then_raise_error(
        self, frequency_band
    ):
        config = {
            "f1-port": 8080,
            "frequency-band": frequency_band,
            "bandwidth": 40,
            "sub-carrier-spacing": 30,
            "center-frequency": "3500.22",
        }
        with pytest.raises(ValidationError):
            DUConfig(**config)


class TestBandwidthValidation:
    @pytest.mark.parametrize(
        "bandwidth, frequency_band, sub_carrier_spacing, center_frequency",
        [
            (20, 38, 30, "2590"),
            (15, 77, 15, "3700"),
            (100, 77, 30, "3700"),
            (40, 79, 30, "4520"),
        ],
    )
    def test_bandwidth_validation_when_valid_values_given_then_return_expected_values(
        self, bandwidth, frequency_band, sub_carrier_spacing, center_frequency
    ):
        config = {
            "f1-port": 8080,
            "bandwidth": bandwidth,
            "frequency-band": frequency_band,
            "sub-carrier-spacing": sub_carrier_spacing,
            "center-frequency": center_frequency,
        }
        assert DUConfig(**config).bandwidth == bandwidth

    @pytest.mark.parametrize(
        "bandwidth, frequency_band, sub_carrier_spacing",
        [
            (200, 77, 30),
            (3, 38, 15),
            (50, 103, 15),
            (60, 40, 30),
        ],
    )
    def test_bandwidth_validation_when_invalid_values_given_then_raise_error(
        self, bandwidth, frequency_band, sub_carrier_spacing
    ):
        config = {
            "f1-port": 8080,
            "bandwidth": bandwidth,
            "frequency-band": frequency_band,
            "sub-carrier-spacing": sub_carrier_spacing,
            "center-frequency": "3500",
        }
        with pytest.raises(ValidationError or ValueError):
            DUConfig(**config)


class TestCenterFrequencyValidation:
    @pytest.mark.parametrize(
        "center_frequency, frequency_band, bandwidth, subcarrier_spacing",
        [
            ("3750", 77, 40, 30),
            ("4900", 79, 40, 30),
            ("1429.5", 51, 5, 15),
            ("3330", 78, 50, 15),
        ],
    )
    def test_center_frequency_validation_when_valid_inputs_given_then_return_expected_result(
        self, center_frequency, frequency_band, bandwidth, subcarrier_spacing
    ):
        config = {
            "f1-port": 8080,
            "center-frequency": center_frequency,
            "frequency-band": frequency_band,
            "bandwidth": bandwidth,
            "sub-carrier-spacing": subcarrier_spacing,
        }
        assert DUConfig(**config).center_frequency == center_frequency

    @pytest.mark.parametrize(
        "center_frequency, frequency_band, bandwidth",
        [
            ("4201", 77, 40),
            ("1431", 51, 5),
            ("8000", 96, 60),
        ],
    )
    def test_center_frequency_validation_when_invalid_input_given_then_raise_error(
        self, center_frequency, frequency_band, bandwidth
    ):
        config = {
            "f1-port": 8080,
            "center-frequency": center_frequency,
            "frequency-band": frequency_band,
            "bandwidth": bandwidth,
            "sub-carrier-spacing": 30,
        }

        with pytest.raises(
            ValidationError,
            match=f"Center_frequency {center_frequency} must be within the usable range",
        ):
            DUConfig(**config)


class TestSubCarrierSpacingValidation:
    @pytest.mark.parametrize(
        "sub_carrier_spacing, frequency_band, bandwidth, center_frequency",
        [
            (30, 38, 40, "2599"),
            (15, 34, 10, "2016"),
            (30, 77, 100, "3360"),
            (30, 90, 80, "2540"),
        ],
    )
    def test_sub_carrier_spacing_validation_when_valid_input_given_then_return_expected_result(
        self, sub_carrier_spacing, frequency_band, bandwidth, center_frequency
    ):
        config = {
            "f1-port": 8080,
            "sub-carrier-spacing": sub_carrier_spacing,
            "frequency-band": frequency_band,
            "bandwidth": bandwidth,
            "center-frequency": center_frequency,
        }
        assert DUConfig(**config).sub_carrier_spacing == sub_carrier_spacing

    @pytest.mark.parametrize(
        "sub_carrier_spacing, frequency_band, bandwidth",
        [
            (15, 38, 100),
            (25, 77, 50),
            (60, 51, 5),
            (15, 40, 12),
        ],
    )
    def test_sub_carrier_spacing_validation_when_invalid_input_given_then_raise_error(
        self, sub_carrier_spacing, frequency_band, bandwidth
    ):
        config = {
            "f1-port": 8080,
            "sub-carrier-spacing": sub_carrier_spacing,
            "frequency-band": frequency_band,
            "bandwidth": bandwidth,
            "center-frequency": "3500",
        }
        with pytest.raises(ValidationError):
            DUConfig(**config)


class TestFullDUConfigValidation:
    @pytest.mark.parametrize(
        "frequency_band, bandwidth, sub_carrier_spacing, center_frequency",
        [
            (38, 40, 30, "2592"),
            (77, 25, 15, "3700"),
            (78, 20, 30, "3400"),
        ],
    )
    def test_full_du_config_validation_for_all_attributes_when_valid_inputs_given_then_return_expected_results(  # noqa: E501
        self,
        frequency_band,
        bandwidth,
        sub_carrier_spacing,
        center_frequency,
    ):
        config = {
            "f1-port": 8080,
            "frequency-band": frequency_band,
            "bandwidth": bandwidth,
            "sub-carrier-spacing": sub_carrier_spacing,
            "center-frequency": center_frequency,
        }
        assert DUConfig(**config).frequency_band == frequency_band
        assert DUConfig(**config).bandwidth == bandwidth
        assert DUConfig(**config).sub_carrier_spacing == sub_carrier_spacing
        assert DUConfig(**config).center_frequency == center_frequency

    @pytest.mark.parametrize(
        "frequency_band, bandwidth, sub_carrier_spacing, center_frequency",
        [
            (77, 150, 60, "3700"),
            (77, 40, 15, "5000"),
            (33, 40, 30, "3500"),
            (90, 25, 20, "2500"),
            (38, 40, 30, "20000"),
        ],
    )
    def test_full_du_config_validation_for_all_attributes_when_invalid_inputs_given_then_raise_error(  # noqa: E501
        self, frequency_band, bandwidth, sub_carrier_spacing, center_frequency
    ):
        config = {
            "f1-port": 8080,
            "frequency-band": frequency_band,
            "bandwidth": bandwidth,
            "sub-carrier-spacing": sub_carrier_spacing,
            "center-frequency": center_frequency,
        }
        with pytest.raises(ValueError):
            DUConfig(**config)

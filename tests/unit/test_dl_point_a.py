# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import patch

import pytest

from src.du_parameters.dl_point_a import get_dl_absolute_freq_point_a


class TestDLAbsoluteFreqPointA:
    @pytest.mark.parametrize(
        "center_freq, bandwidth, expected_result",
        [
            (3500, 100, 695312),  # Valid case with ints
            (3400.5, 50.5, 704256),  # Valid case with floats
        ],
    )
    @patch("src.du_parameters.dl_point_a.freq_to_arfcn")
    def test_get_dl_absolute_freq_point_a_when_valid_input_provided_then_return_valid_output(
        self, mock_freq_to_arfcn, center_freq, bandwidth, expected_result
    ):
        mock_freq_to_arfcn.return_value = expected_result
        result = get_dl_absolute_freq_point_a(center_freq, bandwidth)
        assert result == expected_result

    @pytest.mark.parametrize(
        "center_freq, bandwidth",
        [
            ("invalid", 100),  # Invalid center_freq: string
            (3500, "invalid"),  # Invalid bandwidth: string
            (None, 100),  # center_freq is None
            (3500, None),  # bandwidth is None
        ],
    )
    def test_get_dl_absolute_freq_point_a_when_invalid_inputs_are_provided_then_return_none(
        self, center_freq, bandwidth
    ):
        result = get_dl_absolute_freq_point_a(center_freq, bandwidth)
        assert result is None

    @patch("src.du_parameters.dl_point_a.freq_to_arfcn")
    def test_get_dl_absolute_freq_point_a_when_freq_to_arfcn_returns_value_error_then_return_none(
        self, mock_freq_to_arfcn
    ):
        mock_freq_to_arfcn.side_effect = ValueError("Invalid frequency")
        result = get_dl_absolute_freq_point_a(3500, 100)
        assert result is None

    @patch("src.du_parameters.dl_point_a.freq_to_arfcn")
    def test_get_dl_absolute_freq_point_a_when_freq_to_arfcn_returns_unhandled_exception_then_result_is_none(  # noqa: E501
        self, mock_freq_to_arfcn
    ):
        mock_freq_to_arfcn.side_effect = Exception("Unexpected error")
        result = get_dl_absolute_freq_point_a(3500, 100)
        assert result is None

    @patch("src.du_parameters.dl_point_a.freq_to_arfcn")
    def test_get_dl_absolute_freq_point_a_when_error_occurred_then_error_logged(
        self, mock_freq_to_arfcn, caplog
    ):
        mock_freq_to_arfcn.side_effect = ValueError("Invalid ARFCN calculation")
        with caplog.at_level("ERROR"):
            result = get_dl_absolute_freq_point_a(3500, 100)
        assert result is None
        assert "Failed to calculate dl_absoluteFrequencyPointA" in caplog.text

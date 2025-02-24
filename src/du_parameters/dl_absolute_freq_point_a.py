# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Calculate the frequency location of Point A in the downlink."""

import decimal
import logging
from decimal import Decimal

from .frequency import (
    ARFCN,
    Frequency,
    GetRangeFromFrequencyError,
)

logger = logging.getLogger(__name__)

CONFIG_CONSTANT_TWO = Decimal("2")


class DLAbsoluteFrequencyPointAError(Exception):
    """Exception raised when Downlink Absolute Frequency Point A calculation fails."""

    pass


def get_dl_absolute_frequency_point_a(
    center_freq: Frequency, bandwidth: Frequency, sub_carrier_spacing: Frequency
) -> "ARFCN":
    """Calculate downlink absolute frequency Point A using center frequency and bandwidth.

    Args:
        center_freq (Frequency): Center frequency
        bandwidth (Frequency): Bandwidth
        sub_carrier_spacing (Frequency): Subcarrier spacing

    Returns:
        ARFCN: The dl absolute frequency point A in ARFCN format

    Raises:
        DLAbsoluteFrequencyPointAError: If calculation fails due to invalid inputs or operations
    """
    try:
        lowest_freq = center_freq - (bandwidth / CONFIG_CONSTANT_TWO)
        # Align the lowest frequency to the channel raster
        aligned_lowest_freq = round(lowest_freq / sub_carrier_spacing) * sub_carrier_spacing
        # Ensure aligned_lowest_freq is not less than lowest_freq
        if aligned_lowest_freq < lowest_freq:
            aligned_lowest_freq += sub_carrier_spacing
        arfcn = ARFCN.from_frequency(Frequency(aligned_lowest_freq))
        logger.info("Calculated downlink absolute frequency Point A: %s", arfcn)
        return arfcn
    except (
        TypeError,
        ValueError,
        decimal.InvalidOperation,
        NotImplementedError,
        GetRangeFromFrequencyError,
    ) as e:
        logger.error(
            "Error calculating downlink absolute frequency Point A"
            " using center_freq=%s and bandwidth=%s: %s",
            center_freq,
            bandwidth,
            str(e),
        )
        raise DLAbsoluteFrequencyPointAError(
            f"Error calculating downlink absolute frequency Point A "
            f"using center_freq={center_freq} and bandwidth={bandwidth}: {e}"
        )

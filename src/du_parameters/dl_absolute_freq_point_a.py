# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Calculate the frequency location of Point A in the downlink."""

import decimal
import logging
from decimal import Decimal

from src.du_parameters.frequency import (
    ARFCN,
    Frequency,
    GetRangeFromFrequencyError,
)

logger = logging.getLogger(__name__)

CONFIG_CONSTANT_TWO = Decimal("2")


class DLAbsoluteFrequencyPointAError(Exception):
    """Exception raised when Downlink Absolute Frequency Point A calculation fails."""

    pass


def get_dl_absolute_frequency_point_a(center_freq: Frequency, bandwidth: Frequency) -> ARFCN:
    """Calculate downlink absolute frequency Point A using center frequency and bandwidth.

    Args:
        center_freq (Frequency): Center frequency
        bandwidth (Frequency): Bandwidth

    Returns:
        ARFCN: The dl absolute frequency point A in ARFCN format

    Raises:
        DLAbsoluteFrequencyPointAError: If calculation fails due to invalid inputs or operations
    """
    try:
        lowest_freq = center_freq - (bandwidth / CONFIG_CONSTANT_TWO)
        return ARFCN.from_frequency(lowest_freq)
    except (
        TypeError,
        ValueError,
        decimal.InvalidOperation,
        NotImplementedError,
        GetRangeFromFrequencyError,
    ) as e:
        raise DLAbsoluteFrequencyPointAError(
            f"Error calculating downlink absolute frequency Point A "
            f"using center_freq={center_freq} and bandwidth={bandwidth}: {e}"
        )

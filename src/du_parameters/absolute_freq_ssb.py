# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Calculate Synchronization Signal Block ARFCN for given 5G RF center frequency."""

import decimal
import logging

from src.du_parameters.frequency import (
    ARFCN,
    GSCN,
    Frequency,
    GetRangeFromFrequencyError,
)

logger = logging.getLogger(__name__)


class AbsoluteFrequencySSBError(Exception):
    """Exception raised when absolute frequency SSB calculation fails."""

    pass


def get_absolute_frequency_ssb(center_freq: Frequency) -> ARFCN:
    """Calculate absolute frequency SSB using center frequency.

    Args:
        center_freq (Frequency): Center frequency

    Returns:
        ARFCN: The absolute SSB frequency in ARFCN format

    Raises:
        AbsoluteFrequencySSBError: If calculation fails
    """
    try:
        gscn = GSCN.from_frequency(center_freq)
        adjusted_frequency = GSCN.to_frequency(gscn)
        return ARFCN.from_frequency(adjusted_frequency)
    except (
        TypeError,
        ValueError,
        decimal.InvalidOperation,
        NotImplementedError,
        GetRangeFromFrequencyError,
        GetRangeFromFrequencyError,
    ) as e:
        raise AbsoluteFrequencySSBError(
            f"Error calculating absolute frequency for SSB with center_freq={center_freq}: {e}"
        )

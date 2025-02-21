# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Calculate Synchronization Signal Block ARFCN for given 5G RF center frequency."""

import decimal
import logging

from .frequency import (
    ARFCN,
    GSCN,
    Frequency,
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
        adjusted_frequency = gscn.to_frequency()
        afrcn = ARFCN.from_frequency(adjusted_frequency)
        logger.info(
            "Calculated absolute frequency for SSB with center_freq=%s: %s",
            center_freq,
            afrcn,
        )
        return afrcn
    except (
        TypeError,
        ValueError,
        decimal.InvalidOperation,
        NotImplementedError,
    ) as e:
        logger.error(
            "Error calculating absolute frequency for SSB with center_freq=%s", center_freq
        )
        raise AbsoluteFrequencySSBError(
            f"Error calculating absolute frequency for SSB with center_freq={center_freq}: {e}"
        )

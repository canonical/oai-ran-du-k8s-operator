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

        # TODO: This is a workaround for n79, it will requires future redesign
        # n79 needs the GSCN on a raster of 16, so we take the remainder of the
        # division with 16, and if it is lower than 8, subtract it from the GSCN.
        # Otherwise, we add its difference from 16 to the GSCN. This will give
        # a GSCN that is divisible by 16.
        if center_freq >= Frequency.from_mhz(4400) and center_freq <= Frequency.from_mhz(5000):
            modulo = gscn % 16
            if modulo < 8:
                gscn = gscn - modulo
            else:
                gscn = gscn + (16 - modulo)

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

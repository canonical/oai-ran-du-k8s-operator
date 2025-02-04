# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Calculate Synchronization Signal Block frequency for given 5G RF center frequency."""

import logging

from src.du_parameters.frequency import ARFCN, GSCN, Frequency, get_config_for_frequency

logger = logging.getLogger(__name__)


def get_absolute_frequency_ssb(center_freq: float | int) -> int | None:
    """Calculate absolute frequency SSB using center frequency.

    Args:
        center_freq (float or int): Center frequency in MHz.

    Returns:
        int | None: The absolute SSB frequency in ARFCN format, or None if calculation fails.
    """
    try:
        if not isinstance(center_freq, (int, float)) or center_freq <= 0:
            logger.error(f"Invalid center frequency: {center_freq}")
            return None

        frequency = Frequency.from_mhz(center_freq)
        config = get_config_for_frequency(frequency)
        if config is None:
            logger.error(f"Invalid frequency: {frequency}")
            return None

        gscn = GSCN.freq_to_gcsn(frequency)
        adjusted_freq = GSCN.gscn_to_freq(config, gscn)
        return ARFCN.freq_to_arfcn(adjusted_freq)

    except (TypeError, AttributeError, ValueError) as e:
        logger.error(
            f"Error calculating absolute frequency for SSB with center_freq={center_freq}: {e}"
        )
        return None

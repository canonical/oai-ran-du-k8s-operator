# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Calculate absoluteFrequencySSB (ARFCN)."""

import logging
from typing import Optional

from src.du_parameters.gscn_arfcn import DetectFrequencyRange

logger = logging.getLogger(__name__)


def get_absolute_frequency_ssb(center_freq: float) -> Optional[int, None]:
    """Calculate absolute frequency for ssb using center frequency.

    Args:
        center_freq (float): Center frequency
    Returns:
        arfcn (int): if successful, else None
    """
    try:
        if not isinstance(center_freq, (int, float)) or center_freq <= 0:
            logger.error(f"Invalid center frequency: {center_freq}")
            return None

        frequency_range = DetectFrequencyRange(center_freq)
        frequency_instance = frequency_range.get_frequency_instance()
        if frequency_instance is None:
            logger.error(f"Failed to get a valid frequency instance for center_freq={center_freq}")
            return None

        # Calculate GSCN
        gcsn = frequency_instance.freq_to_gscn()
        # Convert GSCN to frequency
        frequency_from_gcsn = frequency_instance.gscn_to_freq(gcsn)

        try:
            # Set new frequency attribute
            frequency_instance.frequency = frequency_from_gcsn
        except ValueError as e:
            logger.error(f"Failed to set frequency to {frequency_from_gcsn}: {e}")
            return None

        # Convert frequency to ARFCN
        return frequency_instance.freq_to_arfcn()

    except Exception as e:
        logger.error(
            f"Error in getting absolute frequency for ssb using center_freq={center_freq}: {e}"
        )
        return None

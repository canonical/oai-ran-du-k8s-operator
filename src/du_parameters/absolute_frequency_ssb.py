# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Calculate absoluteFrequencySSB (ARFCN)."""

import logging
from typing import Optional, Union

from src.du_parameters.gscn_arfcn import (
    HighFrequency,
    LowFrequency,
    MidFrequency,
    get_frequency_instance,
)

logger = logging.getLogger(__name__)


def get_absolute_frequency_ssb(center_freq: Optional[Union[int, float]]) -> Optional[int]:
    """Calculate absolute frequency for ssb using center frequency.

    Args:
        center_freq (float or int): Center frequency in MHz.

    Returns:
        arfcn (int): if successful, else None.
    """
    try:
        # Input validation
        if not isinstance(center_freq, (int, float)):
            return None

        # Get frequency instance
        frequency_instance = get_frequency_instance(center_freq)
        if not isinstance(frequency_instance, (HighFrequency, MidFrequency, LowFrequency)):
            logger.error(f"Failed to create a frequency instance for center_freq={center_freq}")
            return None

        # Calculate GSCN
        gcsn = frequency_instance.freq_to_gscn()
        if gcsn is None:
            logger.error(f"Failed to calculate GSCN for center_freq={center_freq}")
            return None

        # Convert GSCN to frequency
        frequency_from_gcsn = frequency_instance.gscn_to_freq(gcsn)
        if not isinstance(frequency_from_gcsn, (int, float)):
            logger.error(f"Computed frequency_from_gscn is not valid: {frequency_from_gcsn}")
            return None

        try:
            # Set new frequency
            frequency_instance.frequency = frequency_from_gcsn
        except ValueError as e:
            logger.error(f"Failed to set frequency to {frequency_from_gcsn}: {e}")
            return None

        # Convert frequency to ARFCN
        arfcn = frequency_instance.freq_to_arfcn()
        if arfcn is None:
            logger.error(f"Failed to calculate ARFCN for center_freq={center_freq}")
            return None

        return arfcn

    except Exception as e:
        logger.error(
            f"Error in getting absolute frequency for ssb using center_freq={center_freq}: {e}"
        )
        return None

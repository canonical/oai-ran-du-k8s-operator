# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Calculate absoluteFrequencySSB (in ARFCN format)."""

import logging
from typing import Optional, Union

from src.du_parameters.afrcn import freq_to_arfcn
from src.du_parameters.ssb import (
    get_frequency_instance,
)

logger = logging.getLogger(__name__)


def get_absolute_frequency_ssb(center_freq: Union[int, float]) -> Optional[int]:
    """Calculate absolute frequency for ssb using center frequency.

    Args:
        center_freq (float or int): Center frequency in MHz.

    Returns:
        arfcn (int): if successful, else None.
    """
    try:
        try:
            # Get frequency instance
            frequency_instance = get_frequency_instance(center_freq)
        except (ValueError, TypeError):
            logger.error(f"Failed to create a frequency instance for center_freq={center_freq}")
            return None

        try:
            # Calculate GSCN
            gcsn = frequency_instance.freq_to_gscn()
        except ValueError:
            logger.error(f"Failed to calculate GSCN for center_freq={center_freq}")
            return None

        try:
            # Convert GSCN to frequency
            frequency_from_gcsn = frequency_instance.gscn_to_freq(gcsn)
        except ValueError:
            logger.error(f"Failed to calculate frequency using gcsn={gcsn}")
            return None

        try:
            # Convert frequency to ARFCN
            arfcn = freq_to_arfcn(frequency_from_gcsn)
        except (ValueError, TypeError):
            logger.error(f"Failed to calculate ARFCN for center_freq={center_freq}")
            return None

        return arfcn

    except Exception as e:
        logger.error(
            f"Error in getting absolute frequency for ssb using center_freq={center_freq}: {e}"
        )
        return None

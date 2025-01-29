# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""dl_absoluteFrequencyPointA calculations."""

import logging
from typing import Optional, Union

from src.du_parameters.afrcn import freq_to_arfcn

logger = logging.getLogger(__name__)


def get_dl_absolute_freq_point_a(
    center_freq: Union[int, float], bandwidth: Union[int, float]
) -> Optional[int]:
    """Calculate dl_absoluteFrequencyPointA using center frequency and bandwidth.

    Args:
        center_freq (float or int): Center frequency in MHz.
        bandwidth (float or int): (MHz)

    Returns:
        dl_point_a (int): if successful, else None.
    """
    try:
        if not isinstance(center_freq, (int, float)):
            logger.error(f"Frequency {center_freq} is not a numeric value.")
            return None

        if not isinstance(bandwidth, (int, float)):
            logger.error(f"Bandwidth {bandwidth} is not a numeric value.")
            return None

        try:
            # Get lowest frequency and convert to ARFCN
            lowest_freq = center_freq - (bandwidth / 2)
            dl_point_a = freq_to_arfcn(lowest_freq)
        except (ValueError, TypeError):
            logger.error(
                f"Failed to calculate dl_absoluteFrequencyPointA using frequency: "
                f"{center_freq} and bandwidth: {bandwidth}"
            )
            return None

        return dl_point_a

    except Exception as e:
        logger.error(
            f"Error in getting dl_absoluteFrequencyPointA using frequency:"
            f" {center_freq} and bandwidth: {bandwidth}: {e}"
        )
        return None

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Calculate Initial BWP location And Bandwidth.

Uses subcarrier spacing and carrier bandwidth as inputs.
"""

import logging

from frequency import Frequency

logger = logging.getLogger(__name__)


class CalculateBWPLocationBandwidthError(Exception):
    """Exception raised when calculation of BWP location and bandwidth fails."""

    pass


def get_total_prbs_from_scs(subcarrier_spacing: Frequency) -> int:
    """Get the number of Physical Resource Blocks (PRBs) based on Subcarrier Spacing (SCS).

    Args:
        subcarrier_spacing (Frequency): Subcarrier Spacing as Frequency object.
        Valid values: 15, 30, 60, 120.

    Returns:
        int: Number of PRBs for given Subcarrier spacing value.

    Raises:
        ValueError: If the Subcarrier spacing value is not supported.
        TypeError: If the Subcarrier spacing is not a Frequency object.
    """
    scs_to_prbs = {
        Frequency.from_khz(15): 275,
        Frequency.from_khz(30): 137,
        Frequency.from_khz(60): 69,
        Frequency.from_khz(120): 33,
    }
    try:
        return scs_to_prbs[subcarrier_spacing]
    except KeyError:
        supported_subcarrier_spacing = ", ".join(str(freq) for freq in scs_to_prbs)
        logger.error(
            "Subcarrier spacing value: %s is not supported. Supported values: %s",
            subcarrier_spacing,
            supported_subcarrier_spacing,
        )
        raise ValueError(
            f"Subcarrier spacing value {subcarrier_spacing} is not supported."
            f"Supported values: {supported_subcarrier_spacing}"
        )


def calculate_initial_bwp(carrier_bandwidth: int, subcarrier_spacing: Frequency) -> int:
    """Calculate the initial BWP location and bandwidth.

    Uses carrier bandwidth and Subcarrier Spacing.

    Formula:
        initialBWPlocationAndBandwidth (int) = (Total_PRB * (L - 1)) + RBstart
        RBstart (int) = 0 the starting resource block for initial BWP location
        Total_PRB (int) = Total number of Physical Resource Blocks (PRBs) based
         on Subcarrier Spacing (SCS)
        L (int) = Carrier bandwidth

    Args:
        carrier_bandwidth (int): Channel bandwidths of the carrier in terms of Resource Blocks.
                                Indicated as L in the formula.
        subcarrier_spacing (Frequency): Subcarrier Spacing in Frequency object.

    Returns:
        int: The calculated initialBWP location and bandwidth.
    """
    if carrier_bandwidth <= 0:
        logger.error("Carrier bandwidth must be greater than 0.")
        raise ValueError("Carrier bandwidth must be greater than 0.")

    try:
        total_prb = get_total_prbs_from_scs(subcarrier_spacing)
    except (ValueError, TypeError) as err:
        logger.error(
            "Error calculating total PRBs using "
            "carrier_bandwidth: %s and subcarrier spacing: %s: %s",
            carrier_bandwidth,
            subcarrier_spacing,
            str(err),
        )

        raise CalculateBWPLocationBandwidthError(
            f"Error calculating total PRBs using"
            f" {carrier_bandwidth} and {subcarrier_spacing}: {str(err)}"
        ) from err

    rb_start = 0
    initial_bwp = (total_prb * (carrier_bandwidth - 1)) + rb_start
    logger.info(
        "Calculated initial BWP location and bandwidth using"
        " carrier_bandwidth: %s and subcarrier spacing: %s: %s",
        carrier_bandwidth,
        subcarrier_spacing,
        initial_bwp,
    )
    return initial_bwp

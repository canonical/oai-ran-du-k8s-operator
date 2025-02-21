# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Calculate Initial BWP location And Bandwidth.

Uses subcarrier spacing and carrier bandwidth as inputs.
"""

import logging

logger = logging.getLogger(__name__)


class CalculateBWPLocationBandwidthError(Exception):
    """Exception raised when calculation of BWP location and bandwidth fails."""

    pass


def get_initial_bwp(carrier_bandwidth: int) -> int:
    """Get the initial BWP location and bandwidth.

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

    Returns:
        int: The calculated initialBWP location and bandwidth.
    """
    if carrier_bandwidth <= 0:
        logger.error("Carrier bandwidth must be greater than 0.")
        raise ValueError("Carrier bandwidth must be greater than 0.")

    # Maximum bandwidth configurations per SCS for NR frequency bands
    # Reference TS 38.104 Table 5.3.2.-1
    # For 15, 30 and 60 KHz sub carrier spacing, total number of PRBs are 275.
    total_prbs = 275
    rb_start = 0
    initial_bwp = (total_prbs * (carrier_bandwidth - 1)) + rb_start
    logger.info(
        "Calculated initial BWP location and bandwidth using" " carrier_bandwidth: %s: %s",
        carrier_bandwidth,
        initial_bwp,
    )
    return initial_bwp

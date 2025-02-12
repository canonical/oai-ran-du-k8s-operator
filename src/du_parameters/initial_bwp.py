# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Calculate Initial BWP location And Bandwidth for given SCS and carrier bandwidth."""

import logging

from src.du_parameters.frequency import Frequency

logger = logging.getLogger(__name__)


class CalculateBWPLocationBandwidthError(Exception):
    """Exception raised when calculation of BWP location and bandwidth fails."""

    pass


def get_total_prbs_from_scs(scs: Frequency) -> int:
    """Get the number of Physical Resource Blocks (PRBs) based on Subcarrier Spacing (SCS).

    Args:
        scs (Frequency): Subcarrier Spacing as Frequency object.
        Valid values: 15, 30, 60, 120.

    Returns:
        int: Number of PRBs for given SCS value.

    Raises:
        ValueError: If the SCS value is not supported.
        TypeError: If the SCS is not a Frequency object.
    """
    if not isinstance(scs, Frequency):
        raise TypeError(f"SCS must be a Frequency object, not {type(scs)}")

    scs_to_prbs = {
        Frequency.from_khz(15): 275,
        Frequency.from_khz(30): 137,
        Frequency.from_khz(60): 69,
        Frequency.from_khz(120): 33,
    }
    try:
        return scs_to_prbs[scs]
    except KeyError:
        supported_scs = ", ".join(str(freq) for freq in scs_to_prbs.keys())
        logger.error("SCS value: %s is not supported. Supported values: %s", scs, supported_scs)
        raise ValueError(f"SCS value {scs} is not supported. Supported values: {supported_scs}")


def calculate_initial_bwp(carrier_bandwidth: int, scs: Frequency) -> int:
    """Calculate the initial BWP location and bandwidth using carrier bandwidth and SCS.

    Formula:
        initialBWPlocationAndBandwidth (int) = (Total_PRB * (L - 1)) + RBstart
        RBstart (int) = 0 the starting resource block for initial BWP location
        Total_PRB (int) = Total number of Physical Resource Blocks (PRBs) based
         on Subcarrier Spacing (SCS)
        L (int) = Carrier bandwidth

    Args:
        carrier_bandwidth (int): Channel bandwidths of the carrier in terms of Resource Blocks.
                                Indicated as L in the formula.
        scs (Frequency): Subcarrier Spacing in Frequency object.

    Returns:
        int: The calculated initialBWP location and bandwidth.
    """
    if not isinstance(scs, Frequency):
        logger.error("SCS must be a Frequency object, not %s", type(scs))
        raise TypeError(f"SCS must be a Frequency object, not {type(scs)}")
    if not isinstance(carrier_bandwidth, int):
        logger.error("Carrier bandwidth must be an integer, not %s", type(carrier_bandwidth))
        raise TypeError(f"Carrier bandwidth must be an integer, not {type(carrier_bandwidth)}")
    if carrier_bandwidth <= 0:
        logger.error("Carrier bandwidth must be greater than 0.")
        raise ValueError("Carrier bandwidth must be greater than 0.")
    try:
        total_prb = get_total_prbs_from_scs(scs)
    except (ValueError, TypeError) as err:
        logger.error("Error calculating total PRBs: %s", err)
        raise CalculateBWPLocationBandwidthError(f"Error calculating total PRBs: {err}") from err

    rb_start = 0
    initial_bwp = (total_prb * (carrier_bandwidth - 1)) + rb_start
    logger.info("Calculated initial BWP location and bandwidth: %s", initial_bwp)
    return initial_bwp

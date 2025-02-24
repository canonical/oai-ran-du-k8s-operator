# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Calculate Carrier Bandwidth using bandwidth and subcarrier spacing."""

import decimal
import logging
from decimal import Decimal

from .frequency import (
    Frequency,
)
from .guard_band import GuardBandError, get_minimum_guard_band

logger = logging.getLogger(__name__)

CONFIG_CONSTANT_TWO = Decimal("2")
NUMBER_OF_SUBCARRIERS = Decimal("12")


class CarrierBandwidthError(Exception):
    """Exception raised when carrier bandwidth calculation fails."""

    pass


def get_carrier_bandwidth(bandwidth: Frequency, subcarrier_spacing: Frequency) -> int:
    """Calculate channel bandwidths of the carrier.

    Result should be in terms of Resource Blocks (RB) using bandwidth and subcarrier spacing.

    Args:
        bandwidth (Frequency): bandwidth
        subcarrier_spacing (Frequency): subcarrier spacing

    Returns:
        carrier bandwidth (int): The channel bandwidths of the carrier
         in terms of Resource Blocks (RB)

    Raises:
        ValueError: If bandwidth or subcarrier spacing are not greater than 0.
        CarrierBandwidthError: If calculation fails or Guard band calculation fails.
    """
    if subcarrier_spacing <= Frequency(0) or bandwidth <= Frequency(0):
        logger.error("Both bandwidth and subcarrier spacing must be greater than 0.")
        raise ValueError("Both bandwidth and subcarrier spacing must be greater than 0.")

    try:
        guard_band = get_minimum_guard_band(subcarrier_spacing, bandwidth)
    except (TypeError, GuardBandError) as e:
        logger.error(
            "Guard band calculation failed for bandwidth: %s and subcarrier spacing: %s: %s",
            bandwidth,
            subcarrier_spacing,
            str(e),
        )
        raise CarrierBandwidthError(
            "Guard band calculation failed for bandwidth: %s and subcarrier spacing: %s: %s",
            bandwidth,
            subcarrier_spacing,
            str(e),
        )

    try:
        carrier_bandwidth = (
            (bandwidth - CONFIG_CONSTANT_TWO * guard_band) / subcarrier_spacing
        ) / NUMBER_OF_SUBCARRIERS
        carrier_bandwidth_int = int(carrier_bandwidth)
        logger.info(
            "Calculated channel bandwidth for bandwidth=%s and subcarrier spacing=%s: %s",
            bandwidth,
            subcarrier_spacing,
            carrier_bandwidth_int,
        )
        return carrier_bandwidth_int

    except (
        TypeError,
        ValueError,
        decimal.InvalidOperation,
    ) as e:
        logger.error(
            "Error calculating carrier bandwidth for bandwidth=%s and subcarrier spacing=%s: %s",
            bandwidth,
            subcarrier_spacing,
            str(e),
        )
        raise CarrierBandwidthError(
            f"Error calculating carrier bandwidth for bandwidth={bandwidth}"
            f" and subcarrier spacing={subcarrier_spacing}: {e}"
        )

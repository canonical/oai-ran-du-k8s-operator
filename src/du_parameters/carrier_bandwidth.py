# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Calculate Carrier Bandwidth using bandwidth and subcarrier spacing."""

import decimal
import logging
from decimal import Decimal

from src.du_parameters.frequency import (
    Frequency,
)
from src.du_parameters.guard_band import GuardBandError, get_minimum_guard_band

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
        channel bandwidth (int): The channel bandwidths of the carrier
         in terms of Resource Blocks (RB)

    Raises:
        TypeError: If bandwidth or subcarrier_spacing are not of type Frequency.
        ValueError: If bandwidth or subcarrier_spacing are not greater than 0.
        CarrierBandwidthError: If calculation fails
    """
    if not isinstance(bandwidth, Frequency) or not isinstance(subcarrier_spacing, Frequency):
        raise TypeError("Both bandwidth and subcarrier_spacing must be of type Frequency.")

    if subcarrier_spacing <= Frequency(0) or bandwidth <= Frequency(0):
        raise ValueError("Both bandwidth and subcarrier_spacing must be greater than 0.")
    try:
        guard_band = get_minimum_guard_band(subcarrier_spacing, bandwidth)
        carrier_bandwidth = (
            (bandwidth - CONFIG_CONSTANT_TWO * guard_band) / subcarrier_spacing
        ) / NUMBER_OF_SUBCARRIERS
        return int(carrier_bandwidth)
    except (
        TypeError,
        ValueError,
        decimal.InvalidOperation,
        GuardBandError,
    ) as e:
        raise CarrierBandwidthError(
            f"Error calculating carrier bandwidth for bandwidth={bandwidth}"
            f" and subcarrier_spacing={subcarrier_spacing}: {e}"
        )

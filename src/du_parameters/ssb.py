# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Synchronization Signal block calculations for different frequencies."""

import logging
from abc import ABC
from typing import Optional, Union

from src.du_parameters.afrcn import freq_to_arfcn

logger = logging.getLogger(__name__)


class BaseSSB(ABC):
    """Base class for calculations in different frequencies."""

    RANGE = (0, 0)
    BASE_GSCN = 0
    MULTIPLICATION_FACTOR = 0
    BASE_FREQ = 0
    MAX_N = 0
    MIN_N = 0

    def __init__(self, frequency: Union[int, float]):
        """Initialize frequency with validation."""
        if self.__class__ == BaseSSB:
            raise NotImplementedError("BaseFrequency cannot be instantiated directly.")

        if not isinstance(frequency, (int, float)):
            raise TypeError(f"Frequency {frequency} is not a numeric value.")

        if not (self.RANGE[0] <= frequency < self.RANGE[1]):
            raise ValueError(
                f"Frequency {frequency} is out of range for {self.__class__.__name__}."
            )

        self.frequency: Union[int, float] = frequency

    def freq_to_gscn(self) -> int:
        """Calculate GSCN according to frequency.

        Returns:
            gscn: int

        Raises:
            ValueError: If the MULTIPLICATION_FACTOR is 0 or N is out of range.
        """
        if self.MULTIPLICATION_FACTOR == 0:
            raise ValueError(f"{self.__class__.__name__}.MULTIPLICATION_FACTOR cannot be zero.")

        n = (self.frequency - self.BASE_FREQ) / self.MULTIPLICATION_FACTOR  # type: ignore

        if self.MIN_N <= n <= self.MAX_N:
            return int(n + self.BASE_GSCN)

        raise ValueError(f"Value of N: {n} is out of supported range ({self.MIN_N}-{self.MAX_N}).")

    def gscn_to_freq(self, gscn: int) -> float:
        """Calculate frequency according to GSCN value.

        Args:
            gscn: int

        Returns:
            frequency: float(MHz)

        Raises:
            ValueError: If N is out of range.
        """
        n = gscn - self.BASE_GSCN

        if self.MIN_N <= n <= self.MAX_N:
            return n * self.MULTIPLICATION_FACTOR + self.BASE_FREQ

        raise ValueError(f"Value of N: {n} is out of supported range ({self.MIN_N}-{self.MAX_N}).")


class HighFrequencySSB(BaseSSB):
    """Perform GSCN calculations for high level frequencies.

    The value of N must remain within a specified valid range, depending on the frequency.
    """

    RANGE = (24250, 100000)
    MULTIPLICATION_FACTOR = 17.28  # MHz
    BASE_FREQ = 24250.08  # MHz
    MAX_N = 4383
    MIN_N = 0
    BASE_GSCN = 22256


class MidFrequencySSB(BaseSSB):
    """Perform GSCN calculations for mid level frequencies.

    The value of N must remain within a specified valid range, depending on the frequency.
    """

    RANGE = (3000, 24250)
    MULTIPLICATION_FACTOR = 1.44  # MHz
    BASE_FREQ = 3000  # MHz
    MAX_N = 14756
    MIN_N = 0
    BASE_GSCN = 7499


class LowFrequencySSB(BaseSSB):
    """Perform GSCN calculations for low frequencies.

    M is a scaling factor used to adjust how frequencies are divided and mapped in specific ranges
    The default value of M is 3.
    The value of N must remain within a specified valid range, depending on the frequency.
    """

    RANGE = (0, 3000)
    M = 3
    M_MULTIPLICATION_FACTOR = 0.05  # MHz
    MULTIPLICATION_FACTOR = 1.2  # MHz
    MAX_N = 2499
    MIN_N = 1

    def freq_to_gscn(self) -> int:
        """Calculate GSCN according to frequency.

        Returns:
            gscn: int

        Raises:
            ValueError: If the  MULTIPLICATION_FACTOR is 0 or N is out of range.
        """
        if self.MULTIPLICATION_FACTOR == 0:
            raise ValueError(f"{self.__class__.__name__}.MULTIPLICATION_FACTOR cannot be zero.")

        n = (self.frequency - (self.M * self.M_MULTIPLICATION_FACTOR)) / self.MULTIPLICATION_FACTOR  # type: ignore
        if self.MIN_N <= n <= self.MAX_N:
            return int((3 * n) + (self.M - 3) / 2)

        raise ValueError(f"Value of N: {n} is out of supported range ({self.MIN_N}-{self.MAX_N}).")

    def gscn_to_freq(self, gscn: int) -> float:
        """Calculate frequency according to GSCN value.

        Args:
            gscn: int

        Returns:
            frequency: float(MHz)
        """
        n = (gscn - (self.M - 3) / 2) / 3
        return n * self.MULTIPLICATION_FACTOR + self.M * self.M_MULTIPLICATION_FACTOR


def get_frequency_instance(frequency: Union[float, int]) -> BaseSSB:
    """Create the instance according to appropriate frequency range class.

    Args:
        frequency: float or int

    Returns:
        BaseSSB: instance

    Raises:
        ValueError: If frequency is out of supported range
        TypeError: If frequency is not a numeric value
    """
    if not isinstance(frequency, (int, float)):
        raise TypeError(f"Frequency {frequency} is not a numeric value.")

    ranges = [
        ((0, 3000), LowFrequencySSB),
        ((3000, 24250), MidFrequencySSB),
        ((24250, 100000), HighFrequencySSB),
    ]

    for (range_min, range_max), frequency_cls in ranges:
        if range_min <= frequency < range_max:
            return frequency_cls(frequency)

    raise ValueError(f"Frequency {frequency} is out of supported range.")


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

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
"""ARFCN and GSCN calculations for DU configuration."""

from abc import ABC


class BaseFrequency(ABC):
    """Base class for calculations in different frequencies."""

    RANGE = (0, 0)
    BASE_GSCN = 0
    MULTIPLICATION_FACTOR = 0
    BASE_FREQ = 0
    MAX_N = 0
    MIN_N = 0
    FREQ_GRID = 0
    FREQ_OFFSET = 0
    ARFCN_OFFSET = 0

    def __init__(self, frequency: float):
        """Initialize frequency with validation."""
        if self.__class__ == BaseFrequency:
            raise NotImplementedError("BaseFrequency cannot be instantiated directly.")

        if not isinstance(frequency, (int, float)):
            raise TypeError(f"Frequency {frequency} is not a numeric value.")

        if not (self.RANGE[0] <= frequency < self.RANGE[1]):
            raise ValueError(
                f"Frequency {frequency} is out of range for {self.__class__.__name__}."
            )

        self._frequency = None
        self.frequency = frequency

    @property
    def frequency(self):
        """Get frequency."""
        return self._frequency

    @frequency.setter
    def frequency(self, value: float):
        if not (self.RANGE[0] <= value < self.RANGE[1]):
            raise ValueError(f"Frequency {value} is out of range for {self.__class__.__name__}.")
        self._frequency = value

    def freq_to_gscn(self) -> int:
        """Calculate GSCN according to frequency.

        Returns:
            gscn: int

        Raises:
            ValueError: If the  MULTIPLICATION_FACTOR is invalid.
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
        """
        n = gscn - self.BASE_GSCN
        if self.MIN_N <= n <= self.MAX_N:
            return n * self.MULTIPLICATION_FACTOR + self.BASE_FREQ

        raise ValueError(f"Value of N: {n} is out of supported range ({self.MIN_N}-{self.MAX_N}).")

    def freq_to_arfcn(self) -> int:
        """Calculate Absolute Radio Frequency Channel Number (ARFCN).

        Returns:
            arfcn: int

        Raises:
            ValueError: If the FREQ_GRID is invalid.
        """
        if self.FREQ_GRID == 0:
            raise ValueError(f"{self.__class__.__name__}.FREQ_GRID cannot be zero.")

        return int(self.ARFCN_OFFSET + ((self.frequency - self.FREQ_OFFSET) / self.FREQ_GRID))  # type: ignore


class HighFrequency(BaseFrequency):
    """Perform ARFCN, GSCN and frequency calculations for high level frequencies.

    The value of N must remain within a specified valid range, depending on the frequency.
    """

    RANGE = (24250, 100000)
    MULTIPLICATION_FACTOR = 17.28  # MHz
    BASE_FREQ = 24250.08  # MHz
    MAX_N = 4383
    MIN_N = 0
    BASE_GSCN = 22256
    FREQ_GRID = 0.06  # MHz
    FREQ_OFFSET = 24250  # MHz
    ARFCN_OFFSET = 2016667


class MidFrequency(BaseFrequency):
    """Perform ARFCN, GSCN and frequency calculations for mid level frequencies.

    The value of N must remain within a specified valid range, depending on the frequency.
    """

    RANGE = (3000, 24250)
    MULTIPLICATION_FACTOR = 1.44  # MHz
    BASE_FREQ = 3000  # MHz
    MAX_N = 14756
    MIN_N = 0
    BASE_GSCN = 7499
    FREQ_GRID = 0.015  # MHz
    FREQ_OFFSET = 3000  # MHz
    ARFCN_OFFSET = 600_000


class LowFrequency(BaseFrequency):
    """Perform ARFCN, GSCN and frequency calculations for low frequencies.

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
    FREQ_GRID = 0.005  # MHz
    FREQ_OFFSET = 0  # MHz
    ARFCN_OFFSET = 0

    def freq_to_gscn(self) -> int:
        """Calculate GSCN according to frequency.

        Returns:
            gscn: int

        Raises:
            ValueError: If the  MULTIPLICATION_FACTOR is invalid.
        """
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


def get_frequency_instance(frequency: float) -> BaseFrequency:
    """Create the instance according to appropriate frequency range class."""
    ranges = [
        ((0, 3000), LowFrequency),
        ((3000, 24250), MidFrequency),
        ((24250, 100_000), HighFrequency),
    ]
    if frequency is None:
        raise TypeError("Frequency cannot be None.")

    if not isinstance(frequency, (int, float)):
        raise TypeError(f"Frequency {frequency} is not a numeric value.")

    for (range_min, range_max), frequency_cls in ranges:
        if range_min <= frequency < range_max:
            return frequency_cls(frequency)

    raise ValueError(f"Frequency {frequency} is out of supported range.")

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
"""ARFCN and GSCN calculations for DU configuration."""

from typing import Tuple


class DetectFrequencyRange:
    """Detect frequency range for different frequencies and create frequency instances."""

    def __init__(self, frequency: float):
        """Set frequency range for different frequencies.

        Args:
            frequency: float (MHz)
        """
        self.frequency = frequency
        self.low_range: Tuple[float, float] = (0, 3000)
        self.mid_range: Tuple[float, float] = (3000, 24250)
        self.high_range: Tuple[float, float] = (24250, 100_000)

    def get_frequency_instance(self):
        """Get frequency instance based on frequency range."""
        if self.low_range[0] <= self.frequency < self.low_range[1]:
            return LowFrequency(self.frequency)
        if self.mid_range[0] <= self.frequency < self.mid_range[1]:
            return MidFrequency(self.frequency)
        if self.high_range[0] <= self.frequency < self.high_range[1]:
            return HighFrequency(self.frequency)
        raise ValueError(f"Frequency {self.frequency} is out of supported range.")


class FrequencyMeta(type):
    """Metaclass to define shared validation for frequency ranges."""

    def __new__(cls, name, bases, class_dict):
        """Add frequency property with validation."""

        def freq_getter(self):
            return self._frequency

        def freq_setter(self, value):
            if not (self.RANGE[0] <= value < self.RANGE[1]):
                raise ValueError(
                    f"Frequency {value} is out of the valid range for {self.__class__.__name__}."
                )
            self._frequency = value

        class_dict["frequency"] = property(freq_getter, freq_setter)

        return super().__new__(cls, name, bases, class_dict)


class BaseFrequency(metaclass=FrequencyMeta):
    """Base class for calculations in different frequencies."""

    RANGE = (0, 0)

    def __init__(self, frequency: float):
        """Initialize frequency with validation."""
        self._frequency = None
        self.frequency = frequency


class HighFrequency(BaseFrequency):
    """Perform ARFCN, GSCN and frequency calculations for high level frequencies.

    The value of N must remain within a specified valid range, depending on the frequency.
    """

    RANGE = (24250, 100_000)
    MULTUPLICATION_FACTOR = 17.28  # MHz
    BASE_FREQ = 24250.08  # MHz
    MAX_N = 4383
    MIN_N = 0
    BASE_GSCN = 22256
    FREQ_GRID = 0.06  # MHz
    FREQ_OFFSET = 24250  # MHz
    ARFCN_OFFSET = 2016667

    def freq_to_gscn(self) -> int:
        """Calculate GSCN according to frequency.

        Returns:
            gscn: int
        """
        n = (self.frequency - self.BASE_FREQ) / self.MULTUPLICATION_FACTOR
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
        return n * self.MULTUPLICATION_FACTOR + self.BASE_FREQ

    def freq_to_arfcn(self) -> int:
        """Calculate Absolute Radio Frequency Channel Number (ARFCN).

        Returns:
            arfcn: int
        """
        return int(self.ARFCN_OFFSET + ((self.frequency - self.FREQ_OFFSET) / self.FREQ_GRID))


class MidFrequency(BaseFrequency):
    """Perform ARFCN, GSCN and frequency calculations for mid level frequencies.

    The value of N must remain within a specified valid range, depending on the frequency.
    """

    RANGE = (3000, 24250)
    MULTUPLICATION_FACTOR = 1.44  # MHz
    BASE_FREQ = 3000  # MHz
    MAX_N = 14756
    MIN_N = 0
    BASE_GSCN = 7499
    FREQ_GRID = 0.015  # MHz
    FREQ_OFFSET = 3000  # MHz
    ARFCN_OFFSET = 600_000

    def freq_to_gscn(self) -> int:
        """Calculate GSCN according to frequency.

        Returns:
            gscn: int
        """
        n = (self.frequency - self.BASE_FREQ) / self.MULTUPLICATION_FACTOR
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
        return n * self.MULTUPLICATION_FACTOR + self.BASE_FREQ

    def freq_to_arfcn(self) -> int:
        """Calculate Absolute Radio Frequency Channel Number (ARFCN).

        Returns:
            arfcn: int
        """
        return int(self.ARFCN_OFFSET + ((self.frequency - self.FREQ_OFFSET) / self.FREQ_GRID))


class LowFrequency(BaseFrequency):
    """Perform ARFCN, GSCN and frequency calculations for low frequencies.

    M is a scaling factor used to adjust how frequencies are divided and mapped in specific ranges
    The default value of M is 3.
    The value of N must remain within a specified valid range, depending on the frequency.
    """

    RANGE = (0, 3000)
    M = 3
    M_MULTUPLICATION_FACTOR = 0.05  # MHz
    MULTUPLICATION_FACTOR = 1.2  # MHz
    MAX_N = 2499
    MIN_N = 1
    FREQ_GRID = 0.005  # MHz
    FREQ_OFFSET = 0  # MHz
    ARFCN_OFFSET = 0

    def freq_to_gscn(self) -> int:
        """Calculate GSCN according to frequency.

        Returns:
            gscn: int
        """
        n = (self.frequency - (self.M * self.M_MULTUPLICATION_FACTOR)) / self.MULTUPLICATION_FACTOR
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
        return n * self.MULTUPLICATION_FACTOR + self.M * self.M_MULTUPLICATION_FACTOR

    def freq_to_arfcn(self) -> int:
        """Calculate Absolute Radio Frequency Channel Number (ARFCN).

        Returns:
            arfcn: int
        """
        return int(self.ARFCN_OFFSET + ((self.frequency - self.FREQ_OFFSET) / self.FREQ_GRID))

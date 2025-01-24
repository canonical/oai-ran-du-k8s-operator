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


class HighFrequency:
    """Perform ARFCN, GSCN and frequency calculations for high level frequencies.

    The value of N must remain within a specified valid range, depending on the frequency.
    """

    MULTUPLICATION_FACTOR = 17.28  # MHz
    BASE_FREQ = 24250.08  # MHz
    MAX_N = 4383
    MIN_N = 0
    BASE_GSCN = 22256
    FREQ_GRID = 0.06  # MHz
    FREQ_OFFSET = 24250  # MHz
    ARFCN_OFFSET = 2016667

    def __init__(self, frequency: float):
        """Perform operations in high level frequencies.

        Args:
            frequency: float (MHz)
        """
        self._frequency = None
        self.frequency = frequency
        self.high_range: Tuple[float, float] = (24250, 100_000)

    @property
    def frequency(self) -> float:
        """Get frequency attribute."""
        return self._frequency

    @frequency.setter
    def frequency(self, value: float):
        """Set for the frequency attribute with validation."""
        if not (self.high_range[0] <= value < self.high_range[1]):
            raise ValueError(f"Frequency {value} is out of the valid range for MidFrequency.")
        self._frequency = value

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
        if self.high_range[0] <= self.frequency < self.high_range[1]:
            return int(self.ARFCN_OFFSET + ((self.frequency - self.FREQ_OFFSET) / self.FREQ_GRID))

        raise ValueError(
            f"Frequency {self.frequency} is out of valid range for ARFCN calculations."
        )


class MidFrequency:
    """Perform ARFCN, GSCN and frequency calculations for mid level frequencies.

    The value of N must remain within a specified valid range, depending on the frequency.
    """

    MULTUPLICATION_FACTOR = 1.44  # MHz
    BASE_FREQ = 3000  # MHz
    MAX_N = 14756
    MIN_N = 0
    BASE_GSCN = 7499
    FREQ_GRID = 0.015  # MHz
    FREQ_OFFSET = 3000  # MHz
    ARFCN_OFFSET = 600_000

    def __init__(self, frequency: float):
        """Perform operations in mid level frequencies.

        Args:
            frequency: float (MHz)
        """
        self._frequency = None
        self.frequency = frequency
        self.mid_range: Tuple[float, float] = (3000, 24250)

    @property
    def frequency(self) -> float:
        """Get frequency attribute."""
        return self._frequency

    @frequency.setter
    def frequency(self, value: float):
        """Set for the frequency attribute with validation."""
        if not (self.mid_range[0] <= value < self.mid_range[1]):
            raise ValueError(f"Frequency {value} is out of the valid range for MidFrequency.")
        self._frequency = value

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
        if self.mid_range[0] <= self.frequency < self.mid_range[1]:
            return int(self.ARFCN_OFFSET + ((self.frequency - self.FREQ_OFFSET) / self.FREQ_GRID))

        raise ValueError(
            f"Frequency {self.frequency} is out of valid range for ARFCN calculations."
        )


class LowFrequency:
    """Perform ARFCN, GSCN and frequency calculations for low frequencies.

    M is a scaling factor used to adjust how frequencies are divided and mapped in specific ranges
    The default value of M is 3.
    The value of N must remain within a specified valid range, depending on the frequency.
    """

    M = 3
    M_MULTUPLICATION_FACTOR = 0.05  # MHz
    MULTUPLICATION_FACTOR = 1.2  # MHz
    MAX_N = 2499
    MIN_N = 1
    FREQ_GRID = 0.005  # MHz
    FREQ_OFFSET = 0  # MHz
    ARFCN_OFFSET = 0

    def __init__(self, frequency: float):
        """Perform calculations in low frequencies.

        Args:
            frequency: float (MHz)
        """
        self._frequency = None
        self.frequency = frequency
        self.low_range: Tuple[float, float] = (0, 3000)

    @property
    def frequency(self) -> float:
        """Get frequency attribute."""
        return self._frequency

    @frequency.setter
    def frequency(self, value: float):
        """Set for the frequency attribute with validation."""
        if not (self.low_range[0] <= value < self.low_range[1]):
            raise ValueError(f"Frequency {value} is out of the valid range for LowFrequency.")
        self._frequency = value

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
        if self.low_range[0] <= self.frequency < self.low_range[1]:
            return int(self.ARFCN_OFFSET + ((self.frequency - self.FREQ_OFFSET) / self.FREQ_GRID))

        raise ValueError(
            f"Frequency {self.frequency} is out of valid range for ARFCN calculations."
        )

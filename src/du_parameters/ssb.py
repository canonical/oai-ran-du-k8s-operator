# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Calculate Synchronization Signal Block frequency for given 5G RF center frequency."""

import logging
from abc import ABC
from decimal import Decimal, getcontext

from src.du_parameters.afrcn import freq_to_arfcn

logger = logging.getLogger(__name__)

getcontext().prec = 28
KHZ = Decimal("1000")  # Hz
MHZ = Decimal("1000000")  # Hz


class BaseSSB(ABC):
    """Base class for calculations in different frequencies."""

    RANGE = (Decimal("0"), Decimal("0"))
    BASE_GSCN = Decimal("0")
    MULTIPLICATION_FACTOR = Decimal("0")
    BASE_FREQ = Decimal("0")
    MAX_N = Decimal("0")
    MIN_N = Decimal("0")

    def __init__(self, frequency: int | Decimal):
        """Initialize frequency with validation."""
        if self.__class__ == BaseSSB:
            raise NotImplementedError("BaseFrequency cannot be instantiated directly.")

        if not isinstance(frequency, int | Decimal):
            raise TypeError(f"Frequency {frequency} is not a numeric value.")

        if isinstance(frequency, int):
            frequency = Decimal(frequency)

        self.frequency = frequency

        if not (self.RANGE[0] <= frequency < self.RANGE[1]):
            raise ValueError(
                f"Frequency {frequency} is out of range for {self.__class__.__name__}."
            )

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

    def gscn_to_freq(self, gscn: int) -> int:
        """Calculate frequency according to GSCN value.

        Args:
            gscn: int

        Returns:
            frequency: int (Hz)

        Raises:
            ValueError: If N is out of range.
        """
        n = Decimal(gscn) - self.BASE_GSCN

        if self.MIN_N <= n <= self.MAX_N:
            return int(n * self.MULTIPLICATION_FACTOR + self.BASE_FREQ)

        raise ValueError(f"Value of N: {n} is out of supported range ({self.MIN_N}-{self.MAX_N}).")


class HighFrequencySSB(BaseSSB):
    """Perform GSCN calculations for high level frequencies.

    The value of N must remain within a specified valid range, depending on the frequency.
    """

    RANGE = (Decimal("24250") * MHZ, Decimal("100000") * MHZ)  # Hz
    MULTIPLICATION_FACTOR = Decimal("17.28") * MHZ  # Hz
    BASE_FREQ = Decimal("24250.08") * MHZ  # Hz
    MAX_N = Decimal("4383")
    MIN_N = Decimal("0")
    BASE_GSCN = Decimal("22256")


class MidFrequencySSB(BaseSSB):
    """Perform GSCN calculations for mid level frequencies.

    The value of N must remain within a specified valid range, depending on the frequency.
    """

    RANGE = (Decimal("3000") * MHZ, Decimal("24250") * MHZ)  # Hz
    MULTIPLICATION_FACTOR = Decimal("1.44") * MHZ  # Hz
    BASE_FREQ = Decimal("3000") * MHZ  # Hz
    MAX_N = Decimal("14756")
    MIN_N = Decimal("0")
    BASE_GSCN = Decimal("7499")


class LowFrequencySSB(BaseSSB):
    """Perform GSCN calculations for low frequencies.

    M is a scaling factor used to adjust how frequencies are divided and mapped in specific ranges
    The default value of M is 3.
    The value of N must remain within a specified valid range, depending on the frequency.
    """

    RANGE = (Decimal("0"), Decimal("3000") * MHZ)  # Hz
    M = Decimal("3")
    M_MULTIPLICATION_FACTOR = Decimal("50") * KHZ  # Hz
    MULTIPLICATION_FACTOR = Decimal("1200") * KHZ  # Hz
    MAX_N = Decimal("2499")
    MIN_N = Decimal("1")

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
            return int((Decimal("3") * n) + (self.M - Decimal("3")) / Decimal("2"))

        raise ValueError(f"Value of N: {n} is out of supported range ({self.MIN_N}-{self.MAX_N}).")

    def gscn_to_freq(self, gscn: int) -> int:
        """Calculate frequency according to GSCN value.

        Args:
            gscn: int

        Returns:
            frequency: int(Hz)
        """
        n = (Decimal(gscn) - (self.M - Decimal("3")) / Decimal("2")) / Decimal("3")
        return int(n * self.MULTIPLICATION_FACTOR + self.M * self.M_MULTIPLICATION_FACTOR)


def get_frequency_instance(frequency: int) -> BaseSSB:
    """Create the instance according to appropriate frequency range class.

    Args:
        frequency: int (Hz)

    Returns:
        BaseSSB: instance

    Raises:
        ValueError: If frequency is out of supported range
        TypeError: If frequency is not a numeric value
    """
    if not isinstance(frequency, int | float):
        raise TypeError(f"Frequency {frequency} is not a numeric value.")

    frequency = Decimal(frequency)  # type: ignore

    ranges = [
        ((Decimal("0"), Decimal("3000") * MHZ), LowFrequencySSB),
        ((Decimal("3000") * MHZ, Decimal("24250") * MHZ), MidFrequencySSB),
        ((Decimal("24250") * MHZ, Decimal("100000") * MHZ), HighFrequencySSB),
    ]

    for (range_min, range_max), frequency_cls in ranges:
        if range_min <= frequency < range_max:
            return frequency_cls(frequency)

    raise ValueError(f"Frequency {frequency} is out of supported range.")


def get_absolute_frequency_ssb(center_freq: int) -> int | None:
    """Calculate absolute frequency for ssb using center frequency.

    Args:
        center_freq (int): Center frequency in Hz.

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
            absolute_freq_ssb = freq_to_arfcn(frequency_from_gcsn)
        except (ValueError, TypeError):
            logger.error(f"Failed to calculate ARFCN for center_freq={center_freq}")
            return None

        return absolute_freq_ssb

    except Exception as e:
        logger.error(
            f"Error in getting absolute frequency for ssb using center_freq={center_freq}: {e}"
        )
        return None

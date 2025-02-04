# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Define Frequency, GSCN and ARFCN classes by overloading arithmetic operators.

Handle arithmetic operations with different types (Decimal, int, float).
"""

import logging
from dataclasses import dataclass
from decimal import Decimal

logger = logging.getLogger(__name__)


class Frequency(Decimal):
    """Represents a frequency with unit conversion methods and arithmetic capabilities."""

    class Units:
        """Define Units for Frequency class."""

        KHZ = 1000
        MHZ = 1000 * 1000

    @classmethod
    def from_khz(cls, value: int) -> "Frequency":
        """Convert KHz to Frequency."""
        return cls(Decimal(value) * cls.Units.KHZ)

    @classmethod
    def from_mhz(cls, value: float) -> "Frequency":
        """Convert MHz to Frequency."""
        return cls(Decimal(value) * cls.Units.MHZ)

    def __add__(self, other: "Frequency | Decimal | float | int") -> "Frequency":
        """Add Frequency to others."""
        if not isinstance(other, (Frequency, Decimal, int, float)):
            raise TypeError(f"Unsupported type for addition: {type(other)}")
        return Frequency(super().__add__(Decimal(other)))

    def __sub__(self, other: "Frequency | Decimal | float | int") -> "Frequency":
        """Subtract Frequency from others."""
        if not isinstance(other, (Frequency, Decimal, int, float)):
            raise TypeError(f"Unsupported type for subtraction: {type(other)}")
        return Frequency(super().__sub__(Decimal(other)))

    def __mul__(self, other: "Decimal | float | int") -> "Frequency":
        """Multiply Frequency by others."""
        if not isinstance(other, (Decimal, int, float)):
            raise TypeError(f"Unsupported type for multiplication: {type(other)}")
        return Frequency(super().__mul__(Decimal(other)))

    def __truediv__(self, other: "Decimal | float | int") -> "Frequency":
        """Divide Frequency by other."""
        if not isinstance(other, (Decimal, int, float)):
            raise TypeError(f"Unsupported type for division: {type(other)}")
        return Frequency(super().__truediv__(Decimal(other)))

    def __repr__(self) -> str:
        """Return the Frequency as a string for development purposes."""
        return f"Frequency({self.to_eng_string()})"


@dataclass
class FrequencyRange:
    """Frequency ranges including all attributes."""

    name: str
    lower_frequency: Frequency
    upper_frequency: Frequency
    freq_grid: Frequency
    freq_offset: Frequency
    arfcn_offset: Decimal
    multiplication_factor: Frequency
    base_freq: Frequency
    max_n: Decimal
    min_n: Decimal
    base_gscn: Decimal
    m_scaling: Decimal = Decimal("0")  # Specific to low frequency
    m_multiplication_factor: Frequency = Frequency(0)  # Specific to low frequency


LOW_FREQUENCY = FrequencyRange(
    name="LowFrequency",
    lower_frequency=Frequency.from_mhz(0),
    upper_frequency=Frequency.from_mhz(3000),
    freq_grid=Frequency.from_khz(5),
    freq_offset=Frequency.from_mhz(0),
    arfcn_offset=Decimal("0"),
    multiplication_factor=Frequency.from_khz(1200),
    base_freq=Frequency.from_mhz(0),
    max_n=Decimal("2499"),
    min_n=Decimal("1"),
    base_gscn=Decimal("0"),
    m_scaling=Decimal("3"),
    m_multiplication_factor=Frequency.from_khz(50),
)

MID_FREQUENCY = FrequencyRange(
    name="MidFrequency",
    lower_frequency=Frequency.from_mhz(3000),
    upper_frequency=Frequency.from_mhz(24250),
    freq_grid=Frequency.from_khz(15),
    freq_offset=Frequency.from_mhz(3000),
    arfcn_offset=Decimal("600000"),
    multiplication_factor=Frequency.from_mhz(1.44),
    base_freq=Frequency.from_mhz(3000),
    max_n=Decimal("14756"),
    min_n=Decimal("0"),
    base_gscn=Decimal("7499"),
)

HIGH_FREQUENCY = FrequencyRange(
    name="HighFrequency",
    lower_frequency=Frequency.from_mhz(24250),
    upper_frequency=Frequency.from_mhz(100000),
    freq_grid=Frequency.from_khz(60),
    freq_offset=Frequency.from_mhz(24250),
    arfcn_offset=Decimal("2016667"),
    multiplication_factor=Frequency.from_mhz(17.28),
    base_freq=Frequency.from_mhz(24250.08),
    max_n=Decimal("4383"),
    min_n=Decimal("0"),
    base_gscn=Decimal("22256"),
)


FREQUENCY_RANGES = [LOW_FREQUENCY, MID_FREQUENCY, HIGH_FREQUENCY]


def get_config_for_frequency(frequency: Decimal) -> FrequencyRange | None:
    """Return the appropriate frequency range configuration based on the frequency.

    Args:
        frequency (Decimal): Frequency in MHz.

    Returns:
        FrequencyRange | None:
            Frequency range configuration if frequency is within the range, else None.
    """
    freq_instance = Frequency(Decimal(frequency))
    for config in FREQUENCY_RANGES:
        if config.lower_frequency <= freq_instance < config.upper_frequency:
            return config
    return None


class ARFCN:
    """Represents an Absolute Radio Frequency Channel Number (ARFCN) used in 5G.

    Provides arithmetic operations and conversions from frequencies.

    Args:
        channel (Frequency): The input frequency instance.
    """

    def __init__(self, channel: Frequency):
        if not isinstance(channel, Frequency):
            raise TypeError("Channel must be a Frequency instance.")
        self._channel = channel

    def __repr__(self) -> str:
        """Return the ARFCN as a string for development purposes."""
        return f"ARFCN(channel={self._channel})"

    def __str__(self) -> str:
        """Return the ARFCN as a string."""
        return str(self._channel)

    def __add__(self, other: "ARFCN | Frequency | int") -> "ARFCN":
        """Add another ARFCN, frequency, or integer to this ARFCN.

        Args:
            other: The value to add (ARFCN, Frequency, or int).

        Returns:
            ARFCN: A new ARFCN instance with the updated channel.

        Raises:
            TypeError: If the other value is not an ARFCN, Frequency, or int.
        """
        if isinstance(other, ARFCN):
            return ARFCN(self._channel + other._channel)
        if isinstance(other, (Frequency, int)):
            return ARFCN(self._channel + int(other))
        raise TypeError(f"Unsupported type for addition: {type(other).__name__}")

    def __radd__(self, other: "ARFCN | Frequency | int") -> "ARFCN":
        """Add another ARFCN, frequency, or integer to this ARFCN."""
        return self.__add__(other)

    def __eq__(self, other) -> bool:
        """Check if two ARFCN instances are equal."""
        return isinstance(other, ARFCN) and self._channel == other._channel

    @classmethod
    def freq_to_arfcn(cls, frequency: Decimal) -> int:
        """Find the closest ARFCN corresponding to a given frequency.

        Args:
            frequency (Frequency): The input frequency instance.

        Returns:
            ARFCN (int): The closest ARFCN value to the given frequency.

        Raises:
            ValueError: If no configuration is found for the given frequency.
        """
        config = get_config_for_frequency(frequency)
        if config is None:
            raise ValueError(f"No configuration found for frequency {frequency}")
        offset = (frequency - config.freq_offset) / config.freq_grid
        return int(config.arfcn_offset + offset)


class GSCN:
    """Represents a Global Synchronization Channel Number (GSCN) used in 5G.

    Includes conversions to frequencies and validity checks.

    Args:
        channel (int): The input GSCN.
    """

    def __init__(self, channel: int):
        self._channel = channel

    def __repr__(self) -> str:
        """Return the GSCN as a string for development purposes."""
        return f"GSCN(channel={self._channel})"

    def __str__(self) -> str:
        """Return the GSCN as a string."""
        return str(self._channel)

    def __eq__(self, other) -> bool:
        """Check if two GSCN instances are equal."""
        return isinstance(other, GSCN) and self._channel == other._channel

    @classmethod
    def gscn_to_freq(cls, config: FrequencyRange, gscn: int) -> Decimal:
        """Calculate the frequency for a given GSCN using the given frequency range.

        Args:
            config (FrequencyRange): The frequency range to use for calculations.
            gscn (int): The input GSCN number.

        Returns:
            frequency (Frequency): The closest frequency.

        Raises:
            ValueError: If the frequency is outside the valid range for GSCN or n is out of range.
            TypeError: If the GSCN is not an integer.
        """
        if not isinstance(gscn, int):
            raise TypeError("GSCN must be an integer.")
        if config is None:
            raise ValueError("Frequency range is not available for GSCN calculations.")

        if config.name == "LowFrequency":
            # Special calculation for low frequencies with scaling factor (m_scaling)
            n = (
                Decimal(gscn) - (config.m_multiplication_factor - Decimal("3")) / Decimal("2")
            ) / Decimal("3")
            if config.min_n <= n <= config.max_n:
                return (
                    n * config.multiplication_factor
                    + config.m_scaling * config.m_multiplication_factor
                )

        elif config.name in {"MidFrequency", "HighFrequency"}:
            # For high/medium range frequencies
            n = Decimal(gscn) - config.base_gscn
            if config.min_n <= n <= config.max_n:
                return n * config.multiplication_factor + config.base_freq

        raise ValueError("Invalid GSCN or frequency range.")

    @classmethod
    def freq_to_gcsn(cls, frequency: "Frequency") -> int:
        """Calculate the closest GSCN for a given frequency.

        Args:
            frequency (Frequency): The input frequency.

        Returns:
            GSCN (int): The closest GSCN.

        Raises:
            ValueError: If the frequency is outside the valid range for GSCN or n is out of range.
        """
        config = get_config_for_frequency(frequency)
        if not config:
            raise ValueError(
                f"Frequency {frequency} is out of supported range for GSCN calculations."
            )

        n = (frequency - config.base_freq) / config.multiplication_factor
        if config.min_n <= n <= config.max_n:
            if config.name == "LowFrequency":
                return int(
                    (3 * n) + (config.m_multiplication_factor - Decimal("3")) / Decimal("2")
                )
            else:
                # Handle Medium and High frequency range
                return int(n + config.base_gscn)

        raise ValueError(
            f"Value of N: {n} is out of supported range ({config.min_n}-{config.max_n})."
        )

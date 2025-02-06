# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Define Frequency, GSCN and ARFCN classes by overloading arithmetic operators.

Handle arithmetic operations with different types of objects.
"""

import logging
from dataclasses import dataclass
from decimal import Decimal

logger = logging.getLogger(__name__)

CONFIG_CONSTANT_THREE = Decimal("3")
CONFIG_CONSTANT_TWO = Decimal("2")


class GetRangeFromFrequencyError(Exception):
    """Exception raised when frequency is not appropriate for any frequency range."""

    pass


class GetRangeFromGSCNError(Exception):
    """Exception raised when GSCN is not appropriate for any frequency range."""

    pass


class Frequency(Decimal):
    """Represents a frequency with unit conversion methods and arithmetic capabilities."""

    class Units:
        """Define Units for Frequency class."""

        KHZ = 1000
        MHZ = 1000 * 1000

    @classmethod
    def from_khz(cls, value: int | str) -> "Frequency":
        """Convert KHz to Frequency."""
        return cls(Decimal(value) * cls.Units.KHZ)

    @classmethod
    def from_mhz(cls, value: int | str) -> "Frequency":
        """Convert MHz to Frequency."""
        return cls(Decimal(value) * cls.Units.MHZ)

    def __add__(self, other: "Frequency | Decimal | str | int") -> "Frequency":
        """Add Frequency to others.

        Args:
            other (Frequency | Decimal | str | int): The value to add.

        Returns:
            Frequency: The resulting Frequency after the addition.
        """
        if not isinstance(other, (Frequency, Decimal, int, str)):
            raise NotImplementedError(f"Unsupported type for addition: {type(other)}")
        if isinstance(other, Frequency | Decimal | int | str):
            return Frequency(super().__add__(Decimal(other)))

    def __sub__(self, other: "Frequency | Decimal | str | int") -> "Frequency":
        """Subtract Frequency from others.

        Args:
            other (Frequency | Decimal | str | int): The value to subtract.

        Returns:
            Frequency: The resulting Frequency after the subtraction.
        """
        if not isinstance(other, (Frequency, Decimal, int, str)):
            raise NotImplementedError(f"Unsupported type for subtraction: {type(other)}")
        if isinstance(other, Frequency | Decimal | int | str):
            return Frequency(super().__sub__(Decimal(other)))

    def __rsub__(self, other: "Frequency | Decimal | str | int") -> "Frequency":
        """Subtract Frequency from others.

        Args:
            other (Frequency | Decimal | str | int): The value to reversely subtract from.

        Returns:
            Frequency: The resulting Frequency after the subtraction.
        """
        if not isinstance(other, (Frequency, Decimal, int, str)):
            raise NotImplementedError(f"Unsupported type for subtraction: {type(other)}")
        if isinstance(other, Frequency | Decimal | int | str):
            return Frequency(super().__sub__(Decimal(other)))

    def __mul__(self, other: "Decimal | str| int") -> "Frequency":
        """Multiply Frequency by others.

        Args:
            other (Frequency | Decimal | str | int): The value to multiply by.

        Returns:
            Frequency: The resulting Frequency after the multiplication.
        """
        if not isinstance(other, (Decimal, int, str)):
            raise NotImplementedError(f"Unsupported type for multiplication: {type(other)}")
        if isinstance(other, Frequency | Decimal | int | str):
            return Frequency(super().__mul__(Decimal(other)))

    def __truediv__(self, other: "Decimal | str | int") -> "Frequency":
        """Divide Frequency by others.

        Args:
            other (Frequency | Decimal | str | int): The value to divide by.

        Returns:
            Frequency: The resulting Frequency after the division.
        """
        if not isinstance(other, (Decimal, int, str)):
            raise NotImplementedError(f"Unsupported type for division: {type(other)}")
        if other == 0:
            raise ZeroDivisionError("Division by zero is not allowed.")
        if isinstance(other, Frequency | Decimal | int | str):
            return Frequency(super().__truediv__(Decimal(other)))

    def __repr__(self) -> str:
        """Return the Frequency as a string for development purposes."""
        return f"Frequency({self.to_eng_string()})"

    def __str__(self) -> str:
        """Return the Frequency as a string."""
        return self.to_eng_string()


class ARFCN:
    """Represents an Absolute Radio Frequency Channel Number (ARFCN) used in 5G.

    Provides arithmetic operations and conversions from frequencies.

    Args:
        channel (ARFCN | int): The input ARFCN instance.

    Raises:
        TypeError: If the ARFCN is not an integer or ARFCN instance.
        ValueError: If the ARFCN is not within the valid range for ARFCN.,
        NotImplementedError: If the other value is not an ARFCN, int or Decimal.
    """

    def __init__(self, channel: "int | ARFCN | Decimal"):
        if not isinstance(channel, (int, ARFCN | Decimal)):
            raise TypeError("Channel must be an integer or ARFCN instance.")
        if channel < 0 or channel > 3279165:  # type: ignore[operator]
            raise ValueError("ARFCN must be between 0 and 327916.")
        self._channel = channel

    def __repr__(self) -> str:
        """Return the ARFCN as a string for development purposes."""
        return f"ARFCN(channel={self._channel})"

    def __str__(self) -> str:
        """Return the ARFCN as a string."""
        return str(self._channel)

    def __add__(self, other: "ARFCN | int | Decimal") -> "ARFCN":
        """Add another ARFCN or integer to this ARFCN.

        Args:
            other: The value to add (ARFCN or int or Decimal).

        Returns:
            ARFCN: A new ARFCN instance with the updated channel.

        Raises:
            NotImplementedError: If the other value is not an ARFCN or int.
        """
        if isinstance(other, ARFCN):
            return ARFCN(self._channel + other._channel)  # type: ignore[operator]
        if isinstance(other, int | Decimal):
            return ARFCN(self._channel + other)
        raise NotImplementedError(f"Unsupported type for addition: {type(other).__name__}")

    def __eq__(self, other) -> bool:
        """Check if ARFCN instance and other are equal.

        Args:
            other (ARFCN | Decimal | int): The value to add.

        Returns:
            ARFCN: A new ARFCN instance with the updated channel.
        """
        if isinstance(other, int | Decimal):
            return other == self._channel
        if isinstance(other, ARFCN):
            return other._channel == self._channel
        raise NotImplementedError(f"Unsupported type for equality: {type(other).__name__}")

    @classmethod
    def from_frequency(cls, frequency: Frequency) -> "ARFCN":
        """Find the closest ARFCN corresponding to a given frequency.

        Args:
            frequency (Frequency): The input frequency instance.

        Returns:
            ARFCN (ARFCN): The closest ARFCN value to the given frequency.

        Raises:
            ValueError: If no configuration is found for the given frequency
            or frequency is out of range.
        """
        config = get_range_from_frequency(frequency)
        if config is None:
            raise ValueError(f"No configuration found for frequency {frequency}")
        offset = (frequency - config.freq_offset) / config.freq_grid
        result = config.arfcn_offset + round(Decimal(offset))
        return result


class GSCN:
    """Represent a Global Synchronization Channel Number (GSCN) used in 5G.

    Include conversions to frequencies and validity checks.

    Args:
        channel (GSCN): The input GSCN.

    Raises:
        ValueError: If the GSCN is not within the valid range for GSCN or n is out of range.
        NotImplementedError: If the other value is not an GSCN, int or Decimal.
    """

    def __init__(self, channel: "GSCN | int | Decimal"):
        if channel < 0 or channel > 26639:  # type: ignore[operator]
            raise ValueError(f"GSCN must be between 0 and 26639, got {channel} instead.")
        self._channel = channel

    def __repr__(self) -> str:
        """Return the GSCN as a string for development purposes."""
        return f"GSCN(channel={self._channel})"

    def __str__(self) -> str:
        """Return the GSCN as a string."""
        return f"{self._channel}"

    def __eq__(self, other) -> bool:
        """Check if two GSCN instances are equal.

        Args:
            other: The value to add (GSCN or int or Decimal).

        Returns:
            Bool: True if the two GSCN instances are equal, False otherwise.

        Raises:
            NotImplementedError: If the other value is not an GSCN, int or Decimal.
        """
        if isinstance(other, GSCN):
            return self._channel == other._channel
        if isinstance(other, int | Decimal):
            return self._channel == other
        raise NotImplementedError(f"Unsupported type for equality: {type(other).__name__}")

    def __le__(self, other) -> bool:
        """Check if the current GSCN instance is less than or equal to another.

        Args:
            other (GSCN | int | Decimal): The value to compare.

        Returns:
            bool: True if the current GSCN instance is less than or equal to the other,
             False otherwise.

        Raises:
            NotImplementedError: If the other value is not an GSCN, int or Decimal.
        """
        if isinstance(other, GSCN):
            return self._channel <= other._channel  # type: ignore[operator]
        if isinstance(other, int | Decimal):
            return self._channel <= other
        raise NotImplementedError(f"Unsupported type for comparison: {type(other).__name__}")

    def __sub__(self, other) -> "GSCN":
        """Subtract another GSCN or integer or decimal from this GSCN.

        Args:
            other (GSCN | int | Decimal): The value to subtract.

        Returns:
            GSCN: A new GSCN instance with the updated channel.

        Raises:
            NotImplementedError: If the other value is not an GSCN, int or Decimal.
        """
        if isinstance(other, GSCN):
            return self._channel - other._channel  # type: ignore[operator]
        if isinstance(other, int | Decimal):
            return self._channel - other  # type: ignore[operator]
        raise NotImplementedError(f"Unsupported type for subtraction: {type(other).__name__}")

    def __add__(self, other) -> "GSCN":
        """Add another GSCN or integer or Decimal to this GSCN.

        Args:
            other (GSCN | int | Decimal): The value to add.

        Returns:
            GSCN: A new GSCN instance with the updated channel.

        Raises:
            NotImplementedError: If the other value is not an GSCN, int or Decimal.
        """
        if isinstance(other, GSCN):
            return self._channel + other._channel  # type: ignore[operator]
        if isinstance(other, int | Decimal):
            return self._channel + other  # type: ignore[operator]
        raise NotImplementedError(f"Unsupported type for addition: {type(other).__name__}")

    def __truediv__(self, other) -> "GSCN":
        """Divide GSCN to other GSCN, integer or Decimal.

        Args:
            other (GSCN | int | Decimal): The value to divide by.

        Returns:
            GSCN: A new GSCN instance with the updated channel.

        Raises:
            NotImplementedError: If the other value is not an GSCN, int or Decimal.
        """
        if isinstance(other, GSCN):
            if other._channel == 0:
                raise ZeroDivisionError("Division by zero is not allowed.")
            return self._channel / other._channel  # type: ignore[operator]
        if isinstance(other, int | Decimal):
            if other == 0:
                raise ZeroDivisionError("Division by zero is not allowed.")
            return self._channel / other  # type: ignore[operator]
        raise NotImplementedError(f"Unsupported type for division: {type(other).__name__}")

    @staticmethod
    def to_frequency(gscn: "GSCN") -> Frequency:  # type: ignore[operator]
        """Calculate the frequency using input GSCN.

        Returns:
            frequency (Frequency): The closest frequency.

        Raises:
            ValueError: If the GSCN is out of supported range or n is out of range.
        """
        config = get_range_from_gscn(gscn)
        if config.name == "LowFrequency":
            # Special calculation for low frequencies with scaling factor (m_scaling)
            n = (gscn / CONFIG_CONSTANT_THREE)  # type: ignore[operator]
            if is_valid_n(n, config.min_n, config.max_n):
                result = (
                    config.multiplication_factor * n
                    + config.m_multiplication_factor * config.m_scaling
                )
                return result

            raise ValueError(
                f"Value of N: {n} is out of supported range ({config.min_n}-{config.max_n})."
            )

        elif config.name in {"MidFrequency", "HighFrequency"}:
            # For high/medium range frequencies
            n = gscn - config.base_gscn
            if is_valid_n(n, config.min_n, config.max_n):  # type: ignore
                result = config.multiplication_factor * n + config.base_freq  # type: ignore
                return result

            raise ValueError(
                f"Value of N: {n} is out of supported range ({config.min_n}-{config.max_n})."
            )

        raise ValueError(f"Unsupported configuration name: {config.name}")

    @staticmethod
    def from_frequency(frequency: Frequency) -> "GSCN":
        """Calculate the closest GSCN for a given frequency.

        Args:
            frequency (Frequency): The input frequency.

        Returns:
            GSCN (GSCN): The closest GSCN.

        Raises:
            ValueError: If the frequency is out of supported range or n is out of range.
        """
        config = get_range_from_frequency(frequency)
        if config.name == "LowFrequency":
            n = (frequency - (config.m_scaling * config.m_multiplication_factor)) / config.multiplication_factor
            if is_valid_n(n, config.min_n, config.max_n):
                result = (CONFIG_CONSTANT_THREE * n) + (config.m_scaling - CONFIG_CONSTANT_THREE) / CONFIG_CONSTANT_TWO
                return GSCN(round(result))
            else:
                raise ValueError(
                    f"Value of N: {n} is out of supported range ({config.min_n}-{config.max_n})."
                )

        elif config.name in {"MidFrequency", "HighFrequency"}:
            n = (frequency - config.base_freq) / config.multiplication_factor
            if is_valid_n(n, config.min_n, config.max_n):
                # Handle Medium and High frequency range
                result = config.base_gscn + Decimal(n)
                return GSCN(round(result))  # type: ignore[operator]
            else:
                raise ValueError(
                    f"Value of N: {n} is out of supported range ({config.min_n}-{config.max_n})."
                )

        raise ValueError(f"Unsupported configuration name: {config.name}")


@dataclass
class FrequencyRange:
    """Frequency ranges including all attributes."""

    name: str
    lower_frequency: Frequency
    upper_frequency: Frequency
    freq_grid: Frequency
    freq_offset: Frequency
    arfcn_offset: ARFCN
    multiplication_factor: Frequency
    base_freq: Frequency
    max_n: Decimal
    min_n: Decimal
    base_gscn: GSCN
    m_scaling: Decimal = Decimal("0")  # Specific to low frequency
    m_multiplication_factor: Frequency = Frequency(0)  # Specific to low frequency


LOW_FREQUENCY = FrequencyRange(
    name="LowFrequency",
    lower_frequency=Frequency.from_mhz(0),
    upper_frequency=Frequency.from_mhz(3000),
    freq_grid=Frequency.from_khz(5),
    freq_offset=Frequency.from_mhz(0),
    arfcn_offset=ARFCN(0),
    multiplication_factor=Frequency.from_khz(1200),
    base_freq=Frequency.from_mhz(0),
    max_n=Decimal("2499"),
    min_n=Decimal("1"),
    base_gscn=GSCN(0),
    m_scaling=Decimal("3"),
    m_multiplication_factor=Frequency.from_khz(50),
)

MID_FREQUENCY = FrequencyRange(
    name="MidFrequency",
    lower_frequency=Frequency.from_mhz(3000),
    upper_frequency=Frequency.from_mhz(24250),
    freq_grid=Frequency.from_khz(15),
    freq_offset=Frequency.from_mhz(3000),
    arfcn_offset=ARFCN(600000),
    multiplication_factor=Frequency.from_mhz("1.44"),
    base_freq=Frequency.from_mhz(3000),
    max_n=Decimal("14756"),
    min_n=Decimal("0"),
    base_gscn=GSCN(7499),
)

HIGH_FREQUENCY = FrequencyRange(
    name="HighFrequency",
    lower_frequency=Frequency.from_mhz(24250),
    upper_frequency=Frequency.from_mhz(100000),
    freq_grid=Frequency.from_khz(60),
    freq_offset=Frequency.from_mhz(24250),
    arfcn_offset=ARFCN(2016667),
    multiplication_factor=Frequency.from_mhz("17.28"),
    base_freq=Frequency.from_mhz("24250.08"),
    max_n=Decimal("4383"),
    min_n=Decimal("0"),
    base_gscn=GSCN(22256),
)


def get_range_from_frequency(frequency: Frequency) -> FrequencyRange:
    """Return the appropriate frequency range configuration based on the frequency.

    Args:
        frequency: Frequency instance

    Returns:
        FrequencyRange:
            Frequency range configuration if frequency is within the range.

    Raises:
        GetRangeFromFrequencyError: If frequency is not appropriate for any frequency range.
    """
    try:
        ranges = [LOW_FREQUENCY, MID_FREQUENCY, HIGH_FREQUENCY]
        for config in ranges:
            if config.lower_frequency <= frequency < config.upper_frequency:
                return config
        raise ValueError(f"Frequency {frequency} is out of supported range.")

    except Exception as e:
        raise GetRangeFromFrequencyError(
            f"Frequency {frequency} is not supported for any range: {e}."
        )


def get_range_from_gscn(gscn: GSCN) -> FrequencyRange:
    """Return the appropriate frequency range configuration based on the frequency.

    Args:
        gscn: GSCN instance

    Returns:
        FrequencyRange: Frequency range configuration if GSCN is within the range.

    Raises:
        GetRangeFromGSCNError: If GSCN is not appropriate for any frequency range.
    """
    try:
        if GSCN(2) <= gscn <= GSCN(7498):
            return LOW_FREQUENCY
        if GSCN(7499) <= gscn <= GSCN(22255):
            return MID_FREQUENCY
        if GSCN(22256) <= gscn <= GSCN(26639):
            return HIGH_FREQUENCY
        raise ValueError(f"GSCN {gscn} is out of supported range.")

    except Exception as e:
        raise GetRangeFromGSCNError(f"GSCN {gscn} is not supported for any range: {e}.")


def is_valid_n(n: Decimal, min_n: Decimal, max_n: Decimal) -> bool:
    """Check if n is within the valid range."""
    return min_n <= n <= max_n

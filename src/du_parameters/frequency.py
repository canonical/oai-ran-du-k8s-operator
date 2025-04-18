# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Define Frequency, GSCN and ARFCN classes by overloading arithmetic operators.

Handle arithmetic operations with different types of objects.
"""

import logging
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

logger = logging.getLogger(__name__)

CONFIG_CONSTANT_THREE = Decimal("3")
CONFIG_CONSTANT_TWO = Decimal("2")


class GetRangeFromFrequencyError(Exception):
    """Exception raised when frequency is not appropriate for any frequency range."""

    pass


class GetRangeFromGSCNError(Exception):
    """Exception raised when GSCN is not appropriate for any frequency range."""

    pass


class ARFCNError(Exception):
    """Exception raised when a ARFCN to Frequency conversion fails."""

    pass


class GSCNError(Exception):
    """Exception raised when a GSCN to Frequency or Frequency to GSCN conversion fails."""

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

    def __add__(self, other: Any) -> "Frequency":
        """Add Frequency to others.

        Args:
            other (Any): The value to add.

        Returns:
            Frequency: The resulting Frequency after the addition.

        Raises:
            NotImplementedError: If the other value is float or not compatible with Decimal.
            TypeError: If the other value is float.
        """
        if isinstance(other, float):
            raise TypeError("Float values are not supported, please use str instead.")
        try:
            return Frequency(super().__add__(Decimal(other)))
        except (ValueError, TypeError, InvalidOperation) as e:
            raise NotImplementedError(f"Unsupported type for addition: {type(other)}") from e

    def __sub__(self, other: Any) -> "Frequency":
        """Subtract Frequency from others.

        Args:
            other (Any): The value to subtract.

        Returns:
            Frequency: The resulting Frequency after the subtraction.

        Raises:
             NotImplementedError:  If the other value is float or not compatible with Decimal.
             TypeError: If the other value is float.
        """
        if isinstance(other, float):
            raise TypeError("Float values are not supported, please use str instead.")
        try:
            return Frequency(super().__sub__(Decimal(other)))
        except (ValueError, TypeError, InvalidOperation) as e:
            raise NotImplementedError(f"Unsupported type for subtraction: {type(other)}") from e

    def __rsub__(self, other: Any) -> "Frequency":
        """Subtract Frequency from others.

        Args:
            other (Any): The value to reversely subtract from.

        Returns:
            Frequency: The resulting Frequency after the subtraction.

        Raises:
            NotImplementedError: If the other value is float or not compatible with Decimal.
            TypeError: If the other value is float.
        """
        if isinstance(other, float):
            raise TypeError("Float values are not supported, please use str instead.")
        try:
            return Frequency(super().__rsub__(Decimal(other)))
        except (ValueError, TypeError, InvalidOperation) as e:
            raise NotImplementedError(f"Unsupported type for subtraction: {type(other)}") from e

    def __mul__(self, other: Any) -> "Frequency":
        """Multiply Frequency by others.

        Args:
            other (Any): The value to multiply by.

        Returns:
            Frequency: The resulting Frequency after the multiplication.

        Raises:
            NotImplementedError: If the other value is float or not compatible with Decimal.
            TypeError: If the other value is float.
        """
        if isinstance(other, float):
            raise TypeError("Float values are not supported, please use str instead.")
        try:
            return Frequency(super().__mul__(Decimal(other)))
        except (ValueError, TypeError, InvalidOperation) as e:
            raise NotImplementedError(f"Unsupported type for multiplication: {type(other)}") from e

    def __truediv__(self, other: Any) -> "Frequency":
        """Divide Frequency by others.

        Args:
            other (Any): The value to divide by.

        Returns:
            Frequency: The resulting Frequency after the division.

        Raises:
            NotImplementedError:  If the other value is float or not compatible with Decimal.
            TypeError: If the other value is float.
        """
        if isinstance(other, float):
            raise TypeError("Float values are not supported, please use str instead.")
        try:
            return Frequency(super().__truediv__(Decimal(other)))
        except (ValueError, TypeError, InvalidOperation) as e:
            raise NotImplementedError(f"Unsupported type for division: {type(other)}") from e

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
        channel (int): The input ARFCN instance.

    Raises:
        ValueError: If the ARFCN is not within the valid range for ARFCN.
        TypeError: If the other value is not int.
    """

    MIN_VALUE = 0
    MAX_VALUE = 3279165

    def __init__(self, channel: int):
        if not isinstance(channel, int):
            raise TypeError("Channel must be an integer.")
        if channel < self.MIN_VALUE or channel > self.MAX_VALUE:  # type: ignore[operator]
            raise ValueError(
                f"ARFCN must be between {self.MIN_VALUE} "
                f"and {self.MAX_VALUE}, got {channel} instead."
            )
        self._channel = channel

    def __repr__(self) -> str:
        """Return the ARFCN as a string for development purposes."""
        return f"ARFCN(channel={self._channel})"

    def __str__(self) -> str:
        """Return the ARFCN as a string."""
        return str(self._channel)

    def __int__(self) -> int:
        """Return the ARFCN as an integer."""
        return self._channel

    def __mul__(self, other: Any) -> "ARFCN":
        """Multiply ARFCN by other ARFCN or integer.

        Args:
            other (Any): The value to multiply by.

        Returns:
            ARFCN: A new ARFCN instance with the updated channel.

        Raises:
            NotImplementedError: If the other value is not an ARFCN or int or Decimal.
        """
        if isinstance(other, ARFCN):
            return ARFCN(self._channel * other._channel)  # type: ignore[operator]
        if isinstance(other, int | Decimal):
            return ARFCN(round(self._channel * other))  # type: ignore[operator]
        raise NotImplementedError(f"Unsupported type for multiplication: {type(other).__name__}")

    def __add__(self, other: Any) -> "ARFCN":
        """Add another ARFCN or integer to this ARFCN.

        Args:
            other (Any): The value to add.

        Returns:
            ARFCN: A new ARFCN instance with the updated channel.

        Raises:
            NotImplementedError: If the other value is not an ARFCN or int or Decimal.
        """
        if isinstance(other, ARFCN):
            return ARFCN(self._channel + other._channel)  # type: ignore[operator]
        if isinstance(other, int | Decimal):
            return ARFCN(round(self._channel + other))  # type: ignore[operator]
        raise NotImplementedError(f"Unsupported type for addition: {type(other).__name__}")

    def __sub__(self, other: Any) -> "ARFCN":
        """Subtract another ARFCN or integer from this ARFCN.

        Args:
            other (Any): The value to subtract.

        Returns:
            ARFCN: A new ARFCN instance with the updated channel.

        Raises:
            NotImplementedError: If the other value is not an ARFCN or int or Decimal.
        """
        if isinstance(other, ARFCN):
            return ARFCN(self._channel - other._channel)  # type: ignore[operator]
        if isinstance(other, int | Decimal):
            return ARFCN(round(self._channel - other))  # type: ignore[operator]
        raise NotImplementedError(f"Unsupported type for subtraction: {type(other).__name__}")

    def __eq__(self, other: Any) -> bool:
        """Check if ARFCN instance and other are equal.

        Args:
            other (Any): The value to compare with.

        Returns:
            bool: If the ARFCN instance and other are equal, return True, else False.
        """
        if isinstance(other, int | Decimal):
            return other == self._channel
        if isinstance(other, ARFCN):
            return other._channel == self._channel
        return False

    def __le__(self, other: Any) -> bool:
        """Check if ARFCN is lower than or equal to other ARFCN or integer.

        Args:
            other (Any): The value to compare with.

        Returns:
            bool: If the ARFCN instance is lower than or equal to other ARFCN or integer
                  return True, else False.
        """
        if isinstance(other, int | Decimal):
            return self._channel <= other
        if isinstance(other, ARFCN):
            return self._channel <= other._channel
        return False

    def __lt__(self, other: Any) -> bool:
        """Check if ARFCN is lower than other ARFCN or integer.

        Args:
            other (Any): The value to compare with.

        Returns:
            bool: If the ARFCN instance is lower than other ARFCN or integer return True,
                  else False.
        """
        if isinstance(other, int | Decimal):
            return self._channel < other
        if isinstance(other, ARFCN):
            return self._channel < other._channel
        return False

    def __ge__(self, other: Any) -> bool:
        """Check if ARFCN is greater than or equal to other ARFCN or integer.

        Args:
            other (Any): The value to compare with.

        Returns:
            bool: If the ARFCN instance is greater than or equal to other ARFCN or integer
                  return True, else False.
        """
        if isinstance(other, int | Decimal):
            return self._channel >= other
        if isinstance(other, ARFCN):
            return self._channel >= other._channel
        return False

    def __gt__(self, other: Any) -> bool:
        """Check if ARFCN is greater than other ARFCN or integer.

        Args:
            other (Any): The value to compare with.

        Returns:
            bool: If the ARFCN instance is greater than other ARFCN or integer return True,
                  else False.
        """
        if isinstance(other, int | Decimal):
            return self._channel > other
        if isinstance(other, ARFCN):
            return self._channel > other._channel
        return False

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
            TypeError: If frequency is not a Frequency instance.
        """
        if not isinstance(frequency, Frequency):
            logger.error("Expected Frequency but got: %s.", {type(frequency).__name__})
            raise TypeError(f"Expected Frequency, got {type(frequency).__name__}")
        try:
            config = get_range_from_frequency(frequency)
        except GetRangeFromFrequencyError:
            logger.error("No frequency range found for frequency: %s.", frequency)
            raise ValueError(f"No frequency range found for frequency {frequency}")

        offset = (frequency - config.freq_offset) / config.freq_grid
        result = config.arfcn_offset + offset
        logger.debug("Found ARFCN: %s for frequency: %s.", result, frequency)
        return result

    def to_frequency(self) -> Frequency:
        """Calculate the frequency based on ARFCN.

        Returns:
            frequency (Frequency): The closest frequency.
        """
        if config := get_range_from_arfcn(self):
            return config.base_freq + config.freq_grid * int(self - config.arfcn_offset)

        logger.error("Unable to calculate frequency for ARFCN %s", self)
        raise ARFCNError(f"Unable to calculate frequency for ARFCN %s {self}")


class GSCN:
    """Represent a Global Synchronization Channel Number (GSCN) used in 5G.

    Include conversions to frequencies and validity checks.

    Args:
        channel (int): The input GSCN instance.

    Raises:
        ValueError: If the GSCN is not within the valid range for GSCN or n is out of range.
        TypeError: If the channel is not an integer.
    """

    # Fixme: According to the TS 38.101-1, the MIN_VALUE of GSCN is 2.
    #  Changing the value here breaks the GSCN offset (base_gscn) for LOW_FREQUENCY though.
    MIN_VALUE = 0
    MAX_VALUE = 26639

    def __init__(self, channel: int):
        if not isinstance(channel, int):
            raise TypeError("Channel must be an integer.")
        if channel < self.MIN_VALUE or channel > self.MAX_VALUE:  # type: ignore[operator]
            raise ValueError(
                f"GSCN must be between {self.MIN_VALUE} "
                f"and {self.MAX_VALUE}, got {channel} instead."
            )
        self._channel = channel

    def __repr__(self) -> str:
        """Return the GSCN as a string for development purposes."""
        return f"GSCN(channel={self._channel})"

    def __str__(self) -> str:
        """Return the GSCN as a string."""
        return f"{self._channel}"

    def __eq__(self, other: Any) -> bool:
        """Check if two GSCN instances are equal.

        Args:
            other (Any): The value to compare.

        Returns:
            Bool: True if the GSCN instance and other are equal, False otherwise.
        """
        if isinstance(other, GSCN):
            return self._channel == other._channel
        if isinstance(other, int | Decimal):
            return self._channel == other
        return False

    def __le__(self, other: Any) -> bool:
        """Check if the current GSCN instance is less than or equal to others.

        Args:
            other (Any): The value to compare.

        Returns:
            bool: True if the current GSCN instance is less than or equal to the other,
             False otherwise.
        """
        if isinstance(other, GSCN):
            return self._channel <= other._channel
        if isinstance(other, int | Decimal):
            return self._channel <= other
        return False

    def __ge__(self, other: Any) -> bool:
        """Check if the current GSCN instance is greater than or equal to others.

        Args:
            other (Any): The value to compare.

        Returns:
            bool: True if the current GSCN instance is greater than or equal to the other,
             False otherwise.
        """
        if isinstance(other, GSCN):
            return self._channel >= other._channel
        if isinstance(other, int | Decimal):
            return self._channel >= other
        return False

    def __sub__(self, other: Any) -> "GSCN":
        """Subtract another GSCN or integer or decimal from this GSCN.

        Args:
            other (Any): The value to subtract.

        Returns:
            GSCN: A new GSCN instance with the updated channel.

        Raises:
            NotImplementedError: If the other value is not an GSCN, int or Decimal.
        """
        if isinstance(other, GSCN):
            return GSCN(self._channel - other._channel)  # type: ignore[operator]
        if isinstance(other, int | Decimal):
            return GSCN(self._channel - round(other))
        raise NotImplementedError(f"Unsupported type for subtraction: {type(other).__name__}")

    def __add__(self, other: Any) -> "GSCN":
        """Add another GSCN or integer or Decimal to this GSCN.

        Args:
            other (Any): The value to add.

        Returns:
            GSCN: A new GSCN instance with the updated channel.

        Raises:
            NotImplementedError: If the other value is not an GSCN, int or Decimal.
        """
        if isinstance(other, GSCN):
            return GSCN(self._channel + other._channel)  # type: ignore[operator]
        if isinstance(other, int | Decimal):
            return GSCN(self._channel + round(other))
        raise NotImplementedError(f"Unsupported type for addition: {type(other).__name__}")

    def __truediv__(self, other: Any) -> "GSCN":
        """Divide GSCN to other GSCN, integer or Decimal.

        Args:
            other (Any): The value to divide by.

        Returns:
            GSCN: A new GSCN instance with the updated channel.

        Raises:
            NotImplementedError: If the other value is not an GSCN, int or Decimal.
        """
        if isinstance(other, GSCN):
            return GSCN(round(self._channel / other._channel))  # type: ignore[operator]
        if isinstance(other, int | Decimal):
            return GSCN(round(self._channel / other))  # type: ignore[operator]
        raise NotImplementedError(f"Unsupported type for division: {type(other).__name__}")

    def __mod__(self, other: Any) -> int:
        """Calculate modulo between GSCN and other GSCN or integer.

        Args:
            other (Any): The value to divide by.

        Returns:
            int: Remainder of the division

        Raises:
            NotImplementedError: If the other value is not an GSCN or int.
        """
        if isinstance(other, GSCN):
            return self._channel % other._channel
        if isinstance(other, int):
            return self._channel % other
        raise NotImplementedError(f"Unsupported type for modulo: {type(other).__name__}")

    def to_frequency(self) -> Frequency:
        """Calculate the frequency based on GSCN.

        Returns:
            frequency (Frequency): The closest frequency.

        Raises:
            ValueError: If the GSCN is out of supported range or n is out of range.
        """
        try:
            config = get_range_from_gscn(self)
        except GetRangeFromGSCNError:
            logger.error("No frequency range found for GSCN: %s.", self)
            raise ValueError(f"No frequency range found for GSCN {self}")

        if config.name == "LowFrequency":
            # Special calculation for low frequencies with scaling factor (m_scaling)
            n = self / CONFIG_CONSTANT_THREE
            if is_valid_n(n, config.min_n, config.max_n):  # type: ignore[operator]
                result = (
                    n._channel * config.multiplication_factor  # type: ignore[operator]
                    + config.m_multiplication_factor * config.m_scaling
                )
                logger.debug("Found frequency: %s for GSCN: %s.", result, self)
                return Frequency(result)

            logger.error(
                "Value of N: %s is out of supported range: (%s-%s).", n, config.min_n, config.max_n
            )
            raise ValueError(
                f"Value of N: {n} is out of supported range ({config.min_n}-{config.max_n})."
            )

        elif config.name in {"MidFrequency", "HighFrequency"}:
            # For high/medium range frequencies
            n = self - config.base_gscn
            if is_valid_n(n._channel, config.min_n, config.max_n):  # type: ignore[operator]
                result = config.multiplication_factor * n._channel + config.base_freq  # type: ignore[operator]
                logger.debug("Found frequency: %s for GSCN: %s", result, self)
                return Frequency(result)

            logger.error(
                "Value of N: %s is out of supported range: (%s-%s).", n, config.min_n, config.max_n
            )
            raise ValueError(
                f"Value of N: {n} is out of supported range ({config.min_n}-{config.max_n})."
            )

        logger.error("Given frequency range name: %s is not supported.", config.name)
        raise GSCNError(f"Unsupported frequency range name: {config.name}")

    @classmethod
    def from_frequency(cls, frequency: Frequency) -> "GSCN":
        """Calculate the closest GSCN for a given frequency.

        Args:
            frequency (Frequency): The input frequency.

        Returns:
            GSCN (GSCN): The closest GSCN.

        Raises:
            ValueError: If the frequency is out of supported range or n is out of range.
            TypeError: If the input is not a Frequency.
        """
        if not isinstance(frequency, Frequency):
            logger.error("Expected Frequency but got: %s.", type(frequency).__name__)
            raise TypeError(f"Expected Frequency, got {type(frequency).__name__}")
        try:
            config = get_range_from_frequency(frequency)
        except GetRangeFromFrequencyError:
            logger.error("No frequency range found for frequency: %s.", frequency)
            raise ValueError(f"No frequency range found for frequency {frequency}")
        if config.name == "LowFrequency":
            n = (
                frequency - (config.m_scaling * config.m_multiplication_factor)
            ) / config.multiplication_factor
            if is_valid_n(n, config.min_n, config.max_n):
                result = n * CONFIG_CONSTANT_THREE
                logger.debug("Found GSCN: %s for frequency: %s.", result, frequency)
                return GSCN(round(result))

            logger.error(
                "Value of N: %s is out of supported range: (%s-%s).", n, config.min_n, config.max_n
            )
            raise ValueError(
                f"Value of N: {n} is out of supported range ({config.min_n}-{config.max_n})."
            )

        elif config.name in {"MidFrequency", "HighFrequency"}:
            n = (frequency - config.base_freq) / config.multiplication_factor
            if is_valid_n(n, config.min_n, config.max_n):
                # Handle Medium and High frequency range
                result = config.base_gscn + Decimal(n)
                logger.debug("Found GSCN: %s for frequency: %s.", result, frequency)
                return result  # type: ignore[operator]

            logger.error(
                "Value of N: %s is out of supported range: (%s-%s).", n, config.min_n, config.max_n
            )
            raise ValueError(
                f"Value of N: {n} is out of supported range ({config.min_n}-{config.max_n})."
            )

        logger.error("Given frequency range name: %s is not supported.", config.name)
        raise GSCNError(f"Unsupported frequency range name: {config.name}")


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
        TypeError: If frequency argument is not an instance of Frequency.
        GetRangeFromFrequencyError: If frequency is not appropriate for any frequency range.
    """
    if not isinstance(frequency, Frequency):
        logger.error("Expected Frequency but got: %s.", type(frequency).__name__)
        raise TypeError(f"Expected Frequency, got {type(frequency).__name__}")

    ranges = [LOW_FREQUENCY, MID_FREQUENCY, HIGH_FREQUENCY]
    for config in ranges:
        if config.lower_frequency <= frequency < config.upper_frequency:
            logger.debug("Found frequency range configuration: %s.", config.name)
            return config

    logger.error("Frequency: %s is out of supported range.", frequency)
    raise GetRangeFromFrequencyError(f"Frequency {frequency} is out of supported range.")


def get_range_from_arfcn(arfcn: ARFCN) -> Optional[FrequencyRange]:
    """Return the appropriate frequency range configuration based on ARFCN.

    Args:
        arfcn: ARFCN instance

    Returns:
        FrequencyRange: Frequency range configuration if ARFCN is within the range.

    Raises:
        TypeError: If arfcn argument is not an instance of ARFCN.
    """
    if not isinstance(arfcn, ARFCN):
        logger.error("Expected ARFCN but got: %s.", type(arfcn).__name__)
        raise TypeError(f"Expected ARFCN, got {type(arfcn).__name__}")

    if ARFCN(ARFCN.MIN_VALUE) <= arfcn <= ARFCN(599999):
        logger.debug("Found frequency range configuration: LowFrequency.")
        return LOW_FREQUENCY

    if ARFCN(600000) <= arfcn <= ARFCN(2016666):
        logger.debug("Found frequency range configuration: MidFrequency.")
        return MID_FREQUENCY

    if ARFCN(2016667) <= arfcn <= ARFCN(ARFCN.MAX_VALUE):
        logger.debug("Found frequency range configuration: HighFrequency.")
        return HIGH_FREQUENCY


def get_range_from_gscn(gscn: GSCN) -> FrequencyRange:
    """Return the appropriate frequency range configuration based on GCSN.

    Args:
        gscn: GSCN instance

    Returns:
        FrequencyRange: Frequency range configuration if GSCN is within the range.

    Raises:
        TypeError: If gscn argument is not an instance of GSCN.
        GetRangeFromGSCNError: If GSCN is not appropriate for any frequency range.
    """
    if not isinstance(gscn, GSCN):
        logger.error("Expected GSCN but got: %s.", type(gscn).__name__)
        raise TypeError(f"Expected GSCN, got {type(gscn).__name__}")

    if GSCN(2) <= gscn <= GSCN(7498):
        logger.debug("Found frequency range configuration: LowFrequency.")
        return LOW_FREQUENCY

    if GSCN(7499) <= gscn <= GSCN(22255):
        logger.debug("Found frequency range configuration: MidFrequency.")
        return MID_FREQUENCY

    if GSCN(22256) <= gscn <= GSCN(26639):
        logger.debug("Found frequency range configuration: HighFrequency.")
        return HIGH_FREQUENCY

    logger.error("GSCN: %s is out of supported range.", gscn)
    raise GetRangeFromGSCNError(f"GSCN {gscn} is out of supported range.")


def is_valid_n(n: Decimal, min_n: Decimal, max_n: Decimal) -> bool:
    """Check if n is within the valid range."""
    return min_n <= n <= max_n

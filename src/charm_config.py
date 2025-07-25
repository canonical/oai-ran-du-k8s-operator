#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Config of the Charm."""

import dataclasses
import decimal
import logging
from enum import Enum
from ipaddress import ip_network
from typing import Tuple

import ops
from pydantic import (  # pylint: disable=no-name-in-module,import-error
    BaseModel,
    Field,
    StrictStr,
    ValidationError,
    field_validator,
)
from pydantic_core.core_schema import ValidationInfo

from du_parameters.fr1_bands import ALLOWED_CHANNEL_BANDWIDTHS, TDD_FR1_BANDS
from du_parameters.frequency import Frequency

logger = logging.getLogger(__name__)


class CharmConfigInvalidError(Exception):
    """Exception raised when a charm configuration is found to be invalid."""

    def __init__(self, msg: str):
        """Initialize a new instance of the CharmConfigInvalidError exception.

        Args:
            msg (str): Explanation of the error.
        """
        self.msg = msg


class FrequencyBandNotFoundError(Exception):
    """Custom exception raised when the band N number is not found."""

    pass


class CNIType(str, Enum):
    """Class to define available CNI types for CU operator."""

    bridge = "bridge"
    macvlan = "macvlan"


def to_kebab(name: str) -> str:
    """Convert a snake_case string to kebab-case."""
    return name.replace("_", "-")


def _get_tdd_uplink_downlink(band: int) -> Tuple[int, int]:
    """Retrieve uplink and downlink frequency ranges for a given TDD N number (band).

    Args:
        band (int): The N number (such as 34, 38, 77, etc.)

    Returns:
        Tuple[int, int]: A tuple of uplink and downlink frequencies (MHz).

    Raises:
        FrequencyBandNotFoundError: If the band N number is not found in TDD FR1 bands.
    """
    if band not in TDD_FR1_BANDS:
        logger.error("Frequency band N: %s is not found in TDD FR1 bands.", band)
        raise FrequencyBandNotFoundError(
            f"Frequency band N: {band} is not found in TDD FR1 bands."
        )

    return TDD_FR1_BANDS[band]


class DUConfig(BaseModel):  # pylint: disable=too-few-public-methods
    """Represent the OAI RAN DU operator builtin configuration values."""

    class Config:
        """Represent config for Pydantic model."""

        alias_generator = to_kebab

    cni_type: CNIType = CNIType.bridge
    f1_interface_name: StrictStr = Field(default="f1", min_length=1)
    f1_ip_address: str = Field(default="192.168.254.5/24")
    f1_port: int = Field(ge=1, le=65535)
    simulation_mode: bool = False
    use_three_quarter_sampling: bool = False
    bandwidth: int = Field(ge=5, le=100)
    frequency_band: int = Field(ge=34, le=101)
    sub_carrier_spacing: int = Field(ge=15, le=30)
    center_frequency: str = Field(
        description="Center frequency as an integer or a float wrapped as str."
    )
    use_mimo: bool = False

    @field_validator("f1_ip_address", mode="before")
    @classmethod
    def validate_ip_network_address(cls, value: str, info: ValidationInfo) -> str:
        """Validate that IP network address is valid."""
        ip_network(value, strict=False)
        return value

    @field_validator("sub_carrier_spacing", mode="before")
    @classmethod
    def validate_sub_carrier_spacing(cls, sub_carrier_spacing: int, info: ValidationInfo):
        """Validate the sub carrier spacing."""
        if sub_carrier_spacing not in {15, 30}:
            logger.error("Subcarrier spacing must be one of 15 kHz or 30 kHz.")
            raise ValueError("Subcarrier spacing must be one of 15 kHz or 30 kHz.")
        frequency_band = info.data.get("frequency_band")
        bandwidth = info.data.get("bandwidth")
        if frequency_band is None:
            logger.error("Frequency band must be defined before validating sub_carrier_spacing.")
            raise ValueError(
                "Frequency band must be defined before validating sub_carrier_spacing."
            )
        if bandwidth is None:
            logger.error("Bandwidth must be defined before validating sub_carrier_spacing.")
            raise ValueError("Bandwidth must be defined before validating sub_carrier_spacing.")
        try:
            allowed_bandwidths_by_spacing = ALLOWED_CHANNEL_BANDWIDTHS[frequency_band]
        except KeyError:
            logger.error(
                "Invalid frequency_band: %s. " "No subcarrier spacing data available.",
                frequency_band,
            )
            raise ValueError(
                f"Invalid frequency_band: {frequency_band}. "
                f"No subcarrier spacing data available."
            )

        try:
            allowed_bandwidths = allowed_bandwidths_by_spacing[sub_carrier_spacing]
        except KeyError:
            logger.error(
                "Sub_carrier_spacing %s is not allowed for the specified frequency_band %s.",
                sub_carrier_spacing,
                frequency_band,
            )
            raise ValueError(
                f"Sub_carrier_spacing {sub_carrier_spacing} "
                f"is not allowed for the specified frequency_band {frequency_band}."
            )

        if bandwidth not in allowed_bandwidths:
            logger.error(
                "Bandwidth: %s MHz is not allowed for the "
                "frequency_band %s with sub_carrier_spacing %s. Allowed bandwidths: %s",
                bandwidth,
                frequency_band,
                sub_carrier_spacing,
                sorted(allowed_bandwidths),
            )
            raise ValueError(
                f"Bandwidth {bandwidth} MHz is not allowed "
                f"for the frequency_band {frequency_band} with "
                f"sub_carrier_spacing {sub_carrier_spacing}. "
                f"Allowed bandwidths: {sorted(allowed_bandwidths)}"
            )

        return sub_carrier_spacing

    @field_validator("bandwidth", mode="before")
    @classmethod
    def validate_bandwidth(cls, value, info: ValidationInfo):
        """Validate the bandwidth."""
        allowed_values = {5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100}
        if value not in allowed_values:
            logger.error("Bandwidth must be one of %s", allowed_values)
            raise ValueError(f"Bandwidth must be one of {allowed_values}")
        return value

    @field_validator("frequency_band", mode="before")
    @classmethod
    def validate_frequency_band(cls, value, info: ValidationInfo):
        """Validate the frequency band."""
        if value not in TDD_FR1_BANDS:
            logger.error("Bandwidth must be one of the defined values: %s", TDD_FR1_BANDS.keys())
            raise ValueError("Bandwidth must be one of the defined values:", TDD_FR1_BANDS.keys())
        return value

    @field_validator("center_frequency", mode="before")
    @classmethod
    def validate_center_frequency(cls, center_frequency: str, info: ValidationInfo):
        """Validate the center frequency."""
        try:
            if not (
                Frequency.from_mhz(410)
                <= Frequency.from_mhz(center_frequency)
                <= Frequency.from_mhz(7125)
            ):
                logger.error(
                    "Center_frequency %s must be within the usable range"
                    " [410 MHz, 7125 MHz] for the given bandwidth %s MHz.",
                    center_frequency,
                    info.data.get("bandwidth"),
                )
                raise ValueError(
                    f"Center_frequency {center_frequency} must be within the usable range "
                    f"[410 MHz, 7125 MHz] for the given bandwidth "
                    f"{info.data.get('bandwidth')} MHz."
                )
        except decimal.InvalidOperation:
            logger.error("Center_frequency must be an integer or a float.")
            raise ValueError("Center_frequency must be an integer or a float.")

        frequency_band = info.data.get("frequency_band")
        bandwidth = info.data.get("bandwidth")

        if frequency_band is None:
            raise ValueError(
                f"Frequency band must be defined before validating center_frequency: {info}."
            )

        if bandwidth is None:
            raise ValueError("Bandwidth must be defined before validating center_frequency.")

        try:
            band_start, band_end = _get_tdd_uplink_downlink(frequency_band)
        except FrequencyBandNotFoundError:
            logger.error(
                "Invalid frequency_band: %s. No uplink-downlink range found.",
                frequency_band,
            )
            raise ValueError(
                f"Invalid frequency_band: {frequency_band}. No uplink-downlink range found."
            )

        # Find usable range in Hz for center frequency based on bandwidth
        usable_start = Frequency.from_mhz(band_start) + (Frequency.from_mhz(bandwidth) // 2)
        usable_end = Frequency.from_mhz(band_end) - (Frequency.from_mhz(bandwidth) // 2)

        if not (usable_start <= Frequency.from_mhz(center_frequency) <= usable_end):
            logger.error(
                "Center_frequency %s must be within the usable range"
                " [%s Hz, %s Hz] for the given bandwidth %s MHz.",
                center_frequency,
                usable_start,
                usable_end,
                bandwidth,
            )
            raise ValueError(
                f"Center_frequency {center_frequency} must be within the usable range "
                f"[{usable_start} Hz, {usable_end} Hz] for the given bandwidth {bandwidth} MHz."
            )
        return center_frequency


@dataclasses.dataclass
class CharmConfig:
    """Represents the state of the OAI RAN DU operator charm.

    Attributes:
        cni_type: Multus CNI plugin to use for the interfaces.
        f1_interface_name: Name of the network interface used for F1 traffic
        f1_ip_address: IP address used by f1 interface
        f1_port: Number of the port used for F1 traffic
        simulation_mode: Run DU in simulation mode
        use_three_quarter_sampling: Run DU with three-quarter sampling rate
    """

    cni_type: CNIType
    f1_interface_name: StrictStr
    f1_ip_address: str
    f1_port: int
    simulation_mode: bool
    use_three_quarter_sampling: bool
    frequency_band: int
    sub_carrier_spacing: Frequency
    bandwidth: Frequency
    center_frequency: Frequency
    use_mimo: bool

    def __init__(self, *, du_config: DUConfig):
        """Initialize a new instance of the CharmConfig class.

        Args:
            du_config: OAI RAN DU operator configuration.
        """
        self.cni_type = du_config.cni_type
        self.f1_interface_name = du_config.f1_interface_name
        self.f1_ip_address = du_config.f1_ip_address
        self.f1_port = du_config.f1_port
        self.simulation_mode = du_config.simulation_mode
        self.use_three_quarter_sampling = du_config.use_three_quarter_sampling
        self.frequency_band = du_config.frequency_band
        self.sub_carrier_spacing = Frequency.from_khz(du_config.sub_carrier_spacing)
        self.bandwidth = Frequency.from_mhz(du_config.bandwidth)
        self.center_frequency = Frequency.from_mhz(du_config.center_frequency)
        self.use_mimo = du_config.use_mimo

    @classmethod
    def from_charm(
        cls,
        charm: ops.CharmBase,
    ) -> "CharmConfig":
        """Initialize a new instance of the CharmState class from the associated charm."""
        try:
            # ignoring because mypy fails with:
            # "has incompatible type "**dict[str, str]"; expected ...""
            return cls(du_config=DUConfig(**dict(charm.config.items())))  # type: ignore
        except ValidationError as exc:
            error_fields: list = []
            for error in exc.errors():
                if param := error["loc"]:
                    error_fields.extend(param)
                else:
                    value_error_msg: ValueError = error["ctx"]["error"]  # type: ignore
                    error_fields.extend(str(value_error_msg).split())
            error_fields.sort()
            error_field_str = ", ".join(f"'{f}'" for f in error_fields)
            raise CharmConfigInvalidError(
                f"The following configurations are not valid: [{error_field_str}]"
            ) from exc

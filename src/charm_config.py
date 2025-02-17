#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Config of the Charm."""

import dataclasses
import logging
from enum import Enum
from ipaddress import ip_network
from typing import Optional, Tuple

import ops
from pydantic import (  # pylint: disable=no-name-in-module,import-error
    BaseModel,
    Field,
    StrictStr,
    ValidationError,
    field_validator,
)
from src.du_parameters.frequency import Frequency
from pydantic_core.core_schema import ValidationInfo

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

TDD_FR1_BANDS = {
    # band_number: ( frequency range in MHz)
    34: (2010, 2025),
    38: (2570, 2620),
    39: (1880, 1920),
    40: (2300, 2400),
    41: (2496, 2690),
    48: (3550, 3700),
    50: (1432, 1517),
    51: (1427, 1432),
    77: (3300, 4200),
    78: (3300, 3800),
    79: (4400, 5000),
    90: (2496, 2690),
    96: (5925, 7125),
    101: (1900, 1910),
    102: (5925, 6425),
}


ALLOWED_CHANNEL_BANDWIDTHS = {
    # frequency_band: {sub_carrier_spacing (KHz): {allowed_bandwidths (MHz)}}
    34: {
        15: {5, 10, 15},
        30: {10, 15},
        60: {10, 15},
    },
    38: {
        15: {5, 10, 15, 20, 25, 30, 40},
        30: {10, 15, 20, 25, 30, 40},
        60: {10, 15, 20, 25, 30, 40},
    },
    39: {
        15: {5, 10, 15, 20, 25, 30, 40},
        30: {10, 15, 20, 25, 30, 40},
        60: {10, 15, 20, 25, 30, 40},
    },
    40: {
        15: {5, 10, 15, 20, 25, 30, 40, 50},
        30: {10, 15, 20, 25, 30, 40, 50, 60, 80},
        60: {10, 15, 20, 25, 30, 40, 50, 60, 80},
    },
    41: {
        15: {10, 15, 20, 30, 40, 50},
        30: {10, 15, 20, 30, 40, 50, 60, 80, 90, 100},
        60: {10, 15, 20, 30, 40, 50, 60, 80, 90, 100},
    },
    48: {
        15: {5, 10, 15, 20, 40, 50},
        30: {10, 15, 20, 40, 50, 60, 80, 90, 100},
        60: {10, 15, 20, 40, 50, 60, 80, 90, 100},
    },
    50: {
        15: {5, 10, 15, 20, 30, 40, 50},
        30: {10, 15, 20, 30, 40, 50, 60, 80},
        60: {10, 15, 20, 30, 40, 50, 60, 80},
    },
    51: {
        15: {5},
    },
    77: {
        15: {10, 15, 20, 25, 30, 40, 50},
        30: {10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100},
        60: {10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100},
    },
    78: {
        15: {10, 15, 20, 25, 30, 40, 50},
        30: {10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100},
        60: {10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100},
    },
    79: {
        15: {40, 50},
        30: {40, 50, 60, 80, 100},
        60: {40, 50, 60, 80, 100},
    },
    90: {
        15: {10, 15, 20, 30, 40, 50},
        30: {10, 15, 20, 30, 40, 50, 60, 80, 90, 100},
        60: {10, 15, 20, 30, 40, 50, 60, 80, 90, 100},
    },
    96: {
        15: {20, 40},
        30: {20, 40, 60, 80},
    },
    101: {
        15: {5, 10},
        30: {10},
    },
    102: {
        15: {20, 40},
        30: {20, 40, 60, 80, 100},
        60: {20, 40, 60, 80, 100},
    },
}

def get_tdd_uplink_downlink(band: int) -> Tuple[int, int]:
    """Retrieve uplink and downlink frequency ranges for a given TDD N number (band).

    Args:
        band (int): The N number (such as 34, 38, 77, etc.)

    Returns:
        Optional[Tuple[int, int]]: A tuple of uplink and downlink frequencies (MHz).

    Raises:
        FrequencyBandNotFoundError: If the band N number is not found in TDD FR1 bands.
    """
    if band not in TDD_FR1_BANDS:
        logger.error("Frequency band N: %s is not found in TDD FR1 bands.", band)
        raise FrequencyBandNotFoundError(f"Frequency band N: {band} is not found in TDD FR1 bands.")

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
    center_frequency: str = Field(ge="410", le="7125")
    bandwidth: int = Field(ge=5, le=100)
    frequency_band: int = Field(default=77, ge=34, le=102)
    sub_carrier_spacing: int = Field(default=30, ge=15, le=60)

    @field_validator("f1_ip_address", mode="before")
    @classmethod
    def validate_ip_network_address(cls, value: str, info: ValidationInfo) -> str:
        """Validate that IP network address is valid."""
        ip_network(value, strict=False)
        return value

    @field_validator("sub_carrier_spacing")
    @classmethod
    def validate_sub_carrier_spacing(cls, sub_carrier_spacing: int, values):
        """Validate that the subcarrier spacing is valid for the frequency band and channel bandwidth."""
        frequency_band = values.get("frequency_band")
        bandwidth = values.get("bandwidth")

        if bandwidth is None:
            logger.error("Bandwidth must be defined before validating sub_carrier_spacing.")
            raise ValueError(
                "Bandwidth must be defined before validating sub_carrier_spacing."
            )
        try:
            # Retrieve allowed bandwidths for the current frequency band and subcarrier spacing
            allowed_bandwidths_by_spacing = ALLOWED_CHANNEL_BANDWIDTHS[frequency_band]
        except KeyError:
            logger.error("Invalid frequency_band: %s. No subcarrier spacing data available.", frequency_band)
            raise ValueError(f"Invalid frequency_band: {frequency_band}. No subcarrier spacing data available.")

        try:
            allowed_bandwidths = allowed_bandwidths_by_spacing[sub_carrier_spacing]
        except KeyError:
            logger.error("Sub_carrier_spacing %s is not allowed for the specified frequency_band %s.", sub_carrier_spacing, frequency_band)
            raise ValueError(
                f"Sub_carrier_spacing {sub_carrier_spacing} is not allowed for the specified frequency_band {frequency_band}."
            )

        if bandwidth not in allowed_bandwidths:
            logger.error("Bandwidth: %s MHz is not allowed for the frequency_band %s with sub_carrier_spacing %s. Allowed bandwidths: %s",
                         bandwidth, frequency_band, sub_carrier_spacing, sorted(allowed_bandwidths)
                         )
            raise ValueError(
                f"Bandwidth {bandwidth} MHz is not allowed for the frequency_band {frequency_band} with "
                f"sub_carrier_spacing {sub_carrier_spacing}. Allowed bandwidths: {sorted(allowed_bandwidths)}"
            )

        return sub_carrier_spacing


    @field_validator("bandwidth", mode="before")
    @classmethod
    def validate_bandwidth(cls, value):
        allowed_values = {5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100}
        if value not in allowed_values:
            logger.error("Bandwidth must be one of %s", allowed_values)
            raise ValueError(f"Bandwidth must be one of {allowed_values}")
        return value

    @field_validator("frequency_band", mode="before")
    @classmethod
    def validate_frequency_band(cls, value):
        if value not in TDD_FR1_BANDS:
            logger.error("Bandwidth must be one of the defined values: %s", TDD_FR1_BANDS.keys())
            raise ValueError(f"Bandwidth must be one of the defined values:", TDD_FR1_BANDS.keys())
        return value

    @field_validator("center_frequency", mode="before")
    @classmethod
    def validate_center_frequency(cls, center_frequency: str, values):
        """Validate if the center frequency is within the uplink-downlink range after considering bandwidth.
            Args:
                center_frequency (str): The center frequency to validate.
                values (dict): The values of the other fields.
        """
        frequency_band = values.get("frequency_band")
        bandwidth = values.get("bandwidth")

        if bandwidth is None:
            raise ValueError("Bandwidth must be defined before validating center_frequency.")

        try:
            band_start, band_end = get_tdd_uplink_downlink(frequency_band)
        except FrequencyBandNotFoundError:
            logger.error("Invalid frequency_band: %s. No uplink-downlink range found.", frequency_band)
            raise ValueError(f"Invalid frequency_band: {frequency_band}. No uplink-downlink range found.")

        # Find usable range in Hz for center frequency based on bandwidth
        usable_start = Frequency.from_mhz(band_start) + (Frequency.from_mhz(bandwidth) // 2)
        usable_end = Frequency.from_mhz(band_end) - (Frequency.from_mhz(bandwidth) // 2)

        if not (usable_start <= Frequency.from_mhz(center_frequency) <= usable_end):
            logger.error("Center_frequency %s must be within the usable range [%s Hz, %s Hz] for the given bandwidth %s MHz.",
                         center_frequency, usable_start, usable_end, bandwidth)
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

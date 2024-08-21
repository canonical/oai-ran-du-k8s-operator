#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Config of the Charm."""
import dataclasses
import logging
from enum import Enum
from ipaddress import ip_network

import ops
from pydantic import (  # pylint: disable=no-name-in-module,import-error
    BaseModel,
    Field,
    StrictStr,
    ValidationError,
    field_validator,
)
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


class CNIType(str, Enum):
    """Class to define available CNI types for CU operator."""

    bridge = "bridge"
    macvlan = "macvlan"


def to_kebab(name: str) -> str:
    """Convert a snake_case string to kebab-case."""
    return name.replace("_", "-")


class DUConfig(BaseModel):  # pylint: disable=too-few-public-methods
    """Represent the OAI RAN DU operator builtin configuration values."""

    class Config:
        """Represent config for Pydantic model."""

        alias_generator = to_kebab
    cni_type: CNIType = CNIType.bridge
    f1_interface_name: StrictStr = Field(default="f1", min_length=1)
    f1_ip_address: str = Field(default="192.168.251.5/24")
    f1_port: int = Field(ge=1, le=65535)
    mcc: StrictStr = Field(pattern=r"^\d{3}$")
    mnc: StrictStr = Field(pattern=r"^\d{2}$")
    sst: int = Field(ge=1, le=4)
    tac: int = Field(ge=1, le=16777215)
    simulation_mode: bool = False

    @field_validator("f1_ip_address", mode="before")
    @classmethod
    def validate_ip_network_address(cls, value: str, info: ValidationInfo) -> str:
        """Validate that IP network address is valid."""
        ip_network(value, strict=False)
        return value


@dataclasses.dataclass
class CharmConfig:
    """Represents the state of the OAI RAN DU operator charm.

    Attributes:
        cni_type: Multus CNI plugin to use for the interfaces.
        f1_interface_name: Name of the network interface used for F1 traffic
        f1_ip_address: IP address used by f1 interface
        f1_port: Number of the port used for F1 traffic
        mcc: Mobile Country Code
        mnc: Mobile Network code
        sst: Slice Service Type
        tac: Tracking Area Code
        simulation_mode: Run DU in simulation mode
    """
    cni_type: CNIType
    f1_interface_name: StrictStr
    f1_ip_address: str
    f1_port: int
    mcc: StrictStr
    mnc: StrictStr
    sst: int
    tac: int
    simulation_mode: bool

    def __init__(self, *, du_config: DUConfig):
        """Initialize a new instance of the CharmConfig class.

        Args:
            du_config: OAI RAN DU operator configuration.
        """
        self.cni_type = du_config.cni_type
        self.f1_interface_name = du_config.f1_interface_name
        self.f1_ip_address = du_config.f1_ip_address
        self.f1_port = du_config.f1_port
        self.mcc = du_config.mcc
        self.mnc = du_config.mnc
        self.sst = du_config.sst
        self.tac = du_config.tac
        self.simulation_mode = du_config.simulation_mode

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

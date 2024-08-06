#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Config of the Charm."""

import dataclasses
import logging

import ops
from pydantic import (  # pylint: disable=no-name-in-module,import-error
    BaseModel,
    Field,
    StrictStr,
    ValidationError,
)

logger = logging.getLogger(__name__)


class CharmConfigInvalidError(Exception):
    """Exception raised when a charm configuration is found to be invalid."""

    def __init__(self, msg: str):
        """Initialize a new instance of the CharmConfigInvalidError exception.

        Args:
            msg (str): Explanation of the error.
        """
        self.msg = msg


def to_kebab(name: str) -> str:
    """Convert a snake_case string to kebab-case."""
    return name.replace("_", "-")


class DUConfig(BaseModel):  # pylint: disable=too-few-public-methods
    """Represent the OAI RAN DU operator builtin configuration values."""

    class Config:
        """Represent config for Pydantic model."""

        alias_generator = to_kebab

    f1_interface_name: StrictStr = Field(min_length=1)
    f1_port: int = Field(ge=1, le=65535)
    mcc: StrictStr = Field(pattern=r"^\d{3}$")
    mnc: StrictStr = Field(pattern=r"^\d{2}$")
    sst: int = Field(ge=1, le=4)
    tac: int = Field(ge=1, le=16777215)


@dataclasses.dataclass
class CharmConfig:
    """Represents the state of the OAI RAN DU operator charm.

    Attributes:
        f1_interface_name: Name of the network interface used for F1 traffic
        f1_port: Number of the port used for F1 traffic
        mcc: Mobile Country Code
        mnc: Mobile Network code
        sst: Slice Service Type
        tac: Tracking Area Code
    """

    f1_interface_name: StrictStr
    f1_port: int
    mcc: StrictStr
    mnc: StrictStr
    sst: int
    tac: int

    def __init__(self, *, du_config: DUConfig):
        """Initialize a new instance of the CharmConfig class.

        Args:
            du_config: OAI RAN DU operator configuration.
        """
        self.f1_interface_name = du_config.f1_interface_name
        self.f1_port = du_config.f1_port
        self.mcc = du_config.mcc
        self.mnc = du_config.mnc
        self.sst = du_config.sst
        self.tac = du_config.tac

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

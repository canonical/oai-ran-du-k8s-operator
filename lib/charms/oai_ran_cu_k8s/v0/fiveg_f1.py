# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.


"""Library for the `fiveg_f1` relation.

This library contains the Requires and Provides classes for handling the `fiveg_f1` interface.

The purpose of this library is to relate two charms claiming to be able to communicate
over the F1 interface. In the Telco world this will typically be charms implementing
the CU (Central Unit) and the DU (Distributed Unit).

## Getting Started
From a charm directory, fetch the library using `charmcraft`:

```shell
charmcraft fetch-lib charms.oai_ran_cu_k8s.v0.fiveg_f1
```

Add the following libraries to the charm's `requirements.txt` file:
- pydantic
- pytest-interface-tester

### Provider charm
The provider charm is the one providing the information about the F1 interface.
Typically, this will be the CU charm.

Example:
```python

from ops import main
from ops.charm import CharmBase, RelationChangedEvent, RelationJoinedEvent

from charms.oai_ran_cu_k8s.v0.fiveg_f1 import F1Provides, PLMNConfig


class DummyFivegF1ProviderCharm(CharmBase):

    IP_ADDRESS = "192.168.70.132"
    PORT = 2153
    TAC = 1
    PLMNS = [PLMNConfig(mcc="123", mnc="12", sst=1, sd=1)]

    def __init__(self, *args):
        super().__init__(*args)
        self.f1_provider = F1Provides(self, "fiveg_f1")
        self.framework.observe(
            self.on.fiveg_f1_relation_joined, self._on_fiveg_f1_relation_joined
        )
        self.framework.observe(
            self.on.fiveg_f1_relation_changed, self._on_fiveg_f1_relation_changed
        )

    def _on_fiveg_f1_relation_joined(self, event: RelationJoinedEvent):
        if self.unit.is_leader():
            self.f1_provider.set_f1_information(
                ip_address=self.IP_ADDRESS,
                port=self.PORT,
                tac=self.TAC,
                plmns=self.PLMNS,
            )

    def _on_fiveg_f1_relation_changed(self, event: RelationChangedEvent):
        requirer_f1_port = self.f1_provider.requirer_f1_port
        if requirer_f1_port:
            <do something with port>


if __name__ == "__main__":
    main(DummyFivegF1ProviderCharm)
```

### Requirer charm
The requirer charm is the one requiring the F1 information.
Typically, this will be the DU charm.

Example:
```python

from ops import main
from ops.charm import CharmBase, RelationChangedEvent, RelationJoinedEvent

from charms.oai_ran_cu_k8s.v0.fiveg_f1 import F1Requires


class DummyFivegF1Requires(CharmBase):

    PORT = 2153

    def __init__(self, *args):
        super().__init__(*args)
        self.f1_requirer = F1Requires(self, "fiveg_f1")
        self.framework.observe(
            self.on.fiveg_f1_relation_joined, self._on_fiveg_f1_relation_joined
        )
        self.framework.observe(
            self.on.fiveg_f1_relation_changed, self._on_fiveg_f1_relation_changed
        )

    def _on_fiveg_f1_relation_joined(self, event: RelationJoinedEvent):
        if self.unit.is_leader():
            self.f1_requirer.set_f1_information(port=self.PORT)

    def _on_fiveg_f1_relation_changed(self, event: RelationChangedEvent):
        provider_f1_ip_address = self.f1_requirer.f1_ip_address
        provider_f1_port = self.f1_requirer.f1_port
        provider_f1_tac = self.f1_requirer.tac
        provider_f1_plmn = self.f1_requirer.plmn
        <do something with the IP address, port, TAC and PLMNs>


if __name__ == "__main__":
    main(DummyFivegF1Requires)
```

"""

import json
import logging
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from typing import Any, Dict, Optional

from interface_tester.schema_base import DataBagSchema
from ops.charm import CharmBase
from ops.framework import Object
from ops.model import Relation
from pydantic import BaseModel, Field, IPvAnyAddress, ValidationError, conlist

# The unique Charmhub library identifier, never change it
LIBID = "544f1e90a3bd49c68d523c506e383579"

# Increment this major API version when introducing breaking changes
LIBAPI = 0

# Increment this PATCH version before using `charmcraft publish-lib` or reset
# to 0 if you are raising the major API version
LIBPATCH = 3

logger = logging.getLogger(__name__)

"""Schemas definition for the provider and requirer sides of the `fiveg_f1` interface.
It exposes two interfaces.schema_base.DataBagSchema subclasses called:
- ProviderSchema
- RequirerSchema
Examples:
    ProviderSchema:
        unit: <empty>
        app: {
            "f1_ip_address": "192.168.70.132"
            "f1_port": 2153,
            "tac": 1,
            "plmns": [
                {
                    "mcc": "001",
                    "mnc": "01",
                    "sst": 1,
                    "sd": 1,
                }
            ],
        }
    RequirerSchema:
        unit: <empty>
        app:  {
            "f1_port": 2153
        }
"""


@dataclass
class PLMNConfig(BaseModel):
    """Dataclass representing the configuration for a PLMN."""

    def __init__(self, mcc: str, mnc: str, sst: int, sd: Optional[int] = None) -> None:
        super().__init__(mcc=mcc, mnc=mnc, sst=sst, sd=sd)

    mcc: str = Field(
        description="Mobile Country Code",
        examples=["001", "208", "302"],
        pattern=r"^[0-9][0-9][0-9]$",
    )
    mnc: str = Field(
        description="Mobile Network Code",
        examples=["01", "001", "999"],
        pattern=r"^[0-9][0-9][0-9]?$",
    )
    sst: int = Field(
        description="Slice/Service Type",
        examples=[1, 2, 3, 4],
        ge=0,
        le=255,
    )
    sd: Optional[int] = Field(
        description="Slice Differentiator",
        default=None,
        examples=[1],
        ge=0,
        le=16777215,
    )

    def asdict(self):
        """Convert the dataclass into a dictionary."""
        return {"mcc": self.mcc, "mnc": self.mnc, "sst": self.sst, "sd": self.sd}


class ProviderAppData(BaseModel):
    """Provider app data for fiveg_f1."""

    f1_ip_address: IPvAnyAddress = Field(
        description="IPv4 address of the network interface used for F1 traffic.",
        examples=["192.168.70.132"],
    )
    f1_port: int = Field(
        description="Number of the port used for F1 traffic.",
        examples=[2153],
    )
    tac: int = Field(
        description="Tracking Area Code",
        strict=True,
        examples=[1],
        ge=1,
        le=16777215,
    )
    plmns: conlist(PLMNConfig, min_length=1)  # type: ignore[reportInvalidTypeForm]


class ProviderSchema(DataBagSchema):
    """Provider schema for fiveg_f1."""

    app_data: ProviderAppData


class RequirerAppData(BaseModel):
    """Requirer app data for fiveg_f1."""

    f1_port: int = Field(
        description="Number of the port used for F1 traffic.",
        examples=[2153],
    )


class RequirerSchema(DataBagSchema):
    """Requirer schema for fiveg_f1."""

    app_data: RequirerAppData


def provider_data_is_valid(data: dict) -> bool:
    """Return whether the provider data is valid.

    Args:
        data (dict): Data to be validated.

    Returns:
        bool: True if data is valid, False otherwise.
    """
    try:
        ProviderSchema(app_data=ProviderAppData(**data))
        return True
    except ValidationError as e:
        logger.error("Invalid data: %s", e)
        return False


def requirer_data_is_valid(data: dict) -> bool:
    """Return whether the requirer data is valid.

    Args:
        data (dict): Data to be validated.

    Returns:
        bool: True if data is valid, False otherwise.
    """
    try:
        RequirerSchema(app_data=RequirerAppData(**data))
        return True
    except ValidationError as e:
        logger.error("Invalid data: %s", e)
        return False


class FivegF1Error(Exception):
    """Custom error class for the `fiveg_f1` library."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class F1Provides(Object):
    """Class to be instantiated by the charm providing relation using the `fiveg_f1` interface."""

    def __init__(self, charm: CharmBase, relation_name: str):
        """Init."""
        super().__init__(charm, relation_name)
        self.relation_name = relation_name
        self.charm = charm

    def set_f1_information(
        self, ip_address: str, port: int, tac: int, plmns: list[PLMNConfig]
    ) -> None:
        """Push the information about the F1 interface in the application relation data.

        Args:
            ip_address (str): IPv4 address of the network interface used for F1 traffic.
            port (int): Number of the port used for F1 traffic.
            tac (int): Tracking Area Code.
            plmns (list[PLMNConfig]): Configured PLMNs.
        """
        if not self.charm.unit.is_leader():
            raise FivegF1Error("Unit must be leader to set application relation data.")
        relations = self.model.relations[self.relation_name]
        if not relations:
            raise FivegF1Error(f"Relation {self.relation_name} not created yet.")
        if not provider_data_is_valid(
            {
                "f1_ip_address": ip_address,
                "f1_port": port,
                "tac": tac,
                "plmns": plmns,
            }
        ):
            raise FivegF1Error("Invalid relation data")
        for relation in relations:
            relation.data[self.charm.app].update(
                {
                    "f1_ip_address": ip_address,
                    "f1_port": str(port),
                    "tac": str(tac),
                    "plmns": json.dumps([plmn.asdict() for plmn in plmns]),
                }
            )

    @property
    def requirer_f1_port(self) -> Optional[int]:
        """Return the number of the port used for F1 traffic.

        Returns:
            Optional[int]: Port number.
        """
        if remote_app_relation_data := self._get_remote_app_relation_data():
            return remote_app_relation_data.f1_port
        return None

    def _get_remote_app_relation_data(
        self, relation: Optional[Relation] = None
    ) -> Optional[RequirerAppData]:
        """Get relation data for the remote application.

        Args:
            relation: Juju relation object (optional).

        Returns:
            RequirerAppData: Relation data for the remote application if valid, None otherwise.
        """
        relation = relation or self.model.get_relation(self.relation_name)
        if not relation:
            logger.error("No relation: %s", self.relation_name)
            return None
        if not relation.app:
            logger.warning("No remote application in relation: %s", self.relation_name)
            return None
        remote_app_relation_data: Dict[str, Any] = dict(relation.data[relation.app])
        try:
            requirer_app_data = RequirerAppData(**remote_app_relation_data)
        except ValidationError:
            logger.error("Invalid relation data: %s", remote_app_relation_data)
            return None
        return requirer_app_data


class F1Requires(Object):
    """Class to be instantiated by the charm requiring relation using the `fiveg_f1` interface."""

    def __init__(self, charm: CharmBase, relation_name: str):
        """Init."""
        super().__init__(charm, relation_name)
        self.charm = charm
        self.relation_name = relation_name

    def set_f1_information(self, port: int) -> None:
        """Push the information about the F1 interface in the application relation data.

        Args:
            port (int): Number of the port used for F1 traffic.
        """
        if not self.charm.unit.is_leader():
            raise FivegF1Error("Unit must be leader to set application relation data.")
        relations = self.model.relations[self.relation_name]
        if not relations:
            raise FivegF1Error(f"Relation {self.relation_name} not created yet.")
        if not requirer_data_is_valid({"f1_port": port}):
            raise FivegF1Error("Invalid relation data")
        for relation in relations:
            relation.data[self.charm.app].update({"f1_port": str(port)})

    def get_provider_f1_information(
        self, relation: Optional[Relation] = None
    ) -> Optional[ProviderAppData]:
        """Get relation data for the remote application.

        Args:
            relation: Juju relation object (optional).

        Returns:
            ProviderAppData: Relation data for the remote application if valid, None otherwise.
        """
        relation = relation or self.model.get_relation(self.relation_name)
        if not relation:
            logger.error("No relation: %s", self.relation_name)
            return None
        if not relation.app:
            logger.warning("No remote application in relation: %s", self.relation_name)
            return None
        remote_app_relation_data: Dict[str, Any] = dict(relation.data[relation.app])
        remote_plmns = remote_app_relation_data.get("plmns", "")
        try:
            remote_app_relation_data["tac"] = int(remote_app_relation_data.get("tac", ""))
            remote_app_relation_data["plmns"] = [
                PLMNConfig(**data) for data in json.loads(remote_plmns)
            ]
        except (JSONDecodeError, ValidationError, ValueError):
            logger.error("Invalid relation data: %s", remote_app_relation_data)
            return None
        try:
            provider_app_data = ProviderAppData(**remote_app_relation_data)
        except ValidationError:
            logger.error("Invalid relation data: %s", remote_app_relation_data)
            return None
        return provider_app_data

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

from ops.charm import CharmBase, RelationJoinedEvent
from ops.main import main

from charms.oai_ran_cu_k8s.v0.fiveg_f1 import F1Provides


class DummyFivegF1ProviderCharm(CharmBase):

    IP_ADDRESS = "192.168.70.132"
    PORT = 2153

    def __init__(self, *args):
        super().__init__(*args)
        self.f1_provider = F1Provides(self, "fiveg_f1")
        self.framework.observe(
            self.on.fiveg_f1_relation_joined, self._on_fiveg_f1_relation_joined
        )

    def _on_fiveg_f1_relation_joined(self, event: RelationJoinedEvent):
        if self.unit.is_leader():
            self.f1_provider.set_f1_information(
                ip_address=self.IP_ADDRESS,
                port=self.PORT,
            )


if __name__ == "__main__":
    main(DummyFivegF1ProviderCharm)
```

### Requirer charm
The requirer charm is the one requiring the F1 information.
Typically, this will be the DU charm.

Example:
```python

from ops.charm import CharmBase
from ops.main import main

from charms.oai_ran_cu_k8s.v0.fiveg_f1 import FivegF1ProviderAvailableEvent, F1Requires

logger = logging.getLogger(__name__)


class DummyFivegF1Requires(CharmBase):

    PORT = 2153

    def __init__(self, *args):
        super().__init__(*args)
        self.f1_requirer = F1Requires(self, "fiveg_f1")
        self.framework.observe(
            self.on.fiveg_f1_relation_joined, self._on_fiveg_f1_relation_joined
        )
        self.framework.observe(
            self.f1_requirer.on.fiveg_f1_provider_available, self._on_f1_information_available
        )

    def _on_fiveg_f1_relation_joined(self, event: RelationJoinedEvent):
        if self.unit.is_leader():
            self.f1_requirer.set_f1_information(port=self.PORT)

    def _on_f1_information_available(self, event: FivegF1ProviderAvailableEvent):
        provider_f1_ip_address = event.f1_ip_address
        provider_f1_port = event.f1_port
        <do something with the IP and port>


if __name__ == "__main__":
    main(DummyFivegF1Requires)
```

"""

import logging
from typing import Dict, Optional

from interface_tester.schema_base import DataBagSchema  # type: ignore[import]
from ops.charm import CharmBase, CharmEvents, RelationChangedEvent, RelationJoinedEvent
from ops.framework import EventBase, EventSource, Handle, Object
from ops.model import Relation
from pydantic import BaseModel, Field, IPvAnyAddress, ValidationError

# The unique Charmhub library identifier, never change it
LIBID = "544f1e90a3bd49c68d523c506e383579"

# Increment this major API version when introducing breaking changes
LIBAPI = 0

# Increment this PATCH version before using `charmcraft publish-lib` or reset
# to 0 if you are raising the major API version
LIBPATCH = 1

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
            "f1_port": 2153
        }
    RequirerSchema:
        unit: <empty>
        app:  {
            "f1_port": 2153
        }
"""


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


class ProviderSchema(DataBagSchema):
    """Provider schema for fiveg_f1."""

    app: ProviderAppData


class RequirerAppData(BaseModel):
    """Requirer app data for fiveg_f1."""

    f1_port: int = Field(
        description="Number of the port used for F1 traffic.",
        examples=[2153],
    )


class RequirerSchema(DataBagSchema):
    """Requirer schema for fiveg_f1."""

    app: RequirerAppData


def provider_data_is_valid(data: dict) -> bool:
    """Return whether the provider data is valid.

    Args:
        data (dict): Data to be validated.

    Returns:
        bool: True if data is valid, False otherwise.
    """
    try:
        ProviderSchema(app=data)
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
        RequirerSchema(app=data)
        return True
    except ValidationError as e:
        logger.error("Invalid data: %s", e)
        return False


class FivegF1ProviderAvailableEvent(EventBase):
    """Charm event emitted when the F1 provider info is available.

    The event carries the F1 provider's IP address and port.
    """

    def __init__(self, handle: Handle, f1_ip_address: str, f1_port: int):
        """Init."""
        super().__init__(handle)
        self.f1_ip_address = f1_ip_address
        self.f1_port = f1_port

    def snapshot(self) -> dict:
        """Return snapshot."""
        return {
            "f1_ip_address": self.f1_ip_address,
            "f1_port": self.f1_port,
        }

    def restore(self, snapshot: dict) -> None:
        """Restores snapshot."""
        self.f1_ip_address = snapshot["f1_ip_address"]
        self.f1_port = snapshot["f1_port"]


class FivegF1RequestEvent(EventBase):
    """Charm event emitted when the F1 requirer joins."""

    def __init__(self, handle: Handle, relation_id: int):
        """Set relation id.

        Args:
            handle (Handle): Juju framework handle.
            relation_id : ID of the relation.
        """
        super().__init__(handle)
        self.relation_id = relation_id

    def snapshot(self) -> dict:
        """Return event data.

        Returns:
            (dict): contains the relation ID.
        """
        return {
            "relation_id": self.relation_id,
        }

    def restore(self, snapshot: dict) -> None:
        """Restore event data.

        Args:
            snapshot (dict): contains the relation ID.
        """
        self.relation_id = snapshot["relation_id"]


class FivegF1RequirerAvailableEvent(EventBase):
    """Charm event emitted when the F1 requirer info is available.

    The event carries the F1 requirer's  port.
    """

    def __init__(self, handle: Handle, f1_port: int):
        """Init."""
        super().__init__(handle)
        self.f1_port = f1_port

    def snapshot(self) -> dict:
        """Return snapshot."""
        return {"f1_port": self.f1_port}

    def restore(self, snapshot: dict) -> None:
        """Restores snapshot."""
        self.f1_port = snapshot["f1_port"]


class FivegF1ProviderCharmEvents(CharmEvents):
    """List of events that the F1 provider charm can leverage."""

    fiveg_f1_request = EventSource(FivegF1RequestEvent)
    fiveg_f1_requirer_available = EventSource(FivegF1RequirerAvailableEvent)


class FivegF1RequirerCharmEvents(CharmEvents):
    """List of events that the F1 requirer charm can leverage."""

    fiveg_f1_provider_available = EventSource(FivegF1ProviderAvailableEvent)


class FivegF1Error(Exception):
    """Custom error class for the `fiveg_f1` library."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class F1Provides(Object):
    """Class to be instantiated by the charm providing relation using the `fiveg_f1` interface."""

    on = FivegF1ProviderCharmEvents()

    def __init__(self, charm: CharmBase, relation_name: str):
        """Init."""
        super().__init__(charm, relation_name)
        self.relation_name = relation_name
        self.charm = charm
        self.framework.observe(charm.on[relation_name].relation_joined, self._on_relation_joined)
        self.framework.observe(charm.on[relation_name].relation_changed, self._on_relation_changed)

    def _on_relation_joined(self, event: RelationJoinedEvent) -> None:
        """Handle relation joined event.

        Args:
            event (RelationJoinedEvent): Juju event.
        """
        self.on.fiveg_f1_request.emit(relation_id=event.relation.id)

    def _on_relation_changed(self, event: RelationChangedEvent) -> None:
        """Handle relation changed event.

        Args:
            event (RelationChangedEvent): Juju event.
        """
        if remote_app_relation_data := self._get_remote_app_relation_data(event.relation):
            self.on.fiveg_f1_requirer_available.emit(f1_port=remote_app_relation_data["f1_port"])

    def set_f1_information(self, ip_address: str, port: int) -> None:
        """Push the information about the F1 interface in the application relation data.

        Args:
            ip_address (str): IPv4 address of the network interface used for F1 traffic.
            port (int): Number of the port used for F1 traffic.
        """
        if not self.charm.unit.is_leader():
            raise FivegF1Error("Unit must be leader to set application relation data.")
        relations = self.model.relations[self.relation_name]
        if not relations:
            raise FivegF1Error(f"Relation {self.relation_name} not created yet.")
        if not provider_data_is_valid({"f1_ip_address": ip_address, "f1_port": port}):
            raise FivegF1Error("Invalid relation data")
        for relation in relations:
            relation.data[self.charm.app].update(
                {
                    "f1_ip_address": ip_address,
                    "f1_port": str(port),
                }
            )

    @property
    def requirer_f1_port(self) -> Optional[int]:
        """Return the number of the port used for F1 traffic.

        Returns:
            int: Port number.
        """
        if remote_app_relation_data := self._get_remote_app_relation_data():
            return int(remote_app_relation_data.get("f1_port"))  # type: ignore[arg-type]
        return None

    def _get_remote_app_relation_data(
        self, relation: Optional[Relation] = None
    ) -> Optional[Dict[str, str]]:
        """Get relation data for the remote application.

        Args:
            relation: Juju relation object (optional).

        Returns:
            Dict: Relation data for the remote application or None if the relation data is invalid.
        """
        relation = relation or self.model.get_relation(self.relation_name)
        if not relation:
            logger.error("No relation: %s", self.relation_name)
            return None
        if not relation.app:
            logger.warning("No remote application in relation: %s", self.relation_name)
            return None
        remote_app_relation_data = dict(relation.data[relation.app])
        if not requirer_data_is_valid(remote_app_relation_data):
            logger.error("Invalid relation data: %s", remote_app_relation_data)
            return None
        return remote_app_relation_data


class F1Requires(Object):
    """Class to be instantiated by the charm requiring relation using the `fiveg_f1` interface."""

    on = FivegF1RequirerCharmEvents()

    def __init__(self, charm: CharmBase, relation_name: str):
        """Init."""
        super().__init__(charm, relation_name)
        self.charm = charm
        self.relation_name = relation_name
        self.framework.observe(charm.on[relation_name].relation_changed, self._on_relation_changed)

    def _on_relation_changed(self, event: RelationChangedEvent) -> None:
        """Handle relation changed event.

        Args:
            event (RelationChangedEvent): Juju event.
        """
        if remote_app_relation_data := self._get_remote_app_relation_data(event.relation):
            self.on.fiveg_f1_provider_available.emit(
                f1_ip_address=remote_app_relation_data["f1_ip_address"],
                f1_port=remote_app_relation_data["f1_port"],
            )

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

    @property
    def f1_ip_address(self) -> Optional[str]:
        """Return IPv4 address of the network interface used for F1 traffic.

        Returns:
            str: IPv4 address.
        """
        if remote_app_relation_data := self._get_remote_app_relation_data():
            return remote_app_relation_data.get("f1_ip_address")
        return None

    @property
    def f1_port(self) -> Optional[int]:
        """Return the number of the port used for F1 traffic.

        Returns:
            int: Port number.
        """
        if remote_app_relation_data := self._get_remote_app_relation_data():
            return int(remote_app_relation_data.get("f1_port"))  # type: ignore[arg-type]
        return None

    def _get_remote_app_relation_data(
        self, relation: Optional[Relation] = None
    ) -> Optional[Dict[str, str]]:
        """Get relation data for the remote application.

        Args:
            relation: Juju relation object (optional).

        Returns:
            Dict: Relation data for the remote application or None if the relation data is invalid.
        """
        relation = relation or self.model.get_relation(self.relation_name)
        if not relation:
            logger.error("No relation: %s", self.relation_name)
            return None
        if not relation.app:
            logger.warning("No remote application in relation: %s", self.relation_name)
            return None
        remote_app_relation_data = dict(relation.data[relation.app])
        if not provider_data_is_valid(remote_app_relation_data):
            logger.error("Invalid relation data: %s", remote_app_relation_data)
            return None
        return remote_app_relation_data

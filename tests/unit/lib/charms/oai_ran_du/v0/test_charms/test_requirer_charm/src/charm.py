# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

from ops.charm import ActionEvent, CharmBase
from ops.main import main

from lib.charms.oai_ran_du_k8s.v0.fiveg_rfsim import (
    RFSIMRequires,
)


class DummyFivegRFSIMRequires(CharmBase):
    """Dummy charm implementing the requirer side of the fiveg_rfsim interface."""

    def __init__(self, *args):
        super().__init__(*args)
        self.rfsim_requirer = RFSIMRequires(self, "fiveg_rfsim")
        self.framework.observe(
            self.on.get_rfsim_information_action, self._on_get_rfsim_information_action
        )

    def _on_get_rfsim_information_action(self, event: ActionEvent):
        event.set_results(
            results={
                "rfsim-address": self.rfsim_requirer.rfsim_address,
            }
        )


if __name__ == "__main__":
    main(DummyFivegRFSIMRequires)

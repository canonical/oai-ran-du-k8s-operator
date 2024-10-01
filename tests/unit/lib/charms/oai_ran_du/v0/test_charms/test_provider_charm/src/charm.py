# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import logging

from ops.charm import ActionEvent, CharmBase
from ops.main import main

from lib.charms.oai_ran_du_k8s.v0.fiveg_rfsim import RFSIMProvides

logger = logging.getLogger(__name__)


class DummyFivegRFSIMProviderCharm(CharmBase):
    """Dummy charm implementing the provider side of the fiveg_rfsim interface."""

    def __init__(self, *args):
        super().__init__(*args)
        self.rfsim_provider = RFSIMProvides(self, "fiveg_rfsim")
        self.framework.observe(
            self.on.set_rfsim_information_action, self._on_set_rfsim_information_action
        )

    def _on_set_rfsim_information_action(self, event: ActionEvent):
        rfsim_address = event.params.get("rfsim_address", "")
        self.rfsim_provider.set_rfsim_information(
            rfsim_address=rfsim_address,
        )


if __name__ == "__main__":
    main(DummyFivegRFSIMProviderCharm)

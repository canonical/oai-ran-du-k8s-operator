# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import logging

from ops import main
from ops.charm import ActionEvent, CharmBase

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
        sst = event.params.get("sst", "")
        sd = event.params.get("sd", "")
        band = event.params.get("band", "")
        dl_freq = event.params.get("dl_freq", "")
        carrier_bandwidth = event.params.get("carrier_bandwidth", "")
        numerology = event.params.get("numerology", "")
        start_subcarrier = event.params.get("start_subcarrier", "")
        self.rfsim_provider.set_rfsim_information(
            rfsim_address=rfsim_address,
            sst=int(sst),
            sd=int(sd) if sd else None,
            band=int(band),
            dl_freq=int(dl_freq),
            carrier_bandwidth=int(carrier_bandwidth),
            numerology=int(numerology),
            start_subcarrier=int(start_subcarrier),
        )


if __name__ == "__main__":
    main(DummyFivegRFSIMProviderCharm)

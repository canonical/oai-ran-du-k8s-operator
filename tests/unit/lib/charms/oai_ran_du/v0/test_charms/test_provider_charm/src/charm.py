# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import logging

from ops import main
from ops.charm import ActionEvent, CharmBase

from lib.charms.oai_ran_du_k8s.v0.fiveg_rf_config import RFConfigProvides

logger = logging.getLogger(__name__)


class DummyFivegRFConfigProviderCharm(CharmBase):
    """Dummy charm implementing the provider side of the fiveg_rf_config relation."""

    def __init__(self, *args):
        super().__init__(*args)
        self.rf_config_provider = RFConfigProvides(self, "fiveg_rf_config")
        self.framework.observe(
            self.on.set_rf_config_information_action, self._on_set_rf_config_information_action
        )

    def _on_set_rf_config_information_action(self, event: ActionEvent):
        rfsim_address = event.params.get("rfsim_address", "")
        sst = event.params.get("sst", "")
        sd = event.params.get("sd", "")
        band = event.params.get("band", "")
        dl_freq = event.params.get("dl_freq", "")
        carrier_bandwidth = event.params.get("carrier_bandwidth", "")
        numerology = event.params.get("numerology", "")
        start_subcarrier = event.params.get("start_subcarrier", "")
        self.rf_config_provider.set_rf_config_information(
            rfsim_address=rfsim_address if rfsim_address else None,
            sst=int(sst),
            sd=int(sd) if sd else None,
            band=int(band),
            dl_freq=int(dl_freq),
            carrier_bandwidth=int(carrier_bandwidth),
            numerology=int(numerology),
            start_subcarrier=int(start_subcarrier),
        )


if __name__ == "__main__":
    main(DummyFivegRFConfigProviderCharm)

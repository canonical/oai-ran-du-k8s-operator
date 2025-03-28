# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.


from ops import main
from ops.charm import ActionEvent, CharmBase

from lib.charms.oai_ran_du_k8s.v0.fiveg_rfsim import LIBAPI, ProviderAppData, RFSIMRequires


class DummyFivegRFSIMRequires(CharmBase):
    """Dummy charm implementing the requirer side of the fiveg_rfsim interface."""

    def __init__(self, *args):
        super().__init__(*args)
        self.rfsim_requirer = RFSIMRequires(self, "fiveg_rfsim")
        self.framework.observe(
            self.on.get_rfsim_information_action, self._on_get_rfsim_information_action
        )
        self.framework.observe(
            self.on.get_rfsim_information_invalid_action,
            self._on_get_rfsim_information_invalid_action,
        )
        self.framework.observe(
            self.on.set_rfsim_information_action,
            self._on_set_rfsim_information_action,
        )

    def _on_get_rfsim_information_action(self, event: ActionEvent):
        version = event.params.get("expected_version", "")
        rfsim_address = event.params.get("expected_rfsim_address", "")
        sst = event.params.get("expected_sst", "")
        sd = event.params.get("expected_sd", "")
        band = event.params.get("expected_band", "")
        dl_freq = event.params.get("expected_dl_freq", "")
        carrier_bandwidth = event.params.get("expected_carrier_bandwidth", "")
        numerology = event.params.get("expected_numerology", "")
        start_subcarrier = event.params.get("expected_start_subcarrier", "")
        data = {
            "version": version,
            "rfsim_address": rfsim_address,
            "sst": int(sst),
            "band": int(band),
            "dl_freq": int(dl_freq),
            "carrier_bandwidth": int(carrier_bandwidth),
            "numerology": int(numerology),
            "start_subcarrier": int(start_subcarrier),
        }
        if sd:
            data["sd"] = int(sd)
        provider_app_data = ProviderAppData(**data)
        assert provider_app_data == self.rfsim_requirer.get_provider_rfsim_information()

    def _on_get_rfsim_information_invalid_action(self, event: ActionEvent):
        assert self.rfsim_requirer.get_provider_rfsim_information() is None

    def _on_set_rfsim_information_action(self, event: ActionEvent):
        self.rfsim_requirer.set_rfsim_information()
        relation = self.model.get_relation(self.rfsim_requirer.relation_name)
        if not relation:
            assert False
        assert int(relation.data[self.app].get("version", "")) == LIBAPI


if __name__ == "__main__":
    main(DummyFivegRFSIMRequires)

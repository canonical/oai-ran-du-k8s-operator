# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.


from ops import main
from ops.charm import ActionEvent, CharmBase

from lib.charms.oai_ran_du_k8s.v0.fiveg_rf_config import LIBAPI, ProviderAppData, RFConfigRequires


class DummyFivegRFConfigRequires(CharmBase):
    """Dummy charm implementing the requirer side of the fiveg_rf_config relation."""

    def __init__(self, *args):
        super().__init__(*args)
        self.rf_config_requirer = RFConfigRequires(self, "fiveg_rf_config")
        self.framework.observe(
            self.on.get_rf_config_information_action, self._on_get_rf_config_information_action
        )
        self.framework.observe(
            self.on.get_rf_config_information_invalid_action,
            self._on_get_rf_config_information_invalid_action,
        )
        self.framework.observe(
            self.on.set_rf_config_information_action,
            self._on_set_rf_config_information_action,
        )

    def _on_get_rf_config_information_action(self, event: ActionEvent):
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
            "sst": int(sst),
            "band": int(band),
            "dl_freq": int(dl_freq),
            "carrier_bandwidth": int(carrier_bandwidth),
            "numerology": int(numerology),
            "start_subcarrier": int(start_subcarrier),
        }
        if rfsim_address:
            data["rfsim_address"] = str(rfsim_address)
        if sd:
            data["sd"] = int(sd)
        provider_app_data = ProviderAppData(**data)
        assert provider_app_data == self.rf_config_requirer.get_provider_rf_config_information()

    def _on_get_rf_config_information_invalid_action(self, event: ActionEvent):
        assert self.rf_config_requirer.get_provider_rf_config_information() is None

    def _on_set_rf_config_information_action(self, event: ActionEvent):
        self.rf_config_requirer.set_rf_config_information()
        relation = self.model.get_relation(self.rf_config_requirer.relation_name)
        if not relation:
            assert False
        assert int(relation.data[self.app].get("version", "")) == LIBAPI


if __name__ == "__main__":
    main(DummyFivegRFConfigRequires)

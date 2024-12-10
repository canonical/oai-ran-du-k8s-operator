# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.


from ops import main
from ops.charm import ActionEvent, CharmBase

from lib.charms.oai_ran_du_k8s.v0.fiveg_rfsim import ProviderAppData, RFSIMRequires


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

    def _on_get_rfsim_information_action(self, event: ActionEvent):
        rfsim_address = event.params.get("expected_rfsim_address", "")
        sst = event.params.get("expected_sst", "")
        sd = event.params.get("expected_sd", "")
        data = {
            "rfsim_address": rfsim_address,
            "sst": int(sst),
            "sd": int(sd),
        }
        provider_app_data = ProviderAppData(**data)
        assert provider_app_data == self.rfsim_requirer.get_provider_rfsim_information()

    def _on_get_rfsim_information_invalid_action(self, event: ActionEvent):
        assert self.rfsim_requirer.get_provider_rfsim_information() is None


if __name__ == "__main__":
    main(DummyFivegRFSIMRequires)

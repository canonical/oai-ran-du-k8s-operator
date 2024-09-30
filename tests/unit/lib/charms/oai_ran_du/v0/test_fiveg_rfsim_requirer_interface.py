# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import patch

import pytest
import scenario

from lib.charms.oai_ran_du_k8s.v0.fiveg_rfsim import FivegRFSIMInformationAvailableEvent
from tests.unit.lib.charms.oai_ran_du.v0.test_charms.test_requirer_charm.src.charm import (
    DummyFivegRFSIMRequires,
)


class TestFivegRFSIMRequires:
    @pytest.fixture(autouse=True)
    def setUp(self, request):
        yield
        request.addfinalizer(self.tearDown)

    def tearDown(self) -> None:
        patch.stopall()

    @pytest.fixture(autouse=True)
    def context(self):
        self.ctx = scenario.Context(
            charm_type=DummyFivegRFSIMRequires,
            meta={
                "name": "rfsim-requirer-charm",
                "requires": {"fiveg_rfsim": {"interface": "fiveg_rfsim"}},
            },
            actions={
                "get-rfsim-information": {"params": {}},
            },
        )

    def test_given_fiveg_rfsim_relation_created_when_relation_changed_then_event_with_provider_rfsim_address_is_emitted(  # noqa: E501
        self,
    ):
        fiveg_rfsim_relation = scenario.Relation(
            endpoint="fiveg_rfsim",
            interface="fiveg_rfsim",
            remote_app_data={
                "rfsim_address": "192.168.70.130",
            },
        )
        state_in = scenario.State(
            relations=[fiveg_rfsim_relation],
            leader=True,
        )

        self.ctx.run(self.ctx.on.relation_changed(fiveg_rfsim_relation), state_in)

        assert len(self.ctx.emitted_events) == 2
        assert isinstance(self.ctx.emitted_events[1], FivegRFSIMInformationAvailableEvent)
        assert self.ctx.emitted_events[1].rfsim_address == "192.168.70.130"

    def test_given_rfsim_information_not_in_relation_data_when_relation_changed_then_rfsim_information_available_event_is_not_emitted(  # noqa: E501
        self,
    ):
        fiveg_rfsim_relation = scenario.Relation(
            endpoint="fiveg_rfsim",
            interface="fiveg_rfsim",
        )
        state_in = scenario.State(
            leader=True,
            relations=[fiveg_rfsim_relation],
        )

        self.ctx.run(self.ctx.on.relation_changed(fiveg_rfsim_relation), state_in)

        assert len(self.ctx.emitted_events) == 1

    def test_given_rfsim_information_in_relation_data_when_get_rfsim_information_is_called_then_information_is_returned(  # noqa: E501
        self,
    ):
        fiveg_rfsim_relation = scenario.Relation(
            endpoint="fiveg_rfsim",
            interface="fiveg_rfsim",
            remote_app_data={
                "rfsim_address": "192.168.70.130",
            },
        )
        state_in = scenario.State(
            leader=True,
            relations=[fiveg_rfsim_relation],
        )

        self.ctx.run(self.ctx.on.action("get-rfsim-information"), state_in)

        assert self.ctx.action_results
        assert self.ctx.action_results == {"rfsim-address": "192.168.70.130"}

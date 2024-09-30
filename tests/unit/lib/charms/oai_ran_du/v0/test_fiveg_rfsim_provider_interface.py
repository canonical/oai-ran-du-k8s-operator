# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import patch

import pytest
import scenario

from tests.unit.lib.charms.oai_ran_du.v0.test_charms.test_provider_charm.src.charm import (
    DummyFivegRFSIMProviderCharm,
)


class TestFivegRFSIMProvides:
    @pytest.fixture(autouse=True)
    def setUp(self, request):
        yield
        request.addfinalizer(self.tearDown)

    def tearDown(self) -> None:
        patch.stopall()

    @pytest.fixture(autouse=True)
    def context(self):
        self.ctx = scenario.Context(
            charm_type=DummyFivegRFSIMProviderCharm,
            meta={
                "name": "rfsim-provider-charm",
                "provides": {"fiveg_rfsim": {"interface": "fiveg_rfsim"}},
            },
            actions={
                "set-rfsim-information": {"params": {"rfsim_address": {"type": "string"}}},
            },
        )

    def test_given_valid_rfsim_interface_data_when_set_rfsim_information_then_rfsim_address_is_pushed_to_the_relation_databag(  # noqa: E501
        self,
    ):
        fiveg_rfsim_relation = scenario.Relation(
            endpoint="fiveg_rfsim",
            interface="fiveg_rfsim",
        )
        state_in = scenario.State(
            relations=[fiveg_rfsim_relation],
            leader=True,
        )
        params = {
            "rfsim_address": "1.2.3.4",
        }

        state_out = self.ctx.run(
            self.ctx.on.action("set-rfsim-information", params=params), state_in
        )

        relation = state_out.get_relation(fiveg_rfsim_relation.id)
        assert relation.local_app_data == {"rfsim_address": "1.2.3.4"}

    def test_given_invalid_rfsim_address_when_set_rfsim_information_then_error_is_raised(self):
        fiveg_rfsim_relation = scenario.Relation(
            endpoint="fiveg_rfsim",
            interface="fiveg_rfsim",
        )
        state_in = scenario.State(
            relations=[fiveg_rfsim_relation],
            leader=True,
        )
        params = {
            "rfsim_address": 1111,
        }

        with pytest.raises(Exception) as e:
            self.ctx.run(self.ctx.on.action("set-rfsim-information", params=params), state_in)

        assert "Inconsistent scenario" in str(e.value)

    def test_given_unit_is_not_leader_when_fiveg_rfsim_relation_joined_then_data_is_not_in_application_databag(  # noqa: E501
        self,
    ):
        fiveg_rfsim_relation = scenario.Relation(
            endpoint="fiveg_rfsim",
            interface="fiveg_rfsim",
        )
        state_in = scenario.State(
            leader=False,
            relations=[fiveg_rfsim_relation],
        )
        params = {
            "rfsim_address": "1.2.3.4",
        }

        with pytest.raises(Exception) as e:
            self.ctx.run(self.ctx.on.action("set-rfsim-information", params=params), state_in)

        assert "Unit must be leader" in str(e.value)

#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.


from ops import testing

from tests.unit.fixtures import DUFixtures

SAMPLE_CONFIG = {
    "bandwidth": 20,
    "frequency-band": 77,
    "sub-carrier-spacing": 15,
    "center-frequency": "3500",
}


class TestCharmRemove(DUFixtures):
    def test_given_unit_is_leader_when_remove_then_k8s_multus_is_removed(self):
        container = testing.Container(
            name="du",
            can_connect=False,
        )
        state_in = testing.State(leader=True, containers=[container], config=SAMPLE_CONFIG)

        self.ctx.run(self.ctx.on.remove(), state_in)

        self.mock_k8s_multus.remove.assert_called_once()

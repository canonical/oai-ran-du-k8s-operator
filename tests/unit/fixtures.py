#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import PropertyMock, patch

import pytest
from ops import testing

from charm import OAIRANDUOperator


class DUFixtures:
    patcher_k8s_service_patch = patch("charm.KubernetesServicePatch")
    patcher_check_output = patch("charm.check_output")
    patcher_du_security_context = patch("charm.DUSecurityContext")
    patcher_du_usb_volume = patch("charm.DUUSBVolume")
    patcher_k8s_multus = patch("charm.KubernetesMultusCharmLib")
    patcher_f1_requires_f1_ip_address = patch(
        "charm.F1Requires.f1_ip_address", new_callable=PropertyMock
    )
    patcher_f1_requires_f1_port = patch("charm.F1Requires.f1_port", new_callable=PropertyMock)
    patcher_f1_requires_set_f1_information = patch("charm.F1Requires.set_f1_information")
    patcher_rfsim_provides_set_rfsim_information = patch(
        "charm.RFSIMProvides.set_rfsim_information"
    )

    @pytest.fixture(autouse=True)
    def setUp(self, request):
        self.mock_k8s_service_patch = DUFixtures.patcher_k8s_service_patch.start()
        self.mock_check_output = DUFixtures.patcher_check_output.start()
        self.mock_du_security_context = DUFixtures.patcher_du_security_context.start().return_value
        self.mock_du_usb_volume = DUFixtures.patcher_du_usb_volume.start().return_value
        self.mock_k8s_multus = DUFixtures.patcher_k8s_multus.start().return_value
        self.mock_f1_requires_f1_ip_address = DUFixtures.patcher_f1_requires_f1_ip_address.start()
        self.mock_f1_requires_f1_port = DUFixtures.patcher_f1_requires_f1_port.start()
        self.mock_f1_set_information = DUFixtures.patcher_f1_requires_set_f1_information.start()
        self.mock_rfsim_set_information = (
            DUFixtures.patcher_rfsim_provides_set_rfsim_information.start()
        )
        yield
        request.addfinalizer(self.tearDown)

    def tearDown(self) -> None:
        patch.stopall()

    @pytest.fixture(autouse=True)
    def context(self):
        self.ctx = testing.Context(
            charm_type=OAIRANDUOperator,
        )

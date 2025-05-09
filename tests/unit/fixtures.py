#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

from ipaddress import IPv4Address
from unittest.mock import patch

import pytest
from charms.oai_ran_cu_k8s.v0.fiveg_f1 import PLMNConfig, ProviderAppData
from ops import testing

from charm import OAIRANDUOperator

F1_PROVIDER_DATA = ProviderAppData(
    f1_ip_address=IPv4Address("4.3.2.1"),
    f1_port=2152,
    tac=1,
    plmns=[PLMNConfig(mcc="001", mnc="01", sst=1)],
)

F1_PROVIDER_DATA_WITH_SD = ProviderAppData(
    f1_ip_address=IPv4Address("4.3.2.1"),
    f1_port=2152,
    tac=1,
    plmns=[PLMNConfig(mcc="001", mnc="01", sst=1, sd=1)],
)


class DUFixtures:
    patcher_check_output = patch("charm.check_output")
    patcher_du_security_context = patch("charm.DUSecurityContext")
    patcher_du_usb_volume = patch("charm.DUUSBVolume")
    patcher_k8s_multus = patch("charm.KubernetesMultusCharmLib")
    patcher_f1_get_remote_data = patch(
        "charm.F1Requires.get_provider_f1_information",
    )
    patcher_f1_requires_set_f1_information = patch("charm.F1Requires.set_f1_information")
    patcher_rf_config_provides_set_rf_config_information = patch(
        "charm.RFConfigProvides.set_rf_config_information"
    )

    @pytest.fixture(autouse=True)
    def setUp(self, request):
        self.mock_check_output = DUFixtures.patcher_check_output.start()
        self.mock_du_security_context = DUFixtures.patcher_du_security_context.start().return_value
        self.mock_du_usb_volume = DUFixtures.patcher_du_usb_volume.start().return_value
        self.mock_k8s_multus = DUFixtures.patcher_k8s_multus.start().return_value
        self.mock_f1_get_remote_data = DUFixtures.patcher_f1_get_remote_data.start()
        self.mock_f1_set_information = DUFixtures.patcher_f1_requires_set_f1_information.start()
        self.mock_rf_config_set_information = (
            DUFixtures.patcher_rf_config_provides_set_rf_config_information.start()
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

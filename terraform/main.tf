# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "du" {
  name  = var.app_name
  model = var.model

  charm {
    name     = "oai-ran-du-k8s"
    channel  = var.channel
    revision = var.revision
  }

  config      = var.config
  constraints = var.constraints
  units       = var.units
  resources   = var.resources
  trust       = true
}

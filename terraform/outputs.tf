# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

output "app_name" {
  description = "Name of the deployed application."
  value       = juju_application.du.name
}

output "provides" {
  value = {
    "fiveg_rf_config" = "fiveg_rf_config"
  }
}

output "requires" {
  value = {
    "fiveg_f1" = "fiveg_f1"
    "logging"  = "logging"
  }
}

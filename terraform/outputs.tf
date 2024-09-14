# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "app_name" {
  description = "Name of the deployed application."
  value       = juju_application.du.name
}

# Required integration endpoints

output "fiveg_f1_endpoint" {
  description = "Name of the endpoint used to provide information about F1 interface."
  value       = "fiveg_f1"
}

output "fiveg_rfsim_endpoint" {
  description = "Name of the endpoint used to provide information about the rfsim interface."
  value       = "fiveg_rfsim"
}

output "logging_endpoint" {
  description = "Name of the endpoint used to integrate with the Logging provider."
  value       = "logging"
}

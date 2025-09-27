output "config_file" {
  description = "Path to the generated Fluence service configuration"
  value       = local_file.fluence_config.filename
}

output "service_name" {
  description = "Name of the Fluence service"
  value       = var.service_name
}

output "deployment_command" {
  description = "Command to deploy the service manually"
  value       = "fluence service deploy --config ${local_file.fluence_config.filename}"
}
output "service_id" {
  description = "ID of the deployed Fluence service"
  value       = fluence_service.echonet_service.id
}

output "service_url" {
  description = "URL of the deployed service"
  value       = fluence_service.echonet_service.url
}

output "service_status" {
  description = "Status of the deployed service"
  value       = fluence_service.echonet_service.status
}
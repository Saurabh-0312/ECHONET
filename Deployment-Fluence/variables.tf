variable "service_name" {
  description = "Name of the Fluence service"
  type        = string
  default     = "echonet-service"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "memory_limit" {
  description = "Memory limit for the service"
  type        = string
  default     = "512Mi"
}

variable "cpu_limit" {
  description = "CPU limit for the service"
  type        = string
  default     = "500m"
}

variable "service_port" {
  description = "Port for the service"
  type        = number
  default     = 8080
}
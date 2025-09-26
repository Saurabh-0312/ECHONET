terraform {
  required_version = ">= 1.0"
  required_providers {
    fluence = {
      source = "fluencelabs/fluence"
      version = "~> 0.1"
    }
  }
}

provider "fluence" {
  # Configuration will be handled via environment variables
  # FLUENCE_API_KEY and FLUENCE_PROJECT_ID
}

# Basic Fluence service deployment
resource "fluence_service" "echonet_service" {
  name = var.service_name
  
  # Minimal service configuration
  config {
    memory = var.memory_limit
    cpu    = var.cpu_limit
  }

  # Environment variables
  environment = {
    NODE_ENV = var.environment
    PORT     = var.service_port
  }

  tags = {
    project     = "echonet"
    environment = var.environment
    managed_by  = "terraform"
  }
}
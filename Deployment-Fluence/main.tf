terraform {
  required_version = ">= 1.0"
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

# Generate Fluence service configuration file
resource "local_file" "fluence_config" {
  filename = "${path.module}/fluence-service.json"
  content = jsonencode({
    name = var.service_name
    version = "1.0.0"
    config = {
      memory = var.memory_limit
      cpu    = var.cpu_limit
    }
    environment = {
      NODE_ENV = var.environment
      PORT     = var.service_port
    }
    tags = {
      project     = "echonet"
      environment = var.environment
      managed_by  = "terraform"
    }
  })
}

# Deploy to Fluence using CLI (requires fluence CLI to be installed)
resource "null_resource" "deploy_fluence_service" {
  depends_on = [local_file.fluence_config]
  
  triggers = {
    config_hash = local_file.fluence_config.content_md5
  }

  provisioner "local-exec" {
    command = <<-EOT
      echo "Fluence service configuration generated at: ${local_file.fluence_config.filename}"
      echo "To deploy manually, run: fluence service deploy --config ${local_file.fluence_config.filename}"
      echo "Service name: ${var.service_name}"
      echo "Environment: ${var.environment}"
    EOT
  }
}
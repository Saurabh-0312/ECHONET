# Fluence Terraform Deployment

A minimal Terraform configuration for deploying ECHONET services on Fluence.

## Prerequisites

1. [Terraform](https://terraform.io) >= 1.0
2. Fluence account and API credentials

## Setup

1. Set environment variables:
```bash
export FLUENCE_API_KEY="your-api-key"
export FLUENCE_PROJECT_ID="your-project-id"
```

2. Copy and customize variables:
```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

## Deploy

```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply changes
terraform apply
```

## Clean Up

```bash
terraform destroy
```

## Configuration

- `main.tf` - Main Fluence service configuration
- `variables.tf` - Input variables
- `outputs.tf` - Deployment outputs
- `terraform.tfvars` - Your custom values
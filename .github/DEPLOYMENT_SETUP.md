# Deployment Setup Guide

## GitHub Actions Automatic Deployment

This repository is configured for automatic deployment to your production server when code is pushed to the `main` branch in the `Frontend/` or `Server/` directories.

## Required Setup

### 1. Add SSH Private Key to GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Name: `SSH_PRIVATE_KEY`
5. Value: Copy the entire contents of your `cloud_rsa` private key file

```bash
# To get your private key content:
cat ~/.ssh/cloud_rsa
```

Copy the entire output including the `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----` lines.

### 2. Server Requirements

Your server should have:
- Git installed
- Docker and Docker Compose installed
- The ECHONET repository cloned in `/home/ubuntu/ECHONET`
- SSH key-based authentication configured

### 3. Deployment Trigger

The deployment will automatically trigger when:
- Code is pushed to the `main` branch
- Changes are made in `Frontend/**` or `Server/**` directories
- Manual trigger via GitHub Actions tab (workflow_dispatch)

### 4. Deployment Process

The workflow will:
1. Connect to your server via SSH
2. Pull the latest code from the main branch
3. Stop existing containers
4. Rebuild and start containers with `docker compose up --build -d --force-recreate`
5. Verify the deployment status

## Manual Deployment

If you need to deploy manually:

```bash
ssh -i ~/.ssh/cloud_rsa ubuntu@82.177.167.151
cd ECHONET
git pull origin main
sudo docker compose up --build -d --force-recreate
```

## Troubleshooting

### SSH Key Issues
- Ensure the private key is correctly formatted in GitHub secrets
- Verify the server's public key is added to your repository's deploy keys (if needed)
- Check that the ubuntu user has proper permissions

### Docker Issues
- Verify Docker daemon is running: `sudo systemctl status docker`
- Check container logs: `sudo docker compose logs`
- Restart Docker if needed: `sudo systemctl restart docker`

### Permission Issues
- Ensure ubuntu user can run Docker commands without sudo (add to docker group)
- Or use sudo in commands as configured in the workflow
# Docker Setup for ECHONET Frontend

This document explains how to run the ECHONET frontend application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed (usually comes with Docker Desktop)

## Quick Start

### Production Build

To build and run the production version:

```bash
# Build and start the production container
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

The application will be available at `http://localhost:3000`

### Development with Hot Reload

To run the development version with hot reloading:

```bash
# Start development environment
docker-compose --profile dev up frontend-dev --build

# Or run in detached mode
docker-compose --profile dev up -d frontend-dev --build
```

The development server will be available at `http://localhost:5173`

## Docker Commands

### Build Images

```bash
# Build production image
docker build -t echonet-frontend:latest .

# Build development image
docker build -f Dockerfile.dev --target development -t echonet-frontend:dev .
```

### Run Containers

```bash
# Run production container
docker run -p 3000:80 echonet-frontend:latest

# Run development container with volume mounting
docker run -p 5173:5173 -v $(pwd):/app -v /app/node_modules echonet-frontend:dev
```

### Management Commands

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs -f frontend

# Access container shell
docker-compose exec frontend sh
```

## Environment Variables

You can set environment variables in a `.env` file in the same directory as your docker-compose.yml:

```env
NODE_ENV=production
VITE_API_URL=https://your-api-url.com
VITE_CHAIN_ID=1
```

## File Structure

```
Frontend/
├── Dockerfile              # Production multi-stage build
├── Dockerfile.dev          # Development build with hot reload
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore           # Files to ignore during Docker build
├── nginx.conf              # Nginx configuration for production
└── ...
```

## Troubleshooting

### Port Conflicts

If ports 3000 or 5173 are already in use, modify the ports in `docker-compose.yml`:

```yaml
ports:
  - "3001:80"  # Change 3000 to 3001
```

### Permission Issues

If you encounter permission issues on Linux/macOS:

```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Or run with sudo
sudo docker-compose up
```

### Build Issues

If the build fails, try:

```bash
# Clean up Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

## Production Deployment

For production deployment, consider:

1. Using environment-specific `.env` files
2. Setting up SSL/TLS certificates in nginx.conf
3. Using Docker Swarm or Kubernetes for orchestration
4. Implementing health checks and monitoring

## Performance Optimization

The Dockerfile includes several optimizations:

- Multi-stage builds to reduce image size
- Nginx compression enabled
- Proper caching headers
- Static file serving optimizations

## Security Considerations

- The nginx configuration includes security headers
- Sensitive files are excluded via `.dockerignore`
- Non-root user can be configured if needed
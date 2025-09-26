# ECHONET Docker Setup

This Docker configuration provides a complete containerized setup for the ECHONET application with the following services:

- **Frontend**: React application served by Nginx
- **Backend**: Node.js API server
- **Nginx**: Web server with API proxy and SPA routing

## Prerequisites

- Docker and Docker Compose installed on your system
- Git (to clone the repository)

## Quick Start

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd ECHONET
   ```

2. **Set up environment variables**:
   ```bash
   cp Server/.env.example Server/.env
   # Edit Server/.env with your actual configuration
   ```

3. **Build and run the application**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Frontend: http://localhost
   - Backend API: http://localhost:3000
   - Health check: http://localhost/health

## Docker Commands

### Development Commands

```bash
# Build and start services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild specific service
docker-compose build frontend
docker-compose build backend
```

### Production Commands

```bash
# Production build
docker-compose -f docker-compose.yml up -d --build

# Scale services (if needed)
docker-compose up --scale backend=2

# Update and restart
docker-compose pull && docker-compose up -d
```

### Maintenance Commands

```bash
# Remove all containers and volumes
docker-compose down -v

# Clean up Docker system
docker system prune -a

# View service status
docker-compose ps

# Execute commands in running containers
docker-compose exec backend sh
docker-compose exec frontend sh
```

## Architecture

### Frontend Service
- **Base Image**: nginx:alpine
- **Build Process**: Multi-stage build with Node.js for building React app
- **Port**: 80
- **Features**:
  - Optimized Nginx configuration
  - SPA routing support
  - Static asset caching
  - API proxy to backend
  - Security headers
  - Compression enabled

### Backend Service
- **Base Image**: node:20-alpine
- **Port**: 3000
- **Features**:
  - Health checks
  - Non-root user execution
  - Production optimized
  - Environment variable support

### Networking
- Custom bridge network (`echonet-network`)
- Internal service communication
- External access via ports 80 (frontend) and 3000 (backend)

## Configuration Files

### Frontend
- `Frontend/Dockerfile`: Multi-stage build configuration
- `Frontend/nginx.conf`: Nginx web server configuration
- `Frontend/.dockerignore`: Build context optimization

### Backend
- `Server/Dockerfile`: Node.js application configuration
- `Server/healthcheck.js`: Health check script
- `Server/.dockerignore`: Build context optimization
- `Server/.env`: Environment variables (create from .env.example)

### Docker Compose
- `docker-compose.yml`: Service orchestration

## Environment Variables

### Backend (.env file)
```env
NODE_ENV=production
PORT=3000
# Add your application-specific variables here
```

## Health Checks

Both services include health checks:
- **Frontend**: HTTP check on `/health` endpoint
- **Backend**: Custom Node.js health check script

## Security Features

- Non-root user execution in containers
- Security headers in Nginx
- Network isolation
- Minimal base images (Alpine Linux)

## Troubleshooting

### Common Issues

1. **Port conflicts**:
   ```bash
   # Check if ports are in use
   lsof -i :80
   lsof -i :3000
   ```

2. **Build failures**:
   ```bash
   # Clean build cache
   docker-compose build --no-cache
   ```

3. **Environment variables**:
   ```bash
   # Verify .env file exists
   ls -la Server/.env
   ```

4. **Service health**:
   ```bash
   # Check service logs
   docker-compose logs backend
   docker-compose logs frontend
   ```

### Performance Optimization

1. **Build performance**:
   - Use `.dockerignore` files (already configured)
   - Leverage Docker layer caching
   - Use multi-stage builds (already implemented)

2. **Runtime performance**:
   - Nginx compression enabled
   - Static asset caching
   - Health checks for load balancing

## Development vs Production

### Development
- Volume mounting for hot reload
- Development server ports exposed
- Debug logging enabled

### Production
- Optimized builds
- Security hardening
- Health checks
- Restart policies

## Monitoring

Monitor your containers:
```bash
# Container stats
docker stats

# Service logs
docker-compose logs -f --tail=100

# Health status
curl http://localhost/health
curl http://localhost:3000/health
```
# ECHONET Docker Setup

This Docker Compose configuration sets up the ECHONET application with Frontend and Backend services.

## Services

- **Frontend**: React application served via Nginx on port 3000
- **Backend**: Node.js API server on port 3001

## Quick Start

1. Make sure you have Docker and Docker Compose installed
2. Clone the repository and navigate to the root directory
3. Build and start the services:

```bash
docker-compose up --build
```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:3001

## Development Mode

To run in development mode with live reloading:

```bash
docker-compose up --build -d
```

## Stop Services

```bash
docker-compose down
```

## Rebuild Services

```bash
docker-compose up --build --force-recreate
```

## Environment Variables

- Frontend environment variables are in `/Frontend/.env`
- Backend environment variables are in `/Server/.env`

## Network

Both services run on the `echonet-network` bridge network with subnet `172.20.0.0/16`.

The Frontend automatically proxies API requests to the Backend service via nginx configuration.
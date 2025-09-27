# DePIN Marketplace Docker Deployment

This document explains how to run the DePIN Marketplace application using Docker.

## Prerequisites

- Docker and Docker Compose installed
- Your `.env` file configured with the required environment variables

## Quick Start

1. **Build and run the application**:
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode**:
   ```bash
   docker-compose up -d --build
   ```

3. **Stop the application**:
   ```bash
   docker-compose down
   ```

## Configuration

The application runs on port **5002** and includes the following features:

- **Health Check**: Available at `http://localhost:5002/health`
- **Auto-restart**: Container automatically restarts unless stopped manually
- **Environment Variables**: Loaded from `.env` file
- **Networks**: Runs on isolated Docker network `depin-network`

## Available Scripts

- `docker-compose up --build` - Build and start the application
- `docker-compose logs -f` - View application logs
- `docker-compose ps` - Check service status
- `docker-compose exec depin-marketplace sh` - Access container shell

## Environment Variables

Ensure your `.env` file contains:

```env
PORT=5002
RPC_URL=your_rpc_url
MAIN_CONTRACT_ADDRESS=your_contract_address
FACILITATOR_URL=your_facilitator_url
SERVER_WALLET_PRIVATE_KEY=your_private_key
PAYMENT_TOKEN_ADDRESS=your_token_address
BUYER_WALLET_PRIVATE_KEY=your_buyer_private_key
```

## Health Check

The application includes a health check endpoint accessible at:
- http://localhost:5002/health

Docker will automatically monitor this endpoint to ensure the container is healthy.

## Logs

To view real-time logs:
```bash
docker-compose logs -f depin-marketplace
```

## Troubleshooting

1. **Port already in use**: Change the port mapping in `docker-compose.yml`
2. **Environment variables not loaded**: Check your `.env` file formatting
3. **Build fails**: Ensure all dependencies are properly listed in `package.json`

For more details, check the container logs using `docker-compose logs`.
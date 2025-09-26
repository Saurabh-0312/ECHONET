# ECHONET Docker Monitoring Scripts

## Overview
The monitoring scripts help you track the status and health of your ECHONET Docker containers and network connectivity.

## Files
- `monitor_echonet.sh` - Main monitoring script
- `README_monitoring.md` - This documentation file

## Usage

### Basic Monitoring
Run a single status check:
```bash
./monitor_echonet.sh
```

### Continuous Monitoring
Monitor continuously every 30 seconds:
```bash
./monitor_echonet.sh --continuous
```

### Log-Only Mode (for automation/cron)
Run without colored output:
```bash
./monitor_echonet.sh --log-only
```

### Help
Display help information:
```bash
./monitor_echonet.sh --help
```

## What the Script Monitors

### Docker Infrastructure
- ✅ Docker daemon status
- ✅ Container existence and running state
- ✅ Container health status (using Docker health checks)
- ✅ Resource usage (CPU, Memory, Network I/O)

### Network Connectivity
- ✅ Custom network (`echonet-network`) existence
- ✅ Containers connected to the network
- ✅ Inter-container communication (frontend ↔ backend)

### Service Endpoints
- ✅ Backend health endpoint (`http://localhost:3001/health`)
- ✅ Frontend endpoint (`http://localhost:80`)
- ✅ HTTP response status codes

### Docker Compose Integration
- ✅ Docker Compose service detection
- ✅ Service status reporting

## Log Files
The script generates daily log files named: `echonet_monitor_YYYYMMDD.log`

Each log entry includes:
- Timestamp
- Check type and result
- Error messages and status codes
- Resource usage statistics

## Automation Examples

### Cron Job Setup
Add to your crontab to run every 5 minutes:
```bash
# Edit crontab
crontab -e

# Add this line (adjust path as needed)
*/5 * * * * /Users/ekas/Desktop/ECHONET/monitor_echonet.sh --log-only >> /Users/ekas/Desktop/ECHONET/cron_monitor.log 2>&1
```

### Integration with Docker Compose
You can integrate monitoring with your Docker Compose workflow:

```bash
# Start services and monitor
docker-compose up -d && ./monitor_echonet.sh

# Monitor during development
./monitor_echonet.sh --continuous
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   chmod +x monitor_echonet.sh
   ```

2. **Docker Not Running**
   ```bash
   # Start Docker Desktop on macOS
   open -a Docker
   ```

3. **Containers Not Found**
   ```bash
   # Start the services
   docker-compose up -d
   ```

4. **Network Issues**
   ```bash
   # Recreate the network
   docker-compose down
   docker-compose up -d
   ```

### Exit Codes
- `0` - Success
- `1` - Error (Docker daemon not running, containers not found, etc.)

## Monitoring Checklist

When troubleshooting issues, the script checks:

1. 🔧 **Docker Daemon** - Is Docker running?
2. 📦 **Backend Container** - Status, health, resources
3. 🌐 **Frontend Container** - Status, health, resources  
4. 🔗 **Network** - Custom network exists and containers are connected
5. 🌍 **Endpoints** - HTTP services are responding
6. 🔄 **Inter-service** - Frontend can communicate with backend
7. 📋 **Compose** - Docker Compose service status

## Color Coding (Interactive Mode)
- 🟢 **Green** - Success/Healthy
- 🔴 **Red** - Error/Failure
- 🟡 **Yellow** - Warning/Starting
- 🔵 **Blue** - Information/Status

## Sample Output
```
🔍 ECHONET Container and Link Status Monitor
Started at: 2025-09-27 14:30:15
Log file: echonet_monitor_20250927.log

=== Checking Docker Daemon ===
✓ Docker daemon is running

=== Checking Container: echonet-backend ===
✓ Container 'echonet-backend' is running
✓ Container 'echonet-backend' is healthy
📊 Resource usage: 0.50%    45.2MiB / 1.944GiB   1.2kB / 856B

=== Checking Container: echonet-frontend ===
✓ Container 'echonet-frontend' is running
✓ Container 'echonet-frontend' is healthy
📊 Resource usage: 0.10%    12.1MiB / 1.944GiB   2.1kB / 1.2kB

=== Summary Report ===
📊 Containers: 2 running / 2 total
📋 Full log saved to: echonet_monitor_20250927.log
```
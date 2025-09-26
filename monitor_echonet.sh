#!/bin/bash

# ECHONET Docker Container and Link Status Monitor
# This script logs the status of Docker containers and network connectivity

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LOG_FILE="echonet_monitor_$(date +%Y%m%d).log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
BACKEND_PORT=3001
FRONTEND_PORT=80
NETWORK_NAME="echonet-network"

# Service names
BACKEND_SERVICE="echonet-backend"
FRONTEND_SERVICE="echonet-frontend"

# Function to log messages
log_message() {
    echo -e "$1"
    echo "[$TIMESTAMP] $2" >> "$LOG_FILE"
}

# Function to check if Docker is running
check_docker_daemon() {
    log_message "${BLUE}=== Checking Docker Daemon ===${NC}" "=== Checking Docker Daemon ==="
    
    if ! docker info >/dev/null 2>&1; then
        log_message "${RED}✗ Docker daemon is not running${NC}" "ERROR: Docker daemon is not running"
        return 1
    else
        log_message "${GREEN}✓ Docker daemon is running${NC}" "SUCCESS: Docker daemon is running"
        return 0
    fi
}

# Function to check container status
check_container_status() {
    local container_name=$1
    
    log_message "${BLUE}=== Checking Container: $container_name ===${NC}" "=== Checking Container: $container_name ==="
    
    # Check if container exists
    if ! docker ps -a --format "table {{.Names}}" | grep -q "^$container_name$"; then
        log_message "${RED}✗ Container '$container_name' does not exist${NC}" "ERROR: Container '$container_name' does not exist"
        return 1
    fi
    
    # Get container status
    local status=$(docker inspect --format '{{.State.Status}}' "$container_name" 2>/dev/null)
    local health=$(docker inspect --format '{{.State.Health.Status}}' "$container_name" 2>/dev/null)
    
    case $status in
        "running")
            log_message "${GREEN}✓ Container '$container_name' is running${NC}" "SUCCESS: Container '$container_name' is running"
            
            # Check health status if available
            if [[ "$health" != "<no value>" && -n "$health" ]]; then
                case $health in
                    "healthy")
                        log_message "${GREEN}✓ Container '$container_name' is healthy${NC}" "SUCCESS: Container '$container_name' is healthy"
                        ;;
                    "unhealthy")
                        log_message "${RED}✗ Container '$container_name' is unhealthy${NC}" "ERROR: Container '$container_name' is unhealthy"
                        ;;
                    "starting")
                        log_message "${YELLOW}⚠ Container '$container_name' health check is starting${NC}" "WARNING: Container '$container_name' health check is starting"
                        ;;
                esac
            fi
            ;;
        "exited")
            local exit_code=$(docker inspect --format '{{.State.ExitCode}}' "$container_name")
            log_message "${RED}✗ Container '$container_name' has exited (code: $exit_code)${NC}" "ERROR: Container '$container_name' has exited (code: $exit_code)"
            ;;
        "paused")
            log_message "${YELLOW}⚠ Container '$container_name' is paused${NC}" "WARNING: Container '$container_name' is paused"
            ;;
        *)
            log_message "${RED}✗ Container '$container_name' status: $status${NC}" "ERROR: Container '$container_name' status: $status"
            ;;
    esac
    
    # Show resource usage
    local stats=$(docker stats --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" "$container_name" 2>/dev/null | tail -1)
    if [[ -n "$stats" ]]; then
        log_message "${BLUE}📊 Resource usage: $stats${NC}" "INFO: Resource usage for '$container_name': $stats"
    fi
}

# Function to check network connectivity
check_network_connectivity() {
    log_message "${BLUE}=== Checking Network Connectivity ===${NC}" "=== Checking Network Connectivity ==="
    
    # Check if custom network exists
    if ! docker network ls --format "{{.Name}}" | grep -q "^$NETWORK_NAME$"; then
        log_message "${RED}✗ Network '$NETWORK_NAME' does not exist${NC}" "ERROR: Network '$NETWORK_NAME' does not exist"
        return 1
    fi
    
    log_message "${GREEN}✓ Network '$NETWORK_NAME' exists${NC}" "SUCCESS: Network '$NETWORK_NAME' exists"
    
    # Check network details
    local network_info=$(docker network inspect "$NETWORK_NAME" --format '{{range .Containers}}{{.Name}} {{end}}' 2>/dev/null)
    if [[ -n "$network_info" ]]; then
        log_message "${BLUE}📡 Connected containers: $network_info${NC}" "INFO: Connected containers to '$NETWORK_NAME': $network_info"
    fi
}

# Function to check service endpoints
check_service_endpoints() {
    log_message "${BLUE}=== Checking Service Endpoints ===${NC}" "=== Checking Service Endpoints ==="
    
    # Check backend endpoint
    log_message "${BLUE}Checking backend health endpoint...${NC}" "Checking backend health endpoint..."
    if curl -sf "http://localhost:$BACKEND_PORT/healthz" >/dev/null 2>&1; then
        log_message "${GREEN}✓ Backend health endpoint responding${NC}" "SUCCESS: Backend health endpoint (port $BACKEND_PORT) responding"
    else
        log_message "${RED}✗ Backend health endpoint not responding${NC}" "ERROR: Backend health endpoint (port $BACKEND_PORT) not responding"
        # Try alternative endpoints
        if curl -sf "http://localhost:$BACKEND_PORT/" >/dev/null 2>&1; then
            log_message "${YELLOW}⚠ Backend root endpoint responding (health endpoint may need fixing)${NC}" "WARNING: Backend root endpoint responding but /healthz failed"
        fi
    fi
    
    # Check frontend endpoint
    log_message "${BLUE}Checking frontend endpoint...${NC}" "Checking frontend endpoint..."
    if curl -sf "http://localhost:$FRONTEND_PORT/health" >/dev/null 2>&1; then
        log_message "${GREEN}✓ Frontend health endpoint responding${NC}" "SUCCESS: Frontend health endpoint (port $FRONTEND_PORT) responding"
    else
        # Try basic connection to frontend
        if curl -sf "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1; then
            log_message "${GREEN}✓ Frontend endpoint responding${NC}" "SUCCESS: Frontend endpoint (port $FRONTEND_PORT) responding"
        else
            log_message "${RED}✗ Frontend endpoint not responding${NC}" "ERROR: Frontend endpoint (port $FRONTEND_PORT) not responding"
        fi
    fi
}

# Function to check inter-container connectivity
check_inter_container_connectivity() {
    log_message "${BLUE}=== Checking Inter-Container Connectivity ===${NC}" "=== Checking Inter-Container Connectivity ==="
    
    # Check if both containers are running before testing connectivity
    if docker ps --format "{{.Names}}" | grep -q "^$BACKEND_SERVICE$" && \
       docker ps --format "{{.Names}}" | grep -q "^$FRONTEND_SERVICE$"; then
        
        # Test frontend -> backend connectivity
        log_message "${BLUE}Testing frontend -> backend connectivity...${NC}" "Testing frontend -> backend connectivity..."
        if docker exec "$FRONTEND_SERVICE" wget --spider -q "http://$BACKEND_SERVICE:$BACKEND_PORT/health" 2>/dev/null; then
            log_message "${GREEN}✓ Frontend can reach backend${NC}" "SUCCESS: Frontend can reach backend"
        else
            log_message "${RED}✗ Frontend cannot reach backend${NC}" "ERROR: Frontend cannot reach backend"
        fi
    else
        log_message "${YELLOW}⚠ Skipping inter-container connectivity test (containers not running)${NC}" "WARNING: Skipping inter-container connectivity test (containers not running)"
    fi
}

# Function to show Docker Compose status
check_compose_status() {
    log_message "${BLUE}=== Checking Docker Compose Status ===${NC}" "=== Checking Docker Compose Status ==="
    
    if command -v docker-compose >/dev/null 2>&1; then
        local compose_status=$(docker-compose ps --services 2>/dev/null)
        if [[ $? -eq 0 && -n "$compose_status" ]]; then
            log_message "${GREEN}✓ Docker Compose services detected${NC}" "SUCCESS: Docker Compose services detected"
            log_message "${BLUE}Services: $compose_status${NC}" "INFO: Docker Compose services: $compose_status"
        else
            log_message "${YELLOW}⚠ No Docker Compose services running or docker-compose.yml not found${NC}" "WARNING: No Docker Compose services running or docker-compose.yml not found"
        fi
    else
        log_message "${YELLOW}⚠ docker-compose command not found${NC}" "WARNING: docker-compose command not found"
    fi
}

# Function to generate summary report
generate_summary() {
    log_message "${BLUE}=== Summary Report ===${NC}" "=== Summary Report ==="
    
    local running_containers=$(docker ps --format "{{.Names}}" | wc -l)
    local total_containers=$(docker ps -a --format "{{.Names}}" | wc -l)
    
    log_message "${BLUE}📊 Containers: $running_containers running / $total_containers total${NC}" "INFO: Containers: $running_containers running / $total_containers total"
    log_message "${BLUE}📋 Full log saved to: $LOG_FILE${NC}" "INFO: Full log saved to: $LOG_FILE"
}

# Main execution
main() {
    echo -e "${GREEN}🔍 ECHONET Container and Link Status Monitor${NC}"
    echo -e "${BLUE}Started at: $TIMESTAMP${NC}"
    echo -e "${BLUE}Log file: $LOG_FILE${NC}"
    echo ""
    
    log_message "" "=== ECHONET Monitor Started at $TIMESTAMP ==="
    
    # Run all checks
    check_docker_daemon || exit 1
    
    echo ""
    check_container_status "$BACKEND_SERVICE"
    
    echo ""
    check_container_status "$FRONTEND_SERVICE"
    
    echo ""
    check_network_connectivity
    
    echo ""
    check_service_endpoints
    
    echo ""
    check_inter_container_connectivity
    
    echo ""
    check_compose_status
    
    echo ""
    generate_summary
    
    log_message "" "=== ECHONET Monitor Completed at $(date '+%Y-%m-%d %H:%M:%S') ==="
}

# Check if script is run with arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --continuous   Run monitoring in continuous mode (every 30 seconds)"
        echo "  --log-only     Run without colored output (suitable for cron jobs)"
        exit 0
        ;;
    --continuous)
        echo "Running in continuous monitoring mode (Ctrl+C to stop)"
        while true; do
            main
            echo ""
            echo "Waiting 30 seconds before next check..."
            sleep 30
            clear
        done
        ;;
    --log-only)
        # Disable colors for log-only mode
        RED=''
        GREEN=''
        YELLOW=''
        BLUE=''
        NC=''
        main
        ;;
    *)
        main
        ;;
esac
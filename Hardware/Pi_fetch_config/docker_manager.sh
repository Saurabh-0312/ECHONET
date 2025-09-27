#!/bin/bash

# ECHONET Device Node Docker Management Script
echo "🚀 ECHONET Device Node Docker Setup"

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker daemon is not running. Please start Docker Desktop and try again."
        echo "   On macOS: open -a Docker"
        exit 1
    fi
    echo "✅ Docker daemon is running"
}

# Function to build the Docker image
build_image() {
    echo "🔨 Building Docker image..."
    docker build -t echonet-device-node .
    
    if [ $? -eq 0 ]; then
        echo "✅ Docker image built successfully"
    else
        echo "❌ Failed to build Docker image"
        exit 1
    fi
}

# Function to run the container using docker-compose
run_container() {
    echo "🚀 Starting container with docker-compose..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo "✅ Container started successfully"
        echo "📋 Container status:"
        docker-compose ps
        echo ""
        echo "📖 To view logs: docker-compose logs -f"
        echo "🛑 To stop: docker-compose down"
    else
        echo "❌ Failed to start container"
        exit 1
    fi
}

# Function to run the container directly with Docker
run_docker_direct() {
    echo "🚀 Running container directly with Docker..."
    
    # If MAC address is provided as argument, use it
    if [ ! -z "$1" ]; then
        echo "📡 Using MAC address: $1"
        docker run -d --name echonet-device-node --network host echonet-device-node python device_node.py "$1"
    else
        echo "📡 Using auto-detected MAC address"
        docker run -d --name echonet-device-node --network host echonet-device-node
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ Container started successfully"
        echo "📋 Container status:"
        docker ps | grep echonet-device-node
        echo ""
        echo "📖 To view logs: docker logs -f echonet-device-node"
        echo "🛑 To stop: docker stop echonet-device-node && docker rm echonet-device-node"
    else
        echo "❌ Failed to start container"
        exit 1
    fi
}

# Function to show logs
show_logs() {
    echo "📖 Showing container logs..."
    if docker-compose ps | grep -q echonet-device-node; then
        docker-compose logs -f
    else
        docker logs -f echonet-device-node
    fi
}

# Function to stop containers
stop_containers() {
    echo "🛑 Stopping containers..."
    docker-compose down 2>/dev/null || true
    docker stop echonet-device-node 2>/dev/null && docker rm echonet-device-node 2>/dev/null || true
    echo "✅ Containers stopped"
}

# Main script logic
case "$1" in
    "build")
        check_docker
        build_image
        ;;
    "run")
        check_docker
        run_container
        ;;
    "run-direct")
        check_docker
        run_docker_direct "$2"
        ;;
    "logs")
        show_logs
        ;;
    "stop")
        stop_containers
        ;;
    "restart")
        stop_containers
        sleep 2
        check_docker
        run_container
        ;;
    *)
        echo "📚 Usage: $0 {build|run|run-direct [MAC_ADDRESS]|logs|stop|restart}"
        echo ""
        echo "Commands:"
        echo "  build       - Build the Docker image"
        echo "  run         - Run using docker-compose"
        echo "  run-direct  - Run directly with Docker (optionally specify MAC address)"
        echo "  logs        - Show container logs"
        echo "  stop        - Stop all containers"
        echo "  restart     - Stop and restart containers"
        echo ""
        echo "Examples:"
        echo "  $0 build"
        echo "  $0 run"
        echo "  $0 run-direct 00:1A:2B:3C:4D:5E"
        echo "  $0 logs"
        exit 1
        ;;
esac
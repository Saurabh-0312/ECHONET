#!/bin/bash
#
# EchoNet Kernel Monitor Installation Script for Raspberry Pi OS
# This script installs and configures the binary execution monitoring system
#
# Usage: sudo ./install_monitor.sh
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/usr/local/bin"
CONFIG_DIR="/usr/local/etc/echonet"
SERVICE_DIR="/etc/systemd/system"
LOG_DIR="/var/log"

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Check system compatibility
check_system() {
    print_status "Checking system compatibility..."
    
    # Check if running on Raspberry Pi OS
    if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null && ! grep -q "BCM" /proc/cpuinfo 2>/dev/null; then
        print_warning "This script is designed for Raspberry Pi OS but will continue anyway"
    fi
    
    # Check required commands
    local required_commands=("openssl" "sha256sum" "systemctl" "cargo" "rustc")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            print_error "Required command not found: $cmd"
            if [[ "$cmd" == "cargo" || "$cmd" == "rustc" ]]; then
                print_status "Installing Rust..."
                curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
                source ~/.cargo/env
            elif [[ "$cmd" == "openssl" ]]; then
                print_status "Installing OpenSSL..."
                apt-get update && apt-get install -y openssl libssl-dev
            else
                print_error "Please install $cmd manually"
                exit 1
            fi
        fi
    done
    
    print_success "System compatibility check passed"
}

# Install dependencies
install_dependencies() {
    print_status "Installing system dependencies..."
    
    apt-get update
    apt-get install -y \
        build-essential \
        libssl-dev \
        pkg-config \
        curl \
        git \
        openssl \
        coreutils \
        procps \
        lsof
    
    print_success "Dependencies installed"
}

# Build the Rust kernel monitor
build_monitor() {
    print_status "Building kernel monitoring binary..."
    
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    if [[ ! -f "$script_dir/Cargo.toml" ]]; then
        print_error "Cargo.toml not found in $script_dir"
        exit 1
    fi
    
    cd "$script_dir"
    
    # Build in release mode for better performance
    cargo build --release
    
    if [[ ! -f "target/release/kernel_monitoring" ]]; then
        print_error "Failed to build kernel_monitoring binary"
        exit 1
    fi
    
    print_success "Kernel monitoring binary built successfully"
}

# Install binaries and scripts
install_binaries() {
    print_status "Installing binaries and scripts..."
    
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Create directories
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"
    
    # Install kernel monitor binary
    cp "$script_dir/target/release/kernel_monitoring" "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/kernel_monitoring"
    
    # Install pre-execution monitor script
    cp "$script_dir/pre_exec_monitor.sh" "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/pre_exec_monitor.sh"
    
    # Install systemd service
    cp "$script_dir/echonet-monitor.service" "$SERVICE_DIR/"
    
    print_success "Binaries and scripts installed"
}

# Generate cryptographic keys and signatures
setup_crypto() {
    print_status "Setting up cryptographic keys..."
    
    # Generate RSA key pair if not exists
    if [[ ! -f "$CONFIG_DIR/private.pem" ]]; then
        openssl genrsa -out "$CONFIG_DIR/private.pem" 2048
        chmod 600 "$CONFIG_DIR/private.pem"
        print_success "Generated private key"
    fi
    
    if [[ ! -f "$CONFIG_DIR/public.pem" ]]; then
        openssl rsa -in "$CONFIG_DIR/private.pem" -pubout -out "$CONFIG_DIR/public.pem"
        chmod 644 "$CONFIG_DIR/public.pem"
        print_success "Generated public key"
    fi
    
    # Create a dummy allowed binary and sign it (for demonstration)
    local dummy_binary="$CONFIG_DIR/echonet_sensor"
    if [[ ! -f "$dummy_binary" ]]; then
        cat > "$dummy_binary" << 'EOF'
#!/bin/bash
echo "EchoNet Sensor - Authorized Binary"
echo "This is a placeholder for the actual sensor binary"
EOF
        chmod +x "$dummy_binary"
        
        # Sign the dummy binary
        openssl dgst -sha256 -sign "$CONFIG_DIR/private.pem" -out "$CONFIG_DIR/binary.sig" "$dummy_binary"
        print_success "Created and signed dummy sensor binary"
    fi
    
    print_success "Cryptographic setup completed"
}

# Configure system integration
setup_system_integration() {
    print_status "Setting up system integration..."
    
    # Initialize monitor environment
    "$INSTALL_DIR/pre_exec_monitor.sh" setup
    
    # Enable and start systemd service
    systemctl daemon-reload
    systemctl enable echonet-monitor.service
    
    print_success "System integration configured"
}

# Setup shell hooks (optional, experimental)
setup_shell_hooks() {
    print_status "Setting up shell execution hooks..."
    
    # Add to system-wide bash configuration
    if [[ -f /etc/bash.bashrc ]]; then
        if ! grep -q "EchoNet Pre-execution Monitor" /etc/bash.bashrc; then
            cat >> /etc/bash.bashrc << 'EOF'

# EchoNet Pre-execution Monitor Hook
# This provides basic shell-level monitoring (experimental)
if [[ -x /usr/local/bin/pre_exec_monitor.sh && "$PS1" ]]; then
    # Only enable in interactive shells to avoid breaking scripts
    if [[ $- == *i* ]]; then
        preexec_echonet() {
            if [[ -n "$BASH_COMMAND" && "$BASH_COMMAND" != "preexec_echonet" ]]; then
                local cmd_parts=($BASH_COMMAND)
                local binary="${cmd_parts[0]}"
                # Only check if it looks like a binary execution
                if [[ "$binary" =~ ^(/|\./) ]] || command -v "$binary" >/dev/null 2>&1; then
                    local full_path="$(which "$binary" 2>/dev/null || echo "$binary")"
                    if [[ -x "$full_path" ]]; then
                        /usr/local/bin/pre_exec_monitor.sh "$full_path" 2>/dev/null || true
                    fi
                fi
            fi
        }
        
        # Note: This is experimental and may impact performance
        # trap 'preexec_echonet' DEBUG
    fi
fi
EOF
            print_success "Shell hooks added to /etc/bash.bashrc"
        else
            print_warning "Shell hooks already present in /etc/bash.bashrc"
        fi
    fi
}

# Create uninstall script
create_uninstall_script() {
    print_status "Creating uninstall script..."
    
    cat > "$INSTALL_DIR/uninstall_echonet_monitor.sh" << 'EOF'
#!/bin/bash
# EchoNet Monitor Uninstall Script

set -e

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (use sudo)"
    exit 1
fi

echo "Stopping and disabling EchoNet monitor service..."
systemctl stop echonet-monitor.service 2>/dev/null || true
systemctl disable echonet-monitor.service 2>/dev/null || true

echo "Removing files..."
rm -f /usr/local/bin/kernel_monitoring
rm -f /usr/local/bin/pre_exec_monitor.sh
rm -f /usr/local/bin/uninstall_echonet_monitor.sh
rm -f /etc/systemd/system/echonet-monitor.service
rm -rf /usr/local/etc/echonet
rm -f /var/run/echonet_monitor.pid

echo "Cleaning up shell hooks..."
sed -i '/# EchoNet Pre-execution Monitor/,/^$/d' /etc/bash.bashrc 2>/dev/null || true

systemctl daemon-reload

echo "EchoNet monitor uninstalled successfully"
EOF
    
    chmod +x "$INSTALL_DIR/uninstall_echonet_monitor.sh"
    print_success "Uninstall script created at $INSTALL_DIR/uninstall_echonet_monitor.sh"
}

# Main installation function
main() {
    print_status "Starting EchoNet Kernel Monitor installation..."
    
    check_root
    check_system
    install_dependencies
    build_monitor
    install_binaries
    setup_crypto
    setup_system_integration
    setup_shell_hooks
    create_uninstall_script
    
    print_success "Installation completed successfully!"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Start the monitor service: sudo systemctl start echonet-monitor.service"
    echo "2. Check service status: sudo systemctl status echonet-monitor.service"
    echo "3. View logs: sudo tail -f /var/log/echonet_monitor.log"
    echo "4. Test with: sudo /usr/local/bin/pre_exec_monitor.sh /bin/ls"
    echo ""
    echo -e "${YELLOW}Note:${NC} Replace /usr/local/etc/echonet/echonet_sensor with your actual binary"
    echo "      and sign it with: openssl dgst -sha256 -sign /usr/local/etc/echonet/private.pem -out /usr/local/etc/echonet/binary.sig /path/to/your/binary"
}

# Run main function
main "$@"
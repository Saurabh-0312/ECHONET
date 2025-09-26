#!/bin/bash
#
# Pre-execution Binary Monitoring Script for Raspberry Pi OS
# This script should be integrated into the kernel to check binaries before execution
#
# Installation:
# 1. Copy this script to /usr/local/bin/pre_exec_monitor.sh
# 2. Make it executable: chmod +x /usr/local/bin/pre_exec_monitor.sh
# 3. Add to /etc/bash.bashrc or /etc/profile for shell integration
# 4. For kernel-level integration, modify /etc/ld.so.preload or use ptrace/seccomp
#
# Usage: pre_exec_monitor.sh <binary_path> [allowed_binary] [signature_file] [public_key]
#

set -euo pipefail

# Configuration - these should be set according to your environment
ALLOWED_BINARY_DEFAULT="/usr/local/bin/echonet_sensor"
SIGNATURE_FILE_DEFAULT="/usr/local/etc/echonet/binary.sig"
PUBLIC_KEY_DEFAULT="/usr/local/etc/echonet/public.pem"
KERNEL_MONITOR_BINARY="/usr/local/bin/kernel_monitoring"
LOG_FILE="/var/log/echonet_monitor.log"
MONITOR_PID_FILE="/var/run/echonet_monitor.pid"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "${LOG_FILE}"
}

# Function to verify binary signature using OpenSSL
verify_binary_signature() {
    local binary_path="$1"
    local signature_file="$2"
    local public_key="$3"
    
    if [[ ! -f "$binary_path" ]]; then
        log_message "ERROR: Binary file not found: $binary_path"
        return 1
    fi
    
    if [[ ! -f "$signature_file" ]]; then
        log_message "ERROR: Signature file not found: $signature_file"
        return 1
    fi
    
    if [[ ! -f "$public_key" ]]; then
        log_message "ERROR: Public key file not found: $public_key"
        return 1
    fi
    
    # Verify signature using OpenSSL
    if openssl dgst -sha256 -verify "$public_key" -signature "$signature_file" "$binary_path" >/dev/null 2>&1; then
        log_message "INFO: Signature verification successful for: $binary_path"
        return 0
    else
        log_message "ERROR: Signature verification failed for: $binary_path"
        return 1
    fi
}

# Function to compute SHA-256 hash of a file
compute_sha256() {
    local file_path="$1"
    if [[ -f "$file_path" ]]; then
        sha256sum "$file_path" | cut -d' ' -f1
    else
        echo ""
    fi
}

# Function to check if kernel monitor is running
is_monitor_running() {
    if [[ -f "$MONITOR_PID_FILE" ]]; then
        local pid=$(cat "$MONITOR_PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        else
            # Stale PID file
            rm -f "$MONITOR_PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start kernel monitor daemon
start_kernel_monitor() {
    local allowed_binary="$1"
    local signature_file="$2"
    local public_key="$3"
    
    if is_monitor_running; then
        log_message "INFO: Kernel monitor already running"
        return 0
    fi
    
    if [[ ! -x "$KERNEL_MONITOR_BINARY" ]]; then
        log_message "WARNING: Kernel monitor binary not found or not executable: $KERNEL_MONITOR_BINARY"
        return 1
    fi
    
    log_message "INFO: Starting kernel monitor daemon"
    nohup "$KERNEL_MONITOR_BINARY" "$allowed_binary" "$signature_file" "$public_key" 5 \
        >> "$LOG_FILE" 2>&1 &
    local monitor_pid=$!
    echo "$monitor_pid" > "$MONITOR_PID_FILE"
    log_message "INFO: Kernel monitor started with PID: $monitor_pid"
}

# Function to check if binary is in whitelist
is_whitelisted_binary() {
    local binary_path="$1"
    
    # System binaries whitelist
    local system_paths=(
        "/bin/"
        "/sbin/"
        "/usr/bin/"
        "/usr/sbin/"
        "/usr/local/bin/"
        "/lib/"
        "/usr/lib/"
        "/opt/"
    )
    
    # Check if binary is in system paths
    for path in "${system_paths[@]}"; do
        if [[ "$binary_path" == "$path"* ]]; then
            return 0
        fi
    done
    
    # Check against specific whitelisted binaries
    local whitelisted_binaries=(
        "/bin/bash"
        "/bin/sh"
        "/bin/dash"
        "/usr/bin/sudo"
        "/usr/bin/ssh"
        "/usr/bin/scp"
        "/usr/bin/rsync"
    )
    
    for allowed in "${whitelisted_binaries[@]}"; do
        if [[ "$binary_path" == "$allowed" ]]; then
            return 0
        fi
    done
    
    return 1
}

# Main execution check function
check_binary_execution() {
    local target_binary="$1"
    local allowed_binary="${2:-$ALLOWED_BINARY_DEFAULT}"
    local signature_file="${3:-$SIGNATURE_FILE_DEFAULT}"
    local public_key="${4:-$PUBLIC_KEY_DEFAULT}"
    
    # Get absolute path
    target_binary=$(realpath "$target_binary" 2>/dev/null || echo "$target_binary")
    
    log_message "INFO: Checking execution permission for: $target_binary"
    
    # Check if it's a whitelisted system binary
    if is_whitelisted_binary "$target_binary"; then
        log_message "INFO: Binary is whitelisted: $target_binary"
        return 0
    fi
    
    # Check if it's the allowed EchoNet binary
    if [[ "$target_binary" == "$allowed_binary" ]]; then
        if verify_binary_signature "$target_binary" "$signature_file" "$public_key"; then
            log_message "INFO: Allowed EchoNet binary execution approved: $target_binary"
            start_kernel_monitor "$allowed_binary" "$signature_file" "$public_key"
            return 0
        else
            log_message "ERROR: EchoNet binary signature verification failed: $target_binary"
            return 1
        fi
    fi
    
    # For other binaries, check if they match the allowed binary hash
    local target_hash=$(compute_sha256 "$target_binary")
    local allowed_hash=$(compute_sha256 "$allowed_binary")
    
    if [[ -n "$target_hash" && -n "$allowed_hash" && "$target_hash" == "$allowed_hash" ]]; then
        log_message "INFO: Binary matches allowed hash: $target_binary"
        return 0
    fi
    
    # Deny execution
    log_message "ERROR: Binary execution denied - not authorized: $target_binary"
    return 1
}

# Function to setup the monitoring environment
setup_monitor() {
    # Create necessary directories
    mkdir -p /usr/local/etc/echonet
    mkdir -p /var/log
    touch "$LOG_FILE"
    
    # Set appropriate permissions
    chmod 644 "$LOG_FILE"
    chmod 755 /usr/local/etc/echonet
    
    log_message "INFO: EchoNet monitoring environment initialized"
}

# Function to install as pre-exec hook (requires root)
install_preexec_hook() {
    if [[ $EUID -ne 0 ]]; then
        echo "ERROR: This function requires root privileges"
        return 1
    fi
    
    # Create wrapper script for ld preload
    cat > /usr/local/lib/preexec_wrapper.so << 'EOF'
#!/bin/bash
# This would need to be implemented as a shared library for ld.so.preload
# For now, we provide shell integration
EOF

    # Add to system-wide shell initialization
    if ! grep -q "pre_exec_monitor" /etc/bash.bashrc 2>/dev/null; then
        cat >> /etc/bash.bashrc << 'EOF'

# EchoNet Pre-execution Monitor
if [[ -x /usr/local/bin/pre_exec_monitor.sh ]]; then
    preexec() {
        if [[ -n "$1" && "$1" != "preexec" ]]; then
            local cmd_parts=($1)
            local binary="${cmd_parts[0]}"
            if [[ -x "$binary" || -x "$(which "$binary" 2>/dev/null)" ]]; then
                /usr/local/bin/pre_exec_monitor.sh "$(which "$binary" 2>/dev/null || echo "$binary")" || return 1
            fi
        fi
    }
    
    # Set up preexec hook for bash
    if [[ "$PS1" ]]; then
        trap 'preexec "$BASH_COMMAND"' DEBUG
    fi
fi
EOF
    fi
    
    log_message "INFO: Pre-execution hook installed system-wide"
}

# Main script logic
main() {
    case "${1:-}" in
        "setup")
            setup_monitor
            ;;
        "install")
            install_preexec_hook
            ;;
        "start-monitor")
            start_kernel_monitor \
                "${2:-$ALLOWED_BINARY_DEFAULT}" \
                "${3:-$SIGNATURE_FILE_DEFAULT}" \
                "${4:-$PUBLIC_KEY_DEFAULT}"
            ;;
        "status")
            if is_monitor_running; then
                echo "Kernel monitor is running (PID: $(cat "$MONITOR_PID_FILE"))"
            else
                echo "Kernel monitor is not running"
            fi
            ;;
        "stop")
            if [[ -f "$MONITOR_PID_FILE" ]]; then
                local pid=$(cat "$MONITOR_PID_FILE")
                if kill "$pid" 2>/dev/null; then
                    log_message "INFO: Stopped kernel monitor (PID: $pid)"
                    rm -f "$MONITOR_PID_FILE"
                else
                    log_message "WARNING: Could not stop kernel monitor (PID: $pid)"
                    rm -f "$MONITOR_PID_FILE"
                fi
            else
                echo "No monitor PID file found"
            fi
            ;;
        "")
            echo "Usage: $0 <binary_path> [allowed_binary] [signature_file] [public_key]"
            echo "       $0 {setup|install|start-monitor|status|stop}"
            exit 1
            ;;
        *)
            # Main execution check
            check_binary_execution "$@"
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
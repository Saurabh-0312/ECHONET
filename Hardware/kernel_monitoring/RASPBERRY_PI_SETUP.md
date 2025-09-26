# EchoNet Kernel Binary Monitoring for Raspberry Pi OS

This system provides kernel-level binary execution monitoring for Raspberry Pi OS, ensuring only cryptographically signed and authorized binaries can execute on the system.

## Overview

The monitoring system consists of three main components:

1. **Kernel Monitor Daemon** (`kernel_monitoring`) - Rust binary that continuously monitors running processes
2. **Pre-execution Script** (`pre_exec_monitor.sh`) - Shell script that checks binaries before execution
3. **System Integration** - SystemD service and shell hooks for comprehensive monitoring

## Features

- **Cryptographic Verification**: RSA PKCS#1 v1.5 signature verification with SHA-256
- **Real-time Process Monitoring**: Continuous monitoring of all running processes
- **Automatic Process Termination**: Kills unauthorized processes automatically
- **System Integration**: Integrates with Raspberry Pi OS through SystemD and shell hooks
- **Whitelist Support**: System binaries and essential tools are whitelisted
- **Logging**: Comprehensive logging of all monitoring activities

## Quick Installation

1. **Clone and navigate to the kernel monitoring directory:**
   ```bash
   cd /path/to/ECHONET/Hardware/kernel_monitoring
   ```

2. **Run the installation script:**
   ```bash
   sudo ./install_monitor.sh
   ```

3. **Start the monitoring service:**
   ```bash
   sudo systemctl start echonet-monitor.service
   ```

## Manual Installation Steps

### Prerequisites

```bash
# Install required packages
sudo apt-get update
sudo apt-get install -y build-essential libssl-dev pkg-config curl git openssl

# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

### Build the Monitor

```bash
# Build the Rust kernel monitor
cargo build --release

# The binary will be created at: target/release/kernel_monitoring
```

### Install Components

```bash
# Copy binaries to system paths
sudo cp target/release/kernel_monitoring /usr/local/bin/
sudo cp pre_exec_monitor.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/kernel_monitoring
sudo chmod +x /usr/local/bin/pre_exec_monitor.sh

# Install systemd service
sudo cp echonet-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### Setup Cryptographic Keys

```bash
# Create configuration directory
sudo mkdir -p /usr/local/etc/echonet

# Generate RSA key pair
sudo openssl genrsa -out /usr/local/etc/echonet/private.pem 2048
sudo openssl rsa -in /usr/local/etc/echonet/private.pem -pubout -out /usr/local/etc/echonet/public.pem

# Set proper permissions
sudo chmod 600 /usr/local/etc/echonet/private.pem
sudo chmod 644 /usr/local/etc/echonet/public.pem
```

### Sign Your Binary

```bash
# Sign your EchoNet sensor binary
sudo openssl dgst -sha256 -sign /usr/local/etc/echonet/private.pem \
    -out /usr/local/etc/echonet/binary.sig \
    /path/to/your/echonet_sensor_binary

# Copy your binary to the expected location
sudo cp /path/to/your/echonet_sensor_binary /usr/local/etc/echonet/echonet_sensor
sudo chmod +x /usr/local/etc/echonet/echonet_sensor
```

## Usage

### Service Management

```bash
# Start the monitor service
sudo systemctl start echonet-monitor.service

# Enable auto-start on boot
sudo systemctl enable echonet-monitor.service

# Check service status
sudo systemctl status echonet-monitor.service

# Stop the service
sudo systemctl stop echonet-monitor.service

# View service logs
sudo journalctl -u echonet-monitor.service -f
```

### Manual Operations

```bash
# Test binary verification
sudo /usr/local/bin/pre_exec_monitor.sh /path/to/binary

# Start monitor manually
sudo /usr/local/bin/pre_exec_monitor.sh start-monitor

# Check monitor status
sudo /usr/local/bin/pre_exec_monitor.sh status

# Stop monitor
sudo /usr/local/bin/pre_exec_monitor.sh stop

# Setup environment
sudo /usr/local/bin/pre_exec_monitor.sh setup
```

### Viewing Logs

```bash
# Monitor logs in real-time
sudo tail -f /var/log/echonet_monitor.log

# View recent log entries
sudo cat /var/log/echonet_monitor.log | tail -50
```

## Configuration

### Default Paths

- **Allowed Binary**: `/usr/local/etc/echonet/echonet_sensor`
- **Signature File**: `/usr/local/etc/echonet/binary.sig`
- **Public Key**: `/usr/local/etc/echonet/public.pem`
- **Private Key**: `/usr/local/etc/echonet/private.pem`
- **Log File**: `/var/log/echonet_monitor.log`
- **PID File**: `/var/run/echonet_monitor.pid`

### Customization

To use different paths or multiple allowed binaries, modify the configuration variables in `pre_exec_monitor.sh`:

```bash
ALLOWED_BINARY_DEFAULT="/path/to/your/binary"
SIGNATURE_FILE_DEFAULT="/path/to/your/signature"
PUBLIC_KEY_DEFAULT="/path/to/your/public_key"
```

## How It Works

### Process Flow

1. **System Boot**: SystemD starts the EchoNet monitor service
2. **Binary Execution**: When a binary is executed, the pre-execution script is triggered
3. **Verification**: The script checks if the binary is whitelisted or matches allowed signatures
4. **Decision**: Allows execution if verified, denies and logs if not
5. **Monitoring**: The kernel monitor daemon continuously watches running processes
6. **Enforcement**: Unauthorized processes are automatically terminated

### Security Model

- **Whitelist-based**: System binaries are whitelisted for normal operation
- **Signature Verification**: Non-system binaries must be cryptographically signed
- **Hash Comparison**: Runtime verification using SHA-256 hashes
- **Process Monitoring**: Continuous monitoring prevents runtime tampering
- **Automatic Enforcement**: Unauthorized processes are killed immediately

## Integration Levels

### 1. Shell-Level Integration (Default)
- Hooks into bash execution via DEBUG trap
- Provides basic protection for interactive shells
- Limited scope but easy to implement

### 2. SystemD Integration
- Service-level monitoring with automatic restart
- Comprehensive process monitoring
- Better for server/headless environments

### 3. Kernel-Level Integration (Advanced)
For deeper integration, consider:
- **LD_PRELOAD**: Intercept library calls
- **ptrace**: System call tracing
- **seccomp**: System call filtering
- **LSM (Linux Security Modules)**: Kernel-level security hooks

## Troubleshooting

### Common Issues

1. **Service won't start**:
   ```bash
   sudo journalctl -u echonet-monitor.service
   sudo /usr/local/bin/pre_exec_monitor.sh setup
   ```

2. **Permission denied**:
   ```bash
   sudo chmod +x /usr/local/bin/kernel_monitoring
   sudo chmod +x /usr/local/bin/pre_exec_monitor.sh
   ```

3. **Signature verification fails**:
   ```bash
   # Re-sign your binary
   sudo openssl dgst -sha256 -sign /usr/local/etc/echonet/private.pem \
       -out /usr/local/etc/echonet/binary.sig \
       /usr/local/etc/echonet/echonet_sensor
   ```

4. **Monitor not killing processes**:
   - Check if monitor is running: `sudo /usr/local/bin/pre_exec_monitor.sh status`
   - Verify log file: `sudo tail /var/log/echonet_monitor.log`
   - Restart service: `sudo systemctl restart echonet-monitor.service`

### Debug Mode

Enable verbose logging by modifying the service file:
```bash
sudo systemctl edit echonet-monitor.service
```

Add:
```ini
[Service]
Environment=RUST_LOG=debug
```

## Security Considerations

### Strengths
- Cryptographic verification prevents tampering
- Continuous monitoring catches runtime modifications
- Automatic enforcement reduces response time
- Whitelisting prevents most unauthorized executions

### Limitations
- Can be bypassed by kernel-level exploits
- Shell hooks can be disabled by advanced attackers
- System binaries are trusted (potential attack vector)
- Performance impact from continuous monitoring

### Recommendations
1. Keep the private key secure and offline when possible
2. Regularly rotate cryptographic keys
3. Monitor logs for suspicious activity
4. Combine with other security measures (firewall, IDS, etc.)
5. Test thoroughly before production deployment

## Uninstallation

To remove the monitoring system:

```bash
sudo /usr/local/bin/uninstall_echonet_monitor.sh
```

Or manually:
```bash
sudo systemctl stop echonet-monitor.service
sudo systemctl disable echonet-monitor.service
sudo rm -f /usr/local/bin/kernel_monitoring
sudo rm -f /usr/local/bin/pre_exec_monitor.sh
sudo rm -f /etc/systemd/system/echonet-monitor.service
sudo rm -rf /usr/local/etc/echonet
sudo systemctl daemon-reload
```

## Contributing

To contribute to the EchoNet kernel monitoring system:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on Raspberry Pi OS
5. Submit a pull request

## License

This project is part of the EchoNet ecosystem. Please refer to the main project license.

---

For more information about the EchoNet project, visit the main repository at: https://github.com/Saurabh-0312/ECHONET
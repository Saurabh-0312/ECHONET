# Kernel Monitoring Tool

A Rust-based security monitoring tool that validates running processes against cryptographically signed binaries and terminates unauthorized processes.

## Overview

This tool monitors all running processes on macOS systems and ensures only cryptographically verified binaries are allowed to execute. It uses RSA PKCS#1 v1.5 signatures with SHA-256 hashing to verify the integrity and authenticity of allowed binaries.

## Features

- **Cryptographic Verification**: Validates binary signatures using RSA public key cryptography
- **Process Monitoring**: Continuously monitors all running processes on the system
- **Automatic Termination**: Kills unauthorized processes that don't match the allowed binary signature
- **SHA-256 Hashing**: Uses secure hash comparison for binary verification
- **macOS Compatibility**: Optimized for macOS using `ps` and `lsof` commands
- **Configurable Polling**: Adjustable monitoring interval

## Prerequisites

- Rust (2024 edition)
- macOS operating system
- OpenSSL development libraries
- Required system commands: `ps`, `lsof`

## Dependencies

- `anyhow` - Error handling
- `hex` - Hexadecimal encoding/decoding
- `nix` - Unix system calls (signals, processes)
- `openssl` - Cryptographic operations
- `sha2` - SHA-256 hashing
- `log` - Logging framework
- `env_logger` - Environment-based logging

## Usage 

1. Build the project:
```bash
cargo build --release
```

## Usage

```bash
./target/release/kernel_monitoring <allowed_binary_path> <signature_file> <public_key_pem> [poll_seconds]
```

### Parameters

- `allowed_binary_path`: Path to the binary that is allowed to run
- `signature_file`: Path to the RSA signature file for the allowed binary
- `public_key_pem`: Path to the RSA public key in PEM format
- `poll_seconds`: Optional polling interval in seconds (default: 2)

### Example

```bash
./target/release/kernel_monitoring /usr/bin/my_app /path/to/my_app.sig /path/to/public_key.pem 5
```

## How It Works

1. **Startup Verification**: Verifies the signature of the allowed binary against the provided public key
2. **Hash Calculation**: Computes SHA-256 hash of the allowed binary for comparison
3. **Process Monitoring**: Continuously scans all running processes using `ps` and `lsof`
4. **Binary Comparison**: For each process, retrieves the executable path and computes its hash
5. **Termination**: Kills any process whose binary hash doesn't match the allowed binary hash

## Security Model

- Only processes running the exact same binary (same SHA-256 hash) as the allowed binary are permitted
- All other processes are terminated with SIGKILL
- The monitoring process itself and system init process (PID 1) are exempt from termination
- Signature verification ensures the allowed binary hasn't been tampered with

## Logging

The tool uses environment-based logging. Set the `RUST_LOG` environment variable to control log levels:

```bash
RUST_LOG=info ./target/release/kernel_monitoring ...
RUST_LOG=debug ./target/release/kernel_monitoring ...
```

Log levels:
- `info`: Basic operation information
- `warn`: Warnings about failed operations
- `error`: Critical errors
- `debug`: Detailed debugging information

## Error Handling

The tool handles various error conditions gracefully:
- Invalid signatures result in immediate exit
- Failed process enumeration is logged but doesn't stop monitoring
- Inaccessible executable files are logged as warnings
- Permission errors when killing processes are logged

## Building from Source

```bash
# Debug build
cargo build

# Release build (recommended for production)
cargo build --release

# Run tests
cargo test

# Check code
cargo check
```

## Limitations

- Currently macOS-only (uses macOS-specific `ps` and `lsof` commands)
- Requires root privileges to kill other processes
- May not detect processes that quickly start and exit between polling intervals
- Cannot monitor kernel-level processes

## Security Considerations

- Run with appropriate privileges (typically requires root for process termination)
- Protect the private key used for signing binaries
- Regularly rotate cryptographic keys
- Monitor the tool's own logs for security events
- Consider the polling interval vs. system performance trade-off

## Future Enhancements

- Linux compatibility
- Real-time process monitoring (using kernel events)
- Configuration file support
- Multiple allowed binaries
- Integration with system security frameworks
- Performance optimizations

## License

[Specify your license here]

## Contributing

[Add contribution guidelines here]

## Support

[Add support information here]
use anyhow::{Context, Result};
use hex::encode;
use nix::sys::signal::{kill, Signal};
use nix::unistd::Pid;
use openssl::pkey::PKey;
use openssl::sign::Verifier;
use openssl::hash::MessageDigest;
use sha2::{Digest, Sha256};
use std::fs;
use std::io::{Read};
use std::path::{Path, PathBuf};
use std::process::Command;
use std::thread;
use std::time::Duration;
use log::{info, warn, error};

/// Read a file fully into a Vec<u8>.
fn read_file_bytes(path: &Path) -> Result<Vec<u8>> {
    let mut f = fs::File::open(path)
        .with_context(|| format!("opening file {}", path.display()))?;
    let mut buf = Vec::new();
    f.read_to_end(&mut buf)?;
    Ok(buf)
}

/// Compute SHA-256 hex for a file (reading it streaming).
fn sha256_of_file(path: &Path) -> Result<String> {
    let mut f = fs::File::open(path)
        .with_context(|| format!("opening file {}", path.display()))?;
    let mut hasher = Sha256::new();
    let mut buf = [0u8; 8192];
    loop {
        let n = f.read(&mut buf)?;
        if n == 0 { break; }
        hasher.update(&buf[..n]);
    }
    Ok(encode(hasher.finalize()))
}

/// Verify signature (signature is raw bytes) over the file contents using a PEM public key.
/// We assume RSA PKCS#1 v1.5 with SHA-256 (common pattern for binary.sig/public.pem).
fn verify_signature(public_pem: &Path, target_file: &Path, signature_file: &Path) -> Result<bool> {
    let pub_pem = read_file_bytes(public_pem)?;
    let signature = read_file_bytes(signature_file)?;
    let content = read_file_bytes(target_file)?;
    let pkey = PKey::public_key_from_pem(&pub_pem)
        .with_context(|| format!("loading public key {}", public_pem.display()))?;
    let mut verifier = Verifier::new(MessageDigest::sha256(), &pkey)
        .context("creating verifier")?;
    verifier.update(&content)?;
    let ok = verifier.verify(&signature)?;
    Ok(ok)
}

/// Try to kill a process by pid (SIGKILL). Returns true if kill was attempted.
fn attempt_kill(pid: i32) -> bool {
    match kill(Pid::from_raw(pid), Signal::SIGKILL) {
        Ok(_) => {
            info!("Sent SIGKILL to pid {}", pid);
            true
        }
        Err(e) => {
            warn!("Failed to kill pid {}: {}", pid, e);
            false
        }
    }
}

/// Get all running processes on macOS using `ps` command
fn get_macos_processes() -> Result<Vec<(i32, PathBuf)>> {
    let output = Command::new("ps")
        .args(&["-eo", "pid,comm"])
        .output()
        .context("Failed to execute ps command")?;

    if !output.status.success() {
        return Err(anyhow::anyhow!("ps command failed"));
    }

    let stdout = String::from_utf8(output.stdout)
        .context("ps output is not valid UTF-8")?;

    let mut processes = Vec::new();
    
    for line in stdout.lines().skip(1) { // Skip header
        let parts: Vec<&str> = line.trim().split_whitespace().collect();
        if parts.len() >= 2 {
            if let Ok(pid) = parts[0].parse::<i32>() {
                let comm = parts[1..].join(" ");
                if let Ok(exe_path) = get_executable_path(pid) {
                    processes.push((pid, exe_path));
                }
            }
        }
    }

    Ok(processes)
}

/// Get executable path for a given PID on macOS
fn get_executable_path(pid: i32) -> Result<PathBuf> {
    let output = Command::new("lsof")
        .args(&["-p", &pid.to_string(), "-Fn"])
        .output()
        .context("Failed to execute lsof command")?;

    if !output.status.success() {
        return Err(anyhow::anyhow!("lsof command failed for pid {}", pid));
    }

    let stdout = String::from_utf8(output.stdout)
        .context("lsof output is not valid UTF-8")?;

    // Look for the first executable file (txt type)
    for line in stdout.lines() {
        if line.starts_with("n/") && !line.contains("(deleted)") {
            let path_str = &line[1..]; // Remove the 'n' prefix
            let path = PathBuf::from(path_str);
            if path.exists() && is_executable(&path) {
                return Ok(path);
            }
        }
    }

    Err(anyhow::anyhow!("Could not find executable path for pid {}", pid))
}

/// Check if a file is executable
fn is_executable(path: &Path) -> bool {
    use std::os::unix::fs::PermissionsExt;
    
    if let Ok(metadata) = fs::metadata(path) {
        let permissions = metadata.permissions();
        permissions.mode() & 0o111 != 0
    } else {
        false
    }
}

fn main() -> Result<()> {
    env_logger::init();

    // Basic CLI: args: allowed_binary, signature, public_pem, poll_seconds
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 4 {
        eprintln!("Usage: {} <allowed_binary_path> <sig_path> <public_pem> [poll_seconds]", args[0]);
        std::process::exit(2);
    }

    let allowed_path = PathBuf::from(&args[1]);
    let sig_path = PathBuf::from(&args[2]);
    let public_pem = PathBuf::from(&args[3]);
    let poll_seconds: u64 = args.get(4)
        .and_then(|s| s.parse::<u64>().ok())
        .unwrap_or(2);

    info!("Starting proc_monitor. Allowed binary: {}", allowed_path.display());

    // Verify signature at startup
    match verify_signature(&public_pem, &allowed_path, &sig_path) {
        Ok(true) => info!("Signature verification succeeded."),
        Ok(false) => {
            error!("Signature verification FAILED. Not starting monitor.");
            std::process::exit(1);
        }
        Err(e) => {
            error!("Signature verification error: {:?}", e);
            std::process::exit(1);
        }
    }

    // Compute allowed hash once (used to compare)
    let allowed_hash = sha256_of_file(&allowed_path)
        .with_context(|| format!("computing hash of {}", allowed_path.display()))?;
    info!("Allowed binary hash: {}", allowed_hash);

    let self_pid = std::process::id() as i32;

    loop {
        // Get all processes using macOS-compatible method
        match get_macos_processes() {
            Ok(processes) => {
                for (pid, exe_path) in processes {
                    // Skip init and ourselves
                    if pid == 1 || pid == self_pid {
                        continue;
                    }

                    // If exe is same path as allowed_path, OK
                    if exe_path == allowed_path {
                        continue;
                    }

                    // Try to compute hash of the exe file.
                    // Some processes may have deleted executables or weird entries; handle errors gracefully.
                    match sha256_of_file(&exe_path) {
                        Ok(h) => {
                            if h != allowed_hash {
                                info!("PID {} exe {} has hash {} -> mismatch. Killing.", pid, exe_path.display(), h);
                                attempt_kill(pid);
                            } else {
                                // matches allowed hash (possibly different path but same bytes)
                            }
                        }
                        Err(e) => {
                            // Could be permission or deleted file; log at debug level
                            warn!("Could not hash {} for pid {}: {}", exe_path.display(), pid, e);
                        }
                    }
                }
            }
            Err(e) => {
                warn!("Failed to list processes: {}", e);
            }
        }

        thread::sleep(Duration::from_secs(poll_seconds));
    }
}

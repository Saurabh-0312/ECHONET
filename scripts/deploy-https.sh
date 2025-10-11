#!/usr/bin/env bash
set -euo pipefail

# deploy-https.sh
# Idempotent helper to bring up the Compose stack, obtain Let's Encrypt certificates
# (webroot) for a domain, ensure the frontend container has access to the certs, reload
# nginx and register a renewal cron. Intended to run on the server from the repository root.
#
# Usage:
#   sudo ./scripts/deploy-https.sh --email you@example.com [--staging] [--domain echonet.live]
#
# Notes:
# - The script assumes you're in the repo root where docker-compose.yml lives.
# - It writes cert files into ./certbot/conf (project mount used by the frontend) by copying
#   from /etc/letsencrypt after Certbot issues them. Alternatively, you can change compose to
#   mount /etc/letsencrypt directly.

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DOMAIN="echonet.live"
EMAIL=""
STAGING=0

usage() {
  cat <<EOF
Usage: sudo $0 --email you@example.com [--staging] [--domain domain]

Options:
  --email EMAIL     Email address for certbot registration (required)
  --staging         Use Let's Encrypt staging server (for testing)
  --domain DOMAIN   Domain to request cert for (default: ${DOMAIN})
  -h|--help         Show this help
EOF
  exit 1
}

while [[ ${#} -gt 0 ]]; do
  case "$1" in
    --email)
      EMAIL="$2"; shift 2;;
    --staging)
      STAGING=1; shift;;
    --domain)
      DOMAIN="$2"; shift 2;;
    -h|--help)
      usage;;
    *)
      echo "Unknown arg: $1"; usage;;
  esac
done

if [[ -z "$EMAIL" ]]; then
  echo "--email is required" >&2
  usage
fi

echo "Running deploy-https for domain: $DOMAIN"
echo "Repository dir: $REPO_DIR"
echo "Email: $EMAIL"
if [[ "$STAGING" -eq 1 ]]; then
  echo "Using Let's Encrypt staging server (safe for tests)"
fi

cd "$REPO_DIR"

# Ensure certbot directories exist in project
mkdir -p ./certbot/www ./certbot/conf ./certbot/work ./certbot/logs
chmod 755 ./certbot/www

echo "Bringing up docker compose (build)"
sudo docker compose up -d --build

# Ensure nginx is serving the ACME webroot before requesting certs
echo "Checking ACME webroot is served by nginx..."
if curl -fsS http://localhost/.well-known/acme-challenge/ >/dev/null 2>&1; then
  echo "ACME webroot reachable locally"
else
  echo "ACME webroot not reachable locally; ensure frontend container is up and listening on port 80" >&2
fi

# Use certbot to obtain/renew certificate. If the system /etc/letsencrypt already contains
# a certificate, certbot may only renew; we'll force renewal when necessary.
CERTBOT_ARGS=(certonly --webroot -w ./certbot/www -d "$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive)
if [[ "$STAGING" -eq 1 ]]; then
  CERTBOT_ARGS+=(--staging)
fi

echo "Running certbot..."
# Use sudo to ensure certbot can write into system /etc/letsencrypt if needed
sudo certbot "${CERTBOT_ARGS[@]}" || {
  echo "Certbot failed; see /var/log/letsencrypt/letsencrypt.log" >&2
}

# After certbot runs, copy the issued certs from system /etc/letsencrypt into project mount so
# the frontend container will pick them up (this repo uses ./certbot/conf mounted into container)
if [[ -d "/etc/letsencrypt/live/$DOMAIN" ]]; then
  echo "Copying certs from /etc/letsencrypt to project certbot/conf"
  sudo mkdir -p ./certbot/conf/live/$DOMAIN ./certbot/conf/archive/$DOMAIN ./certbot/conf/renewal
  sudo cp -a /etc/letsencrypt/live/$DOMAIN/* ./certbot/conf/live/$DOMAIN/ || true
  sudo cp -a /etc/letsencrypt/archive/$DOMAIN/* ./certbot/conf/archive/$DOMAIN/ 2>/dev/null || true
  sudo cp -a /etc/letsencrypt/renewal/$DOMAIN.conf ./certbot/conf/renewal/ 2>/dev/null || true
  sudo chown -R root:root ./certbot/conf
  sudo chmod -R 755 ./certbot/conf
  sudo chmod 644 ./certbot/conf/live/$DOMAIN/fullchain.pem || true
  sudo chmod 600 ./certbot/conf/live/$DOMAIN/privkey.pem || true
else
  echo "/etc/letsencrypt/live/$DOMAIN not found; certbot may have written to another location" >&2
fi

echo "Reloading nginx inside frontend container"
sudo docker compose exec frontend nginx -s reload || sudo docker compose restart frontend

echo "Validating HTTPS externally is recommended (curl from your workstation): curl -I https://$DOMAIN"

# Set up a simple cron job for renewals if systemd timer is not present
if systemctl list-timers | grep -qi certbot; then
  echo "certbot systemd timer appears present; skipping cron setup"
else
  echo "Installing cron job for certbot renew (/etc/cron.d/certbot-renew)"
  sudo bash -c 'cat > /etc/cron.d/certbot-renew <<EOF
# Renew twice daily; if renewed, restart frontend so nginx picks up certs
0 3 * * * root certbot renew --quiet --deploy-hook "cd $REPO_DIR && docker compose restart frontend"
0 15 * * * root certbot renew --quiet --deploy-hook "cd $REPO_DIR && docker compose restart frontend"
EOF'
  echo "Installed /etc/cron.d/certbot-renew"
fi

echo "Done."

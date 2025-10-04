#!/usr/bin/env bash
# renew-and-reload.sh
# Run certbot renew using the docker-compose certbot service and reload frontend nginx if certificates changed.
set -euo pipefail

REPO_DIR="$(dirname "$0")"
cd "$REPO_DIR"

# Run renewal
echo "Running certbot renew..."
docker compose run --rm certbot renew --webroot -w /var/www/certbot

# If renewal succeeded, restart frontend so nginx picks up new certs
echo "Reloading frontend (nginx) container..."
docker compose restart frontend

echo "Renewal finished and frontend reloaded."

#!/usr/bin/env bash
# certbot-init.sh
# Helper script to obtain Let's Encrypt certificates using the certbot Docker image
# Usage: ./certbot-init.sh -d example.com -d www.example.com -m your@email.com --staging

set -euo pipefail

DOMAINS=()
EMAIL=""
STAGING=0

usage() {
  echo "Usage: $0 -d domain [-d domain2 ...] -m email [--staging]"
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--domain)
      shift
      DOMAINS+=("$1")
      ;;
    -m|--email)
      shift
      EMAIL="$1"
      ;;
    --staging)
      STAGING=1
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown arg: $1"
      usage
      ;;
  esac
  shift
done

if [ ${#DOMAINS[@]} -eq 0 ] || [ -z "$EMAIL" ]; then
  usage
fi

STAGING_ARG=""
if [ "$STAGING" -eq 1 ]; then
  STAGING_ARG="--staging"
fi

# Build domain args for certbot
DOMAIN_ARGS=()
for d in "${DOMAINS[@]}"; do
  DOMAIN_ARGS+=("-d" "$d")
done

# Run certbot using docker compose service
# This will use the webroot plugin and place challenge files under ./certbot-www (mapped to /var/www/certbot)

docker compose run --rm certbot certonly --webroot -w /var/www/certbot ${STAGING_ARG} --agree-tos --no-eff-email --email "$EMAIL" ${DOMAIN_ARGS[@]}

echo "Certificate request completed. Certificates stored in the certbot-etc volume (mounted at /etc/letsencrypt in the certbot container)."

echo "To copy certificates to your host for inspection:"
echo "  docker compose run --rm certbot cat /etc/letsencrypt/live/${DOMAINS[0]}/fullchain.pem > fullchain.pem"

exit 0

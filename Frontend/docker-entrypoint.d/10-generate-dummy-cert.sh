#!/bin/sh
# Generate a self-signed certificate if Let's Encrypt certs are missing
set -e

DOM=echonet.live
LE_DIR="/etc/letsencrypt/live/$DOM"

if [ -f "$LE_DIR/fullchain.pem" ] && [ -f "$LE_DIR/privkey.pem" ]; then
  echo "Let's Encrypt certs found, skipping dummy cert generation"
  exit 0
fi

echo "Let's Encrypt certs not found. Generating self-signed certificate for $DOM"

mkdir -p "$LE_DIR"

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "$LE_DIR/privkey.pem" \
  -out "$LE_DIR/fullchain.pem" \
  -subj "/C=US/ST=Unset/L=Unset/O=ECHONET/CN=$DOM"

chmod 644 "$LE_DIR/fullchain.pem" "$LE_DIR/privkey.pem"
echo "Dummy certificate created at $LE_DIR"

exit 0

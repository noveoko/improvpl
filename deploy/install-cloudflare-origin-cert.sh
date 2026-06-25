#!/usr/bin/env bash
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
    echo "Run as root: sudo bash deploy/install-cloudflare-origin-cert.sh"
    exit 1
fi

CERT_DIR="/etc/ssl/cloudflare"
CERT_FILE="$CERT_DIR/improv.pl.pem"
KEY_FILE="$CERT_DIR/improv.pl.key"
APP_DIR="/home/improvuser/improvpl"

if [[ ! -f "$CERT_FILE" || ! -f "$KEY_FILE" ]]; then
    echo "Missing certificate files."
    echo "1. Cloudflare → SSL/TLS → Origin Server → Create Certificate"
    echo "2. Save certificate to: $CERT_FILE"
    echo "3. Save private key to:  $KEY_FILE"
    echo "4. chmod 600 $KEY_FILE"
    exit 1
fi

chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"

cp "$APP_DIR/deploy/nginx/improvpl.conf" /etc/nginx/sites-available/improvpl
nginx -t
systemctl restart nginx
systemctl restart gunicorn

echo "Cloudflare Origin Certificate installed. Set Cloudflare SSL mode to Full (strict)."
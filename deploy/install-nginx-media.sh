#!/usr/bin/env bash
# One-time fix: enable nginx to serve uploaded media files.
# Run on the server with sudo:
#   sudo bash /home/improvuser/improvpl/deploy/install-nginx-media.sh
set -euo pipefail

APP_DIR="/home/improvuser/improvpl"
CONF_SRC="$APP_DIR/deploy/nginx/improvpl-http-only.conf"
CONF_DST="/etc/nginx/sites-available/improvpl"

if [[ ! -f /etc/ssl/cloudflare/improv.pl.pem ]]; then
  cp "$CONF_SRC" "$CONF_DST"
else
  cp "$APP_DIR/deploy/nginx/improvpl.conf" "$CONF_DST"
fi

nginx -t
systemctl reload nginx
echo "Nginx updated — /media/ should now be served."
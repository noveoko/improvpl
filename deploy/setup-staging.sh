#!/usr/bin/env bash
# One-time staging environment setup on the production droplet (run as improvuser).
set -euo pipefail

STAGING_DIR="/home/improvuser/improvpl-staging"

if [[ -d "$STAGING_DIR" ]]; then
  echo "Staging directory already exists: $STAGING_DIR"
  exit 1
fi

git clone git@github.com:noveoko/improvpl.git "$STAGING_DIR"
cd "$STAGING_DIR"
git checkout staging 2>/dev/null || git checkout -b staging

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

if [[ ! -f .env ]]; then
  echo "Create $STAGING_DIR/.env (copy from production and adjust ALLOWED_HOSTS / DATABASE_URL)."
  cp .env.example .env
fi

python manage.py migrate
python manage.py collectstatic --noinput

echo "Next steps (as root):"
echo "  sudo cp $STAGING_DIR/deploy/gunicorn-staging.service /etc/systemd/system/"
echo "  sudo cp $STAGING_DIR/deploy/nginx/improvpl-staging.conf /etc/nginx/sites-available/"
echo "  sudo ln -sf /etc/nginx/sites-available/improvpl-staging.conf /etc/nginx/sites-enabled/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable --now gunicorn-staging"
echo "  sudo nginx -t && sudo systemctl reload nginx"
echo "  echo 'improvuser ALL=(ALL) NOPASSWD: /bin/systemctl restart gunicorn-staging' | sudo tee /etc/sudoers.d/improvuser-gunicorn-staging"
echo "Add Cloudflare DNS: A record staging -> <DROPLET_IP> (proxied)"
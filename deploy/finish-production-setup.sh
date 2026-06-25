#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/improvuser/improvpl"
cd "$APP_DIR"

echo "==> Installing poll cron job"
bash deploy/setup-cron.sh

echo "==> Seeding demo events and polls"
source venv/bin/activate
python manage.py seed_demo_data

echo ""
echo "Production setup steps on this server:"
echo "  [ ] Brevo:  bash deploy/configure-brevo.sh <login> <smtp-key>"
echo "  [ ] SSL:    install origin cert, then sudo bash deploy/install-cloudflare-origin-cert.sh"
echo "  [ ] Deploy: ensure GitHub Actions secrets are set (see deploy/GITHUB_ACTIONS.md)"
echo ""
echo "Done."
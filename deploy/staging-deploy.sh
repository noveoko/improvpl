#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/improvuser/improvpl-staging"
cd "$APP_DIR"

git fetch origin staging
git reset --hard origin/staging

mkdir -p "$APP_DIR/media"

source venv/bin/activate
pip install -r requirements.txt --quiet
python manage.py migrate --noinput
python manage.py collectstatic --noinput

sudo systemctl restart gunicorn-staging
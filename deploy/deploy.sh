#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/improvuser/improvpl"
cd "$APP_DIR"

git fetch origin main
git reset --hard origin/main

mkdir -p "$APP_DIR/media"

source venv/bin/activate
pip install -r requirements.txt --quiet
python manage.py migrate --noinput
python manage.py collectstatic --noinput

sudo systemctl restart gunicorn
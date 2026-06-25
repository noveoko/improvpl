#!/usr/bin/env bash
set -euo pipefail

CRON_LINE='0 9 * * * /home/improvuser/improvpl/venv/bin/python /home/improvuser/improvpl/manage.py close_polls >> /var/log/improvpl_cron.log 2>&1'
MARKER='# improvpl-close-polls'

if crontab -l 2>/dev/null | grep -qF "$MARKER"; then
    echo "Cron job already installed."
    exit 0
fi

(crontab -l 2>/dev/null || true; echo "$MARKER"; echo "$CRON_LINE") | crontab -
echo "Installed daily close_polls cron (09:00 Europe/Warsaw server time)."
crontab -l
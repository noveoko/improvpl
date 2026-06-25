#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: configure-brevo.sh <brevo-smtp-login> <brevo-smtp-key>"
    echo "Get credentials: Brevo → SMTP & API → SMTP keys"
    exit 1
fi

BREVO_LOGIN="$1"
BREVO_KEY="$2"
ENV_FILE="/home/improvuser/improvpl/.env"

set_env() {
    local key="$1"
    local value="$2"
    if grep -q "^${key}=" "$ENV_FILE"; then
        sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
    else
        echo "${key}=${value}" >> "$ENV_FILE"
    fi
}

set_env EMAIL_BACKEND django.core.mail.backends.smtp.EmailBackend
set_env EMAIL_HOST smtp-relay.brevo.com
set_env EMAIL_PORT 587
set_env EMAIL_USE_TLS True
set_env EMAIL_HOST_USER "$BREVO_LOGIN"
set_env EMAIL_HOST_PASSWORD "$BREVO_KEY"
set_env DEFAULT_FROM_EMAIL hello@improv.pl

echo "Brevo SMTP configured in $ENV_FILE"
echo "Restart Gunicorn: sudo systemctl restart gunicorn"
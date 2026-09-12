#!/bin/bash
# Обёртка: грузит пароль админа из файла секретов (не храните пароль в истории shell).
# Использование: bash scripts/smoke_audit.sh [файл-с-паролем]
SECRETS="${1:-$HOME/.openclaw-autoclaw/workspace/projects/keycloak-restore/prod-secrets-20260903.json}"
export SMOKE_BASE_URL="${SMOKE_BASE_URL:-https://audit.netbrainpower.ru}"
export SMOKE_ADMIN_PASSWORD="${SMOKE_ADMIN_PASSWORD:-$(python3 -c "import json,sys; print(json.load(open('$SECRETS'))['platform_admin_password'])")}"
python3 "$(dirname "$0")/smoke_audit.py" "$@"

#!/bin/bash
# Мониторинг источников аудитов и конверсии партнёрских каналов.
# Использование: RESEARCH_TOKEN=<токен research/export-csv> bash scripts/monitor_partners.sh
set -euo pipefail

if [ -z "${RESEARCH_TOKEN:-}" ]; then
  echo "Ошибка: задайте RESEARCH_TOKEN (токен research/export-csv)" >&2
  exit 1
fi

BASE_URL="${BASE_URL:-https://audit.netbrainpower.ru}"
CSV_URL="$BASE_URL/api/v1/admin/research/export-csv?token=$RESEARCH_TOKEN"

echo "=== Мониторинг источников ($(date +%d.%m.%Y\ %H:%M)) ==="
curl -s "$CSV_URL" | tail -n +2 | cut -d, -f7 | sort | uniq -c | sort -rn

echo ""
echo "=== Конверсия партнёрских каналов ==="
curl -s "$CSV_URL" | tail -n +2 | grep "tg_partner" | cut -d, -f7 | sort | uniq -c | sort -rn

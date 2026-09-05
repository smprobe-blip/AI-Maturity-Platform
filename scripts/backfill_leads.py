"""Разовая синхронизация существующих аудитов в Baserow (лиды). Дедуп по Audit ID.

Запуск (внутри контейнера backend):
  docker exec ai-maturity-backend python /app/scripts/backfill_leads.py
Аудиты с source=test*/verify* пропускаются.
"""
import asyncio
import sys

sys.path.insert(0, '/app')

from app.integrations.baserow_client import BaserowClient  # noqa: E402
from app.storage.json_storage import JSONStorage  # noqa: E402


def main() -> int:
    import requests

    client = BaserowClient()
    storage = JSONStorage()
    audits = storage.list_audits(limit=100000)

    r = requests.get(client.api_url + '&size=200', headers={'Authorization': f'Token {client.api_token}', 'Host': 'localhost:3001'}, timeout=15)
    existing = set()
    for row in r.json().get('results', []):
        aid = row.get('Audit ID')
        if aid:
            existing.add(str(aid))

    created = skipped_dup = skipped_test = failed = 0
    for a in audits:
        req_data = a.get('request') or {}
        src = (req_data.get('source') or '').lower()
        aid = a.get('audit_id')
        if src.startswith('test') or src.startswith('verify'):
            skipped_test += 1
            continue
        if aid in existing:
            skipped_dup += 1
            continue
        crm_audit = {
            'audit_id': aid,
            'created_at': a.get('created_at'),
            'contact': {
                'email': req_data.get('contact_email') or '',
                'name': req_data.get('contact_name') or '',
                'position': req_data.get('respondent_role') or '',
            },
            'company_profile': {
                'industry': req_data.get('company_industry') or '',
                'company_size': req_data.get('company_size') or '',
            },
            'request': {
                'company_industry': req_data.get('company_industry') or '',
                'company_size': req_data.get('company_size') or '',
            },
            'calculated_indices': a.get('calculated_indices') or {},
            'source': src or 'unknown',
        }
        try:
            row_id = asyncio.run(client.sync_lead(crm_audit))
            if row_id:
                created += 1
                existing.add(aid)
            else:
                failed += 1
        except Exception as e:
            print(f'  FAIL {aid}: {e}')
            failed += 1

    print(f'итог: создано {created}, дубли/тесты пропущены {skipped_dup + skipped_test} (тестовых {skipped_test}), ошибок {failed}')
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())

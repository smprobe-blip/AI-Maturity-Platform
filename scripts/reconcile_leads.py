"""Сверка лидов CRM с аудитами: удалить сирот, досинхронизировать недостающие.

Запуск (внутри контейнера backend):
  docker exec ai-maturity-backend python /app/scripts/reconcile_leads.py
Аудиты с source=test*/verify* в лиды не синхронизируются (удаляются вручную).
"""
import json
import sys

sys.path.insert(0, '/app')

import requests  # noqa: E402

from app.integrations.baserow_client import BaserowClient  # noqa: E402
from app.storage.json_storage import JSONStorage  # noqa: E402


def main() -> int:
    client = BaserowClient()
    storage = JSONStorage()

    audits = storage.list_audits(limit=100000)
    prod_ids = {a.get('audit_id') for a in audits}

    r = requests.get(client.api_url + '&size=200',
                     headers={'Authorization': f'Token {client.api_token}',
                              'Host': 'localhost:3001'}, timeout=20)
    rows = r.json().get('results', [])

    existing_by_aid = {}
    for row in rows:
        aid = (row.get('Audit ID') or '').strip()
        if aid:
            existing_by_aid[aid] = row['id']

    deleted_orphans = 0
    for aid, row_id in list(existing_by_aid.items()):
        if aid not in prod_ids:
            try:
                d = requests.delete(f'{client.base_url}/api/database/rows/table/{client.leads_table_id}/{row_id}/?user_field_names=true',
                                    headers={'Authorization': f'Token {client.api_token}',
                                             'Host': 'localhost:3001'}, timeout=20)
                if d.status_code in (200, 204):
                    deleted_orphans += 1
                    existing_by_aid.pop(aid, None)
            except Exception as e:
                print(f'  ошибка удаления сироты {aid}: {e}')

    created = 0
    failed = 0
    for a in audits:
        aid = a.get('audit_id')
        if not aid or aid in existing_by_aid:
            continue
        req_data = a.get('request') or {}
        src = (req_data.get('source') or '').lower()
        if src.startswith('test') or src.startswith('verify'):
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
            import asyncio
            row_id = asyncio.run(client.sync_lead(crm_audit))
            if row_id:
                created += 1
            else:
                failed += 1
        except Exception as e:
            print(f'  ошибка синка {aid}: {e}')
            failed += 1

    print(f'итог: сирот удалено {deleted_orphans}, лидов создано {created}, ошибок {failed}')
    print(f'лидов в CRM теперь: {len(existing_by_aid) + created}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

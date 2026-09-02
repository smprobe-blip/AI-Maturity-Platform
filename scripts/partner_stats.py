#!/usr/bin/env python3
"""Статистика партнёрской атрибуции: количество и конверсия завершённых аудитов по src-тегам.

Использование:
  python3 scripts/partner_stats.py [--path PATH] [--json]

Путь по умолчанию — data_storage/raw_audits рядом с backend. Работает и локально, и на VPS.
"""
import argparse
import glob
import json
import os
import sys
from collections import Counter
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser(description='Статистика источников (src-тегов) аудитов')
    ap.add_argument('--path', default=None, help='Каталог data_storage/raw_audits (или его корень)')
    ap.add_argument('--json', action='store_true', help='JSON-вывод')
    args = ap.parse_args()

    base = args.path
    if not base:
        here = Path(__file__).resolve().parent.parent
        base = here / 'backend' / 'data_storage' / 'raw_audits'
    base = Path(base)
    if base.name != 'raw_audits' and (base / 'raw_audits').exists():
        base = base / 'raw_audits'
    if not base.exists():
        print(f'Каталог не найден: {base}', file=sys.stderr)
        return 1

    files = sorted(glob.glob(str(base / '**' / '*.json'), recursive=True))
    counter: Counter = Counter()
    total = 0
    for fp in files:
        try:
            d = json.load(open(fp, encoding='utf-8'))
        except Exception:
            counter['unreadable'] += 1
            continue
        total += 1
        src = (
            (d.get('request') or {}).get('source')
            or (d.get('company_profile') or {}).get('source')
            or 'unknown'
        )
        counter[str(src).strip().lower() or 'unknown'] += 1

    rows = counter.most_common()
    if args.json:
        print(json.dumps({'total': total, 'by_source': dict(rows)}, ensure_ascii=False, indent=2))
        return 0

    print(f'Всего аудитов: {total}   (файлов: {len(files)})')
    print(f'{"Источник":<32}{"Аудитов":>8}{"Доля":>8}')
    print('-' * 48)
    for src, n in rows:
        print(f'{src:<32}{n:>8}{n / total * 100:>7.1f}%')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

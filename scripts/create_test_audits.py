#!/usr/bin/env python3
"""Создание тестовых аудитов для проверки академических расчётов (α, EFA, бенчмарки).

Использование:
  python3 scripts/create_test_audits.py --base-url http://127.0.0.1:8000 --count 6
  python3 scripts/create_test_audits.py --base-url https://audit.netbrainpower.ru --count 8

Все тестовые аудиты помечены source='test_manual' — легко найти/заархивировать в админке.
"""
import argparse
import json
import random
import sys
import urllib.request

PROFILES = [
    ('retail', 'large', 'low'), ('it', 'medium', 'high'), ('finance', 'large', 'mid'),
    ('manufacturing', 'enterprise', 'mid'), ('telecom', 'large', 'high'),
    ('construction', 'medium', 'low'), ('retail', 'medium', 'mid'),
    ('it', 'small', 'low'), ('finance', 'medium', 'high'), ('healthcare', 'large', 'mid'),
    ('logistics', 'medium', 'low'), ('education', 'small', 'mid'),
]

def payload(industry, size, profile, seq):
    rng = random.Random(f'{industry}-{size}-{profile}-{seq}')
    base = {'low': 1.4, 'mid': 2.8, 'high': 4.0}[profile]
    responses = {}
    for dim in range(1, 8):
        scores = []
        for q in range(1, 6):
            v = max(1, min(5, round(base + rng.uniform(-1.2, 1.2))))
            scores.append(float(v))
        responses[str(dim)] = {f'{dim}.{q}': s for q, s in enumerate(scores, 1)}
    return {
        'company_industry': industry, 'company_size': size,
        'contact_email': f'test{seq}@test.netbrainpower.ru', 'contact_name': f'Тест {seq}',
        'report_type': 'express', 'responses': responses,
        'pdn_consent': True, 'respondent_role': 'ceo',
        'company_name': f'Тест-компания {seq}', 'research_consent': True,
        'source': 'test_manual',
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--count', type=int, default=6)
    args = ap.parse_args()
    base = args.base_url.rstrip('/')
    ok = 0
    for i in range(args.count):
        ind, size, prof = PROFILES[i % len(PROFILES)]
        body = json.dumps(payload(ind, size, prof, i + 1)).encode()
        req = urllib.request.Request(f'{base}/api/v1/public/audits/express', data=body,
                                     headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read().decode())
            ci = d['calculated_indices']
            print(f"  [{i+1}] {ind}/{size}/{prof}: {d['audit_id'][:8]} -> {ci['composite_score']:.2f} ({ci['maturity_level']})")
            ok += 1
        except Exception as e:
            print(f"  [{i+1}] {ind}/{size}/{prof}: FAIL {e}")
    print(f'создано: {ok}/{args.count} (source=test_manual)')

if __name__ == '__main__':
    main()

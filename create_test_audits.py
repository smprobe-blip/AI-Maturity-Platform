"""Генератор 5 тестовых аудитов для проверки Page3.
Отправляет nested responses (35 вопросов) в новом формате.
"""
import requests
import random
import json

BASE_URL = 'http://localhost:8000/api/v1/public'

# Тестовые данные: 5 разных компаний с разными профилями зрелости
test_cases = [
    {
        'name': 'Ритейл-Корп',
        'industry': 'retail',
        'size': 'large',
        'report_type': 'executive',
        # Средние баллы по 7 осям (стратегия, люди, инфра, данные, модели, внедрение, R&D)
        'avg_scores': [3.5, 2.8, 4.0, 3.2, 2.5, 3.0, 2.0],
    },
    {
        'name': 'ФинТех Банк',
        'industry': 'finance',
        'size': 'enterprise',
        'report_type': 'comprehensive',
        'avg_scores': [4.2, 3.5, 4.5, 4.0, 3.8, 4.0, 3.5],
    },
    {
        'name': 'Завод Будущего',
        'industry': 'manufacturing',
        'size': 'medium',
        'report_type': 'express',
        'avg_scores': [2.5, 2.0, 3.0, 2.8, 2.2, 2.5, 1.8],
    },
    {
        'name': 'AI-Startup',
        'industry': 'it',
        'size': 'small',
        'report_type': 'executive',
        'avg_scores': [4.0, 4.5, 4.2, 4.0, 4.5, 3.8, 4.0],
    },
    {
        'name': 'Телеком-Оператор',
        'industry': 'telecom',
        'size': 'large',
        'report_type': 'comprehensive',
        'avg_scores': [3.0, 2.5, 3.5, 3.0, 2.8, 3.2, 2.5],
    },
]


def generate_nested_responses(avg_scores):
    """Генерирует nested responses: {dim_id: {q_id: score}} для 35 вопросов."""
    responses = {}
    for dim_idx, avg in enumerate(avg_scores, start=1):
        dim_id = str(dim_idx)
        responses[dim_id] = {}
        for q_id in range(1, 6):
            # Вариация ±0.5 вокруг среднего, с ограничением 1-5
            score = avg + random.uniform(-0.5, 0.5)
            score = max(1.0, min(5.0, round(score, 1)))
            responses[dim_id][str(q_id)] = score
    return responses


print('🚀 Генерация 5 тестовых аудитов...\n')
print(f'📡 Backend: {BASE_URL}')
print(f'🔍 Проверка health...')

# Сначала проверяем health
try:
    health = requests.get(f'{BASE_URL.replace("/api/v1/public", "")}/health', timeout=5)
    print(f'✅ Backend OK: {health.json()}')
except Exception as e:
    print(f'❌ Backend недоступен: {e}')
    print('💡 Запустите: docker compose restart backend')
    exit(1)

print()

created_audits = []

for i, case in enumerate(test_cases, 1):
    responses = generate_nested_responses(case['avg_scores'])
    
    payload = {
        'company_industry': case['industry'],
        'company_size': case['size'],
        'contact_email': f'test{i}@example.com',
        'contact_name': case['name'],
        'report_type': case['report_type'],
        'responses': responses,
        'pdn_consent': True,
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/audits/express',
            json=payload,
            timeout=10,
        )
        
        if response.status_code == 201:
            data = response.json()
            audit_id = data['audit_id']
            composite = data['calculated_indices']['composite_score']
            level = data['calculated_indices']['maturity_level']
            pattern = data['calculated_indices'].get('pattern', {})
            pattern_type = pattern.get('pattern_type', 'N/A') if pattern else 'N/A'
            
            created_audits.append({
                'id': audit_id,
                'name': case['name'],
                'industry': case['industry'],
                'report_type': case['report_type'],
                'composite': composite,
                'level': level,
                'pattern': pattern_type,
            })
            
            print(f'✅ [{i}/5] {case["name"]}')
            print(f'   ID: {audit_id}')
            print(f'   Score: {composite:.2f} | Level: {level} | Pattern: {pattern_type}')
            print(f'   Report: {case["report_type"]}')
            print(f'   URL: http://localhost:3000/results/{audit_id}')
            print()
        else:
            print(f'❌ [{i}/5] Ошибка {response.status_code} для {case["name"]}')
            print(f'   Ответ: {response.text[:300]}')
            print()
    except Exception as e:
        print(f'❌ [{i}/5] Исключение для {case["name"]}: {e}')
        print()

print('=' * 70)
print(f'✅ Создано аудитов: {len(created_audits)}/{len(test_cases)}')
print('=' * 70)

if created_audits:
    print('\n🔗 Прямые ссылки для проверки Page3:')
    for audit in created_audits:
        print(f'   {audit["name"].ljust(20)} http://localhost:3000/results/{audit["id"]}')
    
    print('\n📊 Сводка:')
    print(f'   {"Компания":<20} {"Score":>6} {"Level":<15} {"Pattern":<20} {"Report":<15}')
    print('   ' + '-' * 76)
    for audit in created_audits:
        print(f'   {audit["name"]:<20} {audit["composite"]:>6.2f} {audit["level"]:<15} {audit["pattern"]:<20} {audit["report_type"]:<15}')
else:
    print('\n❌ Ни один аудит не создан. Проверьте логи backend:')
    print('   cd C:\\Projects\\AI-Maturity-Platform\\infrastructure')
    print('   docker compose logs backend --tail=30')
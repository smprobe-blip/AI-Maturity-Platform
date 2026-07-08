import requests
from app.core.config import settings

baserow_url = 'http://baserow:80'
table_id = settings.baserow_leads_table_id
api_token = settings.baserow_api_token

url = baserow_url + '/api/database/rows/table/' + str(table_id) + '/'
headers = {
    'Authorization': 'Token ' + api_token,
    'Content-Type': 'application/json'
}

print('=== DIAGNOSTIC: Testing field by field ===')
print('Table ID:', table_id)
print()

# TEST 1: Только PRIMARY поле (audit_id) — БЕЗ user_field_names
print('--- TEST 1: Only audit_id (no user_field_names) ---')
lead_data = {'audit_id': 'DIAG-001'}
response = requests.post(url, headers=headers, json=lead_data, timeout=10)
print('Status:', response.status_code)
print('Response:', response.text[:300])
print()

# TEST 2: audit_id + name — БЕЗ user_field_names
print('--- TEST 2: audit_id + name (no user_field_names) ---')
lead_data = {'audit_id': 'DIAG-002', 'name': 'Test Company'}
response = requests.post(url, headers=headers, json=lead_data, timeout=10)
print('Status:', response.status_code)
print('Response:', response.text[:300])
print()

# TEST 3: audit_id + email — БЕЗ user_field_names
print('--- TEST 3: audit_id + email (no user_field_names) ---')
lead_data = {'audit_id': 'DIAG-003', 'email': 'test@example.com'}
response = requests.post(url, headers=headers, json=lead_data, timeout=10)
print('Status:', response.status_code)
print('Response:', response.text[:300])
print()

# TEST 4: audit_id + name + email — С user_field_names (только в URL)
print('--- TEST 4: audit_id + name + email (user_field_names in URL only) ---')
url_with_param = url + '?user_field_names=true'
lead_data = {'audit_id': 'DIAG-004', 'name': 'Test 4', 'email': 'test4@example.com'}
response = requests.post(url_with_param, headers=headers, json=lead_data, timeout=10)
print('Status:', response.status_code)
print('Response:', response.text[:300])
print()

# TEST 5: Используя ID полей (field_XXXX)
print('--- TEST 5: Using field IDs (field_4740, field_4745) ---')
lead_data = {'field_4740': 'DIAG-005', 'field_4745': 'Test 5'}
response = requests.post(url, headers=headers, json=lead_data, timeout=10)
print('Status:', response.status_code)
print('Response:', response.text[:300])
print()

# TEST 6: Полный набор через field IDs
print('--- TEST 6: Full data via field IDs ---')
lead_data = {
    'field_4740': 'DIAG-006',      # audit_id
    'field_4744': 'test6@example.com',  # email
    'field_4745': 'Test Company 6',     # name
    'field_4746': 'CEO',                # position
    'field_4747': 'Retail',             # industry
    'field_4748': '100-500',            # company_size
    'field_4749': 'Moscow',             # region
    'field_4750': 3.5,                  # composite_score
    'field_4751': 'Developing',         # maturity_level
    'field_4752': 25,                   # roi_estimate
    'field_4753': 'New',                # status
    'field_4754': '2026-07-08'          # created_at
}
response = requests.post(url, headers=headers, json=lead_data, timeout=10)
print('Status:', response.status_code)
print('Response:', response.text[:500])

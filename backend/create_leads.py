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
params = {'user_field_names': 'true'}

# Test leads (using latin characters first)
test_leads = [
    {
        'audit_id': 'AUD-2026-001',
        'name': 'TechnoStart LLC',
        'email': 'info@technostart.ru',
        'position': 'CEO',
        'industry': 'Retail',
        'company_size': '100-500',
        'region': 'Moscow',
        'composite_score': 3.5,
        'maturity_level': 'Developing',
        'roi_estimate': 25,
        'status': 'New',
        'created_at': '2026-07-08'
    },
    {
        'audit_id': 'AUD-2026-002',
        'name': 'Innovations JSC',
        'email': 'contact@innovations.ru',
        'position': 'CTO',
        'industry': 'Manufacturing',
        'company_size': '500-1000',
        'region': 'Saint Petersburg',
        'composite_score': 4.2,
        'maturity_level': 'Defined',
        'roi_estimate': 35,
        'status': 'New',
        'created_at': '2026-07-08'
    },
    {
        'audit_id': 'AUD-2026-003',
        'name': 'Petrov IP',
        'email': 'petrov@mail.ru',
        'position': 'Owner',
        'industry': 'Services',
        'company_size': '1-50',
        'region': 'Kazan',
        'composite_score': 2.1,
        'maturity_level': 'Initial',
        'roi_estimate': 15,
        'status': 'Contacted',
        'created_at': '2026-07-08'
    },
    {
        'audit_id': 'AUD-2026-004',
        'name': 'DataPro LLC',
        'email': 'hello@datapro.ru',
        'position': 'Data Director',
        'industry': 'IT',
        'company_size': '50-100',
        'region': 'Novosibirsk',
        'composite_score': 4.8,
        'maturity_level': 'Managed',
        'roi_estimate': 45,
        'status': 'Qualified',
        'created_at': '2026-07-08'
    },
    {
        'audit_id': 'AUD-2026-005',
        'name': 'FinansGroup PJSC',
        'email': 'info@finansgroup.ru',
        'position': 'CDO',
        'industry': 'Finance',
        'company_size': '1000+',
        'region': 'Moscow',
        'composite_score': 3.9,
        'maturity_level': 'Defined',
        'roi_estimate': 30,
        'status': 'New',
        'created_at': '2026-07-08'
    }
]

print('=== Creating Leads via Python ===')
print('Table ID:', table_id)
print('Token:', api_token[:20] + '...')
print()

for lead in test_leads:
    response = requests.post(url, headers=headers, params=params, json=lead, timeout=10)
    audit_id = lead.get('audit_id', 'N/A')
    name = lead.get('name', 'N/A')
    
    if response.status_code in (200, 201):
        data = response.json()
        row_id = data.get('id', 'N/A')
        print('✅ Created: ' + audit_id + ' | ' + name + ' | Row ID: ' + str(row_id))
    else:
        print('❌ Error ' + audit_id + ': ' + str(response.status_code))
        print('   Response: ' + response.text[:500])

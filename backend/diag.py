cd C:\projects\ai-maturity-platform

# Создаём файл диагностики
@"
from pathlib import Path
import json

base = Path('/data_storage/raw_audits')
print('=== DIAGNOSTICS ===')
print('Base path exists:', base.exists())
print('Contents:', list(base.iterdir()) if base.exists() else 'N/A')

year = base / '2026'
print('Year 2026 exists:', year.exists())
if year.exists():
    all_files = list(year.glob('*.json'))
    audit_files = list(year.glob('audit_*.json'))
    print('All JSON files:', len(all_files))
    print('Files matching audit_*.json:', len(audit_files))
    if all_files:
        print('First 3 files:', [f.name for f in all_files[:3]])
        with open(all_files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
        print('Keys in first file:', list(data.keys()))
        print('Has audit_id:', 'audit_id' in data)
        print('Status:', data.get('status'))
        
        # Test list_audits
        from app.storage.json_storage import JSONStorage
        s = JSONStorage()
        audits = s.list_audits(limit=100, offset=0)
        print('=== list_audits() returned:', len(audits), 'audits ===')
        if audits:
            print('First audit id:', audits[0].get('audit_id'))
"@ | Out-File -FilePath "diag.py" -Encoding UTF8
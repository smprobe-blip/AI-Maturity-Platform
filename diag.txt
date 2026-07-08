docker-compose exec backend python -c "
from pathlib import Path
from app.storage.json_storage import JSONStorage
import json

s = JSONStorage()
print('Base path:', s.base_path)
print('Exists:', s.base_path.exists())
print('Is dir:', s.base_path.is_dir())
print('Contents:', list(s.base_path.iterdir()) if s.base_path.exists() else 'N/A')

# Проверить год
year_path = s.base_path / '2026'
print('Year path:', year_path)
print('Year exists:', year_path.exists())
if year_path.exists():
    files = list(year_path.glob('audit_*.json'))
    print('Files matching audit_*.json:', len(files))
    if files:
        print('First 3 files:', [f.name for f in files[:3]])
        # Попробовать прочитать первый
        with open(files[0], 'r') as f:
            data = json.load(f)
            print('First audit keys:', list(data.keys()))
            print('Status:', data.get('status'))
"
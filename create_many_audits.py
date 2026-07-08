import httpx
import json
import random

industries = ["Retail", "Finance", "Manufacturing", "Healthcare", "Technology"]
sizes = ["Small (1-50)", "Medium (51-250)", "Large (1000+)", "Enterprise (1000+)"]
regions = ["Moscow", "Saint Petersburg", "Central Russia", "Urals", "Siberia"]

def create_audit(i):
    data = {
        "company_profile": {
            "industry": random.choice(industries),
            "company_size": random.choice(sizes),
            "region": random.choice(regions),
        },
        "contact": {
            "email": f"user{i}@example.com",
            "name": f"User {i}",
            "consent_to_process_data": True,
        },
        "raw_responses": []
    }
    
    # Случайные оценки с некоторой закономерностью
    base_score = random.randint(2, 4)
    for dim_id in range(1, 8):
        for q_id in range(1, 6):
            score = max(1, min(5, base_score + random.randint(-1, 1)))
            data["raw_responses"].append({
                "dimension_id": dim_id,
                "question_id": q_id,
                "score": score,
            })
    
    return data

# Создаём 20 аудитов
for i in range(1, 21):
    audit_data = create_audit(i)
    response = httpx.post(
        "http://localhost:8000/api/v1/public/audits/express",
        json=audit_data,
        timeout=30.0
    )
    result = response.json()
    print(f"[{i}/20] Audit {result.get('audit_id', 'ERROR')[:8]}... | "
          f"Score: {result.get('calculated_indices', {}).get('composite_score', 'N/A')} | "
          f"Level: {result.get('calculated_indices', {}).get('maturity_level', 'N/A')}")
"""
Генерация демо-данных с полными raw_responses (35 ответов)
"""
import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Конфигурация
DATA_STORAGE_PATH = Path("/data_storage")
RAW_AUDITS_PATH = DATA_STORAGE_PATH / "raw_audits"

# Создаем папку по текущему году
year = datetime.now().year
YEAR_PATH = RAW_AUDITS_PATH / str(year)
YEAR_PATH.mkdir(parents=True, exist_ok=True)

# Данные компаний
COMPANIES = [
    {"industry": "Retail", "company_size": "Medium (51-250)", "region": "Moscow"},
    {"industry": "Finance", "company_size": "Large (251-1000)", "region": "Moscow"},
    {"industry": "IT", "company_size": "Small (1-50)", "region": "Saint Petersburg"},
    {"industry": "Manufacturing", "company_size": "Large (251-1000)", "region": "Yekaterinburg"},
    {"industry": "Healthcare", "company_size": "Medium (51-250)", "region": "Novosibirsk"},
    {"industry": "Services", "company_size": "Small (1-50)", "region": "Kazan"},
    {"industry": "Retail", "company_size": "Large (251-1000)", "region": "Moscow"},
    {"industry": "Finance", "company_size": "Medium (51-250)", "region": "Saint Petersburg"},
    {"industry": "IT", "company_size": "Large (251-1000)", "region": "Moscow"},
    {"industry": "Manufacturing", "company_size": "Small (1-50)", "region": "Nizhny Novgorod"},
]

CONTACTS = [
    {"email": "ivanov@techprogress.ru", "name": "Иванов А.П.", "position": "CTO"},
    {"email": "petrova@innovations.ru", "name": "Петрова С.М.", "position": "CEO"},
    {"email": "sidorov@digitaltech.ru", "name": "Сидоров К.В.", "position": "CDO"},
    {"email": "kozlova@smartindustry.ru", "name": "Козлова Е.А.", "position": "CIO"},
    {"email": "novikov@datadrive.ru", "name": "Новиков Д.Р.", "position": "Head of AI"},
]

# 7 измерений (dimension_id: 1-7)
DIMENSIONS = {
    1: "strategy",
    2: "people", 
    3: "infrastructure",
    4: "data",
    5: "models",
    6: "implementation",
    7: "rnd"
}

def generate_raw_responses():
    """
    Генерация 35 сырых ответов (7 измерений × 5 вопросов)
    Формат соответствует RawResponse модели:
    - dimension_id: 1-7
    - question_id: 1-5
    - score: 1-5
    - time_to_answer_sec: float
    - confidence_level: 1-5
    """
    raw_responses = []
    
    for dimension_id in range(1, 8):  # 1-7
        for question_id in range(1, 6):  # 1-5
            response = {
                "dimension_id": dimension_id,
                "question_id": question_id,
                "score": random.randint(1, 5),  # Оценка 1-5
                "time_to_answer_sec": round(random.uniform(5.0, 60.0), 2),  # Время 5-60 сек
                "confidence_level": random.randint(2, 5)  # Уверенность 2-5
            }
            raw_responses.append(response)
    
    return raw_responses

def calculate_dimension_scores(raw_responses):
    """Расчет средних оценок по каждому измерению"""
    dimension_scores = {}
    
    for dim_id, dim_name in DIMENSIONS.items():
        # Получаем все ответы для этого измерения
        dim_responses = [r for r in raw_responses if r["dimension_id"] == dim_id]
        # Считаем среднюю оценку
        avg_score = sum(r["score"] for r in dim_responses) / len(dim_responses)
        dimension_scores[dim_name] = round(avg_score, 2)
    
    return dimension_scores

def calculate_composite_score(dimension_scores):
    """Расчет composite score (среднее по всем измерениям)"""
    return round(sum(dimension_scores.values()) / len(dimension_scores), 2)

def get_maturity_level(composite_score):
    """Определение уровня зрелости (шкала 1-5)"""
    if composite_score >= 4.3:
        return "L5 — AI-Native"
    elif composite_score >= 3.5:
        return "L4 — AI-First"
    elif composite_score >= 2.7:
        return "L3 — AI-Driven"
    elif composite_score >= 1.9:
        return "L2 — AI-Enabled"
    else:
        return "L1 — Initial"

def generate_audit_data(audit_num: int, company: dict, contact: dict):
    """Генерация данных одного аудита с полными raw_responses"""
    # Генерируем UUID
    audit_id = str(uuid.uuid4())
    
    # Генерируем 35 сырых ответов
    raw_responses = generate_raw_responses()
    
    # Рассчитываем оценки по измерениям на основе raw_responses
    dimension_scores = calculate_dimension_scores(raw_responses)
    
    # Расчет composite score
    composite_score = calculate_composite_score(dimension_scores)
    
    # Определение уровня зрелости
    maturity_level = get_maturity_level(composite_score)
    
    # Дата создания
    created_at = datetime.now() - timedelta(days=random.randint(0, 365))
    created_at_iso = created_at.isoformat()
    
    # Формируем структуру аудита
    audit_data = {
        "audit_id": audit_id,
        "created_at": created_at_iso,
        "updated_at": created_at_iso,
        "audit_type": "express",
        "status": "completed",
        "company_profile": {
            "industry": company["industry"],
            "company_size": company["company_size"],
            "region": company["region"]
        },
        "contact": {
            "email": contact["email"],
            "name": contact["name"],
            "position": contact["position"],
            "consent_to_process_data": True
        },
        "raw_responses": raw_responses,  # 35 ответов!
        "calculated_indices": {
            "composite_score": composite_score,
            "maturity_level": maturity_level,
            "dimension_scores": dimension_scores,
            "roi_estimate_percent": round(random.uniform(5, 25), 2),
            "tco_estimate_millions": round(random.uniform(1, 10), 2)
        },
        "audit_events": [
            {
                "event": "audit_created",
                "timestamp": created_at_iso,
                "user": "demo_generator"
            }
        ]
    }
    
    return audit_data

def generate_demo_data(num_audits: int = 30):
    """Генерация всех демо-данных"""
    print(f" Генерация {num_audits} аудитов с полными данными...")
    print(f" Папка: {YEAR_PATH}")
    
    audits = []
    total_responses = 0
    
    for i in range(1, num_audits + 1):
        company = random.choice(COMPANIES)
        contact = random.choice(CONTACTS)
        
        audit = generate_audit_data(i, company, contact)
        audits.append(audit)
        
        # Сохранение в правильном формате
        file_path = YEAR_PATH / f"audit_{audit['audit_id']}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(audit, f, ensure_ascii=False, indent=2)
        
        total_responses += len(audit["raw_responses"])
        print(f"  ✅ {i}/{num_audits}: {audit['audit_id'][:8]}... ({len(audit['raw_responses'])} ответов)")
    
    print(f"\n✅ Сгенерировано {num_audits} аудитов")
    print(f"📊 Всего сырых ответов: {total_responses}")
    print(f"📈 Средняя зрелость: {sum(a['calculated_indices']['composite_score'] for a in audits) / len(audits):.2f}")
    
    return audits

if __name__ == "__main__":
    generate_demo_data(30)

#!/usr/bin/env python3
"""Seed demo data for testing and demonstration."""

import json
import uuid
from datetime import datetime
from pathlib import Path

# Demo companies
DEMO_COMPANIES = [
    {
        "industry": "Retail",
        "company_size": "Large (1000+)",
        "region": "Moscow",
        "ai_experience_years": 3,
    },
    {
        "industry": "Finance",
        "company_size": "Enterprise (1000+)",
        "region": "Saint Petersburg",
        "ai_experience_years": 5,
    },
    {
        "industry": "Manufacturing",
        "company_size": "Medium (51-250)",
        "region": "Central Russia",
        "ai_experience_years": 1,
    },
    {
        "industry": "Healthcare",
        "company_size": "Large (1000+)",
        "region": "Moscow",
        "ai_experience_years": 2,
    },
    {
        "industry": "Technology",
        "company_size": "Small (1-50)",
        "region": "Moscow",
        "ai_experience_years": 4,
    },
]


def generate_raw_responses(base_score: int = 3) -> list:
    """Generate 35 raw responses with some variance."""
    import random
    
    responses = []
    for dim_id in range(1, 8):
        for q_id in range(1, 6):
            # Add some variance around base score
            score = max(1, min(5, base_score + random.randint(-1, 1)))
            responses.append({
                "dimension_id": dim_id,
                "question_id": q_id,
                "score": score,
                "time_to_answer_sec": round(random.uniform(10, 30), 1),
                "confidence_level": random.randint(3, 5),
            })
    
    return responses


def calculate_indices(responses: list) -> dict:
    """Calculate maturity indices."""
    # Dimension weights
    weights = {1: 0.15, 2: 0.15, 3: 0.15, 4: 0.15, 5: 0.15, 6: 0.20, 7: 0.05}
    
    # Calculate averages
    dimension_scores = {}
    for dim_id in range(1, 8):
        dim_responses = [r["score"] for r in responses if r["dimension_id"] == dim_id]
        dimension_scores[str(dim_id)] = sum(dim_responses) / len(dim_responses)
    
    # Composite score
    composite = sum(dimension_scores[str(d)] * weights[d] for d in range(1, 8))
    
    # Maturity level
    if composite < 1.5:
        level = "L1 — Initial"
    elif composite < 2.5:
        level = "L2 — Developing"
    elif composite < 3.5:
        level = "L3 — Defined"
    elif composite < 4.5:
        level = "L4 — Managed"
    else:
        level = "L5 — Optimizing"
    
    return {
        "dimension_scores": dimension_scores,
        "composite_score": round(composite, 2),
        "maturity_level": level,
        "roi_estimate_percent": round(max(0, (composite - 1.0) * 100), 1),
        "tco_estimate_millions": round(max(5.0, composite * 15.0), 2),
    }


def seed_demo_data():
    """Generate demo audit data."""
    data_dir = Path("data_storage/raw_audits/2026")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🌱 Seeding demo data to {data_dir}...")
    
    for i, company in enumerate(DEMO_COMPANIES):
        audit_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        # Generate responses with different maturity levels
        base_scores = [2, 3, 4, 3, 5]  # Different maturity levels
        responses = generate_raw_responses(base_scores[i % len(base_scores)])
        
        audit_data = {
            "audit_id": audit_id,
            "created_at": created_at,
            "updated_at": created_at,
            "audit_type": "express",
            "status": "completed",
            "company_profile": company,
            "contact": {
                "email": f"demo{i+1}@example.com",
                "name": f"Demo User {i+1}",
                "position": "CTO",
                "consent_to_process_data": True,
            },
            "raw_responses": responses,
            "calculated_indices": calculate_indices(responses),
            "audit_events": [
                {
                    "event": "audit_created",
                    "timestamp": created_at,
                    "user": "system",
                }
            ],
        }
        
        # Save to file
        file_path = data_dir / f"audit_{audit_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(audit_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Created audit {audit_id[:8]}... ({company['industry']})")
    
    print(f"\n✅ Seeded {len(DEMO_COMPANIES)} demo audits")


if __name__ == "__main__":
    seed_demo_data()
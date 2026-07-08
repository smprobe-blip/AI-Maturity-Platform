"""Integration tests for full assessment flow."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestFullAssessmentFlow:
    """End-to-end integration tests."""
    
    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(app)
    
    def test_complete_assessment_flow(self, client: TestClient):
        """Test complete flow: create → retrieve → email."""
        # Step 1: Create express audit
        create_data = {
            "company_profile": {
                "industry": "Retail",
                "company_size": "Large (1000+)",
                "region": "Moscow",
            },
            "contact": {
                "email": "integration-test@example.com",
                "name": "Integration Test",
                "consent_to_process_data": True,
            },
            "raw_responses": [
                {
                    "dimension_id": dim_id,
                    "question_id": q_id,
                    "score": 4,
                }
                for dim_id in range(1, 8)
                for q_id in range(1, 6)
            ],
        }
        
        response = client.post("/api/v1/public/audits/express", json=create_data)
        assert response.status_code == 201
        
        audit_data = response.json()
        audit_id = audit_data["audit_id"]
        
        # Verify response structure
        assert "calculated_indices" in audit_data
        assert audit_data["calculated_indices"]["composite_score"] > 0
        assert audit_data["calculated_indices"]["maturity_level"] in [
            "L1 — Initial",
            "L2 — Developing",
            "L3 — Defined",
            "L4 — Managed",
            "L5 — Optimizing",
        ]
        
        # Step 2: Retrieve audit
        response = client.get(f"/api/v1/public/audits/{audit_id}")
        assert response.status_code == 200
        
        retrieved = response.json()
        assert retrieved["audit_id"] == audit_id
        assert retrieved["status"] == "completed"
        assert len(retrieved["raw_responses"]) == 35
        
        # Step 3: Send email (mock SMTP)
        response = client.post(
            f"/api/v1/public/audits/{audit_id}/email",
            json={"email": "integration-test@example.com"},
        )
        assert response.status_code == 200
    
    def test_multiple_audits_same_industry(self, client: TestClient):
        """Test creating multiple audits for same industry."""
        for i in range(3):
            data = {
                "company_profile": {
                    "industry": "Finance",
                    "company_size": "Medium (51-250)",
                    "region": "Saint Petersburg",
                },
                "contact": {
                    "email": f"finance{i}@example.com",
                    "consent_to_process_data": True,
                },
                "raw_responses": [
                    {
                        "dimension_id": dim_id,
                        "question_id": q_id,
                        "score": 3 + (i % 2),
                    }
                    for dim_id in range(1, 8)
                    for q_id in range(1, 6)
                ],
            }
            
            response = client.post("/api/v1/public/audits/express", json=data)
            assert response.status_code == 201
    
    def test_benchmark_retrieval(self, client: TestClient):
        """Test retrieving industry benchmarks."""
        industries = ["Retail", "Finance", "Manufacturing"]
        
        for industry in industries:
            response = client.get(f"/api/v1/public/benchmarks/{industry}")
            assert response.status_code == 200
            
            benchmark = response.json()
            assert benchmark["industry"] == industry
            assert "average_score" in benchmark
            assert "sample_size" in benchmark
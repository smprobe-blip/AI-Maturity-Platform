"""Tests for Public API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestPublicAPI:
    """Tests for Public API."""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """FastAPI test client."""
        return TestClient(app)
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
    
    def test_create_express_audit(
        self, client: TestClient, sample_audit_express_data: dict
    ):
        """Test creating express audit."""
        response = client.post("/api/v1/public/audits/express", json=sample_audit_express_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "audit_id" in data
        assert "calculated_indices" in data
        assert data["calculated_indices"]["composite_score"] >= 0
    
    def test_create_express_audit_invalid_data(self, client: TestClient):
        """Test creating express audit with invalid data."""
        invalid_data = {
            "company_profile": {},
            "contact": {},
            "raw_responses": [],
        }
        response = client.post("/api/v1/public/audits/express", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_audit_not_found(self, client: TestClient):
        """Test getting non-existent audit."""
        response = client.get("/api/v1/public/audits/non-existent-id")
        assert response.status_code == 404
    
    def test_get_industry_benchmark(self, client: TestClient):
        """Test getting industry benchmark."""
        response = client.get("/api/v1/public/benchmarks/Retail")
        assert response.status_code == 200
        data = response.json()
        assert data["industry"] == "Retail"
        assert "average_score" in data


# Import app at module level
from app.main import app
"""Tests for Admin API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def admin_client() -> TestClient:
    """Test client with admin auth header."""
    return TestClient(app, headers={"Authorization": "Bearer dev-token"})


@pytest.fixture
def unauthorized_client() -> TestClient:
    """Test client without auth."""
    return TestClient(app)


class TestAdminAuth:
    """Test authentication and RBAC."""

    def test_unauthorized_access(self, unauthorized_client: TestClient):
        """Test that unauthenticated requests are rejected."""
        response = unauthorized_client.get("/api/v1/admin/audits")
        assert response.status_code == 401

    def test_dev_token_access(self, admin_client: TestClient):
        """Test that dev token works for admin endpoints."""
        response = admin_client.get("/api/v1/admin/audits")
        assert response.status_code == 200


class TestAdminAudits:
    """Test admin audit endpoints."""

    def test_list_audits(self, admin_client: TestClient):
        """Test listing audits."""
        response = admin_client.get("/api/v1/admin/audits")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_audits_with_filters(self, admin_client: TestClient):
        """Test listing audits with filters."""
        response = admin_client.get(
            "/api/v1/admin/audits?industry=Retail&limit=10"
        )
        assert response.status_code == 200

    def test_get_audit_not_found(self, admin_client: TestClient):
        """Test getting non-existent audit."""
        response = admin_client.get("/api/v1/admin/audits/non-existent")
        assert response.status_code == 404


class TestAdminBenchmarks:
    """Test benchmark endpoints."""

    def test_list_benchmarks(self, admin_client: TestClient):
        """Test listing benchmarks."""
        response = admin_client.get("/api/v1/admin/benchmarks")
        assert response.status_code == 200

    def test_recalculate_benchmarks(self, admin_client: TestClient):
        """Test recalculating benchmarks."""
        response = admin_client.post("/api/v1/admin/benchmarks/recalculate")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_get_percentile(self, admin_client: TestClient):
        """Test percentile calculation."""
        response = admin_client.get(
            "/api/v1/admin/benchmarks/Retail/percentile?score=3.5"
        )
        assert response.status_code == 200
        data = response.json()
        assert "percentile" in data


class TestAdminDashboard:
    """Test dashboard endpoints."""

    def test_business_dashboard(self, admin_client: TestClient):
        """Test business metrics."""
        response = admin_client.get("/api/v1/admin/dashboard/business")
        assert response.status_code == 200
        data = response.json()
        assert "total_audits" in data
        assert "average_maturity_score" in data

    def test_scientific_dashboard(self, admin_client: TestClient):
        """Test scientific metrics."""
        response = admin_client.get("/api/v1/admin/dashboard/scientific")
        assert response.status_code == 200
        data = response.json()
        assert "sample_size" in data

    def test_operations_dashboard(self, admin_client: TestClient):
        """Test operations metrics."""
        response = admin_client.get("/api/v1/admin/dashboard/operations")
        assert response.status_code == 200

    def test_quality_dashboard(self, admin_client: TestClient):
        """Test quality metrics."""
        response = admin_client.get("/api/v1/admin/dashboard/quality")
        assert response.status_code == 200
        data = response.json()
        assert "total_records" in data
        assert "completeness_rate" in data


class TestAdminExports:
    """Test export endpoints."""

    def test_create_export_no_nda(self, admin_client: TestClient):
        """Test that raw export without NDA is rejected."""
        response = admin_client.post(
            "/api/v1/admin/exports",
            json={
                "export_type": "audits_raw",
                "format": "csv",
                "nda_signed": False,
            },
        )
        assert response.status_code == 403

    def test_create_export_with_nda(self, admin_client: TestClient):
        """Test export creation with NDA."""
        response = admin_client.post(
            "/api/v1/admin/exports",
            json={
                "export_type": "audits_raw",
                "format": "csv",
                "nda_signed": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "export_id" in data
        assert data["status"] == "completed"

    def test_export_history(self, admin_client: TestClient):
        """Test export history."""
        response = admin_client.get("/api/v1/admin/exports/history")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


class TestAdminSettings:
    """Test settings endpoints."""

    def test_get_methodology(self, admin_client: TestClient):
        """Test getting methodology."""
        response = admin_client.get("/api/v1/admin/settings/methodology")
        assert response.status_code == 200
        data = response.json()
        assert "weights" in data
        assert "maturity_levels" in data

    def test_update_methodology(self, admin_client: TestClient):
        """Test updating methodology."""
        response = admin_client.put(
            "/api/v1/admin/settings/methodology",
            json={
                "weights": {
                    "1": 0.15,
                    "2": 0.15,
                    "3": 0.15,
                    "4": 0.15,
                    "5": 0.15,
                    "6": 0.20,
                    "7": 0.05,
                }
            },
        )
        assert response.status_code == 200

    def test_invalid_weights(self, admin_client: TestClient):
        """Test that invalid weights are rejected."""
        response = admin_client.put(
            "/api/v1/admin/settings/methodology",
            json={"weights": {"1": 0.5, "2": 0.5}},
        )
        assert response.status_code == 400

    def test_get_integrations(self, admin_client: TestClient):
        """Test getting integration settings."""
        response = admin_client.get("/api/v1/admin/settings/integrations")
        assert response.status_code == 200


class TestAuditLog:
    """Test audit log endpoint."""

    def test_get_audit_log(self, admin_client: TestClient):
        """Test retrieving audit log."""
        response = admin_client.get("/api/v1/admin/audit-log")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
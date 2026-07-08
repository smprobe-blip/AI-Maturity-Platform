"""Pytest fixtures for backend tests."""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage.json_storage import JSONStorage
from app.storage.parquet_storage import ParquetStorage
from app.storage.s3_client import S3Client


@pytest.fixture(scope="session")
def test_data_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test data."""
    temp_dir = Path(tempfile.mkdtemp(prefix="ai_maturity_test_"))
    yield temp_dir
    
    # Cleanup after tests
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def json_storage(test_data_dir: Path) -> JSONStorage:
    """JSON storage fixture with temp directory."""
    storage_path = test_data_dir / "raw_audits"
    return JSONStorage(base_path=str(storage_path))


@pytest.fixture
def parquet_storage(test_data_dir: Path) -> ParquetStorage:
    """Parquet storage fixture with temp directory."""
    storage_path = test_data_dir / "aggregated"
    return ParquetStorage(base_path=str(storage_path))


@pytest.fixture
def s3_client() -> S3Client:
    """S3 client fixture (uses MinIO in docker-compose)."""
    # For unit tests, we'll mock S3 calls
    # For integration tests, use real MinIO
    return S3Client(
        endpoint_url="http://localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        bucket_name="test-bucket",
        region_name="ru-central1",
    )


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_raw_responses() -> list:
    """Sample raw responses for testing (35 responses)."""
    responses = []
    for dim_id in range(1, 8):
        for q_id in range(1, 6):
            responses.append({
                "dimension_id": dim_id,
                "question_id": q_id,
                "score": 3,
                "time_to_answer_sec": 15.5,
                "confidence_level": 4,
            })
    return responses


@pytest.fixture
def sample_company_profile() -> dict:
    """Sample company profile."""
    return {
        "industry": "Retail",
        "company_size": "Large (1000+)",
        "region": "Russia",
        "ai_experience_years": 2,
        "annual_it_budget_millions": 50.0,
    }


@pytest.fixture
def sample_contact() -> dict:
    """Sample contact info."""
    return {
        "email": "test@example.com",
        "name": "John Doe",
        "position": "CTO",
        "phone": "+7 999 123-45-67",
        "consent_to_process_data": True,
    }


@pytest.fixture
def sample_audit_express_data(
    sample_raw_responses: list,
    sample_company_profile: dict,
    sample_contact: dict,
) -> dict:
    """Sample express audit creation data."""
    return {
        "company_profile": sample_company_profile,
        "contact": sample_contact,
        "raw_responses": sample_raw_responses,
    }
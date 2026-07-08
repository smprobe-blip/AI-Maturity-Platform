"""Application configuration."""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_NAME: str = "AI Maturity Platform"
    APP_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"
    
    # Алиасы в нижнем регистре для совместимости
    app_env: str = "development"
    app_debug: bool = True
    app_name: str = "AI Maturity Platform"
    app_version: str = "1.0.0"
    log_level: str = "INFO"
    
    # Backend
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_cors_origins: str = "http://localhost:3000,http://localhost:8000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
    
    # Yandex S3 / MinIO
    YANDEX_S3_ENDPOINT: str = "http://minio:9000"
    YANDEX_S3_ACCESS_KEY: str = "minioadmin"
    YANDEX_S3_SECRET_KEY: str = "minioadmin"
    YANDEX_S3_BUCKET: str = "ai-maturity-data"
    YANDEX_S3_REGION: str = "ru-central1"
    
    # SMTP (MailHog)
    SMTP_HOST: str = "mailhog"
    SMTP_PORT: int = 1025
    SMTP_USER: str = "test"
    SMTP_PASSWORD: str = "test"
    SMTP_FROM_EMAIL: str = "noreply@ai-maturity.local"
    SMTP_FROM_NAME: str = "AI Maturity Platform"

    # SMTP Settings (lowercase for Pydantic case-insensitive access)
    smtp_host: str = "mailhog"
    smtp_port: int = 1025
    smtp_user: str = "test"
    smtp_password: str = "test"
    smtp_from_email: str = "noreply@ai-maturity.local"
    smtp_use_tls: bool = False
    
    # Baserow Settings
    baserow_api_token: str = "CE49jfknihUgaVqxJDUPqUXixc8hrsmx"
    baserow_leads_table_id: int = 511

    
    # Baserow
    BASEROW_URL: str = "http://baserow:80"
    BASEROW_API_TOKEN: str = ""
    BASEROW_LEADS_TABLE_ID: int = 511
    
    # Keycloak
    KEYCLOAK_URL: str = "http://keycloak:8080"
    KEYCLOAK_REALM: str = "ai-maturity"
    KEYCLOAK_CLIENT_ID: str = "backend-api"
    KEYCLOAK_CLIENT_SECRET: str = ""
    KEYCLOAK_JWKS_URL: str = "http://keycloak:8080/realms/ai-maturity/protocol/openid-connect/certs"
    
    # Data storage paths
    DATA_STORAGE_PATH: str = "/data_storage"
    RAW_AUDITS_PATH: str = "/data_storage/raw_audits"
    AGGREGATED_PATH: str = "/data_storage/aggregated"
    REPORTS_PATH: str = "/data_storage/reports"
    EXPORTS_PATH: str = "/data_storage/exports"
    LOGS_PATH: str = "/data_storage/logs"

    # Алиасы в нижнем регистре для совместимости
    data_storage_path: str = "/data_storage"
    raw_audits_path: str = "/data_storage/raw_audits"
    aggregated_path: str = "/data_storage/aggregated"
    reports_path: str = "/data_storage/reports"
    exports_path: str = "/data_storage/exports"
    logs_path: str = "/data_storage/logs"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


settings = Settings()

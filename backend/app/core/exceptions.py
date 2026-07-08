"""Custom exceptions and exception handlers."""

from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger()


class AppException(Exception):
    """Base application exception."""
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class AuditNotFoundException(AppException):
    """Raised when audit is not found."""
    
    def __init__(self, audit_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="AUDIT_NOT_FOUND",
            message=f"Audit with id '{audit_id}' not found",
            details={"audit_id": audit_id},
        )


class InvalidAuditDataException(AppException):
    """Raised when audit data is invalid."""
    
    def __init__(self, details: Dict[str, Any]):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_AUDIT_DATA",
            message="Invalid audit data provided",
            details=details,
        )


class StorageException(AppException):
    """Raised when storage operation fails."""
    
    def __init__(self, operation: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="STORAGE_ERROR",
            message=f"Storage operation failed: {operation}",
            details=details or {},
        )


class IntegrationException(AppException):
    """Raised when external integration fails."""
    
    def __init__(self, service: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="INTEGRATION_ERROR",
            message=f"Integration with {service} failed",
            details=details or {},
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom AppException."""
    logger.error(
        "app_exception",
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    logger.warning(
        "validation_error",
        errors=exc.errors(),
        body=str(exc.body),
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": exc.errors()},
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.exception("unhandled_exception", exc_info=exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {},
            }
        },
    )
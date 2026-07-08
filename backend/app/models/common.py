"""Common models used across the application."""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: Dict[str, Any] = Field(
        ...,
        description="Error details",
        examples=[
            {
                "code": "AUDIT_NOT_FOUND",
                "message": "Audit with id 'xxx' not found",
                "details": {},
            }
        ],
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Health status", examples=["healthy"])
    version: str = Field(..., description="Application version")
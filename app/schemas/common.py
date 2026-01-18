from datetime import datetime, timezone
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class MetaInfo(BaseModel):
    """Metadata for API responses"""

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper with data and meta"""

    data: T
    meta: MetaInfo = Field(default_factory=MetaInfo)


class ErrorDetail(BaseModel):
    """Error detail structure"""

    code: str
    message: str
    detail: Optional[str] = None


class ApiError(BaseModel):
    """Standard API error response"""

    error: ErrorDetail

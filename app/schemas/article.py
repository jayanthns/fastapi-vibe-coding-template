from datetime import datetime, timezone
from typing import Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

# Generic response wrapper
T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper with extra fields"""

    success: bool = True
    message: str = "Success"
    status_code: int = 200
    data: T | None = None
    error: str | None = None
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create_with_trace_id(
        cls,
        data: T | None = None,
        message: str = "Success",
        status_code: int = 200,
        success: bool = True,
        error: str | None = None,
        trace_id: str | None = None,
    ) -> "APIResponse[T]":
        """
        Create APIResponse with a specific trace_id (from request middleware).

        Usage:
            from app.middleware.trace import get_trace_id

            @router.get("/")
            async def endpoint(request: Request):
                trace_id = get_trace_id(request)
                return APIResponse.create_with_trace_id(
                    data=some_data,
                    message="Success",
                    trace_id=trace_id
                )
        """
        return cls(
            success=success,
            message=message,
            status_code=status_code,
            data=data,
            error=error,
            trace_id=trace_id or str(uuid4()),
            timestamp=datetime.now(timezone.utc),
        )


class ArticleBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = None


class ArticleInDBBase(ArticleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class Article(ArticleInDBBase):
    pass

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PageParams:
    """
    Dependency for pagination parameters.
    """

    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of items to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    ):
        self.skip = skip
        self.limit = limit


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic schema for paginated responses.
    """

    items: list[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: list[T], total: int, params: PageParams) -> "PaginatedResponse[T]":
        pages = (total + params.limit - 1) // params.limit if params.limit > 0 else 0
        page = (params.skip // params.limit) + 1 if params.limit > 0 else 1

        return cls(
            items=items,
            total=total,
            page=page,
            size=params.limit,
            pages=pages,
        )

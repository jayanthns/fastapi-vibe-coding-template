from datetime import datetime

from pydantic import BaseModel, Field


class ArticleBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = None


class ArticleInDBBase(ArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class Article(ArticleInDBBase):
    pass

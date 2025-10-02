from typing import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.articles.models import Article
from src.apps.articles.repository import article_repository
from src.apps.articles.schemas import ArticleCreate, ArticleUpdate


class ArticleService:
    async def create_article(self, db: AsyncSession, payload: ArticleCreate) -> Article:
        return await article_repository.create(
            db, title=payload.title, content=payload.content
        )

    async def get_article(self, db: AsyncSession, article_id: UUID) -> Article | None:
        return await article_repository.get(db, article_id)

    async def list_articles(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Sequence[Article]:
        return await article_repository.list(db, skip=skip, limit=limit)

    async def update_article(
        self, db: AsyncSession, article_id: UUID, payload: ArticleUpdate
    ) -> Article | None:
        return await article_repository.update(
            db, article_id, title=payload.title, content=payload.content
        )

    async def delete_article(self, db: AsyncSession, article_id: UUID) -> bool:
        return await article_repository.delete(db, article_id)


article_service = ArticleService()

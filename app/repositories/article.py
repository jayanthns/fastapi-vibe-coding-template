from typing import Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article


class ArticleRepository:
    async def create(self, db: AsyncSession, *, title: str, content: str) -> Article:
        article = Article(title=title, content=content)
        db.add(article)
        await db.commit()
        await db.refresh(article)
        return article

    async def get(self, db: AsyncSession, article_id: int) -> Article | None:
        result = await db.execute(select(Article).where(Article.id == article_id))
        return result.scalar_one_or_none()

    async def list(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> Sequence[Article]:
        result = await db.execute(
            select(Article)
            .order_by(Article.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        article_id: int,
        *,
        title: str | None,
        content: str | None
    ) -> Article | None:
        values: dict[str, object] = {}
        if title is not None:
            values["title"] = title
        if content is not None:
            values["content"] = content
        if not values:
            return await self.get(db, article_id)
        await db.execute(
            update(Article).where(Article.id == article_id).values(**values)
        )
        await db.commit()
        return await self.get(db, article_id)

    async def delete(self, db: AsyncSession, article_id: int) -> bool:
        result = await db.execute(delete(Article).where(Article.id == article_id))
        await db.commit()
        return result.rowcount > 0


article_repository = ArticleRepository()

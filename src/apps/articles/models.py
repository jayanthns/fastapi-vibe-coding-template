"""
Article model for blog posts and content management.
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.apps.base_models import BaseModel


class Article(BaseModel):
    """
    Article model for blog posts and content management.

    Extends BaseModel to inherit:
    - UUID primary key (id)
    - Created and updated timestamps (created_at, updated_at)
    - Automatic table naming (articles)
    - Common utility methods
    """

    # Article-specific fields
    title: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="Title of the article"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Main content of the article"
    )

    def __repr__(self) -> str:
        """Generate a string representation of the article."""
        return (
            f"<Article(id={self.id}, title='{self.title[:50]}...', "
            f"created_at={self.created_at})>"
        )

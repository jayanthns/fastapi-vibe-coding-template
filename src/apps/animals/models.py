"""
Animal database models.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models import UUIDModel
from src.db.session import Base


class Animal(Base, UUIDModel):
    """Animal model for storing animal information."""

    __tablename__ = "animals"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    species: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<Animal(id={self.id}, name={self.name}, species={self.species})>"

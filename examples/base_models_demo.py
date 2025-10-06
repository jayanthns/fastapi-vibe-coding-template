#!/usr/bin/env python3
"""
Demo script showing how to use the new base model classes.

This script demonstrates:
- BaseModel with common fields (id, created_at, updated_at)
- TimestampedModel for custom primary keys
- SoftDeleteModel for soft delete functionality
- AuditModel for audit trail capabilities
- Automatic table naming
- Utility methods
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.apps.base_models import (
    AuditModel,
    BaseModel,
    SoftDeleteModel,
    TimestampedModel,
)


# Example 1: Basic model using BaseModel
class BlogPost(BaseModel):
    """
    Blog post model using BaseModel.

    Automatically gets:
    - UUID primary key (id)
    - Created and updated timestamps
    - Table name: blog_posts
    - Utility methods
    """

    title: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Title of the blog post"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Content of the blog post"
    )
    author_id: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="ID of the author"
    )

    def __repr__(self) -> str:
        return f"<BlogPost(id={self.id}, title='{self.title[:30]}...')>"


# Example 2: Model with custom primary key using TimestampedModel
class Category(TimestampedModel):
    """
    Category model with custom primary key.

    Gets timestamps but allows custom primary key definition.
    """

    __tablename__ = "categories"

    # Custom primary key
    code: Mapped[str] = mapped_column(
        String(10), primary_key=True, comment="Category code (e.g., 'TECH', 'SPORTS')"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Category name"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Category description"
    )


# Example 3: Model with soft delete functionality
class Comment(SoftDeleteModel):
    """
    Comment model with soft delete capabilities.

    Extends BaseModel and adds:
    - is_deleted field
    - deleted_at field
    - soft_delete() and restore() methods
    - active_records() and deleted_records() class methods
    """

    post_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="ID of the blog post this comment belongs to",
    )
    author_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Name of the comment author"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Comment content"
    )
    likes: Mapped[int] = mapped_column(Integer, default=0, comment="Number of likes")


# Example 4: Model with audit trail
class Article(AuditModel):
    """
    Article model with audit trail capabilities.

    Extends BaseModel and adds:
    - created_by and updated_by fields
    - version field for optimistic locking
    - set_audit_fields() method
    - increment_version() method
    """

    title: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Article title"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Article content"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        comment="Article status (draft, published, archived)",
    )


def demo_base_models():
    """Demonstrate the base model functionality."""
    print("=== Base Models Demo ===\n")

    # Example 1: BaseModel
    print("1. BaseModel Example:")
    blog_post = BlogPost(
        title="Introduction to FastAPI",
        content="FastAPI is a modern web framework...",
        author_id="user-123",
    )

    print(f"BlogPost instance: {blog_post}")
    print(f"Table name: {blog_post.__tablename__}")
    print(f"Has ID: {hasattr(blog_post, 'id')}")
    print(f"Has created_at: {hasattr(blog_post, 'created_at')}")
    print(f"Has updated_at: {hasattr(blog_post, 'updated_at')}")
    print(f"To dict: {blog_post.to_dict()}")
    print()

    # Example 2: TimestampedModel
    print("2. TimestampedModel Example:")
    category = Category(
        code="TECH", name="Technology", description="Technology-related articles"
    )

    print(f"Category instance: {category}")
    print(f"Table name: {category.__tablename__}")
    print(f"Primary key: {category.code}")
    print(f"Has timestamps: {hasattr(category, 'created_at')}")
    print()

    # Example 3: SoftDeleteModel
    print("3. SoftDeleteModel Example:")
    comment = Comment(
        post_id="post-123", author_name="John Doe", content="Great article!", likes=5
    )

    print(f"Comment instance: {comment}")
    print(f"Is deleted: {comment.is_deleted}")
    print(f"Deleted at: {comment.deleted_at}")

    # Demonstrate soft delete
    print("\nSoft deleting comment...")
    comment.soft_delete()
    print(f"Is deleted: {comment.is_deleted}")
    print(f"Deleted at: {comment.deleted_at}")

    # Demonstrate restore
    print("\nRestoring comment...")
    comment.restore()
    print(f"Is deleted: {comment.is_deleted}")
    print(f"Deleted at: {comment.deleted_at}")
    print()

    # Example 4: AuditModel
    print("4. AuditModel Example:")
    article = Article(
        title="Advanced Python Patterns",
        content="This article covers...",
        status="draft",
    )

    print(f"Article instance: {article}")
    print(f"Version: {article.version}")
    print(f"Created by: {article.created_by}")
    print(f"Updated by: {article.updated_by}")

    # Demonstrate audit fields
    print("\nSetting audit fields...")
    article.set_audit_fields("user-456", is_update=False)
    print(f"Created by: {article.created_by}")
    print(f"Updated by: {article.updated_by}")
    print(f"Version: {article.version}")

    # Demonstrate update
    print("\nUpdating article...")
    article.set_audit_fields("user-789", is_update=True)
    print(f"Updated by: {article.updated_by}")
    print(f"Version: {article.version}")
    print()

    # Example 5: Utility methods
    print("5. Utility Methods Example:")

    # Create from dict
    post_data = {
        "title": "New Post",
        "content": "This is a new post",
        "author_id": "user-999",
    }
    new_post = BlogPost.from_dict(post_data)
    print(f"Created from dict: {new_post}")

    # Convert to dict
    post_dict = new_post.to_dict()
    print(f"Converted to dict: {post_dict}")
    print()


def demo_table_naming():
    """Demonstrate automatic table naming."""
    print("=== Automatic Table Naming Demo ===\n")

    class UserProfile(BaseModel):
        """User profile model."""

        pass

    class OrderItem(BaseModel):
        """Order item model."""

        pass

    class ProductCategory(BaseModel):
        """Product category model."""

        pass

    # Show table names
    models = [UserProfile, OrderItem, ProductCategory]
    for model in models:
        print(f"{model.__name__} -> {model.__tablename__}")
    print()


def demo_inheritance_hierarchy():
    """Demonstrate the inheritance hierarchy."""
    print("=== Inheritance Hierarchy Demo ===\n")

    # Show inheritance
    print("BaseModel inheritance:")
    print(f"BlogPost.__bases__: {BlogPost.__bases__}")
    print(f"BlogPost.__mro__: {[cls.__name__ for cls in BlogPost.__mro__]}")
    print()

    print("SoftDeleteModel inheritance:")
    print(f"Comment.__bases__: {Comment.__bases__}")
    print(f"Comment.__mro__: {[cls.__name__ for cls in Comment.__mro__]}")
    print()

    print("AuditModel inheritance:")
    print(f"Article.__bases__: {Article.__bases__}")
    print(f"Article.__mro__: {[cls.__name__ for cls in Article.__mro__]}")
    print()


def demo_field_inheritance():
    """Demonstrate field inheritance."""
    print("=== Field Inheritance Demo ===\n")

    # Show fields for each model type
    models = [
        ("BaseModel", BlogPost),
        ("TimestampedModel", Category),
        ("SoftDeleteModel", Comment),
        ("AuditModel", Article),
    ]

    for model_type, model_class in models:
        print(f"{model_type} ({model_class.__name__}) fields:")
        for column in model_class.__table__.columns:
            print(f"  - {column.name}: {column.type}")
        print()


if __name__ == "__main__":
    demo_base_models()
    demo_table_naming()
    demo_inheritance_hierarchy()
    demo_field_inheritance()

    print("Base models demo completed!")

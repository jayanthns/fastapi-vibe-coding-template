# Base Models Documentation

This document describes the base model classes that provide common database patterns and reduce code duplication across all models in the FastAPI application.

## Overview

The base models provide a foundation for consistent database patterns including:

- **Common Fields**: UUID primary keys, timestamps, and audit fields
- **Automatic Table Naming**: Converts CamelCase class names to snake_case table names
- **Utility Methods**: Dictionary conversion, field validation, and common operations
- **Specialized Patterns**: Soft delete, audit trails, and optimistic locking

## Base Model Classes

### BaseModel

The primary base class that all models should inherit from.

```python
from src.apps.base_models import BaseModel
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

class Article(BaseModel):
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
```

**Inherited Fields:**
- `id`: UUID primary key with auto-generation and indexing
- `created_at`: Timestamp when record was created (with timezone)
- `updated_at`: Timestamp when record was last updated (with timezone)

**Features:**
- Automatic table naming (e.g., `Article` → `articles`)
- Built-in `__repr__` method
- `to_dict()` and `from_dict()` utility methods

### TimestampedModel

For models that need timestamps but want to define their own primary key.

```python
from src.apps.base_models import TimestampedModel
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

class Category(TimestampedModel):
    __tablename__ = "categories"

    code: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
```

**Inherited Fields:**
- `created_at`: Timestamp when record was created
- `updated_at`: Timestamp when record was last updated

### SoftDeleteModel

Extends BaseModel to add soft delete functionality.

```python
from src.apps.base_models import SoftDeleteModel
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

class Comment(SoftDeleteModel):
    post_id: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
```

**Additional Fields:**
- `is_deleted`: Boolean flag for soft delete status
- `deleted_at`: Timestamp when record was soft deleted

**Methods:**
- `soft_delete()`: Mark record as deleted
- `restore()`: Restore soft deleted record
- `active_records()`: Class method to query non-deleted records
- `deleted_records()`: Class method to query soft deleted records

### AuditModel

Extends BaseModel to add audit trail functionality.

```python
from src.apps.base_models import AuditModel
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

class Article(AuditModel):
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    def set_audit_fields(self, user_id: uuid.UUID, is_update: bool = False):
        if is_update:
            self.updated_by = user_id
            self.increment_version()
        else:
            self.created_by = user_id
            self.updated_by = user_id
```

**Additional Fields:**
- `created_by`: UUID of user who created the record
- `updated_by`: UUID of user who last updated the record
- `version`: Integer for optimistic locking

**Methods:**
- `set_audit_fields(user_id, is_update=False)`: Set audit fields
- `increment_version()`: Increment version number

## Field Definitions

### Common Field Patterns

All base models use consistent field definitions:

```python
# UUID Primary Key
id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4,
    index=True,
    comment="Unique identifier for this record"
)

# Created Timestamp
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False,
    index=True,
    comment="When this record was created"
)

# Updated Timestamp
updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
    nullable=False,
    index=True,
    comment="When this record was last updated"
)
```

### Field Features

- **Timezone Support**: All timestamps include timezone information
- **Automatic Indexing**: Common fields are automatically indexed
- **Server Defaults**: Timestamps use database-level defaults
- **Comments**: All fields include descriptive comments
- **Type Hints**: Full type annotation support with SQLAlchemy 2.0

## Automatic Table Naming

Base models automatically generate table names from class names:

```python
class UserProfile(BaseModel):
    pass  # Table name: user_profiles

class OrderItem(BaseModel):
    pass  # Table name: order_items

class ProductCategory(BaseModel):
    pass  # Table name: product_categories
```

**Naming Rules:**
1. Convert CamelCase to snake_case
2. Add 's' for pluralization
3. Override with `__tablename__` if needed

## Utility Methods

### Dictionary Conversion

```python
# Convert model to dictionary
article = Article(title="Test", content="Content")
data = article.to_dict()
# Returns: {"id": "...", "title": "Test", "content": "Content", ...}

# Create model from dictionary
article = Article.from_dict({
    "title": "Test",
    "content": "Content"
})
```

### String Representation

```python
article = Article(id=uuid.uuid4(), title="Test")
print(article)  # <Article(id=123e4567-e89b-12d3-a456-426614174000)>
```

## Migration Guide

### Existing Models

To migrate existing models to use base models:

1. **Update Imports:**
```python
# Before
from src.db.session import Base

# After
from src.apps.base_models import BaseModel
```

2. **Change Base Class:**
```python
# Before
class Article(Base):
    __tablename__ = "articles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    # ... other fields

# After
class Article(BaseModel):
    # id, created_at, updated_at are inherited
    # ... other fields
```

3. **Remove Redundant Fields:**
Remove the common fields that are now inherited from the base model.

4. **Update Field Definitions:**
Use modern SQLAlchemy 2.0 syntax with `Mapped` and `mapped_column`.

### Database Migration

Use the provided migration script to update existing database tables:

```bash
python scripts/migrate_to_base_models.py
```

This script will:
- Add missing base model columns to existing tables
- Create necessary indexes
- Set up updated_at triggers
- Verify the migration

## Best Practices

### Model Design

1. **Use BaseModel by Default:**
```python
class MyModel(BaseModel):
    # Inherits id, created_at, updated_at
    pass
```

2. **Use TimestampedModel for Custom Primary Keys:**
```python
class Category(TimestampedModel):
    code: Mapped[str] = mapped_column(String(10), primary_key=True)
    # Inherits created_at, updated_at
```

3. **Use SoftDeleteModel for Deletable Records:**
```python
class Comment(SoftDeleteModel):
    # Inherits all BaseModel fields plus soft delete fields
    pass
```

4. **Use AuditModel for Tracked Changes:**
```python
class Article(AuditModel):
    # Inherits all BaseModel fields plus audit fields
    pass
```

### Field Definitions

1. **Always Use Type Hints:**
```python
title: Mapped[str] = mapped_column(String(255), nullable=False)
```

2. **Include Comments:**
```python
title: Mapped[str] = mapped_column(
    String(255),
    nullable=False,
    comment="Title of the article"
)
```

3. **Use Appropriate Constraints:**
```python
email: Mapped[str] = mapped_column(
    String(255),
    nullable=False,
    unique=True,
    index=True
)
```

### Query Patterns

1. **Use Active Records for Soft Delete Models:**
```python
# Get only non-deleted comments
active_comments = Comment.active_records().all()
```

2. **Use Version for Optimistic Locking:**
```python
# Check version before update
article = session.get(Article, article_id)
if article.version != expected_version:
    raise OptimisticLockError("Record was modified by another user")
```

## Examples

### Complete Model Example

```python
from src.apps.base_models import BaseModel
from sqlalchemy import String, Text, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

class BlogPost(BaseModel):
    """
    Blog post model with comprehensive fields.

    Extends BaseModel to inherit:
    - UUID primary key (id)
    - Created and updated timestamps
    - Automatic table naming (blog_posts)
    - Utility methods
    """

    # Content fields
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Title of the blog post"
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Main content of the blog post"
    )
    excerpt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Short excerpt for previews"
    )

    # Metadata fields
    author_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="ID of the post author"
    )
    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Post category"
    )

    # Status fields
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the post is published"
    )
    view_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of times the post has been viewed"
    )

    def __repr__(self) -> str:
        return (
            f"<BlogPost(id={self.id}, title='{self.title[:30]}...', "
            f"author_id='{self.author_id}', is_published={self.is_published})>"
        )

    @property
    def word_count(self) -> int:
        """Calculate approximate word count."""
        return len(self.content.split())

    def publish(self) -> None:
        """Publish the blog post."""
        self.is_published = True

    def unpublish(self) -> None:
        """Unpublish the blog post."""
        self.is_published = False
```

### Soft Delete Example

```python
from src.apps.base_models import SoftDeleteModel
from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

class Comment(SoftDeleteModel):
    """Comment model with soft delete functionality."""

    post_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="ID of the blog post this comment belongs to"
    )
    author_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Name of the comment author"
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Comment content"
    )
    likes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="Number of likes"
    )

    def __repr__(self) -> str:
        return (
            f"<Comment(id={self.id}, post_id='{self.post_id}', "
            f"author='{self.author_name}', is_deleted={self.is_deleted})>"
        )

# Usage examples:
comment = Comment(post_id="post-123", author_name="John", content="Great post!")

# Soft delete
comment.soft_delete()
print(comment.is_deleted)  # True
print(comment.deleted_at)  # datetime object

# Restore
comment.restore()
print(comment.is_deleted)  # False
print(comment.deleted_at)  # None

# Query active comments
active_comments = Comment.active_records().all()
deleted_comments = Comment.deleted_records().all()
```

### Audit Model Example

```python
from src.apps.base_models import AuditModel
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
import uuid

class Article(AuditModel):
    """Article model with audit trail."""

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Article title"
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Article content"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        comment="Article status"
    )

    def __repr__(self) -> str:
        return (
            f"<Article(id={self.id}, title='{self.title[:30]}...', "
            f"version={self.version}, status='{self.status}')>"
        )

# Usage examples:
article = Article(title="New Article", content="Content here")

# Set audit fields for creation
user_id = uuid.uuid4()
article.set_audit_fields(user_id, is_update=False)
print(article.created_by)  # user_id
print(article.updated_by)  # user_id
print(article.version)     # 1

# Update article
article.title = "Updated Title"
article.set_audit_fields(user_id, is_update=True)
print(article.updated_by)  # user_id
print(article.version)     # 2
```

## Performance Considerations

### Indexing

Base models automatically create indexes on:
- Primary key (`id`)
- Timestamps (`created_at`, `updated_at`)
- Soft delete fields (`is_deleted`, `deleted_at`)
- Audit fields (`created_by`, `updated_by`)

### Query Optimization

1. **Use Appropriate Base Models:**
   - Use `SoftDeleteModel` only when soft delete is needed
   - Use `AuditModel` only when audit trails are required

2. **Leverage Inherited Indexes:**
   - Query by `created_at` for time-based filtering
   - Use `is_deleted=False` for active records

3. **Consider Composite Indexes:**
   - Add custom indexes for common query patterns
   - Combine base model fields with business fields

## Troubleshooting

### Common Issues

1. **Table Name Conflicts:**
   - Override `__tablename__` if automatic naming conflicts
   - Check for existing tables with similar names

2. **Field Conflicts:**
   - Don't redefine inherited fields
   - Use different names for custom fields

3. **Migration Issues:**
   - Run migration script before deploying new models
   - Verify database schema matches model definitions

### Debugging

1. **Check Model Inheritance:**
```python
print(MyModel.__mro__)  # Method Resolution Order
print(MyModel.__bases__)  # Direct base classes
```

2. **Verify Table Structure:**
```python
print(MyModel.__table__.columns.keys())  # All column names
```

3. **Test Utility Methods:**
```python
instance = MyModel()
print(instance.to_dict())  # Check field serialization
```

## Future Enhancements

Potential improvements for future versions:

1. **Additional Base Models:**
   - `VersionedModel` for content versioning
   - `HierarchicalModel` for tree structures
   - `CachedModel` for caching integration

2. **Enhanced Utilities:**
   - JSON serialization with custom encoders
   - Validation integration with Pydantic
   - Bulk operations support

3. **Performance Optimizations:**
   - Lazy loading for audit fields
   - Connection pooling integration
   - Query optimization hints

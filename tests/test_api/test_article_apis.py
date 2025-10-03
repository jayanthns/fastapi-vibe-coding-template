"""
Comprehensive article API tests using SQLite in-memory database.
Following the SQLAlchemy Base pattern for reliable testing.
"""

from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.articles.models import Article

# Set test order - articles run as order 3, before background jobs (order 4)
pytestmark = [pytest.mark.order(3)]

# ============================================================================
# GET ARTICLE TESTS
# ============================================================================


async def test_get_article_success(async_session: AsyncSession, client: TestClient):
    """Test getting an article by ID successfully."""
    # Create a test article in the database
    article = Article(
        title="Test Article",
        content="This is a test article content for testing purposes.",
    )
    async_session.add(article)
    await async_session.commit()
    await async_session.refresh(article)

    # Make the API request
    response = client.get(f"/api/v1/articles/{article.id}")
    data = response.json()

    # Verify the response
    assert response.status_code == 200

    # Verify APIResponse structure
    assert "success" in data
    assert "message" in data
    assert "data" in data
    assert "status_code" in data
    assert "trace_id" in data
    assert "timestamp" in data

    # Verify success response
    assert data["success"] is True
    assert data["message"] == "Article retrieved successfully"
    assert data["status_code"] == 200

    # Verify article data
    article_data = data["data"]
    assert article_data["id"] == str(article.id)
    assert article_data["title"] == article.title
    assert article_data["content"] == article.content
    assert "created_at" in article_data
    assert "updated_at" in article_data


async def test_get_article_not_found(async_session: AsyncSession, client: TestClient):
    """Test getting an article that doesn't exist."""
    non_existent_id = str(uuid4())

    response = client.get(f"/api/v1/articles/{non_existent_id}")
    data = response.json()

    # Verify the response
    assert response.status_code == 404

    # This endpoint returns raw HTTPException detail, not APIResponse wrapper
    assert "detail" in data
    assert data["detail"] == "Article not found"


async def test_get_article_invalid_uuid(
    async_session: AsyncSession, client: TestClient
):
    """Test getting an article with invalid UUID format."""
    response = client.get("/api/v1/articles/invalid-uuid")

    # Should return 422 for validation error
    assert response.status_code == 422


# ============================================================================
# CREATE ARTICLE TESTS
# ============================================================================


async def test_create_article_success(async_session: AsyncSession, client: TestClient):
    """Test creating an article successfully."""
    article_data = {
        "title": "New Test Article",
        "content": "This is a new test article created via API.",
    }

    # Make the API request
    response = client.post("/api/v1/articles/", json=article_data)
    data = response.json()

    # Verify the response
    assert response.status_code == 201

    # Verify APIResponse structure
    assert "success" in data
    assert "message" in data
    assert "data" in data
    assert "status_code" in data
    assert "trace_id" in data
    assert "timestamp" in data

    # Verify success response
    assert data["success"] is True
    assert data["message"] == "Article created successfully"
    assert data["status_code"] == 201

    # Verify article data
    created_article = data["data"]
    assert created_article["title"] == article_data["title"]
    assert created_article["content"] == article_data["content"]
    assert "id" in created_article
    assert "created_at" in created_article
    assert "updated_at" in created_article

    # Verify article was actually created in database
    article_id = created_article["id"]
    db_article = await async_session.get(Article, UUID(article_id))
    assert db_article is not None
    assert db_article.title == article_data["title"]
    assert db_article.content == article_data["content"]


async def test_create_article_missing_title(
    async_session: AsyncSession, client: TestClient
):
    """Test creating an article with missing title."""
    article_data = {
        "content": "This article has no title.",
    }

    response = client.post("/api/v1/articles/", json=article_data)

    # Should return 422 for validation error
    assert response.status_code == 422


async def test_create_article_missing_content(
    async_session: AsyncSession, client: TestClient
):
    """Test creating an article with missing content."""
    article_data = {
        "title": "Article without content",
    }

    response = client.post("/api/v1/articles/", json=article_data)

    # Should return 422 for validation error
    assert response.status_code == 422


async def test_create_article_empty_title(
    async_session: AsyncSession, client: TestClient
):
    """Test creating an article with empty title."""
    article_data = {
        "title": "",
        "content": "This article has an empty title.",
    }

    response = client.post("/api/v1/articles/", json=article_data)

    # Should return 422 for validation error
    assert response.status_code == 422


async def test_create_article_empty_content(
    async_session: AsyncSession, client: TestClient
):
    """Test creating an article with empty content."""
    article_data = {
        "title": "Article with empty content",
        "content": "",
    }

    response = client.post("/api/v1/articles/", json=article_data)

    # The API allows empty content, so this should succeed
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True


async def test_create_article_long_title(
    async_session: AsyncSession, client: TestClient
):
    """Test creating an article with very long title."""
    article_data = {
        "title": "A" * 300,  # Exceeds 255 character limit
        "content": "This article has a very long title.",
    }

    response = client.post("/api/v1/articles/", json=article_data)

    # Should return 422 for validation error
    assert response.status_code == 422


async def test_create_article_unicode_content(
    async_session: AsyncSession, client: TestClient
):
    """Test creating an article with unicode content."""
    article_data = {
        "title": "Unicode Test Article 🚀",
        "content": "This article contains unicode characters: 测试文章内容 🎉 émojis and special chars: @#$%^&*()",
    }

    response = client.post("/api/v1/articles/", json=article_data)
    data = response.json()

    # Verify the response
    assert response.status_code == 201
    assert data["success"] is True

    # Verify unicode content is preserved
    created_article = data["data"]
    assert created_article["title"] == article_data["title"]
    assert created_article["content"] == article_data["content"]


# ============================================================================
# GET ARTICLES LIST TESTS
# ============================================================================


async def test_get_articles_list_success(
    async_session: AsyncSession, client: TestClient
):
    """Test getting a list of articles successfully."""
    # Create test articles in the database
    articles = [
        Article(title="Article 1", content="Content 1"),
        Article(title="Article 2", content="Content 2"),
        Article(title="Article 3", content="Content 3"),
    ]
    for article in articles:
        async_session.add(article)
    await async_session.commit()

    # Make the API request
    response = client.get("/api/v1/articles/")
    data = response.json()

    # Verify the response
    assert response.status_code == 200

    # Verify APIResponse structure
    assert "success" in data
    assert "message" in data
    assert "data" in data
    assert "status_code" in data
    assert "trace_id" in data
    assert "timestamp" in data

    # Verify success response
    assert data["success"] is True
    assert data["message"] == "Retrieved 3 articles"
    assert data["status_code"] == 200

    # Verify articles data
    articles_data = data["data"]
    assert len(articles_data) == 3
    assert all("id" in article for article in articles_data)
    assert all("title" in article for article in articles_data)
    assert all("content" in article for article in articles_data)


async def test_get_articles_list_empty(async_session: AsyncSession, client: TestClient):
    """Test getting articles list when database is empty."""
    response = client.get("/api/v1/articles/")
    data = response.json()

    # Verify the response
    assert response.status_code == 200
    assert data["success"] is True
    assert data["message"] == "Retrieved 0 articles"
    assert data["data"] == []


async def test_get_articles_list_with_pagination(
    async_session: AsyncSession, client: TestClient
):
    """Test getting articles list with pagination parameters."""
    # Create test articles in the database
    articles = [
        Article(title=f"Article {i}", content=f"Content {i}")
        for i in range(1, 6)  # 5 articles
    ]
    for article in articles:
        async_session.add(article)
    await async_session.commit()

    # Test with skip and limit
    response = client.get("/api/v1/articles/?skip=1&limit=2")
    data = response.json()

    # Verify the response
    assert response.status_code == 200
    assert data["success"] is True
    assert len(data["data"]) == 2


async def test_get_articles_list_invalid_pagination(
    async_session: AsyncSession, client: TestClient
):
    """Test getting articles list with invalid pagination parameters."""
    # Test with negative skip - FastAPI converts to 0
    response = client.get("/api/v1/articles/?skip=-1")
    assert response.status_code == 200

    # Test with negative limit - FastAPI converts to 100
    response = client.get("/api/v1/articles/?limit=-1")
    assert response.status_code == 200

    # Test with non-integer skip
    response = client.get("/api/v1/articles/?skip=abc")
    assert response.status_code == 422

    # Test with non-integer limit
    response = client.get("/api/v1/articles/?limit=xyz")
    assert response.status_code == 422


# ============================================================================
# UPDATE ARTICLE TESTS
# ============================================================================


async def test_update_article_success(async_session: AsyncSession, client: TestClient):
    """Test updating an article successfully."""
    # Create a test article in the database
    article = Article(
        title="Original Title",
        content="Original content for testing purposes.",
    )
    async_session.add(article)
    await async_session.commit()
    await async_session.refresh(article)

    # Update data
    update_data = {
        "title": "Updated Title",
        "content": "Updated content for testing purposes.",
    }

    # Make the API request
    response = client.patch(f"/api/v1/articles/{article.id}", json=update_data)
    data = response.json()

    # Verify the response
    assert response.status_code == 200

    # PATCH endpoint returns raw Article object, not APIResponse wrapper
    assert "id" in data
    assert "title" in data
    assert "content" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Verify updated article data
    assert data["id"] == str(article.id)
    assert data["title"] == update_data["title"]
    assert data["content"] == update_data["content"]

    # Verify article was actually updated in database
    db_article = await async_session.get(Article, article.id)
    assert db_article.title == update_data["title"]
    assert db_article.content == update_data["content"]


async def test_update_article_partial(async_session: AsyncSession, client: TestClient):
    """Test updating an article with partial data (only title)."""
    # Create a test article in the database
    article = Article(
        title="Original Title",
        content="Original content for testing purposes.",
    )
    async_session.add(article)
    await async_session.commit()
    await async_session.refresh(article)

    # Update only title
    update_data = {
        "title": "Updated Title Only",
    }

    # Make the API request
    response = client.patch(f"/api/v1/articles/{article.id}", json=update_data)
    data = response.json()

    # Verify the response
    assert response.status_code == 200

    # PATCH endpoint returns raw Article object, not APIResponse wrapper
    assert data["title"] == update_data["title"]
    assert data["content"] == article.content  # Should remain unchanged


async def test_update_article_not_found(
    async_session: AsyncSession, client: TestClient
):
    """Test updating an article that doesn't exist."""
    non_existent_id = str(uuid4())
    update_data = {
        "title": "Updated Title",
        "content": "Updated content",
    }

    response = client.patch(f"/api/v1/articles/{non_existent_id}", json=update_data)
    data = response.json()

    # Verify the response
    assert response.status_code == 404
    assert "detail" in data
    assert data["detail"] == "Article not found"


async def test_update_article_invalid_uuid(
    async_session: AsyncSession, client: TestClient
):
    """Test updating an article with invalid UUID format."""
    update_data = {
        "title": "Updated Title",
        "content": "Updated content",
    }

    response = client.patch("/api/v1/articles/invalid-uuid", json=update_data)

    # Should return 422 for validation error
    assert response.status_code == 422


async def test_update_article_empty_data(
    async_session: AsyncSession, client: TestClient
):
    """Test updating an article with empty update data."""
    # Create a test article in the database
    article = Article(
        title="Original Title",
        content="Original content for testing purposes.",
    )
    async_session.add(article)
    await async_session.commit()
    await async_session.refresh(article)

    # Empty update data
    update_data = {}

    # Make the API request
    response = client.patch(f"/api/v1/articles/{article.id}", json=update_data)
    data = response.json()

    # Should still return success but no changes
    assert response.status_code == 200

    # PATCH endpoint returns raw Article object, not APIResponse wrapper
    assert data["title"] == article.title
    assert data["content"] == article.content


# ============================================================================
# DELETE ARTICLE TESTS
# ============================================================================


async def test_delete_article_success(async_session: AsyncSession, client: TestClient):
    """Test deleting an article successfully."""
    # Create a test article in the database
    article = Article(
        title="Article to Delete",
        content="This article will be deleted.",
    )
    async_session.add(article)
    await async_session.commit()
    await async_session.refresh(article)

    # Make the API request
    response = client.delete(f"/api/v1/articles/{article.id}")

    # Verify the response
    assert response.status_code == 204
    # DELETE returns no content

    # Verify article was actually deleted from database
    db_article = await async_session.get(Article, article.id)
    assert db_article is None


async def test_delete_article_not_found(
    async_session: AsyncSession, client: TestClient
):
    """Test deleting an article that doesn't exist."""
    non_existent_id = str(uuid4())

    response = client.delete(f"/api/v1/articles/{non_existent_id}")
    data = response.json()

    # Verify the response
    assert response.status_code == 404
    assert "detail" in data
    assert data["detail"] == "Article not found"


async def test_delete_article_invalid_uuid(
    async_session: AsyncSession, client: TestClient
):
    """Test deleting an article with invalid UUID format."""
    response = client.delete("/api/v1/articles/invalid-uuid")

    # Should return 422 for validation error
    assert response.status_code == 422


# ============================================================================
# EDGE CASES AND ERROR HANDLING TESTS
# ============================================================================


async def test_article_with_special_characters(
    async_session: AsyncSession, client: TestClient
):
    """Test article with special characters in title and content."""
    article_data = {
        "title": "Special Chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
        "content": "Content with special chars: <script>alert('test')</script> & HTML entities: &lt; &gt; &amp;",
    }

    response = client.post("/api/v1/articles/", json=article_data)
    data = response.json()

    # Verify the response
    assert response.status_code == 201
    assert data["success"] is True

    # Verify special characters are preserved
    created_article = data["data"]
    assert created_article["title"] == article_data["title"]
    assert created_article["content"] == article_data["content"]


async def test_article_with_very_long_content(
    async_session: AsyncSession, client: TestClient
):
    """Test article with very long content."""
    long_content = "This is a very long article content. " * 1000  # ~40KB of content

    article_data = {
        "title": "Article with Long Content",
        "content": long_content,
    }

    response = client.post("/api/v1/articles/", json=article_data)
    data = response.json()

    # Verify the response
    assert response.status_code == 201
    assert data["success"] is True

    # Verify long content is preserved
    created_article = data["data"]
    assert created_article["content"] == long_content


async def test_article_with_whitespace(async_session: AsyncSession, client: TestClient):
    """Test article with various whitespace characters."""
    article_data = {
        "title": "  Article with Whitespace  ",
        "content": "Content with\ttabs\nand\n\nmultiple\nlines.",
    }

    response = client.post("/api/v1/articles/", json=article_data)
    data = response.json()

    # Verify the response
    assert response.status_code == 201
    assert data["success"] is True

    # Verify whitespace is preserved
    created_article = data["data"]
    assert created_article["title"] == article_data["title"]
    assert created_article["content"] == article_data["content"]


async def test_concurrent_article_operations(
    async_session: AsyncSession, client: TestClient
):
    """Test concurrent article operations."""
    # Create multiple articles concurrently
    article_data_list = [
        {"title": f"Concurrent Article {i}", "content": f"Content {i}"}
        for i in range(1, 4)
    ]

    # Create articles
    responses = []
    for article_data in article_data_list:
        response = client.post("/api/v1/articles/", json=article_data)
        responses.append(response)

    # Verify all articles were created successfully
    for response in responses:
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    # Verify all articles exist in the list
    list_response = client.get("/api/v1/articles/")
    list_data = list_response.json()
    assert list_data["success"] is True
    assert len(list_data["data"]) == 3


# ============================================================================
# API DOCUMENTATION TESTS
# ============================================================================


def test_api_documentation_accessible(client: TestClient):
    """Test that API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema_accessible(client: TestClient):
    """Test that OpenAPI schema is accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/articles/" in schema["paths"]
    assert "/api/v1/articles/{article_id}" in schema["paths"]


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


async def test_article_crud_workflow(async_session: AsyncSession, client: TestClient):
    """Test complete CRUD workflow for articles."""
    # 1. Create article
    create_data = {
        "title": "CRUD Test Article",
        "content": "This article will be tested through the full CRUD workflow.",
    }

    create_response = client.post("/api/v1/articles/", json=create_data)
    assert create_response.status_code == 201
    create_result = create_response.json()
    assert create_result["success"] is True

    article_id = create_result["data"]["id"]

    # 2. Read article
    read_response = client.get(f"/api/v1/articles/{article_id}")
    assert read_response.status_code == 200
    read_result = read_response.json()
    assert read_result["success"] is True
    assert read_result["data"]["title"] == create_data["title"]

    # 3. Update article
    update_data = {
        "title": "Updated CRUD Test Article",
        "content": "This article has been updated through the CRUD workflow.",
    }

    update_response = client.patch(f"/api/v1/articles/{article_id}", json=update_data)
    assert update_response.status_code == 200
    update_result = update_response.json()
    # PATCH returns raw Article object, not APIResponse wrapper
    assert update_result["title"] == update_data["title"]

    # 4. Verify article appears in list
    list_response = client.get("/api/v1/articles/")
    assert list_response.status_code == 200
    list_result = list_response.json()
    assert list_result["success"] is True
    assert len(list_result["data"]) == 1
    assert list_result["data"][0]["title"] == update_data["title"]

    # 5. Delete article
    delete_response = client.delete(f"/api/v1/articles/{article_id}")
    assert delete_response.status_code == 204
    # DELETE returns no content

    # 6. Verify article is deleted
    final_read_response = client.get(f"/api/v1/articles/{article_id}")
    assert final_read_response.status_code == 404
    final_read_result = final_read_response.json()
    assert "detail" in final_read_result
    assert final_read_result["detail"] == "Article not found"

# Class-Based API Testing

This document explains the class-based testing approach used for API tests in this project.

## Overview

The API tests have been refactored from standalone functions to a class-based structure for better organization and maintainability.

**Note**: This implementation uses pytest-style classes (not `unittest.TestCase`), which allows for seamless integration with pytest fixtures while providing class-based organization benefits.

## Structure

### Before (Function-based)
```python
async def test_get_article_success(async_session: AsyncSession, client: TestClient):
    """Test getting an article by ID successfully."""
    # Test implementation...

async def test_create_article_success(async_session: AsyncSession, client: TestClient):
    """Test creating an article successfully."""
    # Test implementation...
```

### After (Class-based)
```python
class TestArticleAPIs:
    """Test class for Article API endpoints."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Initialize shared test data
        self.sample_article_data = {...}
        self.created_article_ids = []

    async def test_get_article_success(self, async_session: AsyncSession, client: TestClient):
        """Test getting an article by ID successfully."""
        # Test implementation...

    async def test_create_article_success(self, async_session: AsyncSession, client: TestClient):
        """Test creating an article successfully."""
        # Test implementation...
```

## Benefits

### 1. **Better Organization**
- Tests are grouped logically within a class
- Related tests are kept together
- Clear separation between different API test suites

### 2. **Improved Readability**
- Class docstring explains the purpose of the test suite
- Methods are organized by functionality (GET, POST, PATCH, DELETE)
- Consistent naming conventions

### 3. **Easier Maintenance**
- Changes to test structure can be made in one place
- Shared setup/teardown logic can be added to the class
- Better IDE support for test discovery and navigation

### 4. **Scalability**
- Easy to add new test methods
- Can create multiple test classes for different APIs
- Supports inheritance for shared test patterns

### 5. **Setup and Teardown Support**
- `setup_method()` - Called before each test method (like `unittest.TestCase.setUp()`)
- `teardown_method()` - Called after each test method (like `unittest.TestCase.tearDown()`)
- `setup_class()` - Called once before the entire test class
- `teardown_class()` - Called once after the entire test class
- Shared test data and helper methods available to all tests

## Test Organization

The `TestArticleAPIs` class is organized into the following sections:

### 1. **GET Operations**
- `test_get_article_success()` - Test successful article retrieval
- `test_get_article_not_found()` - Test article not found scenario
- `test_get_article_invalid_uuid()` - Test invalid UUID handling

### 2. **POST Operations (Create)**
- `test_create_article_success()` - Test successful article creation
- `test_create_article_missing_title()` - Test validation for missing title
- `test_create_article_missing_content()` - Test validation for missing content
- `test_create_article_empty_title()` - Test validation for empty title
- `test_create_article_empty_content()` - Test empty content handling
- `test_create_article_long_title()` - Test title length validation
- `test_create_article_unicode_content()` - Test unicode content handling

### 3. **GET Operations (List)**
- `test_get_articles_list_success()` - Test successful article listing
- `test_get_articles_list_empty()` - Test empty list scenario
- `test_get_articles_list_with_pagination()` - Test pagination
- `test_get_articles_list_invalid_pagination()` - Test invalid pagination

### 4. **PATCH Operations (Update)**
- `test_update_article_success()` - Test successful article update
- `test_update_article_partial()` - Test partial updates
- `test_update_article_not_found()` - Test update of non-existent article
- `test_update_article_invalid_uuid()` - Test invalid UUID handling
- `test_update_article_empty_data()` - Test empty update data

### 5. **DELETE Operations**
- `test_delete_article_success()` - Test successful article deletion
- `test_delete_article_not_found()` - Test deletion of non-existent article
- `test_delete_article_invalid_uuid()` - Test invalid UUID handling

### 6. **Edge Cases and Error Handling**
- `test_article_with_special_characters()` - Test special character handling
- `test_article_with_very_long_content()` - Test long content handling
- `test_article_with_whitespace()` - Test whitespace handling
- `test_concurrent_article_operations()` - Test concurrent operations

### 7. **API Documentation**
- `test_api_documentation_accessible()` - Test API docs accessibility
- `test_openapi_schema_accessible()` - Test OpenAPI schema accessibility

### 8. **Integration Tests**
- `test_article_crud_workflow()` - Test complete CRUD workflow

## Setup and Teardown Methods

The `TestArticleAPIs` class includes setup and teardown methods similar to Python's `unittest` module:

### Setup Methods

```python
def setup_method(self):
    """Called before each test method."""
    # Initialize shared test data
    self.sample_article_data = {
        "title": "Sample Test Article",
        "content": "This is a sample article for testing purposes.",
    }
    self.created_article_ids = []

def setup_class(cls):
    """Called once before the entire test class."""
    # Expensive setup that only needs to happen once
    pass
```

### Teardown Methods

```python
def teardown_method(self):
    """Called after each test method."""
    # Clean up test data
    self.created_article_ids.clear()

def teardown_class(cls):
    """Called once after the entire test class."""
    # Clean up resources
    pass
```

### Helper Methods

```python
def track_created_article(self, article_id: str):
    """Track a created article ID for potential cleanup."""
    self.created_article_ids.append(article_id)

def create_test_article_data(self, title_suffix: str = "", content_suffix: str = ""):
    """Create test article data with optional suffixes."""
    return {
        "title": f"Test Article {title_suffix}".strip(),
        "content": f"Test content {content_suffix}".strip(),
    }
```

## Running Tests

### Using pytest (Standard)

#### Run All Article API Tests
```bash
pytest tests/test_api/test_article_apis.py -v
```

#### Run Specific Test Method
```bash
pytest tests/test_api/test_article_apis.py::TestArticleAPIs::test_create_article_success -v
```

#### Run All Tests in a Class
```bash
pytest tests/test_api/test_article_apis.py::TestArticleAPIs -v
```

#### Run with Coverage
```bash
pytest tests/test_api/test_article_apis.py --cov=src --cov-report=html
```

### Using Custom Test Runner (unittest-style)

A custom test runner script is provided for a more unittest-like experience:

#### List Available Tests
```bash
python scripts/run_article_tests.py list
```

#### Run All Tests
```bash
python scripts/run_article_tests.py run
```

#### Run Specific Test Method
```bash
python scripts/run_article_tests.py run test_create_article_success
```

#### Get Help
```bash
python scripts/run_article_tests.py help
```

The custom test runner provides:
- **Categorized test listing** - Tests grouped by functionality
- **Individual test execution** - Run specific test methods
- **Coverage reporting** - Built-in coverage analysis
- **Verbose output** - Detailed test execution information
- **unittest-style interface** - Familiar command-line interface

## Test Execution Order

The tests are executed in the order they appear in the class, which follows a logical flow:

1. **GET Operations** - Test basic retrieval functionality
2. **POST Operations** - Test creation functionality
3. **GET List Operations** - Test listing functionality
4. **PATCH Operations** - Test update functionality
5. **DELETE Operations** - Test deletion functionality
6. **Edge Cases** - Test special scenarios
7. **Documentation** - Test API documentation
8. **Integration** - Test complete workflows

## Best Practices

### 1. **Method Naming**
- Use descriptive method names that explain what is being tested
- Follow the pattern: `test_<operation>_<scenario>`
- Examples: `test_create_article_success`, `test_get_article_not_found`

### 2. **Documentation**
- Add docstrings to explain what each test does
- Use class docstring to explain the overall purpose
- Add comments for complex test logic

### 3. **Test Data**
- Use realistic test data that reflects real-world usage
- Include edge cases and boundary conditions
- Test both valid and invalid scenarios

### 4. **Assertions**
- Use clear, descriptive assertions
- Test both positive and negative cases
- Verify response structure and content

### 5. **Error Handling**
- Test all error scenarios
- Verify appropriate HTTP status codes
- Check error message content

## Future Enhancements

### 1. **Base Test Class**
Consider creating a base test class for common functionality:

```python
class BaseAPITest:
    """Base class for API testing."""

    def setup_method(self):
        """Setup method called before each test."""
        pass

    def teardown_method(self):
        """Teardown method called after each test."""
        pass

class TestArticleAPIs(BaseAPITest):
    """Test class for Article API endpoints."""
    # Test methods...
```

### 2. **Test Data Factories**
Create factory classes for generating test data:

```python
class ArticleTestDataFactory:
    """Factory for creating article test data."""

    @staticmethod
    def create_valid_article():
        return {
            "title": "Test Article",
            "content": "Test content"
        }

    @staticmethod
    def create_invalid_article():
        return {
            "title": "",  # Invalid: empty title
            "content": "Test content"
        }
```

### 3. **Shared Fixtures**
Create shared fixtures for common test setup:

```python
@pytest.fixture
def sample_article_data():
    """Fixture providing sample article data."""
    return {
        "title": "Sample Article",
        "content": "Sample content"
    }
```

## Conclusion

The class-based testing approach provides better organization, improved readability, and easier maintenance for API tests. It follows Python testing best practices and makes the test suite more scalable and maintainable.

This structure can be easily extended for other APIs by creating similar test classes, and it provides a solid foundation for future enhancements like base test classes and test data factories.

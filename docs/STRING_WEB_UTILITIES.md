# String and Web Utilities

This document describes the comprehensive string and web utilities implemented in the FastAPI application.

## String Utilities (`src/utils/string_utils.py`)

### Overview

The string utilities module provides comprehensive text processing, sanitization, and manipulation capabilities including:

- Text sanitization and validation
- Slug generation (URL-friendly strings)
- Text normalization and cleaning
- Template string processing
- Multi-language text handling

### Classes and Functions

#### StringSanitizer

Text sanitization and validation utilities.

```python
from src.utils.string_utils import StringSanitizer

# Remove HTML tags
clean_text = StringSanitizer.remove_html_tags("<p>Hello</p>")

# Remove script tags
safe_text = StringSanitizer.remove_script_tags("<script>alert('xss')</script>")

# Sanitize HTML with allowed tags
sanitized = StringSanitizer.sanitize_html(html_content, allowed_tags=["p", "b"])

# Detect SQL injection
is_dangerous = StringSanitizer.detect_sql_injection("'; DROP TABLE users; --")

# Sanitize SQL input
safe_input = StringSanitizer.sanitize_sql_input(user_input)

# Clean whitespace
cleaned = StringSanitizer.clean_whitespace("  Hello   World  ")

# Remove control characters
clean_text = StringSanitizer.remove_control_characters("Hello\x00World")
```

#### SlugGenerator

URL-friendly slug generation utilities.

```python
from src.utils.string_utils import SlugGenerator

# Generate basic slug
slug = SlugGenerator.generate_slug("Hello World!")

# Generate slug with custom parameters
slug = SlugGenerator.generate_slug(
    "Hello World!",
    max_length=30,
    separator="_",
    preserve_case=True
)

# Generate unique slug
existing_slugs = ["hello-world", "hello-world-1"]
unique_slug = SlugGenerator.generate_unique_slug("Hello World", existing_slugs)
```

#### TextNormalizer

Text normalization and cleaning utilities.

```python
from src.utils.string_utils import TextNormalizer

# Normalize unicode
normalized = TextNormalizer.normalize_unicode("café", form="NFC")

# Remove accents
no_accents = TextNormalizer.remove_accents("café résumé")

# Normalize whitespace
clean_whitespace = TextNormalizer.normalize_whitespace("Hello\t\nWorld")

# Clean text
cleaned = TextNormalizer.clean_text("  Hello, World!  ", remove_punctuation=True)

# Truncate text
truncated = TextNormalizer.truncate_text(
    "This is a very long text",
    max_length=20,
    suffix="...",
    word_boundary=True
)
```

#### TemplateProcessor

Template string processing utilities.

```python
from src.utils.string_utils import TemplateProcessor

# Process template
template = "Hello {name}, you have {count} messages."
result = TemplateProcessor.process_template(template, {"name": "John", "count": 5})

# Process template in safe mode (HTML escaping)
safe_result = TemplateProcessor.process_template(
    template,
    {"name": "<script>alert('xss')</script>"},
    safe_mode=True
)

# Extract template variables
variables = TemplateProcessor.extract_template_variables(template)

# Validate template
is_valid = TemplateProcessor.validate_template(template, ["name", "count"])
```

#### MultiLanguageHandler

Multi-language text handling utilities.

```python
from src.utils.string_utils import MultiLanguageHandler

# Detect language
language = MultiLanguageHandler.detect_language("The quick brown fox")

# Transliterate Cyrillic
latin_text = MultiLanguageHandler.transliterate_cyrillic("Привет мир")

# Normalize for search
search_text = MultiLanguageHandler.normalize_for_search("Café & Résumé", language="en")
```

#### Convenience Functions

```python
from src.utils.string_utils import (
    sanitize_text,
    create_slug,
    normalize_text,
    process_template_string,
    detect_text_language
)

# Quick text sanitization
clean = sanitize_text("<script>alert('xss')</script>Hello World")

# Quick slug generation
slug = create_slug("Hello World!")

# Quick text normalization
normalized = normalize_text("  Hello   World  ", remove_accents=True)

# Quick template processing
result = process_template_string("Hello {name}!", name="World")

# Quick language detection
language = detect_text_language("Hello World")
```

## Web Utilities (`src/utils/web_utils.py`)

### Overview

The web utilities module provides comprehensive HTTP client operations and advanced networking features including:

- HTTP Client Utilities
- Retry mechanisms with exponential backoff
- Rate limiting and throttling
- Request/response logging
- Circuit breaker patterns
- HTTP client pooling

### Configuration Classes

#### RetryConfig

Configuration for retry mechanisms.

```python
from src.utils.web_utils import RetryConfig, create_retry_config

# Create retry configuration
retry_config = create_retry_config(
    max_attempts=3,
    base_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True
)

# Or create directly
retry_config = RetryConfig(
    max_attempts=5,
    base_delay=2.0,
    retryable_status_codes=[429, 500, 502, 503, 504]
)
```

#### RateLimitConfig

Configuration for rate limiting.

```python
from src.utils.web_utils import RateLimitConfig, create_rate_limit_config

# Create rate limit configuration
rate_config = create_rate_limit_config(
    requests_per_second=10.0,
    burst_size=20
)

# Or create directly
rate_config = RateLimitConfig(
    requests_per_second=5.0,
    burst_size=10,
    window_size=60.0
)
```

#### CircuitBreakerConfig

Configuration for circuit breaker.

```python
from src.utils.web_utils import CircuitBreakerConfig, create_circuit_breaker_config

# Create circuit breaker configuration
circuit_config = create_circuit_breaker_config(
    failure_threshold=5,
    recovery_timeout=60.0
)

# Or create directly
circuit_config = CircuitBreakerConfig(
    failure_threshold=3,
    recovery_timeout=30.0,
    success_threshold=2
)
```

### HTTP Client Usage

#### Basic Usage

```python
from src.utils.web_utils import http_client

# Simple HTTP client
async with http_client(base_url="https://api.example.com") as client:
    response = await client.get("/users")
    data = response.json()
```

#### Advanced Usage with All Features

```python
from src.utils.web_utils import (
    http_client,
    create_retry_config,
    create_rate_limit_config,
    create_circuit_breaker_config
)

# Configure all features
retry_config = create_retry_config(max_attempts=3, base_delay=1.0)
rate_config = create_rate_limit_config(requests_per_second=10.0)
circuit_config = create_circuit_breaker_config(failure_threshold=5)

async with http_client(
    base_url="https://api.example.com",
    timeout=30.0,
    retry_config=retry_config,
    rate_limit_config=rate_config,
    circuit_breaker_config=circuit_config,
    enable_logging=True
) as client:
    # All requests will have retry, rate limiting, and circuit breaker protection
    response = await client.get("/users")
    response = await client.post("/users", json={"name": "John"})
    response = await client.put("/users/1", json={"name": "Jane"})
    response = await client.delete("/users/1")
```

#### Convenience Functions

```python
from src.utils.web_utils import get, post, put, patch, delete

# Simple HTTP requests
response = await get("https://api.example.com/users")
response = await post("https://api.example.com/users", json={"name": "John"})
response = await put("https://api.example.com/users/1", json={"name": "Jane"})
response = await patch("https://api.example.com/users/1", json={"name": "Bob"})
response = await delete("https://api.example.com/users/1")
```

### Individual Components

#### RateLimiter

Token bucket rate limiter implementation.

```python
from src.utils.web_utils import RateLimiter, RateLimitConfig

rate_limiter = RateLimiter(RateLimitConfig(requests_per_second=10.0, burst_size=20))

# Acquire token
if await rate_limiter.acquire():
    # Make request
    pass

# Wait for token
await rate_limiter.wait_for_token()
```

#### CircuitBreaker

Circuit breaker implementation.

```python
from src.utils.web_utils import CircuitBreaker, CircuitBreakerConfig

circuit_breaker = CircuitBreaker(CircuitBreakerConfig(failure_threshold=5))

async def api_call():
    return await some_http_request()

# Execute with circuit breaker protection
try:
    result = await circuit_breaker.call(api_call)
except Exception as e:
    print(f"Request failed: {e}")
```

#### RetryHandler

Retry mechanism with exponential backoff.

```python
from src.utils.web_utils import RetryHandler, RetryConfig

retry_handler = RetryHandler(RetryConfig(max_attempts=3, base_delay=1.0))

async def unreliable_function():
    # This might fail
    return await some_operation()

# Execute with retry
result = await retry_handler.execute_with_retry(unreliable_function)
```

#### RequestLogger

Request/response logging utility.

```python
from src.utils.web_utils import RequestLogger

logger = RequestLogger()

# Log request
await logger.log_request("GET", "https://api.example.com/users")

# Log response
await logger.log_response("GET", "https://api.example.com/users", 200, 0.5)

# Get logs
logs = await logger.get_logs(limit=10)
```

## Integration Example

Here's a complete example showing how to integrate string and web utilities:

```python
import asyncio
from src.utils.string_utils import sanitize_text, create_slug, detect_text_language
from src.utils.web_utils import http_client, create_retry_config

async def process_user_content(user_input: str):
    """Process user content and send to API."""

    # Sanitize user input
    clean_content = sanitize_text(user_input)

    # Generate slug
    slug = create_slug(clean_content)

    # Detect language
    language = detect_text_language(clean_content)

    # Prepare API payload
    payload = {
        "content": clean_content,
        "slug": slug,
        "language": language,
        "metadata": {
            "original_length": len(user_input),
            "cleaned_length": len(clean_content)
        }
    }

    # Send to API with retry protection
    retry_config = create_retry_config(max_attempts=3, base_delay=1.0)

    async with http_client(
        base_url="https://api.example.com",
        retry_config=retry_config
    ) as client:
        response = await client.post("/content", json=payload)
        return response.json()

# Usage
async def main():
    user_input = """
    <script>alert('xss')</script>
    Hello World! This is my blog post about Python programming.
    """

    result = await process_user_content(user_input)
    print(f"Processed content ID: {result['id']}")

asyncio.run(main())
```

## Testing

Both utility modules include comprehensive test suites:

```bash
# Run string utility tests
pytest tests/test_utils/test_string_utils.py -v

# Run web utility tests
pytest tests/test_utils/test_web_utils.py -v

# Run all utility tests
pytest tests/test_utils/ -v
```

## Performance Considerations

### String Utilities

- Unicode normalization can be expensive for large texts
- Template processing with many variables may impact performance
- Language detection is basic and may not be suitable for production use

### Web Utilities

- Rate limiting adds minimal overhead
- Circuit breaker state is maintained in memory
- Retry mechanisms can significantly increase request time
- Connection pooling reduces connection overhead

## Security Considerations

### String Utilities

- HTML sanitization is basic and may not catch all XSS vectors
- SQL injection detection is pattern-based and may have false positives/negatives
- Always use parameterized queries for database operations

### Web Utilities

- Circuit breaker state is not persisted across restarts
- Rate limiting is per-process and not shared across instances
- Request logging may contain sensitive data

## Dependencies

The utilities use the following dependencies (already included in requirements):

- `httpx` - HTTP client library
- `unicodedata` - Unicode normalization (built-in)
- `re` - Regular expressions (built-in)
- `asyncio` - Asynchronous programming (built-in)

## Future Enhancements

Potential improvements for future versions:

### String Utilities

- More sophisticated HTML sanitization
- Advanced language detection
- Text similarity and fuzzy matching
- Advanced template engines integration

### Web Utilities

- Distributed rate limiting with Redis
- Persistent circuit breaker state
- Advanced retry strategies
- Request/response compression
- HTTP/2 support optimization

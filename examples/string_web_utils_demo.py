#!/usr/bin/env python3
"""
Demo script showing how to use the new string and web utilities.

This script demonstrates:
- String sanitization and validation
- Slug generation
- Text normalization
- Template processing
- Multi-language text handling
- HTTP client with retry, rate limiting, and circuit breaker
"""

import asyncio
import logging

from src.utils.string_utils import (
    MultiLanguageHandler,
    SlugGenerator,
    StringSanitizer,
    TemplateProcessor,
    TextNormalizer,
    create_slug,
    detect_text_language,
    normalize_text,
    process_template_string,
    sanitize_text,
)
from src.utils.web_utils import (
    HTTPClientManager,
    create_circuit_breaker_config,
    create_rate_limit_config,
    create_retry_config,
    get,
    http_client,
    post,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demo_string_utilities():
    """Demonstrate string utility functions."""
    print("=== String Utilities Demo ===\n")

    # 1. Text Sanitization
    print("1. Text Sanitization:")
    dirty_html = """
    <p>Safe content</p>
    <script>alert('xss')</script>
    <a href="javascript:alert('xss')">Dangerous link</a>
    """
    clean_text = StringSanitizer.sanitize_html(dirty_html)
    print(f"Original: {dirty_html.strip()}")
    print(f"Sanitized: {clean_text}")
    print()

    # 2. SQL Injection Detection
    print("2. SQL Injection Detection:")
    safe_input = "SELECT * FROM users WHERE name = 'John'"
    dangerous_input = "'; DROP TABLE users; --"
    print(f"Safe input detected: {StringSanitizer.detect_sql_injection(safe_input)}")
    print(
        f"Dangerous input detected: {StringSanitizer.detect_sql_injection(dangerous_input)}"
    )
    print()

    # 3. Slug Generation
    print("3. Slug Generation:")
    titles = [
        "Hello World!",
        "Café & Résumé",
        "This is a very long title that should be truncated",
        "Special Characters: !@#$%^&*()",
    ]
    for title in titles:
        slug = SlugGenerator.generate_slug(title, max_length=30)
        print(f"'{title}' -> '{slug}'")
    print()

    # 4. Text Normalization
    print("4. Text Normalization:")
    messy_text = "  Hello   World  \n\n  Café  "
    normalized = TextNormalizer.clean_text(messy_text, remove_punctuation=True)
    print(f"Original: '{messy_text}'")
    print(f"Normalized: '{normalized}'")
    print()

    # 5. Template Processing
    print("5. Template Processing:")
    template = "Hello {name}, you have {count} new messages from {sender}."
    variables = {"name": "Alice", "count": 5, "sender": "Bob"}
    result = TemplateProcessor.process_template(template, variables)
    print(f"Template: {template}")
    print(f"Variables: {variables}")
    print(f"Result: {result}")
    print()

    # 6. Language Detection
    print("6. Language Detection:")
    texts = [
        "The quick brown fox jumps over the lazy dog",
        "El zorro marrón rápido salta sobre el perro perezoso",
        "Le renard brun rapide saute par-dessus le chien paresseux",
        "Привет мир",
    ]
    for text in texts:
        language = MultiLanguageHandler.detect_language(text)
        print(f"'{text}' -> Language: {language}")
    print()

    # 7. Convenience Functions
    print("7. Convenience Functions:")
    dirty_text = "<script>alert('xss')</script>Hello World"
    clean = sanitize_text(dirty_text)
    slug = create_slug("Hello World!")
    normalized = normalize_text("  Hello   World  ")
    template_result = process_template_string("Hello {name}!", name="World")
    language = detect_text_language("Hello World")

    print(f"sanitize_text: '{clean}'")
    print(f"create_slug: '{slug}'")
    print(f"normalize_text: '{normalized}'")
    print(f"process_template_string: '{template_result}'")
    print(f"detect_text_language: '{language}'")
    print()


async def demo_web_utilities():
    """Demonstrate web utility functions."""
    print("=== Web Utilities Demo ===\n")

    # 1. Configuration Creation
    print("1. Configuration Creation:")
    retry_config = create_retry_config(max_attempts=3, base_delay=1.0)
    rate_limit_config = create_rate_limit_config(requests_per_second=5.0, burst_size=10)
    circuit_config = create_circuit_breaker_config(
        failure_threshold=3, recovery_timeout=30.0
    )

    print(f"Retry config: {retry_config}")
    print(f"Rate limit config: {rate_limit_config}")
    print(f"Circuit breaker config: {circuit_config}")
    print()

    # 2. HTTP Client with Advanced Features
    print("2. HTTP Client with Advanced Features:")
    async with http_client(
        base_url="https://httpbin.org",
        timeout=10.0,
        retry_config=retry_config,
        rate_limit_config=rate_limit_config,
        circuit_breaker_config=circuit_config,
        enable_logging=True,
    ) as client:
        try:
            # Make a GET request
            response = await client.get("/get")
            print(f"GET /get - Status: {response.status_code}")

            # Make a POST request
            response = await client.post("/post", json={"message": "Hello World"})
            print(f"POST /post - Status: {response.status_code}")

        except Exception as e:
            print(f"Request failed: {e}")
    print()

    # 3. Convenience Functions
    print("3. Convenience Functions:")
    try:
        # Simple GET request
        response = await get("https://httpbin.org/get")
        print(f"Simple GET - Status: {response.status_code}")

        # Simple POST request
        response = await post("https://httpbin.org/post", json={"test": "data"})
        print(f"Simple POST - Status: {response.status_code}")

    except Exception as e:
        print(f"Convenience request failed: {e}")
    print()


async def demo_integration():
    """Demonstrate integration between string and web utilities."""
    print("=== Integration Demo ===\n")

    # Simulate processing user input and making API calls
    user_input = """
    <script>alert('xss')</script>
    Hello World! This is a test message.
    Please process this: '; DROP TABLE users; --
    """

    print("1. Processing User Input:")
    print(f"Original input: {user_input.strip()}")

    # Sanitize the input
    clean_input = sanitize_text(user_input)
    print(f"Sanitized input: {clean_input}")

    # Check for SQL injection
    if StringSanitizer.detect_sql_injection(user_input):
        print("⚠️  SQL injection attempt detected!")

    # Generate a slug for the content
    slug = create_slug(clean_input, max_length=50)
    print(f"Generated slug: {slug}")

    # Normalize for search
    search_text = normalize_text(clean_input, remove_accents=True)
    print(f"Search normalized: {search_text}")

    # Detect language
    language = detect_text_language(clean_input)
    print(f"Detected language: {language}")

    print("\n2. Making API Call with Processed Data:")

    # Create a template for API payload
    template = """
    {
        "content": "{content}",
        "slug": "{slug}",
        "language": "{language}",
        "timestamp": "{timestamp}"
    }
    """

    import time

    payload = process_template_string(
        template,
        content=clean_input,
        slug=slug,
        language=language or "unknown",
        timestamp=int(time.time()),
    )

    print(f"API payload: {payload}")

    # Make API call with retry and rate limiting
    try:
        async with http_client(
            base_url="https://httpbin.org",
            retry_config=create_retry_config(max_attempts=2, base_delay=0.5),
            rate_limit_config=create_rate_limit_config(requests_per_second=2.0),
        ) as client:
            response = await client.post(
                "/post", json=payload, headers={"Content-Type": "application/json"}
            )
            print(f"API call successful - Status: {response.status_code}")

    except Exception as e:
        print(f"API call failed: {e}")


async def main():
    """Main demo function."""
    print("String and Web Utilities Demo")
    print("=" * 50)
    print()

    # Run string utilities demo
    demo_string_utilities()

    # Run web utilities demo
    await demo_web_utilities()

    # Run integration demo
    await demo_integration()

    print("Demo completed!")


if __name__ == "__main__":
    asyncio.run(main())

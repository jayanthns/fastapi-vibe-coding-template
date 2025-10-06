"""
Utility modules for the FastAPI application.

This package contains various utility functions and helpers used throughout
the application, including security, logging, string processing, web utilities,
and other common functionality.
"""

from src.utils.security import (
    create_masked_response,
    mask_credentials,
    mask_sensitive_data,
    mask_urls,
    public_response,
    secure_response,
)

from src.utils.string_utils import (
    StringSanitizer,
    SlugGenerator,
    TextNormalizer,
    TemplateProcessor,
    MultiLanguageHandler,
    sanitize_text,
    create_slug,
    normalize_text,
    process_template_string,
    detect_text_language,
)

from src.utils.web_utils import (
    HTTPClientManager,
    RetryConfig,
    RateLimitConfig,
    CircuitBreakerConfig,
    http_client,
    make_request,
    get,
    post,
    put,
    patch,
    delete,
    create_retry_config,
    create_rate_limit_config,
    create_circuit_breaker_config,
)

__all__ = [
    # Security utilities
    "mask_sensitive_data",
    "create_masked_response",
    "secure_response",
    "public_response",
    "mask_urls",
    "mask_credentials",
    # String utilities
    "StringSanitizer",
    "SlugGenerator",
    "TextNormalizer",
    "TemplateProcessor",
    "MultiLanguageHandler",
    "sanitize_text",
    "create_slug",
    "normalize_text",
    "process_template_string",
    "detect_text_language",
    # Web utilities
    "HTTPClientManager",
    "RetryConfig",
    "RateLimitConfig",
    "CircuitBreakerConfig",
    "http_client",
    "make_request",
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "create_retry_config",
    "create_rate_limit_config",
    "create_circuit_breaker_config",
]

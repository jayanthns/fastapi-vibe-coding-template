"""
Security utilities for masking sensitive information in API responses.

This module provides generic masking functions that can be used across
all API endpoints to protect sensitive data based on configuration flags.
"""

import re
from typing import Any, Dict


def mask_sensitive_data(data: Any, mask: bool = False) -> Any:
    """
    Recursively mask sensitive data in response objects.

    Args:
        data: The data to potentially mask
        mask: Whether to apply masking (default: False)

    Returns:
        Masked data if mask=True, original data otherwise
    """
    if not mask:
        return data

    if isinstance(data, dict):
        return _mask_dict(data)
    elif isinstance(data, list):
        return [mask_sensitive_data(item, mask) for item in data]
    elif isinstance(data, str):
        return _mask_string(data)
    else:
        return data


def _mask_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive fields in a dictionary."""
    masked_data = {}

    for key, value in data.items():
        key_lower = key.lower()

        # Check if this is a sensitive field
        if _is_sensitive_field(key_lower):
            masked_data[key] = _mask_value_by_type(value)
        elif isinstance(value, (dict, list)):
            masked_data[key] = mask_sensitive_data(value, True)
        else:
            masked_data[key] = value

    return masked_data


def _is_sensitive_field(field_name: str) -> bool:
    """Check if a field name indicates sensitive data."""
    field_lower = field_name.lower()

    # Exclude common non-sensitive field patterns first
    non_sensitive_patterns = [
        "cache_type",
        "use_redis",
        "redis_type",
        "cache_status",
        "redis_status",
        "cache_enabled",
        "redis_enabled",
        "cache_mode",
        "redis_mode",
        "cache_config",
        "redis_config",
    ]

    # If it matches a non-sensitive pattern, it's not sensitive
    if any(pattern in field_lower for pattern in non_sensitive_patterns):
        return False

    # Check for specific sensitive patterns
    sensitive_patterns = [
        # Authentication & Credentials
        "password",
        "passwd",
        "pwd",
        "secret",
        "token",
        "auth",
        "credential",
        "api_key",
        "access_key",
        "secret_key",
        "private_key",
        "jwt",
        # URLs & Connections
        "url",
        "uri",
        "endpoint",
        "host",
        "server",
        "connection",
        "connection_string",
        "dsn",
        # Personal Information
        "email",
        "phone",
        "ssn",
        "social_security",
        "credit_card",
        "card_number",
        "bank_account",
        "routing_number",
        # Infrastructure
        "ip",
        "address",
        "hostname",
        "domain",
        "instance",
        # Database & Cache (only when they indicate actual sensitive data)
        "database_url",
        "redis_url",
        "cache_url",
        "db_url",
        "database_password",
        "redis_password",
        "cache_password",
        "db_password",
        "database_secret",
        "redis_secret",
        "cache_secret",
        "db_secret",
        "database_token",
        "redis_token",
        "cache_token",
        "db_token",
        "database_key",
        "redis_key",
        "cache_key",
        "db_key",
    ]

    # Check for exact matches
    return field_lower in sensitive_patterns


def _mask_value_by_type(value: Any) -> str:
    """Mask a value based on its type and content."""
    if isinstance(value, str):
        return _mask_string(value)
    elif isinstance(value, (int, float)):
        return "***"
    elif isinstance(value, bool):
        return "***"
    elif isinstance(value, (dict, list)):
        return mask_sensitive_data(value, True)
    else:
        return "***"


def _mask_string(value: str) -> str:
    """Mask sensitive information in a string."""
    if not value or len(value) < 3:
        return "***"

    # URL masking
    if "://" in value:
        return _mask_url(value)

    # Email masking
    if "@" in value and "." in value:
        return _mask_email(value)

    # IP address masking
    if _is_ip_address(value):
        return _mask_ip_address(value)

    # Domain masking
    if "." in value and not value.startswith("http"):
        return _mask_domain(value)

    # Generic string masking (keep first and last char)
    if len(value) <= 4:
        return "*" * len(value)
    else:
        return f"{value[0]}{'*' * (len(value) - 2)}{value[-1]}"


def _mask_url(url: str) -> str:
    """Mask sensitive information in URLs."""
    if "://" not in url:
        return "***"

    protocol, rest = url.split("://", 1)

    if "@" in rest:
        # URL has authentication: protocol://user:pass@host:port/path
        auth_part, host_part = rest.split("@", 1)

        # Mask host details
        if ":" in host_part:
            host, port_path = host_part.split(":", 1)
            if "/" in port_path:
                port, path = port_path.split("/", 1)
                masked_host = _mask_host(host)
                return f"{protocol}://***:***@{masked_host}:{port}/{path}"
            else:
                masked_host = _mask_host(host)
                return f"{protocol}://***:***@{masked_host}:{port_path}"
        else:
            masked_host = _mask_host(host_part)
            return f"{protocol}://***:***@{masked_host}"
    else:
        # No authentication: protocol://host:port/path
        if ":" in rest:
            host, port_path = rest.split(":", 1)
            if "/" in port_path:
                port, path = port_path.split("/", 1)
                masked_host = _mask_host(host)
                return f"{protocol}://{masked_host}:{port}/{path}"
            else:
                masked_host = _mask_host(host)
                return f"{protocol}://{masked_host}:{port_path}"
        else:
            masked_host = _mask_host(rest)
            return f"{protocol}://{masked_host}"


def _mask_email(email: str) -> str:
    """Mask email addresses."""
    if "@" not in email:
        return "***"

    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = f"{local[0]}{'*' * (len(local) - 2)}{local[-1]}"

    masked_domain = _mask_domain(domain)
    return f"{masked_local}@{masked_domain}"


def _mask_ip_address(ip: str) -> str:
    """Mask IP addresses."""
    if ":" in ip and not ip.startswith("["):
        # IPv6 address
        return "[***]"
    elif "." in ip:
        # IPv4 address
        parts = ip.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.***.***"
        return "***.***.***.***"
    else:
        return "***"


def _mask_domain(domain: str) -> str:
    """Mask domain names."""
    if "." not in domain:
        return "***"

    parts = domain.split(".")
    if len(parts) >= 2:
        return f"***.{'.'.join(parts[-2:])}"
    return "***"


def _mask_host(host: str) -> str:
    """Mask host information for security."""
    if not host:
        return "***"

    # Handle localhost and 127.0.0.1 (keep for development)
    if host in ["localhost", "127.0.0.1"]:
        return host

    # Handle IP addresses
    if _is_ip_address(host):
        return _mask_ip_address(host)

    # Handle domains
    if "." in host:
        return _mask_domain(host)

    # Handle other hostnames
    return "***"


def _is_ip_address(host: str) -> bool:
    """Check if a string is an IP address."""
    # IPv4 pattern
    ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if re.match(ipv4_pattern, host):
        return True

    # IPv6 pattern (simplified)
    if ":" in host and not host.startswith("["):
        return True

    return False


def create_masked_response(data: Any, mask: bool = False, **kwargs) -> Dict[str, Any]:
    """
    Create a response with optional data masking.

    Args:
        data: The response data
        mask: Whether to apply masking (default: False)
        **kwargs: Additional response fields

    Returns:
        Response dictionary with potentially masked data
    """
    response = {"data": mask_sensitive_data(data, mask), "masked": mask, **kwargs}

    if mask:
        response["security_note"] = (
            "Sensitive information has been masked for security. "
            "Set mask=false to see actual values (development only)."
        )

    return response


def secure_response(data: Any, **kwargs) -> Dict[str, Any]:
    """
    Create a secure response with automatic data masking.

    This is a convenience function for developers who want to always
    mask sensitive data in their responses.

    Args:
        data: The response data to mask
        **kwargs: Additional response fields

    Returns:
        Response dictionary with masked data
    """
    return create_masked_response(data, mask=True, **kwargs)


def public_response(data: Any, **kwargs) -> Dict[str, Any]:
    """
    Create a public response without data masking.

    This is a convenience function for developers who want to return
    data without any masking (use with caution).

    Args:
        data: The response data (not masked)
        **kwargs: Additional response fields

    Returns:
        Response dictionary with original data
    """
    return create_masked_response(data, mask=False, **kwargs)


# Convenience functions for common masking scenarios
def mask_urls(data: Any, mask: bool = False) -> Any:
    """Mask URLs in data."""
    if not mask:
        return data

    if isinstance(data, str) and "://" in data:
        return _mask_url(data)
    elif isinstance(data, dict):
        return {k: mask_urls(v, mask) for k, v in data.items()}
    elif isinstance(data, list):
        return [mask_urls(item, mask) for item in data]
    else:
        return data


def mask_credentials(data: Any, mask: bool = False) -> Any:
    """Mask credential fields in data."""
    if not mask:
        return data

    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if _is_sensitive_field(key.lower()):
                masked[key] = "***"
            else:
                masked[key] = mask_credentials(value, mask)
        return masked
    elif isinstance(data, list):
        return [mask_credentials(item, mask) for item in data]
    else:
        return data

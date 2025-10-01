"""
Unit tests for app.utils.security module.

Tests all security utility functions including masking, field detection,
and response helpers.
"""

import pytest

from app.utils.security import (
    _is_ip_address,
    _is_sensitive_field,
    _mask_domain,
    _mask_email,
    _mask_host,
    _mask_ip_address,
    _mask_string,
    _mask_url,
    create_masked_response,
    mask_credentials,
    mask_sensitive_data,
    mask_urls,
    public_response,
    secure_response,
)


class TestMaskSensitiveData:
    """Test the main mask_sensitive_data function."""

    def test_mask_disabled_returns_original_data(self):
        """Test that when mask=False, original data is returned unchanged."""
        data = {"password": "secret123", "api_key": "sk-1234567890"}
        result = mask_sensitive_data(data, mask=False)
        assert result == data

    def test_mask_enabled_masks_sensitive_fields(self):
        """Test that when mask=True, sensitive fields are masked."""
        data = {
            "password": "secret123",
            "api_key": "sk-1234567890",
            "normal_field": "this is normal",
        }
        result = mask_sensitive_data(data, mask=True)

        assert result["password"] == "s*******3"
        assert result["api_key"] == "s***********0"
        assert result["normal_field"] == "this is normal"

    def test_mask_nested_structures(self):
        """Test masking in nested dictionaries and lists."""
        data = {
            "user": {"password": "secret123", "profile": {"api_key": "sk-1234567890"}},
            "tokens": ["token1", "token2"],
            "normal_field": "safe",
        }
        result = mask_sensitive_data(data, mask=True)

        assert result["user"]["password"] == "s*******3"
        assert result["user"]["profile"]["api_key"] == "s***********0"
        assert result["tokens"] == ["t****1", "t****2"]
        assert result["normal_field"] == "safe"

    def test_mask_list_of_objects(self):
        """Test masking in list of objects."""
        data = [
            {"password": "secret1", "name": "user1"},
            {"password": "secret2", "name": "user2"},
        ]
        result = mask_sensitive_data(data, mask=True)

        assert result[0]["password"] == "s*****1"
        assert result[0]["name"] == "user1"
        assert result[1]["password"] == "s*****2"
        assert result[1]["name"] == "user2"

    def test_mask_string_values(self):
        """Test masking of string values."""
        result = mask_sensitive_data("password123", mask=True)
        assert result == "p*********3"

    def test_mask_non_sensitive_data_types(self):
        """Test that non-sensitive data types are not masked."""
        data = {"number": 123, "boolean": True, "none_value": None, "float_value": 3.14}
        result = mask_sensitive_data(data, mask=True)

        assert result["number"] == 123
        assert result["boolean"] is True
        assert result["none_value"] is None
        assert result["float_value"] == 3.14


class TestIsSensitiveField:
    """Test the _is_sensitive_field function."""

    def test_sensitive_field_patterns(self):
        """Test that sensitive field patterns are detected."""
        sensitive_fields = [
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
            "email",
            "phone",
            "ssn",
            "social_security",
            "credit_card",
            "card_number",
            "bank_account",
            "routing_number",
            "url",
            "uri",
            "endpoint",
            "host",
            "server",
            "connection",
            "ip",
            "address",
            "hostname",
            "domain",
            "instance",
            "connection_string",
            "dsn",
        ]

        for field in sensitive_fields:
            assert (
                _is_sensitive_field(field) is True
            ), f"Field '{field}' should be sensitive"

    def test_non_sensitive_field_patterns(self):
        """Test that non-sensitive field patterns are not detected."""
        non_sensitive_fields = [
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
            "name",
            "title",
            "description",
            "id",
            "count",
            "total",
            "status",
            "type",
            "value",
            "data",
            "result",
            "response",
        ]

        for field in non_sensitive_fields:
            assert (
                _is_sensitive_field(field) is False
            ), f"Field '{field}' should not be sensitive"

    def test_case_insensitive_detection(self):
        """Test that field detection is case insensitive."""
        assert _is_sensitive_field("PASSWORD") is True
        assert _is_sensitive_field("Api_Key") is True
        assert _is_sensitive_field("CACHE_TYPE") is False
        assert _is_sensitive_field("Use_Redis") is False


class TestMaskString:
    """Test the _mask_string function."""

    def test_short_strings(self):
        """Test masking of short strings."""
        assert _mask_string("a") == "***"
        assert _mask_string("ab") == "***"
        assert _mask_string("abc") == "***"

    def test_medium_strings(self):
        """Test masking of medium strings."""
        assert _mask_string("password") == "p******d"
        assert _mask_string("secret123") == "s*******3"
        assert _mask_string("api_key") == "a*****y"

    def test_long_strings(self):
        """Test masking of long strings."""
        long_string = "a" * 20
        result = _mask_string(long_string)
        assert result == "a" + "*" * 18 + "a"
        assert len(result) == len(long_string)

    def test_empty_string(self):
        """Test masking of empty string."""
        assert _mask_string("") == "***"

    def test_single_character(self):
        """Test masking of single character."""
        assert _mask_string("a") == "***"


class TestMaskUrl:
    """Test the _mask_url function."""

    def test_url_with_credentials(self):
        """Test masking of URL with username and password."""
        url = "redis://user:pass@localhost:6379/0"
        result = _mask_url(url)
        assert result == "redis://***:***@localhost:6379/0"

    def test_url_with_password_only(self):
        """Test masking of URL with password only."""
        url = "redis://:password@localhost:6379/0"
        result = _mask_url(url)
        assert result == "redis://***:***@localhost:6379/0"

    def test_url_without_credentials(self):
        """Test URL without credentials (should not be masked)."""
        url = "redis://localhost:6379/0"
        result = _mask_url(url)
        assert result == url

    def test_https_url_with_credentials(self):
        """Test masking of HTTPS URL with credentials."""
        url = "https://user:pass@api.example.com/path"
        result = _mask_url(url)
        assert result == "https://***:***@***.example.com/path"

    def test_url_with_ip_address(self):
        """Test masking of URL with IP address."""
        url = "redis://user:pass@192.168.1.100:6379/0"
        result = _mask_url(url)
        assert result == "redis://***:***@192.168.***.***:6379/0"

    def test_url_with_domain(self):
        """Test masking of URL with domain name."""
        url = "redis://user:pass@redis.example.com:6379/0"
        result = _mask_url(url)
        assert result == "redis://***:***@***.example.com:6379/0"


class TestMaskEmail:
    """Test the _mask_email function."""

    def test_valid_email(self):
        """Test masking of valid email address."""
        email = "user@example.com"
        result = _mask_email(email)
        assert result == "u**r@***.example.com"

    def test_long_email(self):
        """Test masking of long email address."""
        email = "verylongusername@verylongdomainname.com"
        result = _mask_email(email)
        assert result == "v**************e@***.verylongdomainname.com"

    def test_short_email(self):
        """Test masking of short email address."""
        email = "a@b.c"
        result = _mask_email(email)
        assert result == "*@***.b.c"

    def test_invalid_email_format(self):
        """Test that invalid email formats are masked appropriately."""
        test_cases = [
            ("notanemail", "***"),
            ("@example.com", "@***.example.com"),
            ("user@", "u**r@***"),
            ("user@.com", "u**r@***..com"),
        ]
        for email, expected in test_cases:
            result = _mask_email(email)
            assert (
                result == expected
            ), f"Email '{email}' should be '{expected}', got '{result}'"


class TestMaskIpAddress:
    """Test the _mask_ip_address function."""

    def test_ipv4_address(self):
        """Test masking of IPv4 address."""
        ip = "192.168.1.100"
        result = _mask_ip_address(ip)
        assert result == "192.168.***.***"

    def test_ipv6_address(self):
        """Test masking of IPv6 address."""
        ip = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        result = _mask_ip_address(ip)
        assert result == "[***]"

    def test_short_ipv4(self):
        """Test masking of short IPv4 address."""
        ip = "1.2.3.4"
        result = _mask_ip_address(ip)
        assert result == "1.2.***.***"

    def test_invalid_ip_format(self):
        """Test that invalid IP formats are masked appropriately."""
        test_cases = [("notanip", "***"), ("1.2.3", "***.***.***.***")]
        for ip, expected in test_cases:
            result = _mask_ip_address(ip)
            assert (
                result == expected
            ), f"IP '{ip}' should be '{expected}', got '{result}'"


class TestMaskDomain:
    """Test the _mask_domain function."""

    def test_simple_domain(self):
        """Test masking of simple domain."""
        domain = "example.com"
        result = _mask_domain(domain)
        assert result == "***.example.com"

    def test_subdomain(self):
        """Test masking of subdomain."""
        domain = "api.example.com"
        result = _mask_domain(domain)
        assert result == "***.example.com"

    def test_complex_domain(self):
        """Test masking of complex domain."""
        domain = "very.long.subdomain.example.com"
        result = _mask_domain(domain)
        assert result == "***.example.com"

    def test_single_label_domain(self):
        """Test masking of single label domain."""
        domain = "localhost"
        result = _mask_domain(domain)
        assert result == "***"  # localhost is masked


class TestMaskHost:
    """Test the _mask_host function."""

    def test_ip_address_host(self):
        """Test masking of IP address host."""
        host = "192.168.1.100"
        result = _mask_host(host)
        assert result == "192.168.***.***"

    def test_domain_host(self):
        """Test masking of domain host."""
        host = "api.example.com"
        result = _mask_host(host)
        assert result == "***.example.com"

    def test_localhost_host(self):
        """Test that localhost is not masked."""
        host = "localhost"
        result = _mask_host(host)
        assert result == "localhost"

    def test_ipv6_host(self):
        """Test masking of IPv6 host."""
        host = "2001:0db8::1"
        result = _mask_host(host)
        assert result == "[***]"


class TestIsIpAddress:
    """Test the _is_ip_address function."""

    def test_valid_ipv4_addresses(self):
        """Test detection of valid IPv4 addresses."""
        valid_ips = [
            "192.168.1.1",
            "127.0.0.1",
            "0.0.0.0",
            "255.255.255.255",
            "10.0.0.1",
        ]
        for ip in valid_ips:
            assert _is_ip_address(ip) is True, f"IP '{ip}' should be detected as IPv4"

    def test_valid_ipv6_addresses(self):
        """Test detection of valid IPv6 addresses."""
        valid_ips = [
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "::1",
            "2001:db8::1",
            "fe80::1%lo0",
        ]
        for ip in valid_ips:
            assert _is_ip_address(ip) is True, f"IP '{ip}' should be detected as IPv6"

    def test_invalid_ip_addresses(self):
        """Test detection of invalid IP addresses."""
        invalid_ips = [
            "notanip",
            "1.2.3",
            "localhost",
            "example.com",
            "192.168.1.1.1",
        ]
        for ip in invalid_ips:
            assert (
                _is_ip_address(ip) is False
            ), f"IP '{ip}' should not be detected as valid IP"


class TestCreateMaskedResponse:
    """Test the create_masked_response function."""

    def test_masked_response(self):
        """Test creating a masked response."""
        data = {"password": "secret123", "name": "John"}
        result = create_masked_response(data, mask=True)

        assert result["data"]["password"] == "s*******3"
        assert result["data"]["name"] == "John"
        assert result["masked"] is True
        assert "security_note" in result

    def test_unmasked_response(self):
        """Test creating an unmasked response."""
        data = {"password": "secret123", "name": "John"}
        result = create_masked_response(data, mask=False)

        assert result["data"]["password"] == "secret123"
        assert result["data"]["name"] == "John"
        assert result["masked"] is False
        assert "security_note" not in result

    def test_with_additional_kwargs(self):
        """Test creating response with additional keyword arguments."""
        data = {"password": "secret123"}
        result = create_masked_response(data, mask=True, status="success", code=200)

        assert result["data"]["password"] == "s*******3"
        assert result["status"] == "success"
        assert result["code"] == 200
        assert result["masked"] is True


class TestSecureResponse:
    """Test the secure_response function."""

    def test_secure_response_always_masks(self):
        """Test that secure_response always applies masking."""
        data = {"password": "secret123", "name": "John"}
        result = secure_response(data)

        assert result["data"]["password"] == "s*******3"
        assert result["data"]["name"] == "John"
        assert result["masked"] is True
        assert "security_note" in result

    def test_secure_response_with_kwargs(self):
        """Test secure_response with additional keyword arguments."""
        data = {"api_key": "sk-1234567890"}
        result = secure_response(data, status="error", code=500)

        assert result["data"]["api_key"] == "s***********0"
        assert result["status"] == "error"
        assert result["code"] == 500
        assert result["masked"] is True


class TestPublicResponse:
    """Test the public_response function."""

    def test_public_response_never_masks(self):
        """Test that public_response never applies masking."""
        data = {"password": "secret123", "name": "John"}
        result = public_response(data)

        assert result["data"]["password"] == "secret123"
        assert result["data"]["name"] == "John"
        assert result["masked"] is False
        assert "security_note" not in result

    def test_public_response_with_kwargs(self):
        """Test public_response with additional keyword arguments."""
        data = {"api_key": "sk-1234567890"}
        result = public_response(data, status="success", code=200)

        assert result["data"]["api_key"] == "sk-1234567890"
        assert result["status"] == "success"
        assert result["code"] == 200
        assert result["masked"] is False


class TestMaskUrls:
    """Test the mask_urls function."""

    def test_mask_urls_enabled(self):
        """Test mask_urls when masking is enabled."""
        data = {
            "redis_url": "redis://user:pass@localhost:6379/0",
            "api_url": "https://api.example.com/endpoint",
            "normal_field": "safe",
        }
        result = mask_urls(data, mask=True)

        assert result["redis_url"] == "redis://***:***@localhost:6379/0"
        assert (
            result["api_url"] == "https://***.example.com/endpoint"
        )  # Domain is masked
        assert result["normal_field"] == "safe"

    def test_mask_urls_disabled(self):
        """Test mask_urls when masking is disabled."""
        data = {
            "redis_url": "redis://user:pass@localhost:6379/0",
            "normal_field": "safe",
        }
        result = mask_urls(data, mask=False)

        assert result["redis_url"] == "redis://user:pass@localhost:6379/0"
        assert result["normal_field"] == "safe"

    def test_mask_urls_nested_structures(self):
        """Test mask_urls with nested structures."""
        data = {
            "config": {
                "database_url": "postgresql://user:pass@localhost:5432/db",
                "redis_url": "redis://:password@localhost:6379/0",
            },
            "urls": ["https://api.example.com", "redis://user:pass@localhost:6379/0"],
        }
        result = mask_urls(data, mask=True)

        assert (
            result["config"]["database_url"] == "postgresql://***:***@localhost:5432/db"
        )
        assert result["config"]["redis_url"] == "redis://***:***@localhost:6379/0"
        assert result["urls"][0] == "https://***.example.com"
        assert result["urls"][1] == "redis://***:***@localhost:6379/0"


class TestMaskCredentials:
    """Test the mask_credentials function."""

    def test_mask_credentials_enabled(self):
        """Test mask_credentials when masking is enabled."""
        data = {
            "password": "secret123",
            "api_key": "sk-1234567890",
            "token": "bearer_token_123",
            "normal_field": "safe",
        }
        result = mask_credentials(data, mask=True)

        assert result["password"] == "***"
        assert result["api_key"] == "***"
        assert result["token"] == "***"
        assert result["normal_field"] == "safe"

    def test_mask_credentials_disabled(self):
        """Test mask_credentials when masking is disabled."""
        data = {
            "password": "secret123",
            "api_key": "sk-1234567890",
            "normal_field": "safe",
        }
        result = mask_credentials(data, mask=False)

        assert result["password"] == "secret123"
        assert result["api_key"] == "sk-1234567890"
        assert result["normal_field"] == "safe"

    def test_mask_credentials_nested_structures(self):
        """Test mask_credentials with nested structures."""
        data = {
            "user": {"password": "secret123", "profile": {"api_key": "sk-1234567890"}},
            "tokens": ["token1", "token2"],
            "normal_field": "safe",
        }
        result = mask_credentials(data, mask=True)

        assert result["user"]["password"] == "***"
        assert result["user"]["profile"]["api_key"] == "***"
        assert result["tokens"] == ["token1", "token2"]
        assert result["normal_field"] == "safe"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_data_structures(self):
        """Test handling of empty data structures."""
        empty_data = {}
        result = mask_sensitive_data(empty_data, mask=True)
        assert result == {}

        empty_list = []
        result = mask_sensitive_data(empty_list, mask=True)
        assert result == []

    def test_none_values(self):
        """Test handling of None values."""
        data = {"password": None, "api_key": "sk-1234567890"}
        result = mask_sensitive_data(data, mask=True)

        assert result["password"] == "***"
        assert result["api_key"] == "s***********0"

    def test_boolean_values(self):
        """Test handling of boolean values."""
        data = {"enabled": True, "disabled": False, "password": "secret123"}
        result = mask_sensitive_data(data, mask=True)

        assert result["enabled"] is True
        assert result["disabled"] is False
        assert result["password"] == "s*******3"

    def test_numeric_values(self):
        """Test handling of numeric values."""
        data = {"count": 42, "price": 99.99, "api_key": "sk-1234567890"}
        result = mask_sensitive_data(data, mask=True)

        assert result["count"] == 42
        assert result["price"] == 99.99
        assert result["api_key"] == "s***********0"

    def test_very_long_sensitive_strings(self):
        """Test handling of very long sensitive strings."""
        long_password = "a" * 1000
        data = {"password": long_password}
        result = mask_sensitive_data(data, mask=True)

        assert result["password"].startswith("a***")
        assert result["password"].endswith("a")
        assert len(result["password"]) == len(long_password)

    def test_mixed_data_types_in_list(self):
        """Test handling of mixed data types in lists."""
        data = [
            "password123",
            {"api_key": "sk-1234567890"},
            ["token1", "token2"],
            42,
            True,
            None,
        ]
        result = mask_sensitive_data(data, mask=True)

        assert result[0] == "p*********3"
        assert result[1]["api_key"] == "s***********0"
        assert result[2] == ["t****1", "t****2"]
        assert result[3] == 42
        assert result[4] is True
        assert result[5] is None

"""
Tests for string utilities module.

This module tests all string utility functions including:
- Text sanitization and validation
- Slug generation
- Text normalization
- Template processing
- Multi-language text handling
"""

import pytest

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


class TestStringSanitizer:
    """Test StringSanitizer class."""

    def test_remove_html_tags(self):
        """Test HTML tag removal."""
        assert StringSanitizer.remove_html_tags("") == ""
        assert StringSanitizer.remove_html_tags("Hello World") == "Hello World"
        assert StringSanitizer.remove_html_tags("<p>Hello</p>") == "Hello"
        assert (
            StringSanitizer.remove_html_tags(
                "<div><p>Hello</p><span>World</span></div>"
            )
            == "HelloWorld"
        )

    def test_remove_script_tags(self):
        """Test script tag removal."""
        html_with_script = """
        <html>
        <head><script>alert('xss')</script></head>
        <body><p>Content</p></body>
        </html>
        """
        result = StringSanitizer.remove_script_tags(html_with_script)
        assert "alert('xss')" not in result
        assert "Content" in result

    def test_sanitize_html(self):
        """Test HTML sanitization."""
        dangerous_html = """
        <p>Safe content</p>
        <script>alert('xss')</script>
        <a href="javascript:alert('xss')">Link</a>
        <img src="data:image/png;base64,...">
        """
        result = StringSanitizer.sanitize_html(dangerous_html)
        assert "alert('xss')" not in result
        assert "javascript:" not in result
        assert "data:" not in result
        assert "Safe content" in result

    def test_sanitize_html_with_allowed_tags(self):
        """Test HTML sanitization with allowed tags."""
        html = "<p>Safe</p><script>Bad</script><div>Also safe</div>"
        result = StringSanitizer.sanitize_html(html, allowed_tags=["p"])
        assert "<p>Safe</p>" in result
        assert "script" not in result
        assert "div" not in result

    def test_detect_sql_injection(self):
        """Test SQL injection detection."""
        assert StringSanitizer.detect_sql_injection("") is False
        assert StringSanitizer.detect_sql_injection("Hello World") is False
        assert StringSanitizer.detect_sql_injection("SELECT * FROM users") is True
        assert StringSanitizer.detect_sql_injection("DROP TABLE users") is True
        assert StringSanitizer.detect_sql_injection("INSERT INTO table") is True

    def test_sanitize_sql_input(self):
        """Test SQL input sanitization."""
        dangerous_input = "'; DROP TABLE users; --"
        result = StringSanitizer.sanitize_sql_input(dangerous_input)
        assert "DROP" not in result
        assert "'" not in result
        assert "--" not in result

    def test_clean_whitespace(self):
        """Test whitespace cleaning."""
        assert StringSanitizer.clean_whitespace("") == ""
        assert StringSanitizer.clean_whitespace("  Hello   World  ") == "Hello World"
        assert (
            StringSanitizer.clean_whitespace("Multiple\n\n\nlines") == "Multiple lines"
        )
        assert StringSanitizer.clean_whitespace("Tab\t\tseparated") == "Tab separated"

    def test_remove_control_characters(self):
        """Test control character removal."""
        text_with_control = "Hello\x00World\x01Test"
        result = StringSanitizer.remove_control_characters(text_with_control)
        assert "\x00" not in result
        assert "\x01" not in result
        assert "Hello" in result
        assert "World" in result
        assert "Test" in result


class TestSlugGenerator:
    """Test SlugGenerator class."""

    def test_generate_slug_basic(self):
        """Test basic slug generation."""
        assert SlugGenerator.generate_slug("") == ""
        assert SlugGenerator.generate_slug("Hello World") == "hello-world"
        assert SlugGenerator.generate_slug("Hello, World!") == "hello-world"
        assert SlugGenerator.generate_slug("Hello---World") == "hello-world"

    def test_generate_slug_with_max_length(self):
        """Test slug generation with length limit."""
        long_text = "This is a very long text that should be truncated"
        result = SlugGenerator.generate_slug(long_text, max_length=20)
        assert len(result) <= 20
        assert result.startswith("this-is-a-very")

    def test_generate_slug_with_custom_separator(self):
        """Test slug generation with custom separator."""
        result = SlugGenerator.generate_slug("Hello World", separator="_")
        assert result == "hello_world"

    def test_generate_slug_preserve_case(self):
        """Test slug generation with case preservation."""
        result = SlugGenerator.generate_slug("Hello World", preserve_case=True)
        assert result == "Hello-World"

    def test_generate_slug_unicode(self):
        """Test slug generation with unicode characters."""
        result = SlugGenerator.generate_slug("Café & Résumé")
        assert result == "cafe-resume"

    def test_generate_unique_slug(self):
        """Test unique slug generation."""
        existing_slugs = ["hello-world", "hello-world-1", "hello-world-2"]
        result = SlugGenerator.generate_unique_slug("Hello World", existing_slugs)
        assert result == "hello-world-3"

    def test_generate_unique_slug_no_conflict(self):
        """Test unique slug generation when no conflict exists."""
        existing_slugs = ["other-slug"]
        result = SlugGenerator.generate_unique_slug("Hello World", existing_slugs)
        assert result == "hello-world"


class TestTextNormalizer:
    """Test TextNormalizer class."""

    def test_normalize_unicode(self):
        """Test unicode normalization."""
        # Test with combining characters
        text = "café"  # é is composed
        result = TextNormalizer.normalize_unicode(text, "NFD")
        assert len(result) > len(text)  # Should be decomposed

        result = TextNormalizer.normalize_unicode(text, "NFC")
        assert result == text  # Should remain composed

    def test_normalize_unicode_invalid_form(self):
        """Test unicode normalization with invalid form."""
        with pytest.raises(ValueError):
            TextNormalizer.normalize_unicode("test", "INVALID")

    def test_remove_accents(self):
        """Test accent removal."""
        assert TextNormalizer.remove_accents("") == ""
        assert TextNormalizer.remove_accents("café") == "cafe"
        assert TextNormalizer.remove_accents("naïve") == "naive"
        assert TextNormalizer.remove_accents("résumé") == "resume"

    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        assert TextNormalizer.normalize_whitespace("") == ""
        assert TextNormalizer.normalize_whitespace("Hello\tWorld") == "Hello World"
        assert (
            TextNormalizer.normalize_whitespace("Multiple\n\nlines") == "Multiple lines"
        )
        assert TextNormalizer.normalize_whitespace("  Spaces  ") == "Spaces"

    def test_clean_text(self):
        """Test text cleaning."""
        dirty_text = "  Hello, World!  \n\n"
        result = TextNormalizer.clean_text(dirty_text)
        assert result == "Hello, World!"

        result_no_punct = TextNormalizer.clean_text(dirty_text, remove_punctuation=True)
        assert result_no_punct == "Hello World"

    def test_truncate_text(self):
        """Test text truncation."""
        long_text = "This is a very long text that needs to be truncated"

        # Basic truncation
        result = TextNormalizer.truncate_text(long_text, 20)
        assert len(result) <= 23  # 20 + "..."
        assert result.endswith("...")

        # Word boundary truncation
        result = TextNormalizer.truncate_text(long_text, 20, word_boundary=True)
        assert " " in result[:-3]  # Should break at word boundary

        # No word boundary
        result = TextNormalizer.truncate_text(long_text, 20, word_boundary=False)
        assert len(result) == 20  # Exactly 20 total (17 chars + "...")

    def test_truncate_text_short(self):
        """Test truncation of short text."""
        short_text = "Short"
        result = TextNormalizer.truncate_text(short_text, 20)
        assert result == short_text  # Should not be truncated


class TestTemplateProcessor:
    """Test TemplateProcessor class."""

    def test_process_template_basic(self):
        """Test basic template processing."""
        template = "Hello {name}, you have {count} messages."
        variables = {"name": "John", "count": 5}
        result = TemplateProcessor.process_template(template, variables)
        assert result == "Hello John, you have 5 messages."

    def test_process_template_safe_mode(self):
        """Test template processing in safe mode."""
        template = "Hello {name}"
        variables = {"name": "<script>alert('xss')</script>"}
        result = TemplateProcessor.process_template(template, variables, safe_mode=True)
        assert "&lt;script&gt;" in result
        assert "alert('xss')" not in result

    def test_process_template_missing_variable(self):
        """Test template processing with missing variable."""
        template = "Hello {name}"
        variables = {"other": "value"}
        with pytest.raises(ValueError, match="Missing template variable"):
            TemplateProcessor.process_template(template, variables)

    def test_extract_template_variables(self):
        """Test template variable extraction."""
        template = "Hello {name}, you have {count} messages from {sender}."
        variables = TemplateProcessor.extract_template_variables(template)
        assert set(variables) == {"name", "count", "sender"}

    def test_extract_template_variables_empty(self):
        """Test variable extraction from empty template."""
        assert TemplateProcessor.extract_template_variables("") == []
        assert TemplateProcessor.extract_template_variables("No variables") == []

    def test_validate_template(self):
        """Test template validation."""
        template = "Hello {name}, you have {count} messages."
        required = ["name", "count"]
        assert TemplateProcessor.validate_template(template, required) is True

        required = ["name", "count", "missing"]
        assert TemplateProcessor.validate_template(template, required) is False


class TestMultiLanguageHandler:
    """Test MultiLanguageHandler class."""

    def test_detect_language_english(self):
        """Test English language detection."""
        text = "The quick brown fox jumps over the lazy dog"
        result = MultiLanguageHandler.detect_language(text)
        assert result == "en"

    def test_detect_language_spanish(self):
        """Test Spanish language detection."""
        text = "El zorro marrón rápido salta sobre el perro perezoso"
        result = MultiLanguageHandler.detect_language(text)
        assert result == "es"

    def test_detect_language_french(self):
        """Test French language detection."""
        text = "Le renard brun rapide saute par-dessus le chien paresseux"
        result = MultiLanguageHandler.detect_language(text)
        assert result == "fr"

    def test_detect_language_unknown(self):
        """Test language detection with unknown text."""
        text = "123456789"
        result = MultiLanguageHandler.detect_language(text)
        assert result is None

    def test_detect_language_empty(self):
        """Test language detection with empty text."""
        assert MultiLanguageHandler.detect_language("") is None

    def test_transliterate_cyrillic(self):
        """Test Cyrillic transliteration."""
        cyrillic_text = "Привет мир"
        result = MultiLanguageHandler.transliterate_cyrillic(cyrillic_text)
        assert "Privet" in result
        assert "mir" in result

    def test_transliterate_cyrillic_empty(self):
        """Test Cyrillic transliteration with empty text."""
        assert MultiLanguageHandler.transliterate_cyrillic("") == ""

    def test_normalize_for_search(self):
        """Test text normalization for search."""
        text = "Café & Résumé"
        result = MultiLanguageHandler.normalize_for_search(text)
        assert result == "cafe resume"

    def test_normalize_for_search_russian(self):
        """Test search normalization for Russian text."""
        text = "Привет мир"
        result = MultiLanguageHandler.normalize_for_search(text, language="ru")
        assert "privet" in result
        assert "mir" in result


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_sanitize_text(self):
        """Test sanitize_text convenience function."""
        dirty_text = "<script>alert('xss')</script>Hello World"
        result = sanitize_text(dirty_text)
        assert "script" not in result
        assert "Hello World" in result

    def test_create_slug(self):
        """Test create_slug convenience function."""
        result = create_slug("Hello World!")
        assert result == "hello-world"

    def test_normalize_text(self):
        """Test normalize_text convenience function."""
        result = normalize_text("  Hello   World  ", remove_accents=True)
        assert result == "Hello World"

    def test_process_template_string(self):
        """Test process_template_string convenience function."""
        result = process_template_string("Hello {name}", name="John")
        assert result == "Hello John"

    def test_detect_text_language(self):
        """Test detect_text_language convenience function."""
        result = detect_text_language("The quick brown fox")
        assert result == "en"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_strings(self):
        """Test handling of empty strings."""
        assert StringSanitizer.remove_html_tags("") == ""
        assert SlugGenerator.generate_slug("") == ""
        assert TextNormalizer.normalize_unicode("") == ""
        assert TemplateProcessor.extract_template_variables("") == []
        assert MultiLanguageHandler.detect_language("") is None

    def test_none_values(self):
        """Test handling of None values."""
        # Most functions should handle None gracefully
        result = StringSanitizer.remove_html_tags(None)
        assert result == ""

    def test_very_long_strings(self):
        """Test handling of very long strings."""
        long_string = "a" * 10000
        result = StringSanitizer.clean_whitespace(long_string)
        assert len(result) == 10000
        assert result == long_string

    def test_special_characters(self):
        """Test handling of special characters."""
        special_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        result = SlugGenerator.generate_slug(special_text)
        assert result == "_"  # Underscore is considered a word character

    def test_unicode_edge_cases(self):
        """Test unicode edge cases."""
        # Test with various unicode categories
        unicode_text = "Hello\u200bWorld"  # Zero-width space
        result = TextNormalizer.normalize_whitespace(unicode_text)
        assert "Hello World" in result

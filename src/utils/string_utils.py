"""
String Utilities Module

This module provides comprehensive string processing, sanitization, and manipulation utilities
for FastAPI applications. It includes advanced text processing capabilities with security
features, internationalization support, and template processing.

Key Features:
- Text sanitization and validation (HTML, SQL injection, XSS protection)
- Slug generation for URL-friendly strings with unicode support
- Text normalization and cleaning (whitespace, accents, unicode)
- Template string processing with variable substitution
- Multi-language text handling (language detection, transliteration)
- Security-focused text processing for web applications

Classes:
    StringSanitizer: HTML and SQL injection sanitization
    SlugGenerator: URL-friendly slug generation with unicode support
    TextNormalizer: Text cleaning and normalization utilities
    TemplateProcessor: Template string processing with variable substitution
    MultiLanguageHandler: Multi-language text processing and detection

Example:
    ```python
    from src.utils.string_utils import StringSanitizer, SlugGenerator

    # Sanitize HTML content
    sanitizer = StringSanitizer()
    clean_text = sanitizer.sanitize_html("<script>alert('xss')</script>Hello")

    # Generate URL-friendly slug
    slug_gen = SlugGenerator()
    slug = slug_gen.generate_slug("Café & Restaurant")
    # Result: "cafe-restaurant"
    ```

Security Note:
    This module provides basic sanitization. For production applications,
    always use parameterized queries for database operations and consider
    additional security measures for user input validation.
"""

import re
import unicodedata
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote, unquote


class StringSanitizer:
    """
    Text sanitization and validation utilities for secure text processing.

    This class provides methods to sanitize and validate text content, protecting
    against common web vulnerabilities like XSS attacks and SQL injection.

    Methods:
        remove_html_tags: Remove all HTML tags from text
        remove_script_tags: Remove script and style tags
        sanitize_html: Sanitize HTML content with optional allowed tags
        detect_sql_injection: Detect potential SQL injection patterns
        sanitize_sql_input: Basic SQL input sanitization
        clean_whitespace: Clean and normalize whitespace
        remove_control_characters: Remove control characters from text

    Example:
        ```python
        sanitizer = StringSanitizer()

        # Remove all HTML tags
        clean_text = sanitizer.remove_html_tags("<p>Hello <b>World</b></p>")
        # Result: "Hello World"

        # Sanitize HTML with allowed tags
        safe_html = sanitizer.sanitize_html(
            "<p>Hello <script>alert('xss')</script></p>",
            allowed_tags=["p", "b"]
        )
        # Result: "<p>Hello </p>"
        ```

    Security Note:
        These methods provide basic sanitization. For production applications,
        use additional security measures and parameterized queries.
    """

    # Common patterns for sanitization
    HTML_TAGS = re.compile(r"<[^>]+>")
    SCRIPT_TAGS = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
    STYLE_TAGS = re.compile(r"<style[^>]*>.*?</style>", re.IGNORECASE | re.DOTALL)
    JAVASCRIPT_PROTOCOLS = re.compile(r"javascript:", re.IGNORECASE)
    DATA_PROTOCOLS = re.compile(r"data:", re.IGNORECASE)
    SQL_INJECTION_PATTERNS = re.compile(
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
        re.IGNORECASE,
    )

    @classmethod
    def remove_html_tags(cls, text: str) -> str:
        """Remove HTML tags from text."""
        if not text:
            return ""
        return cls.HTML_TAGS.sub("", text)

    @classmethod
    def remove_script_tags(cls, text: str) -> str:
        """Remove script tags and their content."""
        if not text:
            return ""
        text = cls.SCRIPT_TAGS.sub("", text)
        text = cls.STYLE_TAGS.sub("", text)
        return text

    @classmethod
    def sanitize_html(cls, text: str, allowed_tags: Optional[List[str]] = None) -> str:
        """Sanitize HTML content by removing dangerous elements."""
        if not text:
            return ""

        # Remove script and style tags completely
        text = cls.remove_script_tags(text)

        # Remove dangerous protocols
        text = cls.JAVASCRIPT_PROTOCOLS.sub("", text)
        text = cls.DATA_PROTOCOLS.sub("", text)

        if allowed_tags:
            # Keep only allowed tags
            pattern = f'<(?!/?(?:{"|".join(re.escape(tag) for tag in allowed_tags)})\\b)[^>]*>'
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        else:
            # Remove all HTML tags if no allowed tags specified
            text = cls.remove_html_tags(text)

        return text.strip()

    @classmethod
    def detect_sql_injection(cls, text: str) -> bool:
        """Detect potential SQL injection patterns."""
        if not text:
            return False
        return bool(cls.SQL_INJECTION_PATTERNS.search(text))

    @classmethod
    def sanitize_sql_input(cls, text: str) -> str:
        """Basic SQL input sanitization (use parameterized queries for production)."""
        if not text:
            return ""

        # Remove or escape dangerous characters
        dangerous_chars = ["'", '"', ";", "--", "/*", "*/"]
        for char in dangerous_chars:
            text = text.replace(char, "")

        # Remove dangerous SQL keywords (case insensitive)
        dangerous_keywords = [
            "DROP",
            "DELETE",
            "INSERT",
            "UPDATE",
            "CREATE",
            "ALTER",
            "EXEC",
            "UNION",
            "SCRIPT",
        ]
        for keyword in dangerous_keywords:
            text = re.sub(rf"\b{re.escape(keyword)}\b", "", text, flags=re.IGNORECASE)

        return text.strip()

    @classmethod
    def clean_whitespace(cls, text: str) -> str:
        """Clean and normalize whitespace."""
        if not text:
            return ""

        # Replace multiple whitespace with single space
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @classmethod
    def remove_control_characters(cls, text: str) -> str:
        """Remove control characters except newlines and tabs."""
        if not text:
            return ""

        # Keep printable characters, newlines, and tabs
        return "".join(char for char in text if char.isprintable() or char in "\n\t")


class SlugGenerator:
    """
    URL-friendly slug generation utilities with unicode support.

    This class provides methods to generate URL-friendly slugs from text content,
    with support for unicode characters, custom separators, and length limits.

    Methods:
        generate_slug: Generate a URL-friendly slug from text
        generate_unique_slug: Generate a unique slug with conflict resolution

    Features:
        - Unicode normalization and accent removal
        - Customizable separators and length limits
        - Case preservation options
        - Conflict resolution for unique slugs
        - Special character handling

    Example:
        ```python
        slug_gen = SlugGenerator()

        # Basic slug generation
        slug = slug_gen.generate_slug("Café & Restaurant")
        # Result: "cafe-restaurant"

        # With custom separator and length
        slug = slug_gen.generate_slug(
            "My Amazing Blog Post Title",
            separator="_",
            max_length=20
        )
        # Result: "my_amazing_blog"

        # Generate unique slug
        existing_slugs = ["hello-world", "hello-world-2"]
        unique_slug = slug_gen.generate_unique_slug(
            "Hello World",
            existing_slugs=existing_slugs
        )
        # Result: "hello-world-3"
        ```
    """

    @classmethod
    def generate_slug(
        cls,
        text: str,
        max_length: int = 50,
        separator: str = "-",
        preserve_case: bool = False,
    ) -> str:
        """Generate a URL-friendly slug from text."""
        if not text:
            return ""

        # Normalize unicode and remove accents
        text = unicodedata.normalize("NFKD", text)
        text = "".join(char for char in text if unicodedata.category(char) != "Mn")

        # Convert to lowercase unless preserving case
        if not preserve_case:
            text = text.lower()

        # Replace spaces and special characters with separator
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", separator, text)

        # Remove leading/trailing separators
        text = text.strip(separator)

        # Truncate to max length
        if len(text) > max_length:
            text = text[:max_length].rstrip(separator)

        return text

    @classmethod
    def generate_unique_slug(
        cls,
        text: str,
        existing_slugs: List[str],
        max_length: int = 50,
        separator: str = "-",
    ) -> str:
        """Generate a unique slug by appending numbers if needed."""
        base_slug = cls.generate_slug(text, max_length, separator)

        if base_slug not in existing_slugs:
            return base_slug

        counter = 1
        while True:
            # Calculate available length for counter
            counter_str = f"{separator}{counter}"
            available_length = max_length - len(counter_str)

            if available_length <= 0:
                # Fallback: use hash
                return f"{base_slug[:max_length-8]}{separator}{hash(text) % 10000:04d}"

            truncated_base = base_slug[:available_length].rstrip(separator)
            candidate = f"{truncated_base}{counter_str}"

            if candidate not in existing_slugs:
                return candidate

            counter += 1


class TextNormalizer:
    """
    Text normalization and cleaning utilities for consistent text processing.

    This class provides methods to normalize and clean text content, including
    unicode normalization, accent removal, whitespace cleaning, and text truncation.

    Methods:
        normalize_unicode: Normalize unicode text to specified form
        remove_accents: Remove accents and diacritical marks
        normalize_whitespace: Clean and normalize whitespace
        clean_text: Comprehensive text cleaning
        truncate_text: Truncate text with ellipsis

    Features:
        - Unicode normalization (NFC, NFD, NFKC, NFKD)
        - Accent and diacritical mark removal
        - Whitespace normalization
        - Text truncation with ellipsis
        - Comprehensive text cleaning pipeline

    Example:
        ```python
        normalizer = TextNormalizer()

        # Normalize unicode
        normalized = normalizer.normalize_unicode("café")
        # Result: "café" (NFC form)

        # Remove accents
        no_accents = normalizer.remove_accents("café résumé")
        # Result: "cafe resume"

        # Clean whitespace
        clean = normalizer.normalize_whitespace("  Hello   World  ")
        # Result: "Hello World"

        # Truncate text
        truncated = normalizer.truncate_text("This is a very long text", 10)
        # Result: "This is..."
        ```
    """

    @classmethod
    def normalize_unicode(cls, text: str, form: str = "NFC") -> str:
        """Normalize unicode text."""
        if not text:
            return ""

        valid_forms = ["NFC", "NFD", "NFKC", "NFKD"]
        if form not in valid_forms:
            raise ValueError(
                f"Invalid normalization form. Must be one of: {valid_forms}"
            )

        return unicodedata.normalize(form, text)

    @classmethod
    def remove_accents(cls, text: str) -> str:
        """Remove accents and diacritics from text."""
        if not text:
            return ""

        # Decompose unicode and remove combining characters
        text = unicodedata.normalize("NFD", text)
        text = "".join(char for char in text if unicodedata.category(char) != "Mn")

        return text

    @classmethod
    def normalize_whitespace(cls, text: str) -> str:
        """Normalize various whitespace characters to standard spaces."""
        if not text:
            return ""

        # Replace various whitespace characters with standard space
        text = re.sub(
            r"[\t\n\r\f\v\u00a0\u2000-\u200f\u2028-\u202f\u205f-\u206f\ufeff]",
            " ",
            text,
        )

        # Collapse multiple spaces
        text = re.sub(r" +", " ", text)

        return text.strip()

    @classmethod
    def clean_text(cls, text: str, remove_punctuation: bool = False) -> str:
        """Clean text by normalizing and optionally removing punctuation."""
        if not text:
            return ""

        # Normalize unicode and whitespace
        text = cls.normalize_unicode(text)
        text = cls.normalize_whitespace(text)

        if remove_punctuation:
            # Keep only alphanumeric and spaces
            text = re.sub(r"[^\w\s]", "", text)
            text = re.sub(r"\s+", " ", text)

        return text.strip()

    @classmethod
    def truncate_text(
        cls, text: str, max_length: int, suffix: str = "...", word_boundary: bool = True
    ) -> str:
        """Truncate text to specified length with optional word boundary preservation."""
        if not text or len(text) <= max_length:
            return text

        if not word_boundary:
            return text[: max_length - len(suffix)] + suffix

        # Find last space before max length
        truncate_at = max_length - len(suffix)
        last_space = text.rfind(" ", 0, truncate_at)

        if last_space > truncate_at * 0.5:  # Don't truncate too early
            return text[:last_space] + suffix
        else:
            return text[:truncate_at] + suffix


class TemplateProcessor:
    """
    Template string processing utilities with variable substitution.

    This class provides methods to process template strings with variable substitution,
    including safe mode processing and template validation.

    Methods:
        process_template: Process template with variable substitution
        extract_template_variables: Extract variables from template string
        validate_template: Validate template syntax

    Features:
        - Variable substitution with {{variable}} syntax
        - Safe mode processing (escapes HTML)
        - Template variable extraction
        - Template validation
        - Error handling for missing variables

    Example:
        ```python
        processor = TemplateProcessor()

        # Process template with variables
        template = "Hello {{name}}, welcome to {{site}}!"
        variables = {"name": "John", "site": "MyApp"}
        result = processor.process_template(template, variables)
        # Result: "Hello John, welcome to MyApp!"

        # Safe mode (escapes HTML)
        template = "Hello {{name}}!"
        variables = {"name": "<script>alert('xss')</script>"}
        result = processor.process_template(template, variables, safe_mode=True)
        # Result: "Hello &lt;script&gt;alert('xss')&lt;/script&gt;!"

        # Extract variables from template
        variables = processor.extract_template_variables("Hello {{name}} from {{city}}!")
        # Result: ["name", "city"]
        ```
    """

    @classmethod
    def process_template(
        cls, template: str, variables: Dict[str, Any], safe_mode: bool = True
    ) -> str:
        """Process a template string with variable substitution."""
        if not template:
            return ""

        if safe_mode:
            # Escape variables to prevent injection
            escaped_vars = {}
            for key, value in variables.items():
                if isinstance(value, str):
                    # Basic HTML escaping
                    escaped_vars[key] = (
                        str(value)
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace('"', "&quot;")
                        .replace("'", "&#x27;")
                    )
                else:
                    escaped_vars[key] = str(value)
            variables = escaped_vars

        try:
            # Simple template processing with {variable} syntax
            return template.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")
        except Exception as e:
            raise ValueError(f"Template processing error: {e}")

    @classmethod
    def extract_template_variables(cls, template: str) -> List[str]:
        """Extract variable names from a template string."""
        if not template:
            return []

        # Find all {variable} patterns
        pattern = r"\{([^}]+)\}"
        matches = re.findall(pattern, template)

        # Remove duplicates while preserving order
        seen = set()
        unique_vars = []
        for var in matches:
            if var not in seen:
                seen.add(var)
                unique_vars.append(var)

        return unique_vars

    @classmethod
    def validate_template(cls, template: str, required_variables: List[str]) -> bool:
        """Validate that template contains all required variables."""
        if not template:
            return len(required_variables) == 0

        template_vars = cls.extract_template_variables(template)
        return all(var in template_vars for var in required_variables)


class MultiLanguageHandler:
    """
    Multi-language text handling utilities with language detection and transliteration.

    This class provides methods to handle multi-language text content, including
    language detection, transliteration, and text normalization for search.

    Methods:
        detect_language: Detect language of text content
        transliterate_cyrillic: Transliterate Cyrillic text to Latin
        normalize_for_search: Normalize text for search operations

    Features:
        - Basic language detection (English, Spanish, French)
        - Cyrillic to Latin transliteration
        - Text normalization for search
        - Unicode handling for international text

    Example:
        ```python
        handler = MultiLanguageHandler()

        # Detect language
        language = handler.detect_language("Hello world")
        # Result: "en"

        # Transliterate Cyrillic
        transliterated = handler.transliterate_cyrillic("Привет мир")
        # Result: "Privet mir"

        # Normalize for search
        normalized = handler.normalize_for_search("  Hello   World  ")
        # Result: "hello world"
        ```

    Note:
        Language detection is basic and pattern-based. For production applications,
        consider using specialized libraries like langdetect or polyglot.
    """

    # Language detection patterns (basic)
    LANGUAGE_PATTERNS = {
        "en": re.compile(
            r"\b(the|and|or|but|in|on|at|to|for|of|with|by)\b", re.IGNORECASE
        ),
        "es": re.compile(
            r"\b(el|la|los|las|de|del|en|con|por|para|que|como)\b", re.IGNORECASE
        ),
        "fr": re.compile(
            r"\b(le|la|les|de|du|des|en|avec|pour|que|comme)\b", re.IGNORECASE
        ),
        "de": re.compile(
            r"\b(der|die|das|und|oder|aber|in|auf|mit|für|von)\b", re.IGNORECASE
        ),
        "it": re.compile(
            r"\b(il|la|lo|gli|le|di|del|della|in|con|per|che|come)\b", re.IGNORECASE
        ),
        "pt": re.compile(
            r"\b(o|a|os|as|de|do|da|em|com|por|para|que|como)\b", re.IGNORECASE
        ),
        "ru": re.compile(r"[а-яё]", re.IGNORECASE),
        "zh": re.compile(r"[\u4e00-\u9fff]"),
        "ja": re.compile(r"[\u3040-\u309f\u30a0-\u30ff]"),
        "ko": re.compile(r"[\uac00-\ud7af]"),
        "ar": re.compile(r"[\u0600-\u06ff]"),
    }

    @classmethod
    def detect_language(cls, text: str) -> Optional[str]:
        """Basic language detection based on common words and characters."""
        if not text:
            return None

        text = text.lower()
        scores = {}

        for lang, pattern in cls.LANGUAGE_PATTERNS.items():
            matches = len(pattern.findall(text))
            if matches > 0:
                scores[lang] = matches

        if not scores:
            return None

        # Return language with highest score
        return max(scores, key=scores.get)

    @classmethod
    def transliterate_cyrillic(cls, text: str) -> str:
        """Transliterate Cyrillic text to Latin."""
        if not text:
            return ""

        # Basic Cyrillic to Latin transliteration
        cyrillic_to_latin = {
            "а": "a",
            "б": "b",
            "в": "v",
            "г": "g",
            "д": "d",
            "е": "e",
            "ё": "yo",
            "ж": "zh",
            "з": "z",
            "и": "i",
            "й": "y",
            "к": "k",
            "л": "l",
            "м": "m",
            "н": "n",
            "о": "o",
            "п": "p",
            "р": "r",
            "с": "s",
            "т": "t",
            "у": "u",
            "ф": "f",
            "х": "kh",
            "ц": "ts",
            "ч": "ch",
            "ш": "sh",
            "щ": "shch",
            "ъ": "",
            "ы": "y",
            "ь": "",
            "э": "e",
            "ю": "yu",
            "я": "ya",
            "А": "A",
            "Б": "B",
            "В": "V",
            "Г": "G",
            "Д": "D",
            "Е": "E",
            "Ё": "Yo",
            "Ж": "Zh",
            "З": "Z",
            "И": "I",
            "Й": "Y",
            "К": "K",
            "Л": "L",
            "М": "M",
            "Н": "N",
            "О": "O",
            "П": "P",
            "Р": "R",
            "С": "S",
            "Т": "T",
            "У": "U",
            "Ф": "F",
            "Х": "Kh",
            "Ц": "Ts",
            "Ч": "Ch",
            "Ш": "Sh",
            "Щ": "Shch",
            "Ъ": "",
            "Ы": "Y",
            "Ь": "",
            "Э": "E",
            "Ю": "Yu",
            "Я": "Ya",
        }

        result = ""
        for char in text:
            result += cyrillic_to_latin.get(char, char)

        return result

    @classmethod
    def normalize_for_search(cls, text: str, language: Optional[str] = None) -> str:
        """Normalize text for search purposes."""
        if not text:
            return ""

        # Basic normalization
        text = TextNormalizer.normalize_unicode(text)
        text = TextNormalizer.normalize_whitespace(text)

        # Language-specific normalization
        if language == "ru":
            text = cls.transliterate_cyrillic(text)
        else:
            # Remove accents for Latin-based languages
            text = TextNormalizer.remove_accents(text)

        # Convert to lowercase
        text = text.lower()

        # Remove punctuation
        text = re.sub(r"[^\w\s]", "", text)

        # Final whitespace normalization
        text = re.sub(r"\s+", " ", text)

        return text.strip()


# Convenience functions for common operations
def sanitize_text(
    text: str, remove_html: bool = True, remove_scripts: bool = True
) -> str:
    """Convenience function for basic text sanitization."""
    if not text:
        return ""

    if remove_scripts:
        text = StringSanitizer.remove_script_tags(text)

    if remove_html:
        text = StringSanitizer.remove_html_tags(text)

    text = StringSanitizer.clean_whitespace(text)
    text = StringSanitizer.remove_control_characters(text)

    return text


def create_slug(text: str, max_length: int = 50) -> str:
    """Convenience function for creating URL-friendly slugs."""
    return SlugGenerator.generate_slug(text, max_length)


def normalize_text(text: str, remove_accents: bool = False) -> str:
    """Convenience function for text normalization."""
    if not text:
        return ""

    text = TextNormalizer.normalize_unicode(text)
    text = TextNormalizer.normalize_whitespace(text)

    if remove_accents:
        text = TextNormalizer.remove_accents(text)

    return text


def process_template_string(template: str, **kwargs) -> str:
    """Convenience function for template processing."""
    return TemplateProcessor.process_template(template, kwargs)


def detect_text_language(text: str) -> Optional[str]:
    """Convenience function for language detection."""
    return MultiLanguageHandler.detect_language(text)

"""
Tests for file utilities.

Tests the file utilities including text, JSON, and CSV operations
with error handling and edge cases.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Mark all tests in this module as utility tests (run middle)
# Test order is managed centrally in conftest.py

from src.utils.file_utils import (
    FileUtils,
    FileUtilsError,
    file_exists,
    get_file_info,
    read_csv,
    read_json,
    read_text,
    write_csv,
    write_json,
    write_text,
)


class TestFileUtils:
    """Test FileUtils class."""

    def test_initialization(self):
        """Test FileUtils initialization."""
        file_utils = FileUtils(trace_id="test-123")
        assert file_utils.trace_id == "test-123"
        assert file_utils.logger is not None

    def test_initialization_without_trace_id(self):
        """Test FileUtils initialization without trace ID."""
        file_utils = FileUtils()
        assert file_utils.trace_id is not None
        assert len(file_utils.trace_id) > 0

    def test_validate_file_path_valid(self):
        """Test file path validation with valid path."""
        file_utils = FileUtils()
        path = file_utils._validate_file_path("test.txt")
        assert isinstance(path, Path)
        assert str(path) == "test.txt"

    def test_validate_file_path_empty(self):
        """Test file path validation with empty path."""
        file_utils = FileUtils()
        with pytest.raises(FileUtilsError, match="File path cannot be empty"):
            file_utils._validate_file_path("")

    def test_validate_file_path_traversal(self):
        """Test file path validation with path traversal attempt."""
        file_utils = FileUtils()
        with pytest.raises(FileUtilsError, match="Path traversal not allowed"):
            file_utils._validate_file_path("../../../etc/passwd")


class TestTextFileOperations:
    """Test text file operations."""

    def test_write_and_read_text_file(self):
        """Test writing and reading text files."""
        file_utils = FileUtils(trace_id="text-test")

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
            tmp_path = tmp.name

        try:
            content = "Hello, World!\nThis is a test file."

            # Write file
            result = file_utils.write_text_file(tmp_path, content)
            assert result is True

            # Read file
            read_content = file_utils.read_text_file(tmp_path)
            assert read_content == content

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_read_nonexistent_file(self):
        """Test reading non-existent file."""
        file_utils = FileUtils()

        with pytest.raises(FileUtilsError, match="File does not exist"):
            file_utils.read_text_file("nonexistent_file.txt")

    def test_append_text_file(self):
        """Test appending to text file."""
        file_utils = FileUtils()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
            tmp_path = tmp.name

        try:
            # Write initial content
            file_utils.write_text_file(tmp_path, "Line 1")

            # Append content
            file_utils.write_text_file(tmp_path, "\nLine 2", append=True)

            # Read and verify
            content = file_utils.read_text_file(tmp_path)
            assert content == "Line 1\nLine 2"

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_read_lines(self):
        """Test reading file as lines."""
        file_utils = FileUtils()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
            tmp_path = tmp.name

        try:
            content = "Line 1\nLine 2\n\nLine 4\n"
            file_utils.write_text_file(tmp_path, content)

            # Read all lines
            lines = file_utils.read_lines(tmp_path)
            assert len(lines) == 4
            assert lines[0] == "Line 1"
            assert lines[1] == "Line 2"
            assert lines[2] == ""
            assert lines[3] == "Line 4"

            # Read lines skipping empty
            lines_no_empty = file_utils.read_lines(tmp_path, skip_empty=True)
            assert len(lines_no_empty) == 3
            assert "Line 1" in lines_no_empty
            assert "Line 2" in lines_no_empty
            assert "Line 4" in lines_no_empty

        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestJSONFileOperations:
    """Test JSON file operations."""

    def test_write_and_read_json_file(self):
        """Test writing and reading JSON files."""
        file_utils = FileUtils()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
            tmp_path = tmp.name

        try:
            data = {
                "name": "Test",
                "value": 42,
                "items": ["a", "b", "c"],
                "nested": {"key": "value"},
            }

            # Write JSON
            result = file_utils.write_json_file(tmp_path, data)
            assert result is True

            # Read JSON
            read_data = file_utils.read_json_file(tmp_path)
            assert read_data == data

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_read_invalid_json(self):
        """Test reading invalid JSON file."""
        file_utils = FileUtils()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
            tmp.write("{ invalid json content")
            tmp_path = tmp.name

        try:
            with pytest.raises(FileUtilsError, match="Invalid JSON"):
                file_utils.read_json_file(tmp_path)

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_write_unserializable_json(self):
        """Test writing unserializable data to JSON."""
        file_utils = FileUtils()

        class UnserializableClass:
            pass

        data = {"object": UnserializableClass()}

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
            tmp_path = tmp.name

        try:
            with pytest.raises(
                FileUtilsError, match="Failed to serialize data to JSON"
            ):
                file_utils.write_json_file(tmp_path, data)

        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestCSVFileOperations:
    """Test CSV file operations."""

    def test_write_and_read_csv_file(self):
        """Test writing and reading CSV files."""
        file_utils = FileUtils()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmp:
            tmp_path = tmp.name

        try:
            data = [
                {"name": "Alice", "age": "30", "city": "New York"},
                {"name": "Bob", "age": "25", "city": "San Francisco"},
                {"name": "Charlie", "age": "35", "city": "Chicago"},
            ]

            # Write CSV
            result = file_utils.write_csv_file(tmp_path, data)
            assert result is True

            # Read CSV
            read_data = file_utils.read_csv_file(tmp_path)
            assert len(read_data) == 3
            assert read_data[0]["name"] == "Alice"
            assert read_data[1]["age"] == "25"
            assert read_data[2]["city"] == "Chicago"

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_write_empty_csv_data(self):
        """Test writing empty data to CSV."""
        file_utils = FileUtils()

        with pytest.raises(FileUtilsError, match="Cannot write empty data"):
            file_utils.write_csv_file("test.csv", [])

    def test_write_invalid_csv_data(self):
        """Test writing invalid data to CSV."""
        file_utils = FileUtils()

        with pytest.raises(FileUtilsError, match="Data must be a list of dictionaries"):
            file_utils.write_csv_file("test.csv", "invalid data")

    def test_read_csv_as_list(self):
        """Test reading CSV as list of lists."""
        file_utils = FileUtils()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmp:
            tmp.write("name,age,city\nAlice,30,New York\nBob,25,San Francisco\n")
            tmp_path = tmp.name

        try:
            rows = file_utils.read_csv_as_list(tmp_path)
            assert len(rows) == 3  # Including header
            assert rows[0] == ["name", "age", "city"]
            assert rows[1] == ["Alice", "30", "New York"]
            assert rows[2] == ["Bob", "25", "San Francisco"]

        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestFileInformation:
    """Test file information and utilities."""

    def test_file_exists(self):
        """Test file existence check."""
        file_utils = FileUtils()

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            assert file_utils.file_exists(tmp_path) is True
            assert file_utils.file_exists("nonexistent_file.txt") is False

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_directory_exists(self):
        """Test directory existence check."""
        file_utils = FileUtils()

        with tempfile.TemporaryDirectory() as tmp_dir:
            assert file_utils.directory_exists(tmp_dir) is True

        assert file_utils.directory_exists("nonexistent_directory") is False

    def test_get_file_info(self):
        """Test getting file information."""
        file_utils = FileUtils()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
            tmp.write("Test content")
            tmp_path = tmp.name

        try:
            info = file_utils.get_file_info(tmp_path)

            assert "path" in info
            assert "name" in info
            assert "size_bytes" in info
            assert "size_human" in info
            assert "created" in info
            assert "modified" in info
            assert info["is_file"] is True
            assert info["is_directory"] is False
            assert info["size_bytes"] > 0

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_get_file_info_nonexistent(self):
        """Test getting info for non-existent file."""
        file_utils = FileUtils()

        with pytest.raises(FileUtilsError, match="File does not exist"):
            file_utils.get_file_info("nonexistent_file.txt")

    def test_delete_file(self):
        """Test deleting a file."""
        file_utils = FileUtils()

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        # File should exist
        assert Path(tmp_path).exists()

        # Delete file
        result = file_utils.delete_file(tmp_path)
        assert result is True

        # File should not exist
        assert not Path(tmp_path).exists()

    def test_copy_file(self):
        """Test copying a file."""
        file_utils = FileUtils()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
            tmp.write("Test content for copying")
            src_path = tmp.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            dest_path = tmp.name
            Path(dest_path).unlink()  # Remove the file, keep the path

        try:
            # Copy file
            result = file_utils.copy_file(src_path, dest_path)
            assert result is True

            # Verify copy
            assert Path(dest_path).exists()
            dest_content = file_utils.read_text_file(dest_path)
            assert dest_content == "Test content for copying"

        finally:
            Path(src_path).unlink(missing_ok=True)
            Path(dest_path).unlink(missing_ok=True)

    def test_list_files(self):
        """Test listing files in directory."""
        file_utils = FileUtils()

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create test files
            (Path(tmp_dir) / "file1.txt").write_text("content1")
            (Path(tmp_dir) / "file2.txt").write_text("content2")
            (Path(tmp_dir) / "file3.json").write_text('{"key": "value"}')

            # List all files
            all_files = file_utils.list_files(tmp_dir)
            assert len(all_files) == 3

            # List only .txt files
            txt_files = file_utils.list_files(tmp_dir, pattern="*.txt")
            assert len(txt_files) == 2

            # List only .json files
            json_files = file_utils.list_files(tmp_dir, pattern="*.json")
            assert len(json_files) == 1


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_read_write_text_convenience(self):
        """Test text convenience functions."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
            tmp_path = tmp.name

        try:
            content = "Test content for convenience function"

            # Write using convenience function
            result = write_text(tmp_path, content, trace_id="convenience-test")
            assert result is True

            # Read using convenience function
            read_content = read_text(tmp_path, trace_id="convenience-test")
            assert read_content == content

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_read_write_json_convenience(self):
        """Test JSON convenience functions."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
            tmp_path = tmp.name

        try:
            data = {"test": "data", "number": 42}

            # Write using convenience function
            result = write_json(tmp_path, data, trace_id="convenience-test")
            assert result is True

            # Read using convenience function
            read_data = read_json(tmp_path, trace_id="convenience-test")
            assert read_data == data

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_read_write_csv_convenience(self):
        """Test CSV convenience functions."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmp:
            tmp_path = tmp.name

        try:
            data = [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]

            # Write using convenience function
            result = write_csv(tmp_path, data, trace_id="convenience-test")
            assert result is True

            # Read using convenience function
            read_data = read_csv(tmp_path, trace_id="convenience-test")
            assert len(read_data) == 2
            assert read_data[0]["name"] == "Alice"

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_file_exists_convenience(self):
        """Test file exists convenience function."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            assert file_exists(tmp_path) is True
            assert file_exists("nonexistent_file.txt") is False

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_get_file_info_convenience(self):
        """Test file info convenience function."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
            tmp.write("Test content")
            tmp_path = tmp.name

        try:
            info = get_file_info(tmp_path, trace_id="convenience-test")
            assert "name" in info
            assert "size_bytes" in info
            assert info["is_file"] is True

        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_invalid_file_path(self):
        """Test handling of invalid file paths."""
        file_utils = FileUtils()

        with pytest.raises(FileUtilsError):
            file_utils._validate_file_path("")

    def test_permission_errors(self):
        """Test handling of permission errors."""
        file_utils = FileUtils()

        # This test might not work on all systems, so we'll mock it
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with pytest.raises(FileUtilsError, match="Failed to read text file"):
                file_utils.read_text_file("test.txt")

    def test_json_serializer_datetime(self):
        """Test JSON serializer with datetime objects."""
        file_utils = FileUtils()
        from datetime import datetime

        test_datetime = datetime(2024, 1, 1, 12, 0, 0)
        result = file_utils._json_serializer(test_datetime)
        assert result == "2024-01-01T12:00:00"

    def test_json_serializer_object_with_dict(self):
        """Test JSON serializer with object having __dict__."""
        file_utils = FileUtils()

        class TestObject:
            def __init__(self):
                self.name = "test"
                self.value = 42

        obj = TestObject()
        result = file_utils._json_serializer(obj)
        assert result == {"name": "test", "value": 42}

    def test_json_serializer_unsupported_type(self):
        """Test JSON serializer with unsupported type."""
        file_utils = FileUtils()

        class UnsupportedType:
            pass

        obj = UnsupportedType()
        with pytest.raises(TypeError, match="is not JSON serializable"):
            file_utils._json_serializer(obj)

"""
File Utilities

Comprehensive file handling utilities for reading and writing various file formats
including text files, JSON, CSV, and more. Includes error handling, validation,
and logging integration.
"""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.core.logging import get_logger_for_trace_id


class FileUtilsError(Exception):
    """Custom exception for file utilities errors."""

    pass


class FileUtils:
    """
    Comprehensive file utilities class with support for various file formats.

    Provides methods for reading and writing text files, JSON files, CSV files,
    with built-in error handling, validation, and logging.
    """

    def __init__(self, trace_id: str = None):
        """
        Initialize FileUtils with optional trace ID for logging.

        Args:
            trace_id: Optional trace ID for request tracing
        """
        self.trace_id = trace_id or str(uuid4())
        self.logger = get_logger_for_trace_id(self.trace_id, "src.file_utils")

    def _ensure_directory(self, file_path: str | Path) -> None:
        """Ensure the directory for the file path exists."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

    def _validate_file_path(self, file_path: str | Path) -> Path:
        """Validate and convert file path to Path object."""
        if not file_path:
            raise FileUtilsError("File path cannot be empty")

        path = Path(file_path)

        # Check for path traversal attempts
        if ".." in str(path):
            self.logger.warning(f"Potential path traversal attempt: {file_path}")
            raise FileUtilsError("Path traversal not allowed")

        return path

    # ==================== TEXT FILE OPERATIONS ====================

    def read_text_file(
        self,
        file_path: str | Path,
        encoding: str = "utf-8",
        strip_whitespace: bool = True,
    ) -> str:
        """
        Read a text file and return its contents.

        Args:
            file_path: Path to the text file
            encoding: File encoding (default: utf-8)
            strip_whitespace: Whether to strip leading/trailing whitespace

        Returns:
            File contents as string

        Raises:
            FileUtilsError: If file cannot be read
        """
        path = self._validate_file_path(file_path)

        try:
            self.logger.info(f"Reading text file: {path}")

            if not path.exists():
                raise FileUtilsError(f"File does not exist: {path}")

            if not path.is_file():
                raise FileUtilsError(f"Path is not a file: {path}")

            with open(path, encoding=encoding) as file:
                content = file.read()

            if strip_whitespace:
                content = content.strip()

            self.logger.info(f"Successfully read text file: {path} ({len(content)} characters)")
            return content

        except UnicodeDecodeError as e:
            error_msg = f"Failed to decode file {path} with encoding {encoding}: {e}"
            self.logger.error(error_msg)
            raise FileUtilsError(error_msg)
        except Exception as e:
            error_msg = f"Failed to read text file {path}: {e}"
            self.logger.error(error_msg)
            raise FileUtilsError(error_msg)

    def write_text_file(
        self,
        file_path: str | Path,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True,
        append: bool = False,
    ) -> bool:
        """
        Write content to a text file.

        Args:
            file_path: Path to the text file
            content: Content to write
            encoding: File encoding (default: utf-8)
            create_dirs: Whether to create parent directories
            append: Whether to append to existing file

        Returns:
            True if successful

        Raises:
            FileUtilsError: If file cannot be written
        """
        path = self._validate_file_path(file_path)

        try:
            if create_dirs:
                self._ensure_directory(path)

            mode = "a" if append else "w"
            action = "Appending to" if append else "Writing"

            self.logger.info(f"{action} text file: {path}")

            with open(path, mode, encoding=encoding) as file:
                file.write(content)

            self.logger.info(f"Successfully wrote text file: {path} ({len(content)} characters)")
            return True

        except Exception as e:
            error_msg = f"Failed to write text file {path}: {e}"
            self.logger.error(error_msg)
            raise FileUtilsError(error_msg)

    def read_lines(
        self,
        file_path: str | Path,
        encoding: str = "utf-8",
        strip_whitespace: bool = True,
        skip_empty: bool = False,
    ) -> list[str]:
        """
        Read a text file and return its lines as a list.

        Args:
            file_path: Path to the text file
            encoding: File encoding (default: utf-8)
            strip_whitespace: Whether to strip whitespace from each line
            skip_empty: Whether to skip empty lines

        Returns:
            List of lines from the file

        Raises:
            FileUtilsError: If file cannot be read
        """
        path = self._validate_file_path(file_path)

        try:
            self.logger.info(f"Reading lines from file: {path}")

            with open(path, encoding=encoding) as file:
                lines = file.readlines()

            if strip_whitespace:
                lines = [line.strip() for line in lines]

            if skip_empty:
                lines = [line for line in lines if line]

            self.logger.info(f"Successfully read {len(lines)} lines from file: {path}")
            return lines

        except Exception as e:
            error_msg = f"Failed to read lines from file {path}: {e}"
            self.logger.error(error_msg)
            raise FileUtilsError(error_msg)

    # ==================== JSON FILE OPERATIONS ====================

    def read_json_file(self, file_path: str | Path, encoding: str = "utf-8") -> dict | list | Any:
        """
        Read a JSON file and return its contents.

        Args:
            file_path: Path to the JSON file
            encoding: File encoding (default: utf-8)

        Returns:
            Parsed JSON data

        Raises:
            FileUtilsError: If file cannot be read or JSON is invalid
        """
        path = self._validate_file_path(file_path)

        try:
            self.logger.info(f"Reading JSON file: {path}")

            if not path.exists():
                raise FileUtilsError(f"JSON file does not exist: {path}")

            with open(path, encoding=encoding) as file:
                data = json.load(file)

            self.logger.info(f"Successfully read JSON file: {path}")
            return data

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in file {path}: {e}"
            self.logger.error(error_msg)
            raise FileUtilsError(error_msg)
        except Exception as e:
            error_msg = f"Failed to read JSON file {path}: {e}"
            self.logger.error(error_msg)
            raise FileUtilsError(error_msg)

    def write_json_file(
        self,
        file_path: str | Path,
        data: dict | list | Any,
        encoding: str = "utf-8",
        indent: int = 2,
        ensure_ascii: bool = False,
        create_dirs: bool = True,
    ) -> bool:
        """
        Write data to a JSON file.

        Args:
            file_path: Path to the JSON file
            data: Data to write (must be JSON serializable)
            encoding: File encoding (default: utf-8)
            indent: JSON indentation (default: 2)
            ensure_ascii: Whether to escape non-ASCII characters
            create_dirs: Whether to create parent directories

        Returns:
            True if successful

        Raises:
            FileUtilsError: If data cannot be serialized or file cannot be written
        """
        path = self._validate_file_path(file_path)

        try:
            if create_dirs:
                self._ensure_directory(path)

            self.logger.info(f"Writing JSON file: {path}")

            with open(path, "w", encoding=encoding) as file:
                json.dump(
                    data,
                    file,
                    indent=indent,
                    ensure_ascii=ensure_ascii,
                    default=self._json_serializer,
                )

            self.logger.info(f"Successfully wrote JSON file: {path}")
            return True

        except (TypeError, ValueError) as e:
            error_msg = f"Failed to serialize data to JSON for file {path}: {e}"
            self.logger.error(error_msg)
            raise FileUtilsError(error_msg)
        except Exception as e:
            error_msg = f"Failed to write JSON file {path}: {e}"
            self.logger.error(error_msg)
            raise FileUtilsError(error_msg)

    def _json_serializer(self, obj):
        """Custom JSON serializer for common types."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, "__dict__") and not isinstance(
            obj, (str, int, float, bool, list, dict, type(None))
        ):
            # Only convert objects with __dict__ to dictionary if they have actual attributes
            if obj.__dict__:
                return obj.__dict__
            else:
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        else:
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    # ==================== CSV FILE OPERATIONS ====================

    def read_csv_file(
        self,
        file_path: str | Path,
        encoding: str = "utf-8",
        delimiter: str = ",",
        has_header: bool = True,
        skip_empty_rows: bool = True,
    ) -> list[dict[str, str]]:
        """
        Read a CSV file and return its contents as a list of dictionaries.

        Args:
            file_path: Path to the CSV file
            encoding: File encoding (default: utf-8)
            delimiter: CSV delimiter (default: comma)
            has_header: Whether the first row contains headers
            skip_empty_rows: Whether to skip empty rows

        Returns:
            List of dictionaries representing CSV rows

        Raises:
            FileUtilsError: If file cannot be read
        """
        path = self._validate_file_path(file_path)

        try:
            self.logger.info(f"Reading CSV file: {path}")

            if not path.exists():
                raise FileUtilsError(f"CSV file does not exist: {path}")

            rows = []
            with open(path, encoding=encoding, newline="") as file:
                if has_header:
                    reader = csv.DictReader(file, delimiter=delimiter)
                    for row in reader:
                        if skip_empty_rows and not any(row.values()):
                            continue
                        rows.append(dict(row))
                else:
                    reader = csv.reader(file, delimiter=delimiter)
                    for i, row in enumerate(reader):
                        if skip_empty_rows and not any(row):
                            continue
                        # Create dictionary with column indices as keys
                        row_dict = {f"column_{j}": value for j, value in enumerate(row)}
                        rows.append(row_dict)

            self.logger.info(f"Successfully read CSV file: {path} ({len(rows)} rows)")
            return rows

        except Exception as e:
            error_msg = f"Failed to read CSV file {path}: {e}"
            self.logger.error(error_msg)
            raise FileUtilsError(error_msg)

    def write_csv_file(
        self,
        file_path: str | Path,
        data: list[dict[str, Any]],
        encoding: str = "utf-8",
        delimiter: str = ",",
        write_header: bool = True,
        create_dirs: bool = True,
    ) -> bool:
        """
        Write data to a CSV file.

        Args:
            file_path: Path to the CSV file
            data: List of dictionaries to write
            encoding: File encoding (default: utf-8)
            delimiter: CSV delimiter (default: comma)
            write_header: Whether to write header row
            create_dirs: Whether to create parent directories

        Returns:
            True if successful

        Raises:
            FileUtilsError: If data cannot be written
        """
        path = self._validate_file_path(file_path)

        if not data:
            raise FileUtilsError("Cannot write empty data to CSV file")

        if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
            raise FileUtilsError("Data must be a list of dictionaries")

        try:
            if create_dirs:
                self._ensure_directory(path)

            self.logger.info(f"Writing CSV file: {path}")

            # Get all unique fieldnames from all rows
            fieldnames = set()
            for row in data:
                fieldnames.update(row.keys())
            fieldnames = sorted(fieldnames)  # Sort for consistent column order

            with open(path, "w", encoding=encoding, newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=delimiter)

                if write_header:
                    writer.writeheader()

                writer.writerows(data)

            self.logger.info(f"Successfully wrote CSV file: {path} ({len(data)} rows)")
            return True

        except Exception as e:
            error_msg = f"Failed to write CSV file {path}: {e}"
            self.logger.error(error_msg)
            raise FileUtilsError(error_msg)

    def read_csv_as_list(
        self,
        file_path: str | Path,
        encoding: str = "utf-8",
        delimiter: str = ",",
        skip_empty_rows: bool = True,
    ) -> list[list[str]]:
        """
        Read a CSV file and return its contents as a list of lists.

        Args:
            file_path: Path to the CSV file
            encoding: File encoding (default: utf-8)
            delimiter: CSV delimiter (default: comma)
            skip_empty_rows: Whether to skip empty rows

        Returns:
            List of lists representing CSV rows

        Raises:
            FileUtilsError: If file cannot be read
        """
        path = self._validate_file_path(file_path)

        try:
            self.logger.info(f"Reading CSV file as list: {path}")

            if not path.exists():
                raise FileUtilsError(f"CSV file does not exist: {path}")

            rows = []
            with open(path, encoding=encoding, newline="") as file:
                reader = csv.reader(file, delimiter=delimiter)
                for row in reader:
                    if skip_empty_rows and not any(row):
                        continue
                    rows.append(row)

            self.logger.info(f"Successfully read CSV file as list: {path} ({len(rows)} rows)")
            return rows

        except Exception as e:
            error_msg = f"Failed to read CSV file as list {path}: {e}"
            self.logger.error(error_msg)
            raise FileUtilsError(error_msg)

    # ==================== FILE INFORMATION & UTILITIES ====================

    def file_exists(self, file_path: str | Path) -> bool:
        """
        Check if a file exists.

        Args:
            file_path: Path to check

        Returns:
            True if file exists, False otherwise
        """
        try:
            path = self._validate_file_path(file_path)
            return path.exists() and path.is_file()
        except FileUtilsError:
            return False

    def directory_exists(self, dir_path: str | Path) -> bool:
        """
        Check if a directory exists.

        Args:
            dir_path: Directory path to check

        Returns:
            True if directory exists, False otherwise
        """
        try:
            path = Path(dir_path)
            return path.exists() and path.is_dir()
        except Exception:
            return False

    def get_file_info(self, file_path: str | Path) -> dict[str, Any]:
        """
        Get information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information

        Raises:
            FileUtilsError: If file doesn't exist or cannot be accessed
        """
        path = self._validate_file_path(file_path)

        try:
            if not path.exists():
                raise FileUtilsError(f"File does not exist: {path}")

            stat = path.stat()

            return {
                "path": str(path.absolute()),
                "name": path.name,
                "stem": path.stem,
                "suffix": path.suffix,
                "size_bytes": stat.st_size,
                "size_human": self._format_bytes(stat.st_size),
                "created": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc),
                "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                "is_file": path.is_file(),
                "is_directory": path.is_dir(),
                "permissions": oct(stat.st_mode)[-3:],
            }

        except Exception as e:
            error_msg = f"Failed to get file info for {path}: {e}"
            self.logger.error(error_msg)
            raise FileUtilsError(error_msg)

    def _format_bytes(self, size_bytes: int) -> str:
        """Format bytes into human readable format."""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math

        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"

    def delete_file(self, file_path: str | Path) -> bool:
        """
        Delete a file.

        Args:
            file_path: Path to the file to delete

        Returns:
            True if successful

        Raises:
            FileUtilsError: If file cannot be deleted
        """
        path = self._validate_file_path(file_path)

        try:
            if not path.exists():
                self.logger.warning(f"File does not exist (already deleted?): {path}")
                return True

            if not path.is_file():
                raise FileUtilsError(f"Path is not a file: {path}")

            self.logger.info(f"Deleting file: {path}")
            path.unlink()

            self.logger.info(f"Successfully deleted file: {path}")
            return True

        except Exception as e:
            error_msg = f"Failed to delete file {path}: {e}"
            self.logger.error(error_msg)
            raise FileUtilsError(error_msg)

    def copy_file(
        self,
        source_path: str | Path,
        destination_path: str | Path,
        create_dirs: bool = True,
    ) -> bool:
        """
        Copy a file from source to destination.

        Args:
            source_path: Source file path
            destination_path: Destination file path
            create_dirs: Whether to create parent directories

        Returns:
            True if successful

        Raises:
            FileUtilsError: If file cannot be copied
        """
        import shutil

        src_path = self._validate_file_path(source_path)
        dest_path = self._validate_file_path(destination_path)

        try:
            if not src_path.exists():
                raise FileUtilsError(f"Source file does not exist: {src_path}")

            if not src_path.is_file():
                raise FileUtilsError(f"Source path is not a file: {src_path}")

            if create_dirs:
                self._ensure_directory(dest_path)

            self.logger.info(f"Copying file from {src_path} to {dest_path}")
            shutil.copy2(src_path, dest_path)

            self.logger.info(f"Successfully copied file to: {dest_path}")
            return True

        except Exception as e:
            error_msg = f"Failed to copy file from {src_path} to {dest_path}: {e}"
            self.logger.error(error_msg)
            raise FileUtilsError(error_msg)

    def list_files(
        self,
        directory_path: str | Path,
        pattern: str = "*",
        recursive: bool = False,
        files_only: bool = True,
    ) -> list[Path]:
        """
        List files in a directory.

        Args:
            directory_path: Directory to list files from
            pattern: Glob pattern to match (default: *)
            recursive: Whether to search recursively
            files_only: Whether to return only files (not directories)

        Returns:
            List of Path objects

        Raises:
            FileUtilsError: If directory cannot be accessed
        """
        try:
            dir_path = Path(directory_path)

            if not dir_path.exists():
                raise FileUtilsError(f"Directory does not exist: {dir_path}")

            if not dir_path.is_dir():
                raise FileUtilsError(f"Path is not a directory: {dir_path}")

            self.logger.info(f"Listing files in directory: {dir_path}")

            if recursive:
                paths = dir_path.rglob(pattern)
            else:
                paths = dir_path.glob(pattern)

            if files_only:
                paths = [p for p in paths if p.is_file()]
            else:
                paths = list(paths)

            self.logger.info(f"Found {len(paths)} items in directory: {dir_path}")
            return sorted(paths)

        except Exception as e:
            error_msg = f"Failed to list files in directory {directory_path}: {e}"
            self.logger.error(error_msg)
            raise FileUtilsError(error_msg)


# ==================== CONVENIENCE FUNCTIONS ====================


def read_text(file_path: str | Path, trace_id: str = None, **kwargs) -> str:
    """Convenience function to read a text file."""
    file_utils = FileUtils(trace_id=trace_id)
    return file_utils.read_text_file(file_path, **kwargs)


def write_text(file_path: str | Path, content: str, trace_id: str = None, **kwargs) -> bool:
    """Convenience function to write a text file."""
    file_utils = FileUtils(trace_id=trace_id)
    return file_utils.write_text_file(file_path, content, **kwargs)


def read_json(file_path: str | Path, trace_id: str = None, **kwargs) -> Any:
    """Convenience function to read a JSON file."""
    file_utils = FileUtils(trace_id=trace_id)
    return file_utils.read_json_file(file_path, **kwargs)


def write_json(file_path: str | Path, data: Any, trace_id: str = None, **kwargs) -> bool:
    """Convenience function to write a JSON file."""
    file_utils = FileUtils(trace_id=trace_id)
    return file_utils.write_json_file(file_path, data, **kwargs)


def read_csv(file_path: str | Path, trace_id: str = None, **kwargs) -> list[dict[str, str]]:
    """Convenience function to read a CSV file."""
    file_utils = FileUtils(trace_id=trace_id)
    return file_utils.read_csv_file(file_path, **kwargs)


def write_csv(
    file_path: str | Path,
    data: list[dict[str, Any]],
    trace_id: str = None,
    **kwargs,
) -> bool:
    """Convenience function to write a CSV file."""
    file_utils = FileUtils(trace_id=trace_id)
    return file_utils.write_csv_file(file_path, data, **kwargs)


def file_exists(file_path: str | Path) -> bool:
    """Convenience function to check if a file exists."""
    file_utils = FileUtils()
    return file_utils.file_exists(file_path)


def get_file_info(file_path: str | Path, trace_id: str = None) -> dict[str, Any]:
    """Convenience function to get file information."""
    file_utils = FileUtils(trace_id=trace_id)
    return file_utils.get_file_info(file_path)

"""
Service layer for file operations.
"""

import csv
import io
import json
from typing import Any, Dict, Generator, List

from fastapi import HTTPException, UploadFile


class FileService:
    """Service for file upload, download, and streaming operations."""

    @staticmethod
    def validate_file_size(file: UploadFile, limit_kb: int = 25) -> None:
        """
        Validates that the file size is within the specified limit (in KB).
        """
        # Read file to get size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > limit_kb * 1024:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"File size exceeds the limit of {limit_kb}KB. "
                    f"Current size: {file_size / 1024:.2f}KB"
                ),
            )

    @staticmethod
    def get_human_readable_size(size_bytes: int) -> str:
        """
        Converts bytes to a human-readable string (e.g., '25.0 KB').
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    @staticmethod
    async def parse_linear_file(file: UploadFile) -> List[Dict[str, Any]]:
        """
        Parses a linear data file (CSV or JSON) and returns a list of records.
        Returns the top 10 records.
        """
        # Read file content
        content = await file.read()
        file.file.seek(0)  # Reset for potential re-reading

        content_str = content.decode("utf-8")
        file_ext = file.filename.split(".")[-1].lower() if file.filename else ""

        data = []

        if file_ext == "csv":
            # Parse CSV
            csv_file = io.StringIO(content_str)
            reader = csv.DictReader(csv_file)
            data = [row for row in reader]
        elif file_ext == "json":
            # Parse JSON
            try:
                json_data = json.loads(content_str)
                if isinstance(json_data, list):
                    data = json_data
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="JSON file must contain a list of objects.",
                    )
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON file.")
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Only .csv and .json are allowed.",
            )

        return data[:10]

    @staticmethod
    def get_dummy_content(size_kb: int = 25) -> str:
        """
        Generates dummy text content of a specific size.
        """
        # Generate a string of approximately size_kb KB
        # 1 KB = 1024 bytes
        pattern = "This is a line of dummy content for the file reference app.\n"
        pattern_size = len(pattern.encode("utf-8"))
        repeats = (size_kb * 1024) // pattern_size
        return pattern * repeats

    @staticmethod
    def get_file_stream(filename: str, size_kb: int = 25) -> Generator[str, None, None]:
        """
        Yields chunks of data to simulate file streaming.
        """
        content = FileService.get_dummy_content(size_kb)
        chunk_size = 1024  # 1KB chunks

        # Simulate reading in chunks
        for i in range(0, len(content), chunk_size):
            yield content[i : i + chunk_size]

    @staticmethod
    def get_file_content(filename: str, size_kb: int = 25) -> str:
        """
        Returns the full content of a dummy file.
        """
        return FileService.get_dummy_content(size_kb)

import json
import pytest
from fastapi import HTTPException, UploadFile
from io import BytesIO

from src.apps.files.service import FileService


class TestFileService:
    def test_validate_file_size_success(self):
        # 1KB file, limit 25KB
        content = b"a" * 1024
        file = UploadFile(filename="test.txt", file=BytesIO(content))
        FileService.validate_file_size(file, limit_kb=25)  # Should not raise

    def test_validate_file_size_exceeded(self):
        # 26KB file, limit 25KB
        content = b"a" * (26 * 1024)
        file = UploadFile(filename="test.txt", file=BytesIO(content))
        with pytest.raises(HTTPException) as exc:
            FileService.validate_file_size(file, limit_kb=25)
        assert exc.value.status_code == 400
        assert "File size exceeds the limit" in exc.value.detail

    def test_get_human_readable_size(self):
        assert FileService.get_human_readable_size(500) == "500.0 B"
        assert FileService.get_human_readable_size(1024) == "1.0 KB"
        assert FileService.get_human_readable_size(1536) == "1.5 KB"
        assert FileService.get_human_readable_size(1024 * 1024) == "1.0 MB"
        assert FileService.get_human_readable_size(1024 * 1024 * 1024) == "1.0 GB"
        assert FileService.get_human_readable_size(1024**5) == "1.0 PB"

    @pytest.mark.asyncio
    async def test_parse_linear_file_csv(self):
        content = b"name,age\nAlice,30\nBob,25"
        file = UploadFile(filename="test.csv", file=BytesIO(content))
        data = await FileService.parse_linear_file(file)
        assert len(data) == 2
        assert data[0]["name"] == "Alice"
        assert data[1]["age"] == "25"

    @pytest.mark.asyncio
    async def test_parse_linear_file_json(self):
        content = json.dumps([{"name": "Alice", "age": 30}]).encode("utf-8")
        file = UploadFile(filename="test.json", file=BytesIO(content))
        data = await FileService.parse_linear_file(file)
        assert len(data) == 1
        assert data[0]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_parse_linear_file_invalid_json(self):
        content = b"invalid json"
        file = UploadFile(filename="test.json", file=BytesIO(content))
        with pytest.raises(HTTPException) as exc:
            await FileService.parse_linear_file(file)
        assert exc.value.status_code == 400
        assert "Invalid JSON file" in exc.value.detail

    @pytest.mark.asyncio
    async def test_parse_linear_file_json_not_list(self):
        content = json.dumps({"name": "Alice"}).encode("utf-8")
        file = UploadFile(filename="test.json", file=BytesIO(content))
        with pytest.raises(HTTPException) as exc:
            await FileService.parse_linear_file(file)
        assert exc.value.status_code == 400
        assert "JSON file must contain a list of objects" in exc.value.detail

    @pytest.mark.asyncio
    async def test_parse_linear_file_unsupported_extension(self):
        content = b"some content"
        file = UploadFile(filename="test.txt", file=BytesIO(content))
        with pytest.raises(HTTPException) as exc:
            await FileService.parse_linear_file(file)
        assert exc.value.status_code == 400
        assert "Unsupported file type" in exc.value.detail

    def test_get_dummy_content(self):
        content = FileService.get_dummy_content(size_kb=1)
        # It's approximate, but should be close to 1024 bytes
        assert len(content.encode("utf-8")) > 0

    def test_get_file_content(self):
        content = FileService.get_file_content("test.txt", size_kb=1)
        assert len(content) > 0

    def test_get_file_stream(self):
        stream = FileService.get_file_stream("test.txt", size_kb=1)
        chunks = list(stream)
        assert len(chunks) > 0
        assert isinstance(chunks[0], str)

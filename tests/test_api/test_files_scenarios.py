from fastapi.testclient import TestClient


class TestFileScenarios:
    def test_file_upload_download(self, client: TestClient):
        """Test file upload and download scenarios"""

        # 1. Upload Linear File (CSV)
        files = {"file": ("test.csv", b"name,age\nAlice,30\nBob,25", "text/csv")}
        response = client.post("/api/v1/files/upload/linear", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["filename"] == "test.csv"
        assert len(data["data"]["preview_rows"]) == 2
        assert data["data"]["preview_rows"][0]["name"] == "Alice"

        # 2. Upload Generic File
        files = {"file": ("test.txt", b"Hello World", "text/plain")}
        response = client.post("/api/v1/files/upload/generic", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["filename"] == "test.txt"
        assert data["data"]["size"] == 11
        assert data["data"]["human_readable_size"] == "11.0 B"

        # 3. Download File
        response = client.get("/api/v1/files/download/test_dl.txt")
        assert response.status_code == 200
        assert len(response.content) > 0

        # 4. Stream File
        response = client.get("/api/v1/files/stream/test_stream.txt")
        assert response.status_code == 200
        # Streaming response is consumed by TestClient
        assert len(response.content) > 0

        # 5. Preview File
        response = client.get("/api/v1/files/preview/test_preview.txt")
        assert response.status_code == 200
        assert len(response.text) > 0

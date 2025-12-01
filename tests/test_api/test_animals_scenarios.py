from fastapi.testclient import TestClient


class TestAnimalScenarios:
    def test_animal_lifecycle(self, client: TestClient):
        """Test full lifecycle of an animal: Create -> List -> Get -> Update -> Delete"""

        # 1. Create Animal
        create_payload = {"name": "Simba", "species": "Lion", "age": 5}
        response = client.post("/api/v1/animals/", json=create_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        animal_id = data["data"]["id"]
        assert data["data"]["name"] == "Simba"
        assert data["data"]["species"] == "Lion"
        assert data["data"]["age"] == 5

        # 2. List Animals
        response = client.get("/api/v1/animals/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["items"]) >= 1
        assert any(a["id"] == animal_id for a in data["data"]["items"])

        # 3. Get Animal
        response = client.get(f"/api/v1/animals/{animal_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == animal_id
        assert data["data"]["name"] == "Simba"

        # 4. Update Animal
        update_payload = {"name": "Simba King", "species": "Lion", "age": 6}
        response = client.put(f"/api/v1/animals/{animal_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Simba King"
        assert data["data"]["age"] == 6

        # 5. Delete Animal
        response = client.delete(f"/api/v1/animals/{animal_id}")
        assert response.status_code == 204
        # 204 has no content

        # Verify deletion
        response = client.get(f"/api/v1/animals/{animal_id}")
        assert response.status_code == 404

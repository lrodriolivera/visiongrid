from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from visiongrid.api.app import create_app
from visiongrid.core.config import Settings


@pytest.fixture
def client() -> TestClient:
    settings = Settings(cameras=[])
    app = create_app(settings)
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "cameras" in data

    def test_health_shows_version(self, client: TestClient) -> None:
        response = client.get("/health")
        data = response.json()
        assert data["version"] == "0.1.0"


class TestCamerasEndpoint:
    def test_list_cameras_empty(self, client: TestClient) -> None:
        response = client.get("/api/v1/cameras")
        assert response.status_code == 200
        assert response.json() == []

    def test_add_camera(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/cameras",
            json={
                "name": "test-cam",
                "url": "rtsp://fake:554/stream",
                "protocol": "rtsp",
                "fps": 10,
                "enabled": False,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-cam"

    def test_add_duplicate_camera(self, client: TestClient) -> None:
        client.post(
            "/api/v1/cameras",
            json={"name": "dup", "url": "rtsp://fake:554/stream", "enabled": False},
        )
        response = client.post(
            "/api/v1/cameras",
            json={"name": "dup", "url": "rtsp://fake:554/stream", "enabled": False},
        )
        assert response.status_code == 409

    def test_remove_camera(self, client: TestClient) -> None:
        client.post(
            "/api/v1/cameras",
            json={"name": "to-remove", "url": "rtsp://fake:554/stream", "enabled": False},
        )
        response = client.delete("/api/v1/cameras/to-remove")
        assert response.status_code == 200

    def test_remove_nonexistent_camera(self, client: TestClient) -> None:
        response = client.delete("/api/v1/cameras/ghost")
        assert response.status_code == 404


class TestEventsEndpoint:
    def test_get_events_empty(self, client: TestClient) -> None:
        response = client.get("/api/v1/events")
        assert response.status_code == 200
        assert response.json() == []


class TestDetectionEndpoint:
    def test_list_zones_empty(self, client: TestClient) -> None:
        response = client.get("/api/v1/zones")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_zone(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/zones",
            json={
                "name": "test-zone",
                "camera_name": "cam1",
                "points": [[0.1, 0.1], [0.9, 0.1], [0.9, 0.9], [0.1, 0.9]],
                "triggers": ["enter"],
            },
        )
        assert response.status_code == 201

    def test_get_counts(self, client: TestClient) -> None:
        response = client.get("/api/v1/counting")
        assert response.status_code == 200
        assert "counts" in response.json()

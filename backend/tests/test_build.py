"""Tests for build endpoint."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_build_invalid_board(client: TestClient) -> None:
    response = client.post("/api/build", json={"board_id": "invalid-board"})
    assert response.status_code == 422


def test_build_content_too_large(client: TestClient) -> None:
    response = client.post(
        "/api/build",
        json={
            "board_id": "nodemcu",
            "html": "x" * 600_000,
        },
    )
    assert response.status_code == 413


def test_build_valid_request(client: TestClient) -> None:
    response = client.post(
        "/api/build",
        json={
            "board_id": "nodemcu",
            "html": "<h1>Hello</h1>",
            "css": "body { color: red; }",
            "js": "console.log('hi')",
        },
    )
    # Should return 200 with a job_id (build runs in background)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert "cached" in data

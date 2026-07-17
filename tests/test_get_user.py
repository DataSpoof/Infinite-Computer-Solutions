"""Tests for retrieving a single user."""


def test_get_user_success(client, sample_user_payload):
    created = client.post("/users/", json=sample_user_payload).json()
    user_id = created["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == sample_user_payload["email"]


def test_get_user_not_found(client):
    response = client.get("/users/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_user_invalid_id(client):
    response = client.get("/users/abc")
    assert response.status_code == 422

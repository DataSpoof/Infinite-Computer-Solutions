"""Tests for creating users."""


def test_create_user_success(client, sample_user_payload):
    response = client.post("/users/", json=sample_user_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_user_payload["name"]
    assert data["email"] == sample_user_payload["email"]
    assert data["age"] == sample_user_payload["age"]
    assert data["is_active"] is True
    assert "id" in data


def test_create_user_duplicate_email(client, sample_user_payload):
    first = client.post("/users/", json=sample_user_payload)
    assert first.status_code == 201

    second = client.post("/users/", json=sample_user_payload)
    assert second.status_code == 400
    assert second.json()["detail"] == "Email already registered"


def test_create_user_invalid_email(client):
    payload = {"name": "Bob", "email": "not-an-email"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 422


def test_create_user_missing_name(client):
    payload = {"email": "carol@example.com"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 422

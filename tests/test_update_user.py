"""Tests for replacing users (PUT — full replacement)."""


def test_put_replaces_user(client, sample_user_payload):
    created = client.post("/users/", json=sample_user_payload).json()
    user_id = created["id"]

    # Full replacement requires every field.
    response = client.put(
        f"/users/{user_id}",
        json={
            "name": "Alice Replaced",
            "email": "alice@example.com",
            "age": 31,
            "is_active": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice Replaced"
    assert data["age"] == 31
    assert data["is_active"] is False


def test_put_resets_omitted_optional_fields(client, sample_user_payload):
    # Created with age=30, is_active=True.
    created = client.post("/users/", json=sample_user_payload).json()
    user_id = created["id"]

    # PUT with only the required fields: optionals fall back to schema
    # defaults (age -> None, is_active -> True).
    response = client.put(
        f"/users/{user_id}",
        json={"name": "Alice", "email": "alice@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["age"] is None
    assert data["is_active"] is True


def test_put_missing_required_field(client, sample_user_payload):
    created = client.post("/users/", json=sample_user_payload).json()
    # Missing email -> validation error (PUT is not partial).
    response = client.put(f"/users/{created['id']}", json={"name": "NoEmail"})
    assert response.status_code == 422


def test_put_user_not_found(client):
    response = client.put(
        "/users/9999",
        json={"name": "Nobody", "email": "nobody@example.com"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_put_duplicate_email(client):
    client.post("/users/", json={"name": "A", "email": "a@example.com"})
    second = client.post(
        "/users/", json={"name": "B", "email": "b@example.com"}
    ).json()

    # Try to replace B using A's email.
    response = client.put(
        f"/users/{second['id']}",
        json={"name": "B", "email": "a@example.com"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

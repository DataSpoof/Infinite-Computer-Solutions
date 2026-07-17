"""Tests for partially updating users (PATCH — partial update)."""


def test_patch_updates_single_field(client, sample_user_payload):
    created = client.post("/users/", json=sample_user_payload).json()
    user_id = created["id"]

    response = client.patch(f"/users/{user_id}", json={"age": 31})
    assert response.status_code == 200
    data = response.json()
    assert data["age"] == 31
    # Untouched fields are preserved.
    assert data["name"] == sample_user_payload["name"]
    assert data["email"] == sample_user_payload["email"]
    assert data["is_active"] is True


def test_patch_empty_body_keeps_user(client, sample_user_payload):
    created = client.post("/users/", json=sample_user_payload).json()
    user_id = created["id"]

    response = client.patch(f"/users/{user_id}", json={})
    assert response.status_code == 200
    assert response.json() == created


def test_patch_user_not_found(client):
    response = client.patch("/users/9999", json={"name": "Nobody"})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_patch_duplicate_email(client):
    client.post("/users/", json={"name": "A", "email": "a@example.com"})
    second = client.post(
        "/users/", json={"name": "B", "email": "b@example.com"}
    ).json()

    response = client.patch(
        f"/users/{second['id']}", json={"email": "a@example.com"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_patch_same_email_allowed(client, sample_user_payload):
    created = client.post("/users/", json=sample_user_payload).json()
    response = client.patch(
        f"/users/{created['id']}",
        json={"email": sample_user_payload["email"], "name": "Same Email"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Same Email"

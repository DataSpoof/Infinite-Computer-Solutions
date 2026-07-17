"""Tests for deleting users."""


def test_delete_user_success(client, sample_user_payload):
    created = client.post("/users/", json=sample_user_payload).json()
    user_id = created["id"]

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204

    # Confirm it is really gone.
    follow_up = client.get(f"/users/{user_id}")
    assert follow_up.status_code == 404


def test_delete_user_not_found(client):
    response = client.delete("/users/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user_twice(client, sample_user_payload):
    created = client.post("/users/", json=sample_user_payload).json()
    user_id = created["id"]

    assert client.delete(f"/users/{user_id}").status_code == 204
    assert client.delete(f"/users/{user_id}").status_code == 404

"""Tests for listing users."""


def test_get_users_empty(client):
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_users_returns_all(client):
    users = [
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": "bob@example.com"},
        {"name": "Carol", "email": "carol@example.com"},
    ]
    for user in users:
        assert client.post("/users/", json=user).status_code == 201

    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    emails = {u["email"] for u in data}
    assert emails == {u["email"] for u in users}


def test_get_users_pagination(client):
    for i in range(5):
        client.post(
            "/users/",
            json={"name": f"User{i}", "email": f"user{i}@example.com"},
        )

    response = client.get("/users/?skip=1&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2

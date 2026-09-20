from app.dependences import get_current_user
from app.main import app


def test_login_success_and_account_lookup(client):
    created = client.post(
        "/users/",
        json={"username": "cashier", "password": "password123"},
    )
    assert created.status_code == 201

    login = client.post(
        "/auth/login",
        json={"username": "cashier", "password": "password123"},
    )
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    assert login.json()["access_token"]


def test_login_rejects_wrong_password(client):
    client.post(
        "/users/",
        json={"username": "cashier", "password": "password123"},
    )
    response = client.post(
        "/auth/login",
        json={"username": "cashier", "password": "wrong-pass"},
    )
    assert response.status_code == 401


def test_user_crud_and_duplicate_username(client, admin_headers):
    payload = {"username": "cashier", "password": "password123"}
    created = client.post("/users/", json=payload, headers=admin_headers)
    assert created.status_code == 201
    user_id = created.json()["user_id"]
    assert created.json()["role"] == "cashier"

    duplicate = client.post("/users/", json=payload, headers=admin_headers)
    assert duplicate.status_code == 400

    updated = client.put(
        f"/users/{user_id}",
        json={"username": "updated-cashier"},
        headers=admin_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["username"] == "updated-cashier"

    listed = client.get("/users/", headers=admin_headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    deleted = client.delete(f"/users/{user_id}", headers=admin_headers)
    assert deleted.status_code == 204
    assert client.get(f"/users/{user_id}", headers=admin_headers).status_code == 404


def test_user_validation_and_missing_resource(client, admin_headers):
    invalid = client.post(
        "/users/",
        json={"username": "ab", "password": "short"},
        headers=admin_headers,
    )
    assert invalid.status_code == 422
    assert client.get("/users/999", headers=admin_headers).status_code == 404


def test_protected_endpoint_requires_credentials(client):
    app.dependency_overrides.pop(get_current_user, None)
    response = client.get("/products/")
    assert response.status_code == 401

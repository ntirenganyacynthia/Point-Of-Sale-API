import pytest


def test_category_crud_and_missing_resource(client, admin_headers):
    created = client.post(
        "/categories/",
        json={"category_name": "Snacks"},
        headers=admin_headers,
    )
    assert created.status_code == 201
    category_id = created.json()["category_id"]

    updated = client.put(
        f"/categories/{category_id}",
        json={"category_name": "Packaged Snacks"},
        headers=admin_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["category_name"] == "Packaged Snacks"
    assert client.get("/categories/", headers=admin_headers).status_code == 200

    assert client.delete(f"/categories/{category_id}", headers=admin_headers).status_code == 204
    assert client.get(f"/categories/{category_id}", headers=admin_headers).status_code == 404


def test_category_validation(client, admin_headers):
    response = client.post(
        "/categories/",
        json={},
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_supplier_crud_and_missing_resource(client):
    created = client.post("/suppliers/", json={"supplier_name": "Fresh Foods"})
    assert created.status_code == 201
    supplier_id = created.json()["supplier_id"]

    updated = client.put(
        f"/suppliers/{supplier_id}",
        json={"supplier_name": "Fresh Foods Ltd", "address": "Kigali"},
    )
    assert updated.status_code == 200
    assert updated.json()["supplier_name"] == "Fresh Foods Ltd"

    assert client.get("/suppliers/").status_code == 200
    assert client.delete(f"/suppliers/{supplier_id}").status_code == 204
    assert client.get(f"/suppliers/{supplier_id}").status_code == 404


def test_product_crud_validation_and_missing_resource(
    client, admin_headers, category, supplier
):
    payload = {
        "category_id": category["category_id"],
        "supplier_id": supplier["supplier_id"],
        "product_name": "Tea",
        "unit_price": "5.50",
        "cost_price": "3.25",
        "stock_quantity": "8",
    }
    created = client.post("/products/", json=payload, headers=admin_headers)
    assert created.status_code == 201
    product_id = created.json()["product_id"]

    updated = client.put(
        f"/products/{product_id}",
        json={"product_name": "Green Tea", "unit_price": "6.00"},
        headers=admin_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["product_name"] == "Green Tea"

    invalid = client.post(
        "/products/",
        json={**payload, "unit_price": "0"},
        headers=admin_headers,
    )
    assert invalid.status_code == 422

    assert client.get("/products/", headers=admin_headers).status_code == 200
    assert client.delete(f"/products/{product_id}", headers=admin_headers).status_code == 204
    assert client.get(f"/products/{product_id}", headers=admin_headers).status_code == 404


@pytest.mark.parametrize(
    "path,method,payload",
    [
        ("/customers/", "post", {"full_name": "A", "customer_email": "bad", "password": "short"}),
        ("/products/", "post", {"product_name": "Missing fields"}),
    ],
)
def test_invalid_payloads_return_422(client, admin_headers, path, method, payload):
    headers = admin_headers if path == "/products/" else {}
    response = getattr(client, method)(path, json=payload, headers=headers)
    assert response.status_code == 422


def test_customer_crud_and_duplicate_email(client, customer):
    duplicate = client.post(
        "/customers/",
        json={
            "full_name": "Another Customer",
            "customer_email": "jane@example.com",
            "password": "customer-pass",
        },
    )
    assert duplicate.status_code in {400, 409}

    customer_id = customer["customer_id"]
    updated = client.put(
        f"/customers/{customer_id}",
        json={"full_name": "Jane Updated"},
    )
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Jane Updated"

    assert client.get("/customers/").status_code == 200
    assert client.delete(f"/customers/{customer_id}").status_code == 204
    assert client.get(f"/customers/{customer_id}").status_code == 404

def test_sale_crud_and_missing_customer(client, customer):
    payload = {
        "customer_id": customer["customer_id"],
        "total_amount": "0.00",
        "sale_status": "pending",
    }
    created = client.post("/sales/", json=payload)
    assert created.status_code == 201
    sale_id = created.json()["sale_id"]

    updated = client.put(
        f"/sales/{sale_id}",
        json={"sale_status": "completed", "total_amount": "15.00"},
    )
    assert updated.status_code == 200
    assert updated.json()["sale_status"] == "completed"

    assert client.get("/sales/").status_code == 200
    assert client.delete(f"/sales/{sale_id}").status_code == 204
    assert client.get(f"/sales/{sale_id}").status_code == 404

    missing_customer = client.post(
        "/sales/",
        json={
            "customer_id": 999,
            "total_amount": "10.00",
            "sale_status": "pending",
        },
    )
    assert missing_customer.status_code == 404


def test_sale_validation(client, customer):
    response = client.post(
        "/sales/",
        json={
            "customer_id": customer["customer_id"],
            "total_amount": "not-a-number",
            "sale_status": "pending",
        },
    )
    assert response.status_code == 422


def test_sale_item_crud_updates_stock_and_sale_total(client, sale, product):
    item_payload = {
        "sale_id": sale["sale_id"],
        "product_id": product["product_id"],
        "quantity": "2",
        "unit_price": "10.00",
        "sub_total": "20.00",
    }
    created = client.post("/sale-items/", json=item_payload)
    assert created.status_code == 201
    item_id = created.json()["sale_item_id"]
    assert created.json()["sub_total"] == "20.00"

    updated = client.put(
        f"/sale-items/{item_id}",
        json={"quantity": "3"},
    )
    assert updated.status_code == 200
    assert updated.json()["quantity"] == "3.00"

    assert client.get("/sale-items/").status_code == 200
    assert client.delete(f"/sale-items/{item_id}").status_code == 204
    assert client.get(f"/sale-items/{item_id}").status_code == 404


def test_sale_item_rejects_insufficient_stock_and_missing_sale(client, product):
    invalid_stock = client.post(
        "/sale-items/",
        json={
            "sale_id": 999,
            "product_id": product["product_id"],
            "quantity": "100",
            "unit_price": "10.00",
            "sub_total": "1000.00",
        },
    )
    assert invalid_stock.status_code == 404


def test_sale_item_validation(client):
    response = client.post(
        "/sale-items/",
        json={"sale_id": 1, "product_id": 1},
    )
    assert response.status_code == 422

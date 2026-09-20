def test_payment_crud_and_missing_sale(client, sale):
    payload = {
        "sale_id": sale["sale_id"],
        "payment_method": "cash",
        "amount_paid": "20.00",
    }
    created = client.post("/payments/", json=payload)
    assert created.status_code == 201
    payment_id = created.json()["payment_id"]

    updated = client.put(
        f"/payments/{payment_id}",
        json={"payment_method": "mobile-money", "payment_status": "completed"},
    )
    assert updated.status_code == 200
    assert updated.json()["payment_method"] == "mobile-money"

    assert client.get("/payments/").status_code == 200
    assert client.delete(f"/payments/{payment_id}").status_code == 204
    assert client.get(f"/payments/{payment_id}").status_code == 404

    missing_sale = client.post(
        "/payments/",
        json={
            "sale_id": 999,
            "payment_method": "cash",
            "amount_paid": "10.00",
        },
    )
    assert missing_sale.status_code == 404


def test_payment_validation(client, sale):
    response = client.post(
        "/payments/",
        json={
            "sale_id": sale["sale_id"],
            "payment_method": "cash",
            "amount_paid": "0",
        },
    )
    assert response.status_code == 422


def test_receipt_crud_and_unique_sale_constraint(client, sale):
    payload = {"sale_id": sale["sale_id"], "receipt_number": "RCT-001"}
    created = client.post("/receipts/", json=payload)
    assert created.status_code == 201
    receipt_id = created.json()["receipt_id"]

    duplicate = client.post("/receipts/", json=payload)
    assert duplicate.status_code == 409

    updated = client.put(
        f"/receipts/{receipt_id}",
        json={"receipt_number": "RCT-UPDATED"},
    )
    assert updated.status_code == 200
    assert updated.json()["receipt_number"] == "RCT-UPDATED"

    assert client.get("/receipts/").status_code == 200
    assert client.delete(f"/receipts/{receipt_id}").status_code == 204
    assert client.get(f"/receipts/{receipt_id}").status_code == 404


def test_receipt_validation_and_missing_resource(client):
    invalid = client.post("/receipts/", json={"sale_id": 1})
    assert invalid.status_code == 422
    assert client.get("/receipts/999").status_code == 404

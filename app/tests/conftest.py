from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.dependences import get_current_user
from app.main import app


@pytest.fixture
def client():
 
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        user_id=1,
        username="test-admin",
        role="admin",
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def admin_headers():
  
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def category(client, admin_headers):
    response = client.post(
        "/categories/",
        json={"category_name": "Beverages"},
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def supplier(client):
    response = client.post(
        "/suppliers/",
        json={
            "supplier_name": "Acme Supplies",
            "email": "supplier@example.com",
            "phone_number": "250788123456",
            "address": "Kigali",
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def product(client, admin_headers, category, supplier):
    response = client.post(
        "/products/",
        json={
            "category_id": category["category_id"],
            "supplier_id": supplier["supplier_id"],
            "product_name": "Coffee",
            "unit_price": "10.00",
            "cost_price": "6.00",
            "stock_quantity": "20.00",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def customer(client):
    response = client.post(
        "/customers/",
        json={
            "full_name": "Jane Customer",
            "customer_email": "jane@example.com",
            "customer_phonenumber": "250788123456",
            "password": "customer-pass",
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def sale(client, customer):
    response = client.post(
        "/sales/",
        json={
            "customer_id": customer["customer_id"],
            "total_amount": "20.00",
            "sale_status": "pending",
        },
    )
    assert response.status_code == 201
    return response.json()

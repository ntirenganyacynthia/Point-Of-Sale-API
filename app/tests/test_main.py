from app.main import app


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "POS System Backend API is active",
    }


def test_application_metadata():
    assert app.title == "POS API"
    assert any(getattr(route, "path", None) == "/" for route in app.routes)

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_success():
    response = client.get("/")
    assert response.status_code == 205


def test_websocket_health_check_success():
    with client.websocket_connect("/ws") as websocket:
        assert websocket.receive_text() == "Server is operational"

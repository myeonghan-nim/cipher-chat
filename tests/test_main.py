from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_websocket_echo():
    with client.websocket_connect("/ws") as websocket:
        test_message = "Test Message"
        websocket.send_text(test_message)
        data = websocket.receive_text()
        assert data == f"Received: {test_message}"

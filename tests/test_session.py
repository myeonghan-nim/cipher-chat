from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_session_success():
    response = client.post("/session/create")
    assert response.status_code == 201

    data = response.json()
    assert "session_id" in data


def test_close_session_success():
    # 세션 생성
    create_response = client.post("/session/create")
    session_id = create_response.json()["session_id"]

    # 세션 종료 요청
    close_response = client.post("/session/close", params={"session_id": session_id})
    assert close_response.status_code == 200

    data = close_response.json()
    assert "closed" in data["message"]


def test_close_session_no_session_id():
    response = client.post("/session/close")
    assert response.status_code == 422


def test_close_session_invalid_session_id():
    response = client.post("/session/close", params={"session_id": "invalid"})
    assert response.status_code == 404

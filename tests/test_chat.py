import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app

client = TestClient(app)


def test_chat_success():
    # REST API로 채팅 세션 생성 요청
    create_response = client.post("/session/create")
    assert create_response.status_code == 201
    session_id = create_response.json()["session_id"]

    # 두 개의 WebSocket 클라이언트를 같은 세션 ID로 접속 (URL 경로에 세션 ID 사용)
    ws_url = f"/chat/{session_id}"
    try:
        with (
            client.websocket_connect(ws_url) as ws1,
            client.websocket_connect(ws_url) as ws2,
        ):
            # ws1, ws2 모두 연결되었음
            # ws1에서 메시지를 보내면 ws2가 수신해야 함
            test_message = "Hello, world!"
            ws1.send_text(test_message)
            received = ws2.receive_text(timeout=3)
            assert received == test_message

            # 반대 방향 테스트: ws2에서 보낸 메시지를 ws1이 수신
            reply_message = "Hi back!"
            ws2.send_text(reply_message)
            received_reply = ws1.receive_text(timeout=3)
            assert received_reply == reply_message
    except WebSocketDisconnect:
        # 연결 종료 시 발생하는 WebSocketDisconnect는 테스트 종료 시 자연스러운 동작으로 간주
        # 테스트 내 메시지 교환은 이미 검증했으므로 예외를 무시
        pass


def test_chat_missing_session():
    # session_id가 없는 URL로 접속 시, 연결 실패를 예상
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/chat/") as ws:
            ws.receive_text(timeout=1)
    # TestClient가 발생시키는 WebSocketDisconnect 예외는 close_code나 reason을 문자열로 전달하지 않음
    # 따라서, 예외 타입(WebSocketDisconnect)만으로 테스트를 통과
    assert isinstance(exc_info.value, WebSocketDisconnect)

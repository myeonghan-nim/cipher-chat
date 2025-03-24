from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from redis.exceptions import RedisError

from app.core.redis import redis_client

router = APIRouter()

# 세션 ID를 키로 가지고 웹소켓 연결을 값으로 가지는 딕셔너리
active_sessions = {}


@router.websocket("/{session_id}")
async def chat(websocket: WebSocket, session_id: str):
    # Redis에서 세션 존재 여부 확인
    try:
        exists = await redis_client.exists(session_id)
    except RedisError:
        await websocket.close(code=1011, reason="Internal server error")
        return

    if not exists:
        await websocket.close(code=1008, reason="Session not found")
        return

    # 연결 수락
    await websocket.accept()

    # active_sessions에 연결 추가
    if session_id not in active_sessions:
        active_sessions[session_id] = []
    if len(active_sessions[session_id]) >= 2:
        await websocket.close(code=1008, reason="Session full")
        return
    active_sessions[session_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # 받은 메시지를 같은 세션의 상대방에게 전달
            for conn in active_sessions[session_id]:
                if conn != websocket:
                    await conn.send_text(data)
    except WebSocketDisconnect:
        # 연결 해제 시 목록에서 제거 및 남은 참가자에게 알림
        active_sessions[session_id].remove(websocket)
        if active_sessions[session_id]:
            for conn in active_sessions[session_id]:
                await conn.send_text("Peer disconnected")

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from redis.exceptions import RedisError

from app.core.redis import redis_client
from app.core.logging import logger

router = APIRouter()

# 세션 ID를 키로 가지고 웹소켓 연결을 값으로 가지는 딕셔너리
active_sessions = {}

# Ping/Pong 및 Keep-Alive 확인을 위한 주기
PING_INTERVAL = 30
# Timeout 설정
RECEIVE_TIMEOUT = 60


async def ping_loop(websocket: WebSocket):
    try:
        while True:
            await asyncio.sleep(PING_INTERVAL)
            try:
                await websocket.send_text("ping")
            except Exception as e:
                break
    except asyncio.CancelledError:
        return
    except WebSocketDisconnect:
        return


@router.websocket("/{session_id}")
async def chat(websocket: WebSocket, session_id: str):
    logger.info(f"WebSocket connection established for session: {session_id}")

    # Redis에서 세션 존재 여부 확인
    try:
        exists = await redis_client.exists(session_id)
    except RedisError as e:
        logger.error(f"Redis error: {e}")
        await websocket.close(code=1011, reason="Internal server error")
        return

    if not exists:
        await websocket.close(code=1008, reason="Session not found")
        return

    # 연결 수락
    try:
        await websocket.accept()
    except Exception as e:
        logger.error(f"WebSocket accept error: {e}")
        await websocket.close(code=1011, reason="Internal server error")
        return

    # active_sessions에 연결 추가
    if session_id not in active_sessions:
        active_sessions[session_id] = []
    if len(active_sessions[session_id]) >= 2:
        await websocket.close(code=1008, reason="Session full")
        return
    active_sessions[session_id].append(websocket)

    # Ping/Pong 및 Keep-Alive 확인을 위한 루프 시작
    ping_task = asyncio.create_task(ping_loop(websocket))

    try:
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=RECEIVE_TIMEOUT,
                )
            except asyncio.TimeoutError:
                # Timeout 발생 시 연결 종료
                await websocket.close(code=1008, reason="Timeout")
                break

            # Ping/Pong 메시지 처리
            if data == "pong":
                continue

            # 받은 메시지를 같은 세션의 상대방에게 전달
            for conn in active_sessions[session_id]:
                if conn != websocket:
                    try:
                        await conn.send_text(data)
                    except Exception as e:
                        logger.error(f"WebSocket send error: {e}")
                        pass
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Ping/Pong 루프 종료
        ping_task.cancel()

        # 연결이 종료되고
        if session_id in active_sessions:
            # 상대방에게 연결 종료 알림
            if len(active_sessions[session_id]) > 0:
                for conn in active_sessions[session_id]:
                    if conn != websocket:
                        try:
                            await conn.send_text("Peer disconnected")
                        except Exception:
                            pass

            # 목록에서 제거
            if websocket in active_sessions[session_id]:
                active_sessions[session_id].remove(websocket)

            # Redis에서 세션 삭제
            try:
                await redis_client.delete(session_id)
            except RedisError as e:
                logger.error(f"Redis delete error: {e}")
                pass

            del active_sessions[session_id]

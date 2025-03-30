from fastapi import FastAPI, Response, WebSocket
from prometheus_fastapi_instrumentator import Instrumentator

from app.endpoints.chat import router as chat_router
from app.endpoints.session import router as session_router

app = FastAPI()


# 기본 REST 엔드포인트
# 서버 상태 체크 엔드포인트로 클라이언트 요청 시 205 상태 코드만 응답
@app.get("/", status_code=205)
async def health_check():
    # 205는 컨텐츠 없이 클라이언트에 뷰를 리셋하라는 메시지 전달
    return Response(status_code=205)


# 간단한 WebSocket 엔드포인트
# 서버 상태 체크 엔드포인트로 클라이언트 요청 시 "Server is operational" 메시지 전송 후 연결 종료
@app.websocket("/ws")
async def websocket_health_check(websocket: WebSocket):
    await websocket.accept()
    # 서버가 정상임을 알리는 메시지 전송
    await websocket.send_text("Server is operational")
    # 메시지 전송 후 연결 종료
    await websocket.close()


# 채팅 세션 관련 엔드포인트 통합
app.include_router(session_router, prefix="/session", tags=["session"])
# 채팅 관련 엔드포인트 통합
app.include_router(chat_router, prefix="/chat", tags=["chat"])
# Prometheus Instrumentator 설정: /metrics 엔드포인트 노출
Instrumentator().instrument(app).expose(app)

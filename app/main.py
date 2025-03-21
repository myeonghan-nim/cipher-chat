from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


# 기본 REST API 엔드포인트
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


# 간단한 WebSocket 에코 엔드포인트
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # 클라이언트가 보낸 메시지를 그대로 반환 (에코)
            await websocket.send_text(f"Received: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")

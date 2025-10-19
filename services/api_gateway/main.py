from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio, random, time

app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"Hello": "World"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.websocket("/ws/trades")
async def trades_ws(websocket: WebSocket):
    """Simple dummy feed for the React app."""
    await websocket.accept()
    try:
        while True:
            # Send fake data every second
            trade = {
                "symbol": "BTCUSDT",
                "price": round(64000 + random.random() * 100, 2),
                "qty": round(random.random(), 4),
                "ts": int(time.time() * 1000),
            }
            await websocket.send_json(trade)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Client disconnected")

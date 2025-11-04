from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio, random, time

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'demo-consumer',
    'auto.offset.reset': 'earliest'
}

c = Consumer(conf)
c.subscribe(['raw.trades'])

app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

latest_price = {"binance": {"price": 188.4, "ts": 1699999999}, "hyperliquid": {"price": 188.6, "ts": 1699999998}}

def update_latest_trades(trade):

     if trade['exchange'] == 'binance':
        latest_price['binance']['price'] = trade['price']

    elif trade['exchange'] == 'hyperliquid':
        latest_price['hyperliquid']['price'] = trade['price']

def compute_spread():
    return (latest_price['binance']['price'] - latest_price['hyperliquid']['price'])


async def consume_trades():
    async for message in c:
        trade = decode(message)
        update_latest_trades(trade)
        compute_spread()

# FastAPI app runs an async consumer in the background.

# It updates prices and spread in memory.

# WebSocket sends spread updates to UI.

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

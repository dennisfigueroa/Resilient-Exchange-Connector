from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from confluent_kafka import Consumer
from contextlib import asynccontextmanager
from typing import List
import json
import asyncio

from fastapi.middleware.cors import CORSMiddleware


TOPIC = "analytics.spreads"
KAFKA_CONF = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'fastapi-dashboard-group', 
    'auto.offset.reset': 'latest'
}

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_message(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception: 
                self.disconnect(connection)
    
manager = ConnectionManager()

async def consume_kafka_spreads(): 
    print("Background Kafka Consumer Started..")
    consumer = Consumer(KAFKA_CONF)
    consumer.subscribe([TOPIC])

    try: 
        while True:
            msg = await asyncio.to_thread(consumer.poll, 0.1)

            if msg is None:
                await asyncio.sleep(0.1)
                continue
            
            if msg.error():
                print(f"Consumer error: {msg.error()}") 
                continue

            spread_data = msg.value().decode("utf-8")
            await manager.send_message(spread_data)
    
    except asyncio.CancelledError:
        print("Kafka Consumer cancelled.")

    finally:
        consumer.close()

@asynccontextmanager
async def lifespan(app: FastAPI):

    task = asyncio.create_task(consume_kafka_spreads())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Live Spreads</title>
        <style>
            body { font-family: monospace; text-align: center; padding: 50px; background: #222; color: #fff; }
            #spread-value { font-size: 4em; font-weight: bold; }
            .positive { color: #0f0; }
            .negative { color: #f00; }
        </style>
    </head>
    <body>
        <h1>Crypto Spread</h1>
        <div id="spread-value">Waiting...</div>
        <script>
            var ws = new WebSocket("ws://" + window.location.host + "/ws/spread");
            ws.onmessage = function(event) {
                var data = JSON.parse(event.data);
                var val = document.getElementById('spread-value');
                val.innerText = data.spread.toFixed(4);
                val.className = data.spread >= 0 ? 'positive' : 'negative';
            };
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws/spread")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
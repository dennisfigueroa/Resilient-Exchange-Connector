import asyncio
import json
import websockets
from confluent_kafka import Producer
from prometheus_client import start_http_server, Counter

BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"

producer = Producer({'bootstrap.servers': 'localhost:9092'})
produced_count = Counter("produced_trades_total", "Number of trades produced")

start_http_server(8000)

async def produce_from_binance():
    async with websockets.connect(BINANCE_WS_URL) as ws:
        async for msg in ws:
            data = json.loads(msg)
            trade_event = {
                "exchange": "binance",
                "symbol": data["s"],
                "price": float(data["p"]),
                "qty": float(data["q"]),
                "trade_id": data["t"],
                "ts": data["T"],
            }
            producer.produce("raw.trades", json.dumps(trade_event).encode("utf-8"))
            producer.poll(0)
            produced_count.inc()
            print(f"Produced trade: {trade_event}")

asyncio.run(produce_from_binance())

import asyncio
import json
import websockets
from confluent_kafka import Producer
from prometheus_client import start_http_server, Counter


EXCHANGES = {
    "binance": {
        "url": "wss://stream.binance.com:9443/ws",
        "params": ["btcusdt@trade", "ethusdt@trade", "solusdt@trade"]
    },
   "hyperliquid": {
        "url": "wss://api.hyperliquid.xyz/ws",
        "assets": ["BTC", "ETH", "SOL"] 
    }
}

producer = Producer({'bootstrap.servers': 'localhost:9092'})
produced_count = Counter("produced_trades_total", "Number of trades produced")

start_http_server(8000)

latest_price =  {"binance": {"price": 188.4, "ts": 1699999999}, "hyperliquid": {"price": 188.6, "ts": 1699999998}}

async def produce_from_binance():
    async with websockets.connect(EXCHANGES["binance"]["url"]) as ws:
         
        subscribe_msg = {
            "method": "SUBSCRIBE",
            "params": EXCHANGES["binance"]["params"],
            "id": 1
        }

        await ws.send(json.dumps(subscribe_msg))

        async for msg in ws:
            data = json.loads(msg)

            if "result" in data or "id" in data:
                continue

            trade_event = {
                "exchange": "binance",
                "symbol": data["s"],
                "price": float(data["p"]),
                "qty": float(data["q"]),
                "trade_id": data["t"],
                "ts": data["T"],
            }

            latest_price['binance']['price'] = trade_event['price']

            producer.produce("raw.trades", json.dumps(trade_event).encode("utf-8"))
            producer.poll(0)
            produced_count.inc()
            print(f"Produced trade: {trade_event}")


async def produce_from_hyperliquid():
    async with websockets.connect(EXCHANGES["hyperliquid"]["url"]) as ws:
        for coin in EXCHANGES["hyperliquid"]["assets"]:
            await ws.send(json.dumps({
                "method": "subscribe",
                "subscription": {"type": "trades", "coin": coin}
            }))

        async for msg in ws:
            data = json.loads(msg)  
            if data.get("channel") != "trades":
                continue
            
            trades = data.get("data", [])

            for trade in trades:
                trade_event = {
                    "exchange": "hyperliquid",
                    "symbol": trade["coin"],
                    "side": trade["side"], 
                    "price": float(trade["px"]),
                    "qty": float(trade["sz"]),
                    "trade_id": trade["tid"],
                    "ts": trade["time"],
                    "hash": trade["hash"],
                    "users": trade["users"],
                }

                latest_price['hyperliquid']['price'] = trade_event['price']


                producer.produce("raw.trades", json.dumps(trade_event).encode("utf-8"))
                producer.poll(0)
                produced_count.inc()
                print(f"Produced trade: {trade_event}")


async def main():
    task1 = asyncio.create_task(produce_from_binance())
    task2 = asyncio.create_task(produce_from_hyperliquid())
    # task3 = asyncio.create_task(spread_calculator())


    print("Both tasks started!")
    await asyncio.sleep(100)

    print("Cancelling tasks...")
    task1.cancel()
    task2.cancel()

    await asyncio.gather(task1, task2, return_exceptions=True)
    print("All done.")

asyncio.run(main())

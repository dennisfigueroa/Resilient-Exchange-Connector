    from confluent_kafka import Consumer
    import json

    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'demo-consumer',
        'auto.offset.reset': 'earliest'
    }

    c = Consumer(conf)
    c.subscribe(['raw.trades'])

    latest_price = {"binance": {"price": 188.4, "ts": 1699999999}, "hyperliquid": {"price": 188.6, "ts": 1699999998}}

    async def spread_calculator():
        await asyncio.sleep(1)
        spread = latest_price["binance"]["price"] - latest_price["hyperliquid"]["price"]
        print(f"Spread: {spread}")

    try:
        while True:
            msg = c.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue

            # trade = json.loads(msg.value().decode("utf-8"))
            
            # if trade['exchange'] == 'binance':
            #     latest_price['binance']['price'] = trade['price']

            # elif trade['exchange'] == 'hyperliquid':
            #     latest_price['hyperliquid']['price'] = trade['price']

            # await spread_calculator()

    except KeyboardInterrupt:
        pass
    finally:
        c.close()

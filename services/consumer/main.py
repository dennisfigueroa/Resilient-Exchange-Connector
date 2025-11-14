from confluent_kafka import Consumer
import json
import time

TOPIC = "raw.trades"
SPREAD_EXCHANGES = ("binance", "hyperliquid")
STALE_SECONDS = 5

def make_consumer():
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'demo-consumer',
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(conf)
    consumer.subscribe([TOPIC])
    return consumer


def update_price(state, trade):
    state[trade["exchange"]] = {"price": trade["price"], "ts": trade["ts"]}
    
def latest_spread(state):
    lhs, rhs = SPREAD_EXCHANGES
    first, second = state[lhs], state[rhs]
    if not first or not second:
        return None
    if any(time.time() - leg["ts"] > STALE_SECONDS for leg in (first, second)):
        return None
    return first["price"] - second["price"]

def main():
    consumer = make_consumer()
    latest = {name: None for name in SPREAD_EXCHANGES}

    try:
        while True:
            msg = consumer.poll(1.0)
            if not msg:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            trade = json.loads(msg.value())
            print(f"Received trade: {trade}")

            update_price(latest, trade)

            spread = latest_spread(latest)
            if spread is not None:
                print(f"Spread ({SPREAD_EXCHANGES[0]} - {SPREAD_EXCHANGES[1]}): {spread:.2f}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    main()
"""
Assignment: Implement a background Kafka consumer loop for spreads.
Goal: Learn how to structure a long-running thread safely.
"""

import threading
import json
from typing import Optional

# 🔹 Import your Kafka client (use confluent_kafka.Consumer)
# from confluent_kafka import Consumer

from confluent_kafka import Consumer

# 🔹 Import your state store (this is the file with update_spread(), etc.)
# from . import state, config
from . import state, config 

# ------------------------------------------------------------
# ✅ 1. Global thread + stop event (provided for you)
# ------------------------------------------------------------

_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()



def _consumer_loop():
    """
    Continuously poll Kafka for new messages and update the in-memory state.
    Hints:
      - Use a 'while not _stop_event.is_set()' loop.
      - Use consumer.poll(timeout=1.0)
      - Parse JSON, handle errors cleanly
      - Call state.update_spread() for valid messages
    """

    consumer = Consumer(config.consumer_settings())
    consumer.subscribe([config.SPREAD_TOPIC])

    try:
        while not _stop_event.is_set():

            msg = consumer.poll(1.0)
            if not msg:
                continue
            
            if msg.error():
                print(f"Consumer error: {msg}")
            # Key: None
            # Raw msg: None
            # Raw msg: <cimpl.Message object at 0x104737140>
            # Value: b'{"symbol": "SOLUSDT", "spread": 0.030000000000001137, "exchanges": ["binance", "hyperliquid"], "ts": 1763347091450}'

            try:
                payload = json.loads(msg.value())
                state.update_spread(payload)

            except Exception as exc:
                print(f"Failed to handle message: {exc}")
                continue

    finally:
        print("[spread-consumer] Closing consumer...")
        consumer.close()

def start_consumer():
    """Start background thread for spread consumer."""
    global _thread
    if _thread and _thread.is_alive():
        print("[spread-consumer] Already running.")
        return

    _stop_event.clear()
    _thread = threading.Thread(
        target=_consumer_loop,
        name="spread-consumer",
        daemon=True,
    )
    _thread.start()
    print("[spread-consumer] Started background consumer thread.")


def stop_consumer():
    """Signal thread to stop and wait for it to close."""
    _stop_event.set()
    if _thread and _thread.is_alive():
        print("[spread-consumer] Stopping...")
        _thread.join(timeout=5)
        print("[spread-consumer] Stopped.")

if __name__ == "__main__":
    print("[spread-consumer] Running in standalone mode...")
    start_consumer()

    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_consumer()

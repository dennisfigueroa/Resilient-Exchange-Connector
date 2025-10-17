from confluent_kafka import Consumer
import json

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'demo-consumer',
    'auto.offset.reset': 'earliest'
}

c = Consumer(conf)
c.subscribe(['raw.trades'])

while True:
    msg = c.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue
    trade = json.loads(msg.value().decode("utf-8"))
    print(f"Consumed trade: {trade}")

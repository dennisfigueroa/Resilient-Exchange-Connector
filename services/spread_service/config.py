import os

SPREAD_TOPIC = "analytics.spreads"


def consumer_settings():
    return {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP", "localhost:9092"),
        "group.id": os.getenv("SPREAD_GROUP_ID", "spread-service"),
        "auto.offset.reset": "earliest",
    }

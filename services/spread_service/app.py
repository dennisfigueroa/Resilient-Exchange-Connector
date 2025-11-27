from fastapi import FastAPI
import asyncio 

from .consumer import start_consumer, stop_consumer
from .state import get_all

app = FastAPI(title="Spread Service")

@app.on_event("startup")
async def startup_event():
    # Kick off the background consumer loop when the API starts.
    start_consumer()


@app.on_event("shutdown")
async def shutdown_event():
    # Ensure the consumer loop is stopped cleanly on shutdown.
    stop_consumer()


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api/spreads")
def all_spreads():
    return get_all()
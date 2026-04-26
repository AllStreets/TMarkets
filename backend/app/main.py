from __future__ import annotations

import asyncio
import json

import redis.asyncio as aioredis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import market, signals, predictions, news
from app.websocket import manager

app = FastAPI(title="TMarkets API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router)
app.include_router(signals.router)
app.include_router(predictions.router)
app.include_router(news.router)


@app.on_event("startup")
async def start_redis_listener():
    try:
        asyncio.create_task(_redis_listener())
    except Exception:
        pass


async def _redis_listener():
    try:
        r = aioredis.from_url(settings.redis_url)
        pubsub = r.pubsub()
        await pubsub.subscribe("tmarkets:alerts")
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    payload = json.loads(message["data"])
                    await manager.broadcast(payload)
                except Exception:
                    pass
    except Exception:
        pass  # Redis unavailable at startup (e.g., during tests)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)

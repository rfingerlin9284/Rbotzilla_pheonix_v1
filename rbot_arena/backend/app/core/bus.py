import asyncio
import orjson
import datetime
from collections import deque
from typing import AsyncIterator

class InMemBus:
    def __init__(self):
        self._subs = set()
        self._buf = deque(maxlen=10_000)

    async def publish(self, line: bytes):
        self._buf.append(line)
        dead = set()
        for q in list(self._subs):
            try:
                q.put_nowait(line)
            except Exception:
                dead.add(q)
        self._subs -= dead

    async def subscribe(self) -> AsyncIterator[bytes]:
        q: asyncio.Queue[bytes] = asyncio.Queue(maxsize=1_000)
        self._subs.add(q)
        try:
            # Send last 200 events to new subscribers
            for line in list(self._buf)[-200:]:
                await q.put(line)
            while True:
                yield await q.get()
        finally:
            self._subs.discard(q)

_bus = InMemBus()

async def bus_publish(ev: dict):
    """Publish event to all subscribers"""
    ev.setdefault("ts", datetime.datetime.utcnow().isoformat() + "Z")
    await _bus.publish(orjson.dumps(ev))

async def bus_subscriber() -> AsyncIterator[bytes]:
    """Subscribe to event stream"""
    async for line in _bus.subscribe():
        yield line

#!/usr/bin/env python3
"""
RBOT Arena Gateway - Main runner
"""
import os
import asyncio
import uvicorn
from dotenv import load_dotenv
from app.main import app
from app.agents.mock_emit import run_mock

load_dotenv()

async def background():
    """Start background agents"""
    await asyncio.sleep(0.5)
    
    # Mock emitters for testing (disable once real data flows)
    if os.getenv("ENABLE_MOCK", "true").lower() == "true":
        asyncio.create_task(run_mock("BTC-USD"))
        asyncio.create_task(run_mock("ETH-USD"))
        asyncio.create_task(run_mock("EUR_USD"))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(background())
    
    host = os.getenv("ARENA_HOST", "127.0.0.1")
    port = int(os.getenv("ARENA_PORT", "8787"))
    
    print(f"🤖 RBOT Arena Gateway starting on {host}:{port}")
    print(f"📊 SSE Events: http://{host}:{port}/events")
    print(f"🔌 WebSocket: ws://{host}:{port}/ws")
    print(f"🔐 Auth: POST /auth/login")
    print(f"📋 Health: GET /health")
    
    uvicorn.run(app, host=host, port=port)

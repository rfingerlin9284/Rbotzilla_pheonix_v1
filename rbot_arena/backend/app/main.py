import os
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.bus import bus_publish, bus_subscriber
from app.routers import auth_router, orders, llm_router, openalgo
from app.routers import brokers_oanda, brokers_coinbase, brokers_coinbase_advanced, brokers_oanda_orders

load_dotenv()

app = FastAPI(title="RBOT Arena Gateway", version="1.0.0")

# CORS for browser clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router)
app.include_router(orders.router)
app.include_router(llm_router.router)
app.include_router(openalgo.router)
app.include_router(brokers_oanda.router)
app.include_router(brokers_coinbase.router)
app.include_router(brokers_coinbase_advanced.router)
app.include_router(brokers_oanda_orders.router)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "ok": True,
        "paper": os.getenv("PAPER_MODE", "true"),
        "exec": os.getenv("EXECUTION_ENABLED", "false"),
        "oanda_env": os.getenv("OANDA_ENV", "practice")
    }

@app.get("/events")
async def sse():
    """Server-Sent Events stream for all events"""
    async def gen():
        async for line in bus_subscriber():
            yield b"data: " + line + b"\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")

@app.websocket("/ws")
async def ws(websocket: WebSocket):
    """WebSocket stream for all events"""
    await websocket.accept()
    try:
        async for line in bus_subscriber():
            await websocket.send_bytes(line)
    except WebSocketDisconnect:
        return

@app.on_event("startup")
async def startup():
    """Emit startup event"""
    await bus_publish({
        "source": "arena",
        "type": "heartbeat",
        "payload": {
            "status": "started",
            "mode": os.getenv("PAPER_MODE", "true")
        }
    })

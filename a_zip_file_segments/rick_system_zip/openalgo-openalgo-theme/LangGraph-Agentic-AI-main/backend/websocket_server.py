# backend/websocket_server.py

import asyncio
import json
from datetime import datetime
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware


# your routes and websocket code here...
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

import redis

from config import settings
from db.models import Base, WebSocketEvent, ClientConnection, SystemLog

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("websocket_server")

# Settings from config
DATABASE_URL = settings.database_url
REDIS_URL = settings.redis_url

# Database setup
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.redis = redis.from_url(REDIS_URL)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(
            "chartanalyst_out",
            "riskmanager_out",
            "marketsentinel_out",
            "macroforecaster_out",
            "tacticbot_out",
            "platformpilot_out",
            "agent_status"
        )

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

        # Record connection in DB
        with Session(engine) as session:
            connection = ClientConnection(
                connection_id=client_id,
                ip_address=websocket.client.host,
                user_agent=websocket.headers.get("user-agent"),
                subscribed_channels=[]
            )
            session.add(connection)
            session.commit()

        logger.info(f"Client connected: {client_id}")

    async def disconnect(self, client_id: str):
        websocket = self.active_connections.pop(client_id, None)
        if websocket:
            try:
                await websocket.close()
            except Exception:
                pass

            # Update disconnection in DB
            with Session(engine) as session:
                connection = session.query(ClientConnection).filter_by(connection_id=client_id).first()
                if connection:
                    connection.last_activity = datetime.utcnow()
                    session.commit()

        logger.info(f"Client disconnected: {client_id}")

    async def broadcast(self, event_type: str, payload: dict):
        """Broadcast to all connected clients and store in DB"""
        event_data = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload
        }
        message = json.dumps(event_data)

        # Store in database first
        with Session(engine) as session:
            ws_event = WebSocketEvent(
                event_type=event_type,
                payload=payload,
                delivered=False,
                delivery_count=0
            )

            # Add relationships if available in payload
            if "signal_id" in payload:
                ws_event.signal_id = payload["signal_id"]
            if "agent_id" in payload:
                ws_event.agent_id = payload["agent_id"]

            session.add(ws_event)
            session.commit()

            # Send to all active connections
            for client_id, websocket in list(self.active_connections.items()):
                try:
                    await websocket.send_text(message)
                    ws_event.delivered = True
                    ws_event.delivery_count += 1

                    # Update client activity
                    connection = session.query(ClientConnection).filter_by(connection_id=client_id).first()
                    if connection:
                        connection.last_activity = datetime.utcnow()
                        if event_type not in connection.subscribed_channels:
                            connection.subscribed_channels = connection.subscribed_channels or []
                            connection.subscribed_channels.append(event_type)

                    session.commit()
                except Exception as e:
                    logger.error(f"Error sending to {client_id}: {e}")
                    await self.disconnect(client_id)

    async def redis_listener(self):
        """Listen to Redis pub/sub and broadcast messages"""
        loop = asyncio.get_running_loop()
        def handle_redis_messages():
            for message in self.pubsub.listen():
                if message["type"] == "message":
                    try:
                        channel = message["channel"].decode()
                        data = json.loads(message["data"])
                        # Schedule broadcast on event loop
                        asyncio.run_coroutine_threadsafe(
                            self.broadcast(channel, data),
                            loop
                        )
                    except Exception as e:
                        logger.error(f"Redis listener error: {e}")
        # Run the blocking redis listener in a thread
        asyncio.get_event_loop().run_in_executor(None, handle_redis_messages)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Keep connection alive (can also process client messages here)
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(client_id)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(manager.redis_listener())

# backend/orchestrator/api.py

import asyncio
import json
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import os
from pydantic import BaseModel

from orchestrator.mcp_graph import run_mcp_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RunMcpRequest(BaseModel):
    symbol: str
    timeframe: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting orchestrator service...")
    try:
        # Initialize event bus, DB, or other connections here
        logger.info("✅ Orchestrator startup complete")
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise
    yield
    logger.info("🛑 Shutting down orchestrator...")
    logger.info("✅ Orchestrator shutdown complete")

app = FastAPI(
    title="Orchestrator API",
    description="Agentic System Orchestrator with WebSocket support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Monitoring"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/routes", tags=["Debug"])
async def list_routes():
    return [
        {
            "path": route.path,
            "name": route.name,
            "methods": route.methods
        }
        for route in app.routes
    ]

@app.post("/run_mcp", tags=["MCP"])
async def run_mcp(request: RunMcpRequest):
    logger.info(f"Received MCP run request for symbol: {request.symbol}, timeframe: {request.timeframe}")
    try:
        result = await run_mcp_pipeline(symbol=request.symbol, timeframe=request.timeframe)
        logger.info(f"MCP pipeline completed with result: {result}")
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Error running MCP pipeline: {e}")
        return {"status": "error", "message": str(e)}

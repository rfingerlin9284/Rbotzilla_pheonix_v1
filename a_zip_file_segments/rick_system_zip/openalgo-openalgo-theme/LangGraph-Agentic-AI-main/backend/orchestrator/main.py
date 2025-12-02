# backend/orchestrator/main.py - Entry point for your orchestrator

import asyncio
import logging
import os

import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import your API module (no "s" in orchestrator)
from orchestrator.api import app

if __name__ == "__main__":
    # Configuration from environment variables
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8007))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
    
    logger.info(f"Starting Orchestrator on {HOST}:{PORT}")
    
    # Run the FastAPI application
    uvicorn.run(
        "orchestrator.api:app",  # Use the app from api.py
        host=HOST,
        port=PORT,
        log_level=LOG_LEVEL,
        reload=False  # Set to True for development
    )
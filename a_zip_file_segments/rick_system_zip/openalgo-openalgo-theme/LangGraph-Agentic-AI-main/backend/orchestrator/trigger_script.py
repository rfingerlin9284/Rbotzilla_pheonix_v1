import asyncio
import logging
import os
from dotenv import load_dotenv
from backend.orchestrator.mcp_graph import run_mcp_pipeline

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def trigger_mcp_workflow():
    logger.info("Triggering MCP workflow...")
    symbol = os.getenv("TRIGGER_SYMBOL", "EURUSD")
    timeframe = os.getenv("TRIGGER_TIMEFRAME", "1h")
    
    try:
        final_state = await run_mcp_pipeline(symbol=symbol, timeframe=timeframe)
        logger.info("MCP workflow completed. Final state:")
        logger.info(final_state)
    except Exception as e:
        logger.error(f"An error occurred during MCP workflow: {e}")

if __name__ == "__main__":
    asyncio.run(trigger_mcp_workflow())
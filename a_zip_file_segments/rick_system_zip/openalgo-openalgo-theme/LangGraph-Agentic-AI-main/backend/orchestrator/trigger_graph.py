import asyncio
import os
from dotenv import load_dotenv
from backend.orchestrator.mcp_graph import run_mcp_pipeline

# Load environment variables from .env file
load_dotenv()

async def trigger_mcp_workflow():
    print("Triggering MCP workflow...")
    symbol = os.getenv("TRIGGER_SYMBOL", "EURUSD")
    timeframe = os.getenv("TRIGGER_TIMEFRAME", "1h")
    
    try:
        final_state = await run_mcp_pipeline(symbol=symbol, timeframe=timeframe)
        print("MCP workflow completed. Final state:")
        print(final_state)
    except Exception as e:
        print(f"An error occurred during MCP workflow: {e}")

if __name__ == "__main__":
    asyncio.run(trigger_mcp_workflow())
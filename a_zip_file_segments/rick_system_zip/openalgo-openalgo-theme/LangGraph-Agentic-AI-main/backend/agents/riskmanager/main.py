import asyncio
import os
import logging
from agents.riskmanager.agent import RiskManagerAgent
from orchestrator.event_bus import event_bus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the RiskManager agent."""
    try:
        agent = RiskManagerAgent(
            name="RiskManager",
            subscribe_channels=["technical_signals", "marketsentinel_out", "macroforecaster_out"],
            publish_channel="riskmanager_out"
        )
        
        logger.info("Starting RiskManager agent...")
        
        await agent.start(event_bus)
                
    except Exception as e:
        logger.error(f"Error starting RiskManager agent: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
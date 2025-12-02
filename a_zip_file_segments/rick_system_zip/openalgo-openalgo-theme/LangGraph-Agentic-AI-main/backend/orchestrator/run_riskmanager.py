import asyncio
import os
import logging
from backend.agents.riskmanager.agent import RiskManagerAgent
from backend.orchestrator.event_bus import event_bus

logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(level=logging.INFO)
    try:
        agent = RiskManagerAgent(
            name="RiskManager",
            subscribe_channels=["technical_signals", "marketsentinel_out", "macroforecaster_out"],
            publish_channel="riskmanager_out"
        )
        logger.info("Starting RiskManager agent from orchestrator/run_riskmanager.py...")
        await agent.start(event_bus)
    except Exception as e:
        logger.error(f"Error starting RiskManager agent: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
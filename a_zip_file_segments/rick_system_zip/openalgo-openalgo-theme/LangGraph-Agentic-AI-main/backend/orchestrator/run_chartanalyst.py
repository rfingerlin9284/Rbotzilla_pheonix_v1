import asyncio
import os
import logging
from backend.agents.chartanalyst.agent import ChartAnalystAgent
from backend.orchestrator.event_bus import event_bus

logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(level=logging.INFO)
    try:
        agent = ChartAnalystAgent(
            name="ChartAnalystAgent",
            subscribe_channels=['market_data'], # Subscribing to market_data as per agent's design
            publish_channel="technical_signals", # Publishing to technical_signals as per agent's design
        )
        logger.info("Starting ChartAnalyst agent from orchestrator/run_chartanalyst.py...")
        await agent.start(event_bus)
    except Exception as e:
        logger.error(f"Error starting ChartAnalyst agent: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
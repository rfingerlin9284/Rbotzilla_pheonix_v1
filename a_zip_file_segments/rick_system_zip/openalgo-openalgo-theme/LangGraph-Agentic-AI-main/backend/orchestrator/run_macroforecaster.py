import asyncio
import os
import logging
from backend.agents.macroforecaster.main import MacroforecasterAgent
from backend.orchestrator.event_bus import event_bus

logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(level=logging.INFO)
    try:
        agent = MacroforecasterAgent(
            name="MacroForecaster",
            subscribe_channels=["market_sentiment_analysis"],
            publish_channel="macroforecaster_out"
        )
        logger.info("Starting MacroForecaster agent from orchestrator/run_macroforecaster.py...")
        await agent.start(event_bus)
    except Exception as e:
        logger.error(f"Error starting MacroForecaster agent: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
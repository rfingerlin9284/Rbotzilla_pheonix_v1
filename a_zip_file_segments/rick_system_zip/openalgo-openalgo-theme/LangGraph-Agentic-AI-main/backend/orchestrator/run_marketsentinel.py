import asyncio
import os
import logging
from backend.agents.marketsentinel.main import MarketsentinelAgent
from backend.orchestrator.event_bus import event_bus

logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(level=logging.INFO)
    try:
        agent = MarketsentinelAgent(
            name="MarketSentinel",
            subscribe_channels=["market_news_events"],
            publish_channel="marketsentinel_out"
        )
        logger.info("Starting MarketSentinel agent from orchestrator/run_marketsentinel.py...")
        await agent.start(event_bus)
    except Exception as e:
        logger.error(f"Error starting MarketSentinel agent: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
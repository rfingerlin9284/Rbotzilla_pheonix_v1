import asyncio
import os
import logging
from agents.marketdatafetcher.agent import MarketDataFetcherAgent
from orchestrator.event_bus import event_bus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the MarketDataFetcher agent."""
    try:
        agent = MarketDataFetcherAgent(
            name="MarketDataFetcher",
            subscribe_channels=["market_data_requests"],
            publish_channel="market_data"
        )
        
        logger.info("Starting MarketDataFetcher agent...")
        
        await agent.start(event_bus)
                
    except Exception as e:
        logger.error(f"Error starting MarketDataFetcher agent: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
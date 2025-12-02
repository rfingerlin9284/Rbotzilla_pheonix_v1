import asyncio
import logging
import os
import json
from typing import Dict, Any

from agents.base_agent import BaseAgent
from ai_client import AIModelClient # Not directly used here, but good to have for consistency

logger = logging.getLogger(__name__)

class MarketDataFetcherAgent(BaseAgent):
    def __init__(self, name="MarketDataFetcher", subscribe_channels=None, publish_channel="market_data"):
        super().__init__(
            name=name,
            subscribe_channels=subscribe_channels if subscribe_channels is not None else ["market_data_requests"],
            publish_channel=publish_channel
        )
        logger.info(f"{self.name} initialized.")

    async def process_message(self, channel: str, message: Dict[str, Any]):
        logger.info(f"MarketDataFetcherAgent received message on {channel}: {message}")
        
        if channel == "market_data_requests":
            symbol = message.get("symbol")
            timeframe = message.get("timeframe")
            
            if not symbol or not timeframe:
                logger.warning("Received market_data_request without symbol or timeframe.")
                return

            logger.info(f"Fetching market data for {symbol} ({timeframe})...")
            
            # --- Placeholder for actual market data fetching logic ---
            await asyncio.sleep(2) # Simulate network delay
            
            dummy_data = {
                "symbol": symbol,
                "timeframe": timeframe,
                "price": round(100 + (hash(symbol) % 100) + (hash(timeframe) % 50) + (asyncio.get_event_loop().time() % 10), 2),
                "volume": 100000 + (hash(symbol) % 50000),
                "timestamp": datetime.now().isoformat(),
                "source": self.name
            }
            # --- End Placeholder ---

            logger.info(f"Fetched dummy data: {dummy_data}")
            await self.publish(dummy_data)
            logger.info(f"Published market data for {symbol} to {self.publish_channel}")

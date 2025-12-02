# ChartAnalyst.py
import asyncio
from typing import List, Dict, Any
import json
import logging

# You'll need to implement or import these
from orchestrator.event_bus import event_bus
from agents.base_agent import BaseAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIClient:
    """Mock API client - replace with your actual implementation"""
    async def analyze_chart(self, message: Dict[str, Any]) -> str:
        # This is a placeholder - implement your actual AI analysis here
        logger.info(f"Analyzing chart data: {message}")
        await asyncio.sleep(0.1)  # Simulate API call
        return f"BULLISH signal detected for {message.get('symbol', 'UNKNOWN')} at price {message.get('price', 0)}"

class ChartAnalystAgent(BaseAgent):
    def __init__(self, api_client=None, name="ChartAnalyst"):
        super().__init__(
            name=name,
            subscribe_channels=["market_data"],
            publish_channel="technical_signals"
        )
        self.api_client = api_client or APIClient()
        logger.info(f"Initialized {name} agent")

    async def process_message(self, channel: str, message: Dict[str, Any]):
        """Process incoming market data messages"""
        try:
            logger.info(f"Processing message from channel '{channel}': {message}")
            
            # Validate message format
            if not isinstance(message, dict):
                logger.warning(f"Invalid message format: {type(message)}")
                return
            
            # Call AI model to analyze chart data
            signals_text = await self.api_client.analyze_chart(message)
            logger.info(f"AI analysis result: {signals_text}")
            
            # Parse signals_text into structured signals
            signals = self.parse_signals(signals_text, message)
            
            # Publish signals on event bus
            for signal in signals:
                await self.publish(signal)
                logger.info(f"Published signal: {signal}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def parse_signals(self, text: str, original_message: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Parse AI response text into structured signals"""
        try:
            # Enhanced parsing logic
            signals = []
            
            # Extract basic information
            symbol = original_message.get('symbol', 'UNKNOWN') if original_message else 'UNKNOWN'
            price = original_message.get('price', 0) if original_message else 0
            timestamp = original_message.get('timestamp') if original_message else None
            
            # Simple keyword-based signal detection
            text_upper = text.upper()
            
            if 'BULLISH' in text_upper or 'BUY' in text_upper:
                signals.append({
                    "signal_type": "BUY",
                    "symbol": symbol,
                    "price": price,
                    "confidence": 0.8,
                    "timestamp": timestamp,
                    "analysis": text,
                    "source": "ChartAnalyst"
                })
            elif 'BEARISH' in text_upper or 'SELL' in text_upper:
                signals.append({
                    "signal_type": "SELL",
                    "symbol": symbol,
                    "price": price,
                    "confidence": 0.8,
                    "timestamp": timestamp,
                    "analysis": text,
                    "source": "ChartAnalyst"
                })
            else:
                # Default signal for any other analysis
                signals.append({
                    "signal_type": "NEUTRAL",
                    "symbol": symbol,
                    "price": price,
                    "confidence": 0.5,
                    "timestamp": timestamp,
                    "analysis": text,
                    "source": "ChartAnalyst"
                })
            
            return signals
            
        except Exception as e:
            logger.error(f"Error parsing signals: {e}")
            # Fallback to original simple format
            return [{"signal_text": text}]


# Run_chartanalysis.py
import asyncio
import redis.asyncio as redis
import os
import json
from datetime import datetime

# Assuming the above ChartAnalystAgent is in agents.chartanalyst.main
# from agents.chartanalyst.main import ChartAnalystAgent

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

async def create_mock_market_data():
    """Create some mock market data for testing"""
    return {
        "symbol": "BTCUSD",
        "price": 45000.50,
        "volume": 1000000,
        "timestamp": datetime.now().isoformat(),
        "high": 45500.00,
        "low": 44000.00,
        "open": 44500.00
    }

async def main():
    try:
        # Initialize Redis client
        redis_client = redis.from_url(REDIS_URL)
        
        # Test Redis connection
        await redis_client.ping()
        logger.info("Successfully connected to Redis")
        
        # Create the agent with proper parameters
        agent = ChartAnalystAgent(
            name="ChartAnalystAgent"
        )
        
        # Start the agent
        logger.info("Starting ChartAnalyst agent...")
        
        # For testing purposes, simulate some market data
        market_data = await create_mock_market_data()
        logger.info(f"Created mock market data: {market_data}")
        
        # Process the mock data
        await agent.process_message("market_data", market_data)
        
        # If you want to run continuously, uncomment the following:
        # await agent.start()
        
        logger.info("ChartAnalyst processing completed")
        
    except redis.ConnectionError:
        logger.error("Failed to connect to Redis. Make sure Redis is running.")
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        if 'redis_client' in locals():
            await redis_client.close()

if __name__ == "__main__":
    asyncio.run(main())

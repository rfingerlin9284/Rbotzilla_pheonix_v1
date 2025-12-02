import asyncio
import json
import logging
import os
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from ai_client import AIModelClient
from orchestrator.event_bus import event_bus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketsentinelAgent(BaseAgent):
    def __init__(self, api_client: AIModelClient = None, name="MarketSentinel", subscribe_channels=None, publish_channel="marketsentinel_out"):
        super().__init__(
            name=name,
            subscribe_channels=subscribe_channels if subscribe_channels is not None else ["market_news_events"],
            publish_channel=publish_channel
        )
        self.ai_client = api_client or AIModelClient(
            api_key=os.getenv("GEMINI_API_KEY"),
            model_name=os.getenv("MARKETSENTINEL_MODEL", "gemini-1.5-flash")
        )
        logger.info(f"Initialized {name} agent with AIModelClient")

    async def process_message(self, channel: str, message: Dict[str, Any]):
        """Process incoming market news/events and analyze with AI"""
        try:
            logger.info(f"Processing message from channel '{channel}': {message}")
            
            if not isinstance(message, dict):
                logger.warning(f"Invalid message format: {type(message)}")
                return
            
            prompt = f"""Analyze the following market news/event and provide a sentiment analysis and potential market impact.
            The output should be a JSON object with the following keys:
            - "sentiment": "positive", "negative", or "neutral"
            - "impact_level": "low", "medium", or "high"
            - "impact_reasoning": a brief explanation for the potential impact
            - "relevant_symbols": (optional) a list of symbols that might be affected
            
            Market Event: {json.dumps(message)}
            """
            
            ai_response_text = await self.ai_client.chat_completion(prompt)
            logger.info(f"AI market sentiment raw response: {ai_response_text}")
            
            market_sentiment = self.parse_market_sentiment(ai_response_text, message)
            
            await self.publish(market_sentiment)
            logger.info(f"Published market sentiment: {market_sentiment}")
                
        except Exception as e:
            logger.error(f"Error processing message in MarketSentinelAgent: {e}")

    def parse_market_sentiment(self, ai_response_text: str, original_message: Dict[str, Any] = None) -> Dict[str, Any]:
        """Parse AI response (expected to be JSON) into structured market sentiment"""
        try:
            ai_data = json.loads(ai_response_text)
            
            sentiment = ai_data.get("sentiment", "neutral").lower()
            impact_level = ai_data.get("impact_level", "low").lower()
            impact_reasoning = ai_data.get("impact_reasoning", "No specific impact reasoning provided.")
            relevant_symbols = ai_data.get("relevant_symbols", [])

            market_sentiment = {
                "type": "market_sentiment_analysis",
                "original_event": original_message,
                "sentiment": sentiment,
                "impact_level": impact_level,
                "impact_reasoning": impact_reasoning,
                "relevant_symbols": relevant_symbols,
                "timestamp": original_message.get("timestamp"),
                "source": self.name
            }
                
            return market_sentiment
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error for AI market sentiment: {e} - Raw response: {ai_response_text}")
            return {
                "type": "market_sentiment_analysis",
                "original_event": original_message,
                "sentiment": "error",
                "impact_level": "high",
                "impact_reasoning": f"Failed to parse AI response: {ai_response_text}",
                "relevant_symbols": [],
                "timestamp": original_message.get("timestamp"),
                "source": self.name
            }
        except Exception as e:
            logger.error(f"Error in parse_market_sentiment: {e}")
            return {
                "type": "market_sentiment_analysis",
                "original_event": original_message,
                "sentiment": "error",
                "impact_level": "high",
                "impact_reasoning": f"Unexpected error in parsing: {e}",
                "relevant_symbols": [],
                "timestamp": original_message.get("timestamp"),
                "source": self.name
            }

async def main():
    agent = MarketsentinelAgent()
    await agent.start(event_bus)

if __name__ == "__main__":
    asyncio.run(main())

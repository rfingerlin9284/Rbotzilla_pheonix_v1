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

class MacroforecasterAgent(BaseAgent):
    def __init__(self, api_client: AIModelClient = None, name="MacroForecaster", subscribe_channels=None, publish_channel="macroforecaster_out"):
        super().__init__(
            name=name,
            subscribe_channels=subscribe_channels if subscribe_channels is not None else ["market_sentiment_analysis"],
            publish_channel=publish_channel
        )
        self.ai_client = api_client or AIModelClient(
            api_key=os.getenv("GEMINI_API_KEY"),
            model_name=os.getenv("MACROFORECASTER_MODEL", "gemini-1.5-flash")
        )
        logger.info(f"Initialized {name} agent with AIModelClient")

    async def process_message(self, channel: str, message: Dict[str, Any]):
        """Process incoming market sentiment and provide macro forecast with AI"""
        try:
            logger.info(f"Processing message from channel '{channel}': {message}")
            
            if not isinstance(message, dict):
                logger.warning(f"Invalid message format: {type(message)}")
                return
            
            prompt = f"""Analyze the following market sentiment and provide a macroeconomic forecast and trading bias.
            The output should be a JSON object with the following keys:
            - "macro_outlook": "positive", "negative", or "neutral"
            - "trading_bias": "bullish", "bearish", or "neutral"
            - "forecast_reasoning": a brief explanation for the forecast and bias
            - "key_factors": (optional) a list of key macroeconomic factors considered
            
            Market Sentiment: {json.dumps(message)}
            """
            
            ai_response_text = await self.ai_client.chat_completion(prompt)
            logger.info(f"AI macro forecast raw response: {ai_response_text}")
            
            macro_forecast = self.parse_macro_forecast(ai_response_text, message)
            
            await self.publish(macro_forecast)
            logger.info(f"Published macro forecast: {macro_forecast}")
                
        except Exception as e:
            logger.error(f"Error processing message in MacroforecasterAgent: {e}")

    def parse_macro_forecast(self, ai_response_text: str, original_message: Dict[str, Any] = None) -> Dict[str, Any]:
        """Parse AI response (expected to be JSON) into structured macro forecast"""
        try:
            ai_data = json.loads(ai_response_text)
            
            macro_outlook = ai_data.get("macro_outlook", "neutral").lower()
            trading_bias = ai_data.get("trading_bias", "neutral").lower()
            forecast_reasoning = ai_data.get("forecast_reasoning", "No specific forecast reasoning provided.")
            key_factors = ai_data.get("key_factors", [])

            macro_forecast = {
                "type": "macro_forecast",
                "original_sentiment": original_message,
                "macro_outlook": macro_outlook,
                "trading_bias": trading_bias,
                "forecast_reasoning": forecast_reasoning,
                "key_factors": key_factors,
                "timestamp": original_message.get("timestamp"),
                "source": self.name
            }
                
            return macro_forecast
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error for AI macro forecast: {e} - Raw response: {ai_response_text}")
            return {
                "type": "macro_forecast",
                "original_sentiment": original_message,
                "macro_outlook": "error",
                "trading_bias": "neutral",
                "forecast_reasoning": f"Failed to parse AI response: {ai_response_text}",
                "key_factors": [],
                "timestamp": original_message.get("timestamp"),
                "source": self.name
            }
        except Exception as e:
            logger.error(f"Error in parse_macro_forecast: {e}")
            return {
                "type": "macro_forecast",
                "original_sentiment": original_message,
                "macro_outlook": "error",
                "trading_bias": "neutral",
                "forecast_reasoning": f"Unexpected error in parsing: {e}",
                "key_factors": [],
                "timestamp": original_message.get("timestamp"),
                "source": self.name
            }

async def main():
    agent = MacroforecasterAgent()
    await agent.start(event_bus)

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import logging
import os
import json
from typing import List, Dict, Any
from datetime import datetime

from agents.base_agent import BaseAgent
from ai_client import AIModelClient

logger = logging.getLogger(__name__)

class ChartAnalystAgent(BaseAgent):
    def __init__(self, api_client: AIModelClient = None, name="ChartAnalyst", subscribe_channels=None, publish_channel="technical_signals"):
        super().__init__(
            name=name,
            subscribe_channels=subscribe_channels if subscribe_channels is not None else ["market_data"],
            publish_channel=publish_channel
        )
        self.ai_client = api_client or AIModelClient(
            api_key=os.getenv("GEMINI_API_KEY"),
            model_name=os.getenv("CHARTANALYST_MODEL", "gemini-1.5-flash")
        )
        logger.info(f"Initialized {name} agent with AIModelClient")

    async def process_message(self, channel: str, message: Dict[str, Any]):
        """Process incoming market data messages and provide technical signals with AI"""
        try:
            logger.info(f"{self.name} processing message from '{channel}': {message}")
            
            if not isinstance(message, dict):
                logger.warning(f"Invalid message format: {type(message)}")
                return
            
            prompt = f"""Analyze the following chart data and provide a technical signal.
            The output should be a JSON object with the following keys:
            - "signal_type": "BUY", "SELL", or "NEUTRAL"
            - "confidence": a float between 0.0 and 1.0
            - "reasoning": a brief explanation for the signal
            - "target_price": (optional) a suggested target price
            - "stop_loss": (optional) a suggested stop loss price
            
            Chart Data: {json.dumps(message)}
            """
            
            ai_response_text = await self.ai_client.chat_completion(prompt)
            logger.info(f"AI analysis raw response: {ai_response_text}")
            
            signals = self.parse_signals(ai_response_text, message)
            
            for signal in signals:
                await self.publish(signal)
                logger.info(f"Published signal: {signal}")
                
        except Exception as e:
            logger.error(f"Error processing message in ChartAnalystAgent: {e}")

    def parse_signals(self, ai_response_text: str, original_message: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Parse AI response (expected to be JSON) into structured signals"""
        try:
            ai_data = json.loads(ai_response_text)
            
            signal_type = ai_data.get("signal_type", "NEUTRAL").upper()
            confidence = float(ai_data.get("confidence", 0.5))
            reasoning = ai_data.get("reasoning", "No specific reasoning provided.")
            target_price = ai_data.get("target_price")
            stop_loss = ai_data.get("stop_loss")

            symbol = original_message.get('symbol', 'UNKNOWN') if original_message else 'UNKNOWN'
            price = original_message.get('price', 0) if original_message else 0
            timestamp = original_message.get('timestamp') if original_message else datetime.now().isoformat()
            
            signal = {
                "signal_type": signal_type,
                "symbol": symbol,
                "price": price,
                "confidence": confidence,
                "timestamp": timestamp,
                "analysis": reasoning,
                "source": self.name,
            }
            if target_price is not None:
                signal["target_price"] = target_price
            if stop_loss is not None:
                signal["stop_loss"] = stop_loss
                
            return [signal]
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error for AI response: {e} - Raw response: {ai_response_text}")
            return [{
                "signal_type": "ERROR",
                "symbol": original_message.get('symbol', 'UNKNOWN'),
                "price": original_message.get('price', 0),
                "confidence": 0.0,
                "timestamp": original_message.get('timestamp'),
                "analysis": f"Failed to parse AI response: {ai_response_text}",
                "source": self.name
            }]
        except Exception as e:
            logger.error(f"Error in parse_signals: {e}")
            return [{
                "signal_type": "ERROR",
                "symbol": original_message.get('symbol', 'UNKNOWN'),
                "price": original_message.get('price', 0),
                "confidence": 0.0,
                "timestamp": original_message.get('timestamp'),
                "analysis": f"Unexpected error in parsing: {e}",
                "source": self.name
            }]

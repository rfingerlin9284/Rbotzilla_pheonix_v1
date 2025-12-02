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

class PlatformpilotAgent(BaseAgent):
    def __init__(self, api_client: AIModelClient = None, name="PlatformPilot", subscribe_channels=None, publish_channel="platformpilot_out"):
        super().__init__(
            name=name,
            subscribe_channels=subscribe_channels if subscribe_channels is not None else ["tacticbot_out"],
            publish_channel=publish_channel
        )
        self.ai_client = api_client or AIModelClient(
            api_key=os.getenv("GEMINI_API_KEY"),
            model_name=os.getenv("PLATFORMPILOT_MODEL", "gemini-1.5-flash")
        )
        logger.info(f"Initialized {name} agent with AIModelClient")

    async def process_message(self, channel: str, message: Dict[str, Any]):
        """Process incoming trading decisions and simulate execution with AI"""
        try:
            logger.info(f"Processing message from channel '{channel}': {message}")
            
            if not isinstance(message, dict):
                logger.warning(f"Invalid message format: {type(message)}")
                return
            
            prompt = f"""Simulate the execution of the following trading decision and provide the outcome.
            The output should be a JSON object with the following keys:
            - "execution_status": "FILLED", "PARTIALLY_FILLED", or "REJECTED"
            - "fill_price": (optional) the price at which the order was filled
            - "fill_quantity": (optional) the quantity filled
            - "execution_reasoning": a brief explanation for the execution outcome
            - "trade_id": a unique identifier for the simulated trade
            
            Trading Decision: {json.dumps(message)}
            """
            
            ai_response_text = await self.ai_client.chat_completion(prompt)
            logger.info(f"AI execution simulation raw response: {ai_response_text}")
            
            execution_result = self.parse_execution_result(ai_response_text, message)
            
            await self.publish(execution_result)
            logger.info(f"Published execution result: {execution_result}")
                
        except Exception as e:
            logger.error(f"Error processing message in PlatformpilotAgent: {e}")

    def parse_execution_result(self, ai_response_text: str, original_message: Dict[str, Any] = None) -> Dict[str, Any]:
        """Parse AI response (expected to be JSON) into structured execution result"""
        try:
            ai_data = json.loads(ai_response_text)
            
            execution_status = ai_data.get("execution_status", "REJECTED").upper()
            fill_price = ai_data.get("fill_price")
            fill_quantity = ai_data.get("fill_quantity")
            execution_reasoning = ai_data.get("execution_reasoning", "No specific execution reasoning provided.")
            trade_id = ai_data.get("trade_id", f"trade_{os.urandom(4).hex()}")

            execution_result = {
                "type": "trade_execution_result",
                "original_decision": original_message,
                "execution_status": execution_status,
                "execution_reasoning": execution_reasoning,
                "trade_id": trade_id,
                "timestamp": original_message.get("timestamp"),
                "source": self.name
            }
            if fill_price is not None:
                execution_result["fill_price"] = fill_price
            if fill_quantity is not None:
                execution_result["fill_quantity"] = fill_quantity
                
            return execution_result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error for AI execution result: {e} - Raw response: {ai_response_text}")
            return {
                "type": "trade_execution_result",
                "original_decision": original_message,
                "execution_status": "REJECTED",
                "execution_reasoning": f"Failed to parse AI response: {ai_response_text}",
                "trade_id": f"trade_{os.urandom(4).hex()}",
                "timestamp": original_message.get("timestamp"),
                "source": self.name
            }
        except Exception as e:
            logger.error(f"Error in parse_execution_result: {e}")
            return {
                "type": "trade_execution_result",
                "original_decision": original_message,
                "execution_status": "REJECTED",
                "execution_reasoning": f"Unexpected error in parsing: {e}",
                "trade_id": f"trade_{os.urandom(4).hex()}",
                "timestamp": original_message.get("timestamp"),
                "source": self.name
            }

async def main():
    agent = PlatformpilotAgent()
    await agent.start(event_bus)

if __name__ == "__main__":
    asyncio.run(main())

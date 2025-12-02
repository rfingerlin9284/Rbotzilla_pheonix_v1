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

class TacticbotAgent(BaseAgent):
    def __init__(self, api_client: AIModelClient = None, name="TacticBot", subscribe_channels=None, publish_channel="tacticbot_out"):
        super().__init__(
            name=name,
            subscribe_channels=subscribe_channels if subscribe_channels is not None else ["riskmanager_out"],
            publish_channel=publish_channel
        )
        self.ai_client = api_client or AIModelClient(
            api_key=os.getenv("GEMINI_API_KEY"),
            model_name=os.getenv("TACTICBOT_MODEL", "gemini-1.5-flash")
        )
        logger.info(f"Initialized {name} agent with AIModelClient")

    async def process_message(self, channel: str, message: Dict[str, Any]):
        """Process incoming risk-evaluated signals and determine trading tactics with AI"""
        try:
            logger.info(f"Processing message from channel '{channel}': {message}")
            
            if not isinstance(message, dict):
                logger.warning(f"Invalid message format: {type(message)}")
                return
            
            prompt = f"""Given the following risk-evaluated trading signal, determine the optimal trading tactics.
            The output should be a JSON object with the following keys:
            - "action": "BUY", "SELL", or "HOLD"
            - "order_type": "MARKET", "LIMIT", or "STOP"
            - "entry_price": (optional) the suggested entry price if order_type is LIMIT or STOP
            - "exit_price": (optional) the suggested exit price (take profit)
            - "stop_loss_price": (optional) the suggested stop loss price
            - "quantity": (optional) the suggested trading quantity or percentage of capital
            - "tactic_reasoning": a brief explanation for the chosen tactics
            
            Risk-Evaluated Signal: {json.dumps(message)}
            """
            
            ai_response_text = await self.ai_client.chat_completion(prompt)
            logger.info(f"AI trading tactics raw response: {ai_response_text}")
            
            trading_decision = self.parse_trading_decision(ai_response_text, message)
            
            await self.publish(trading_decision)
            logger.info(f"Published trading decision: {trading_decision}")
                
        except Exception as e:
            logger.error(f"Error processing message in TacticbotAgent: {e}")

    def parse_trading_decision(self, ai_response_text: str, original_message: Dict[str, Any] = None) -> Dict[str, Any]:
        """Parse AI response (expected to be JSON) into structured trading decision"""
        try:
            ai_data = json.loads(ai_response_text)
            
            action = ai_data.get("action", "HOLD").upper()
            order_type = ai_data.get("order_type", "MARKET").upper()
            entry_price = ai_data.get("entry_price")
            exit_price = ai_data.get("exit_price")
            stop_loss_price = ai_data.get("stop_loss_price")
            quantity = ai_data.get("quantity")
            tactic_reasoning = ai_data.get("tactic_reasoning", "No specific tactic reasoning provided.")

            trading_decision = {
                "type": "trading_decision",
                "original_signal": original_message,
                "action": action,
                "order_type": order_type,
                "tactic_reasoning": tactic_reasoning,
                "timestamp": original_message.get("timestamp"),
                "source": self.name
            }
            if entry_price is not None:
                trading_decision["entry_price"] = entry_price
            if exit_price is not None:
                trading_decision["exit_price"] = exit_price
            if stop_loss_price is not None:
                trading_decision["stop_loss_price"] = stop_loss_price
            if quantity is not None:
                trading_decision["quantity"] = quantity
                
            return trading_decision
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error for AI trading decision: {e} - Raw response: {ai_response_text}")
            return {
                "type": "trading_decision",
                "original_signal": original_message,
                "action": "HOLD",
                "order_type": "MARKET",
                "tactic_reasoning": f"Failed to parse AI response: {ai_response_text}",
                "timestamp": original_message.get("timestamp"),
                "source": self.name
            }
        except Exception as e:
            logger.error(f"Error in parse_trading_decision: {e}")
            return {
                "type": "trading_decision",
                "original_signal": original_message,
                "action": "HOLD",
                "order_type": "MARKET",
                "tactic_reasoning": f"Unexpected error in parsing: {e}",
                "timestamp": original_message.get("timestamp"),
                "source": self.name
            }

async def main():
    agent = TacticbotAgent()
    await agent.start(event_bus)

if __name__ == "__main__":
    asyncio.run(main())

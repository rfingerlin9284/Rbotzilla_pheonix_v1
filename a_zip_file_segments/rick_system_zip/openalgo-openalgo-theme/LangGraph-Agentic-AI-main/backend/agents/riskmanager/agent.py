import asyncio
import json
import logging
import os
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from ai_client import AIModelClient

logger = logging.getLogger(__name__)

class RiskManagerAgent(BaseAgent):
    def __init__(self, api_client: AIModelClient = None, name="RiskManager", subscribe_channels=None, publish_channel="riskmanager_out"):
        super().__init__(
            name=name,
            subscribe_channels=subscribe_channels if subscribe_channels is not None else ["technical_signals", "marketsentinel_out", "macroforecaster_out"],
            publish_channel=publish_channel
        )
        self.ai_client = api_client or AIModelClient(
            api_key=os.getenv("GEMINI_API_KEY"),
            model_name=os.getenv("RISKMGR_MODEL", "gemini-1.5-flash")
        )
        logger.info(f"Initialized {name} agent with AIModelClient")

    async def process_message(self, channel: str, message: Dict[str, Any]):
        """Process incoming signals and perform risk assessment with AI"""
        try:
            logger.info(f"Processing message from channel '{channel}': {message}")
            
            if not isinstance(message, dict):
                logger.warning(f"Invalid message format: {type(message)}")
                return
            
            prompt = f"""Assess the risk of the following trading signal and market context.
            The output should be a JSON object with the following keys:
            - "risk_level": "low", "medium", or "high"
            - "risk_reasoning": a brief explanation for the risk assessment
            - "recommendation": "APPROVE", "REJECT", or "ADJUST"
            - "adjusted_params": (optional) a dictionary of adjusted parameters if recommendation is "ADJUST"
            
            Signal and Context: {json.dumps(message)}
            """
            
            ai_response_text = await self.ai_client.chat_completion(prompt)
            logger.info(f"AI risk assessment raw response: {ai_response_text}")
            
            risk_assessment = self.parse_risk_assessment(ai_response_text, message)
            
            await self.publish(risk_assessment)
            logger.info(f"Published risk assessment: {risk_assessment}")
                
        except Exception as e:
            logger.error(f"Error processing message in RiskManagerAgent: {e}")

    def parse_risk_assessment(self, ai_response_text: str, original_message: Dict[str, Any] = None) -> Dict[str, Any]:
        """Parse AI response (expected to be JSON) into structured risk assessment"""
        try:
            ai_data = json.loads(ai_response_text)
            
            risk_level = ai_data.get("risk_level", "medium").lower()
            risk_reasoning = ai_data.get("risk_reasoning", "No specific risk reasoning provided.")
            recommendation = ai_data.get("recommendation", "REJECT").upper()
            adjusted_params = ai_data.get("adjusted_params", {})

            risk_assessment = {
                "type": "risk_evaluated_signal",
                "symbol": original_message.get("symbol", "UNKNOWN"),
                "original_signal": original_message,
                "risk_level": risk_level,
                "risk_reasoning": risk_reasoning,
                "recommendation": recommendation,
                "timestamp": original_message.get("timestamp"),
                "source": self.name
            }
            if adjusted_params:
                risk_assessment["adjusted_params"] = adjusted_params
                
            return risk_assessment
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error for AI risk assessment: {e} - Raw response: {ai_response_text}")
            return {
                "type": "risk_evaluated_signal",
                "symbol": original_message.get('symbol', 'UNKNOWN'),
                "original_signal": original_message,
                "risk_level": "high",
                "risk_reasoning": f"Failed to parse AI response: {ai_response_text}",
                "recommendation": "REJECT",
                "timestamp": original_message.get('timestamp'),
                "source": self.name
            }
        except Exception as e:
            logger.error(f"Error in parse_risk_assessment: {e}")
            return {
                "type": "risk_evaluated_signal",
                "symbol": original_message.get('symbol', 'UNKNOWN'),
                "original_signal": original_message,
                "risk_level": "high",
                "risk_reasoning": f"Unexpected error in parsing: {e}",
                "recommendation": "REJECT",
                "timestamp": original_message.get('timestamp'),
                "source": self.name
            }

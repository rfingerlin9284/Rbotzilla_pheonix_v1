import asyncio
import os
import logging
from backend.agents.tacticbot.main import TacticbotAgent
from backend.orchestrator.event_bus import event_bus

logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(level=logging.INFO)
    try:
        agent = TacticbotAgent(
            name="TacticBot",
            subscribe_channels=["riskmanager_out"],
            publish_channel="tacticbot_out"
        )
        logger.info("Starting TacticBot agent from orchestrator/run_tacticbot.py...")
        await agent.start(event_bus)
    except Exception as e:
        logger.error(f"Error starting TacticBot agent: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
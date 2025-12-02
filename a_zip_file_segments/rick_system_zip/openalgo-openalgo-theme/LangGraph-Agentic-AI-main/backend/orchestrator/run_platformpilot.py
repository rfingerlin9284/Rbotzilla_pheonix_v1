import asyncio
import os
import logging
from backend.agents.platformpilot.main import PlatformpilotAgent
from backend.orchestrator.event_bus import event_bus

logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(level=logging.INFO)
    try:
        agent = PlatformpilotAgent(
            name="PlatformPilot",
            subscribe_channels=["tacticbot_out"],
            publish_channel="platformpilot_out"
        )
        logger.info("Starting PlatformPilot agent from orchestrator/run_platformpilot.py...")
        await agent.start(event_bus)
    except Exception as e:
        logger.error(f"Error starting PlatformPilot agent: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
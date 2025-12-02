import asyncio
import logging
import os

from backend.agents.chartanalyst.agent import ChartAnalystAgent
from backend.agents.riskmanager.agent import RiskManagerAgent
from backend.agents.marketsentinel.main import MarketsentinelAgent
from backend.agents.macroforecaster.main import MacroforecasterAgent
from backend.agents.tacticbot.main import TacticbotAgent
from backend.agents.platformpilot.main import PlatformpilotAgent
from backend.ai_client import AIModelClient
from backend.orchestrator.event_bus import event_bus

logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize shared AI API client
    api_client = AIModelClient(
        api_key=os.getenv("GEMINI_API_KEY"),
        model_name=os.getenv("DEFAULT_AI_MODEL", "gemini-1.5-flash")
    )

    # Instantiate agents with the shared api_client and any config
    agents = [
        ChartAnalystAgent(api_client=api_client),
        RiskManagerAgent(api_client=api_client),
        MarketsentinelAgent(api_client=api_client),
        MacroforecasterAgent(api_client=api_client),
        TacticbotAgent(api_client=api_client),
        PlatformpilotAgent(api_client=api_client),
    ]

    try:
        await event_bus.connect()

        # Initialize all agents with the event bus
        for agent in agents:
            await agent.initialize(event_bus)

        # Start all agents concurrently
        agent_tasks = [asyncio.create_task(agent.start(event_bus)) for agent in agents]
        
        # Start the event bus listener in the background
        event_bus_listener_task = event_bus.start_background_listener()

        logger.info("All agents and event bus listener started.")

        # Keep the main task alive until all agent tasks are done or cancelled
        await asyncio.gather(event_bus_listener_task, *agent_tasks, return_exceptions=True)

    except Exception as e:
        logger.error(f"Error in run_all_agents main: {e}")
    finally:
        await event_bus.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
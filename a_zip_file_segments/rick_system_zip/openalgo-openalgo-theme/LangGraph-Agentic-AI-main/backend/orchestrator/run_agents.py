import asyncio
import logging
import signal
import sys

from backend.agents.chartanalyst.agent import ChartAnalystAgent
from backend.agents.riskmanager.agent import RiskManagerAgent
from backend.agents.marketsentinel.main import MarketsentinelAgent
from backend.agents.macroforecaster.main import MacroforecasterAgent
from backend.agents.tacticbot.main import TacticbotAgent
from backend.agents.platformpilot.main import PlatformpilotAgent
from backend.orchestrator.event_bus import event_bus

logger = logging.getLogger(__name__)

async def create_test_data():
    """Create test market data"""
    while True:
        await asyncio.sleep(5)  # Publish every 5 seconds
        test_data = {
            "symbol": "BTCUSD",
            "price": 45000.50,
            "volume": 1000000,
            "timestamp": "2025-08-12T10:00:00Z",
            "high": 45500.00,
            "low": 44000.00,
            "open": 44500.00
        }
        await event_bus.publish("market_data", test_data)
        logger.info(f"Published test market data: {test_data}")

async def shutdown(signum=None):
    """Graceful shutdown"""
    logger.info(f"Received signal {signum}, shutting down...")
    await event_bus.disconnect()
    sys.exit(0)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        await event_bus.connect()
        
        chart_agent = ChartAnalystAgent()
        risk_agent = RiskManagerAgent()
        marketsentinel_agent = MarketsentinelAgent()
        macroforecaster_agent = MacroforecasterAgent()
        tacticbot_agent = TacticbotAgent()
        platformpilot_agent = PlatformpilotAgent()
        
        await chart_agent.initialize(event_bus)
        await risk_agent.initialize(event_bus)
        await marketsentinel_agent.initialize(event_bus)
        await macroforecaster_agent.initialize(event_bus)
        await tacticbot_agent.initialize(event_bus)
        await platformpilot_agent.initialize(event_bus)
        
        listen_task = event_bus.start_background_listener()
        test_data_task = asyncio.create_task(create_test_data())
        
        logger.info("All agents started. Press Ctrl+C to stop.")
        
        agent_tasks = [
            asyncio.create_task(chart_agent.start(event_bus)),
            asyncio.create_task(risk_agent.start(event_bus)),
            asyncio.create_task(marketsentinel_agent.start(event_bus)),
            asyncio.create_task(macroforecaster_agent.start(event_bus)),
            asyncio.create_task(tacticbot_agent.start(event_bus)),
            asyncio.create_task(platformpilot_agent.start(event_bus)),
        ]
        
        await asyncio.gather(
            listen_task,
            test_data_task,
            *agent_tasks,
            return_exceptions=True
        )
        
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        await event_bus.disconnect()

if __name__ == "__main__":
    if sys.platform != 'win32':
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(sig)))
    
    asyncio.run(main())
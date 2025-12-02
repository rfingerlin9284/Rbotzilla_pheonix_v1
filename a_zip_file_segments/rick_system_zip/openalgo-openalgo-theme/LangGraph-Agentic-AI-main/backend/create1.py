import os

AGENTS = [
    "chartanalyst",
    "riskmanager",
    "marketsentinel",
    "macroforecaster",
    "tacticbot",
    "platformpilot"
]

BASE_AGENT_CODE = '''\
import asyncio
from backend.orchestrator.event_bus import event_bus

class BaseAgent:
    def __init__(self):
        self.running = True

    async def start(self):
        await event_bus.connect()
        await self.subscribe_channels()
        self.listener_task = asyncio.create_task(event_bus.start_listening())
        print(f"{self.__class__.__name__} started listening")
        while self.running:
            await asyncio.sleep(1)

    async def subscribe_channels(self):
        # Override to subscribe to relevant channels
        pass

    async def stop(self):
        self.running = False
        await event_bus.stop_listening()

    async def publish(self, channel, message):
        await event_bus.publish(channel, message)
'''

CHARTANALYST_CODE = '''\
from backend.agents.base_agent import BaseAgent

class ChartanalystAgent(BaseAgent):
    async def subscribe_channels(self):
        await event_bus.subscribe("market_events", self.handle_market_event)

    async def handle_market_event(self, channel, message):
        print(f"[ChartAnalyst] Received market event: {message}")
        # Dummy analysis signal
        signal = {
            "type": "technical_signal",
            "symbol": message.get("symbol"),
            "signal": "buy",
            "confidence": 0.9,
            "timestamp": message.get("timestamp")
        }
        await self.publish("chartanalyst_out", signal)

async def main():
    agent = ChartanalystAgent()
    await agent.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''

RISKMANAGER_CODE = '''\
from backend.agents.base_agent import BaseAgent

class RiskmanagerAgent(BaseAgent):
    async def subscribe_channels(self):
        await event_bus.subscribe("chartanalyst_out", self.handle_signal)

    async def handle_signal(self, channel, message):
        print(f"[RiskManager] Received signal: {message}")
        # Dummy risk logic here
        risk_evaluation = {
            "type": "risk_evaluation",
            "symbol": message.get("symbol"),
            "approved": True,
            "timestamp": message.get("timestamp")
        }
        await self.publish("riskmanager_out", risk_evaluation)

async def main():
    agent = RiskmanagerAgent()
    await agent.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''

ORCHESTRATOR_CODE = '''\
import asyncio
import json
from backend.orchestrator.event_bus import event_bus

async def publish_test_event():
    await event_bus.connect()
    event = {
        "type": "market_event",
        "symbol": "AAPL",
        "price": 170.5,
        "timestamp": "2025-08-09T10:00:00Z",
        "news": "Apple earnings beat expectations"
    }
    print("[Orchestrator] Publishing test market event")
    await event_bus.publish("market_events", event)
    await asyncio.sleep(2)
    await event_bus.disconnect()

if __name__ == "__main__":
    asyncio.run(publish_test_event())
'''

def create_file(path, content):
    if os.path.exists(path):
        print(f"Skipping existing file: {path}")
        return
    with open(path, "w") as f:
        f.write(content)
    print(f"Created {path}")

def main():
    # Create base_agent.py
    os.makedirs("backend/agents", exist_ok=True)
    create_file("backend/agents/base_agent.py", BASE_AGENT_CODE)

    # Create agent folders and main scripts
    for agent in AGENTS:
        folder = f"backend/agents/{agent}"
        os.makedirs(folder, exist_ok=True)
        if agent == "chartanalyst":
            create_file(f"{folder}/main.py", CHARTANALYST_CODE)
        elif agent == "riskmanager":
            create_file(f"{folder}/main.py", RISKMANAGER_CODE)
        else:
            # Create simple stub agent
            stub_code = f'''\
from backend.agents.base_agent import BaseAgent

class {agent.capitalize()}Agent(BaseAgent):
    async def subscribe_channels(self):
        # TODO: subscribe to relevant channels for {agent}
        pass

    async def main_logic(self, channel, message):
        print(f"[{agent.capitalize()}] received message:", message)

async def main():
    agent = {agent.capitalize()}Agent()
    await agent.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''
            create_file(f"{folder}/main.py", stub_code)

    # Create orchestrator script
    os.makedirs("orchestrator", exist_ok=True)
    create_file("orchestrator/publish_test_event.py", ORCHESTRATOR_CODE)

    print("\nSetup complete.")
    print("Run an agent with: python3 backend/agents/chartanalyst/main.py")
    print("Run the orchestrator publisher with: python3 orchestrator/publish_test_event.py")

if __name__ == "__main__":
    main()

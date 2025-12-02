import os

BASE_PATH = "backend/agents"
os.makedirs(BASE_PATH, exist_ok=True)

# Base agent code (simplified)
base_agent_code = '''\
import json
import redis
import threading
import time

class BaseAgent:
    def __init__(self, name, subscribe_channels, publish_channel):
        self.name = name
        self.subscribe_channels = subscribe_channels
        self.publish_channel = publish_channel
        self.redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe(*subscribe_channels)
        self.running = False

    def process_message(self, message):
        # Override this in child classes
        raise NotImplementedError()

    def publish(self, message):
        self.redis_client.publish(self.publish_channel, json.dumps(message))

    def listen(self):
        print(f"Agent '{self.name}' listening on channels: {self.subscribe_channels}")
        for item in self.pubsub.listen():
            if item['type'] == 'message':
                try:
                    data = json.loads(item['data'])
                    print(f"[{self.name}] Received message on {item['channel']}: {data}")
                    output = self.process_message(data)
                    if output:
                        self.publish(output)
                        print(f"[{self.name}] Published message on {self.publish_channel}: {output}")
                except Exception as e:
                    print(f"[{self.name}] Error processing message: {e}")

    def run(self):
        self.running = True
        try:
            self.listen()
        except KeyboardInterrupt:
            print(f"Agent '{self.name}' shutting down.")
            self.running = False
'''

agents = {
    "chartanalyst.py": '''\
from backend.agents.base_agent import BaseAgent

class ChartAnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="chartanalyst",
            subscribe_channels=["market_events"],
            publish_channel="chartanalyst_out"
        )
    
    def process_message(self, message):
        symbol = message.get("symbol")
        price = message.get("price")
        signal = "buy" if int(str(price)[-1]) % 2 == 0 else "hold"
        return {
            "type": "chartanalyst_out",
            "symbol": symbol,
            "signal": signal,
            "timestamp": message.get("timestamp"),
        }

if __name__ == "__main__":
    agent = ChartAnalystAgent()
    agent.run()
''',

    "riskmanager.py": '''\
from backend.agents.base_agent import BaseAgent

class RiskManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="riskmanager",
            subscribe_channels=["chartanalyst_out", "marketsentinel_out", "macroforecaster_out"],
            publish_channel="riskmanager_out"
        )
    
    def process_message(self, message):
        risk_level = "low"
        return {
            "type": "riskmanager_out",
            "symbol": message.get("symbol"),
            "risk_level": risk_level,
            "timestamp": message.get("timestamp"),
        }

if __name__ == "__main__":
    agent = RiskManagerAgent()
    agent.run()
''',

    "marketsentinel.py": '''\
from backend.agents.base_agent import BaseAgent

class MarketSentinelAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="marketsentinel",
            subscribe_channels=["market_events"],
            publish_channel="marketsentinel_out"
        )
    
    def process_message(self, message):
        alert = "none"
        if "crash" in message.get("news", "").lower():
            alert = "market crash alert"
        return {
            "type": "marketsentinel_out",
            "symbol": message.get("symbol"),
            "alert": alert,
            "timestamp": message.get("timestamp"),
        }

if __name__ == "__main__":
    agent = MarketSentinelAgent()
    agent.run()
''',

    "macroforecaster.py": '''\
from backend.agents.base_agent import BaseAgent

class MacroForecasterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="macroforecaster",
            subscribe_channels=["market_events"],
            publish_channel="macroforecaster_out"
        )
    
    def process_message(self, message):
        bias = "neutral"
        price = message.get("price", 0)
        if price > 100:
            bias = "bullish"
        elif price < 50:
            bias = "bearish"
        return {
            "type": "macroforecaster_out",
            "symbol": message.get("symbol"),
            "bias": bias,
            "timestamp": message.get("timestamp"),
        }

if __name__ == "__main__":
    agent = MacroForecasterAgent()
    agent.run()
''',

    "tacticbot.py": '''\
from backend.agents.base_agent import BaseAgent

class TacticBotAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="tacticbot",
            subscribe_channels=["riskmanager_out"],
            publish_channel="tacticbot_out"
        )
    
    def process_message(self, message):
        action = "hold"
        if message.get("risk_level") == "low":
            action = "enter_trade"
        elif message.get("risk_level") == "high":
            action = "exit_trade"
        return {
            "type": "tacticbot_out",
            "symbol": message.get("symbol"),
            "action": action,
            "timestamp": message.get("timestamp"),
        }

if __name__ == "__main__":
    agent = TacticBotAgent()
    agent.run()
''',

    "platformpilot.py": '''\
from backend.agents.base_agent import BaseAgent

class PlatformPilotAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="platformpilot",
            subscribe_channels=["tacticbot_out"],
            publish_channel="platformpilot_out"
        )
    
    def process_message(self, message):
        status = f"Action {message.get('action')} executed"
        return {
            "type": "platformpilot_out",
            "symbol": message.get("symbol"),
            "status": status,
            "timestamp": message.get("timestamp"),
        }

if __name__ == "__main__":
    agent = PlatformPilotAgent()
    agent.run()
'''
}

def write_file(filepath, content):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Creating base agent class in {BASE_PATH}/base_agent.py...")
write_file(f"{BASE_PATH}/base_agent.py", base_agent_code)

for filename, code in agents.items():
    full_path = f"{BASE_PATH}/{filename}"
    print(f"Creating agent script {full_path}...")
    write_file(full_path, code)

print("All agent scripts and folder structure created!")

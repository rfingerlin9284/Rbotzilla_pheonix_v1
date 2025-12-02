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

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

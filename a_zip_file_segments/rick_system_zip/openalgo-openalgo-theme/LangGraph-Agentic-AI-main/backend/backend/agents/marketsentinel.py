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

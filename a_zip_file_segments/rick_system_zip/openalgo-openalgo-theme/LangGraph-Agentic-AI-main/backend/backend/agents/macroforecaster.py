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

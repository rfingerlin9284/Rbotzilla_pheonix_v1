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

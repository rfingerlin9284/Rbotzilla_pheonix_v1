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

import os

BASE_DIR = "backend/agents/chartanalyst"

FILES_CONTENT = {
    "__init__.py": "",
    
    "main.py": '''\
def analyze_market_event(event):
    """
    Replace this with real AI calls (Mistral, LLaMA, etc.)
    event: dict with keys like 'symbol', 'price', 'timestamp'
    """
    symbol = event.get("symbol")
    price = event.get("price")
    
    # Dummy logic: signal "buy" if price ends with even digit else "hold"
    signal = "buy" if int(str(price)[-1]) % 2 == 0 else "hold"
    
    return {
        "type": "chartanalyst_out",
        "symbol": symbol,
        "signal": signal,
        "timestamp": event.get("timestamp"),
    }
''',

    "pubsub.py": '''\
import redis
import json
from backend.agents.chartanalyst.main import analyze_market_event

def run_agent():
    r = redis.Redis(host='redis', port=6379, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.subscribe("market_events")

    print("ChartAnalyst subscribed to market_events")

    for message in pubsub.listen():
        if message['type'] == 'message':
            event = json.loads(message['data'])
            print(f"ChartAnalyst received: {event}")

            signal = analyze_market_event(event)
            r.publish("chartanalyst_out", json.dumps(signal))
            print(f"ChartAnalyst published: {signal}")

if __name__ == "__main__":
    run_agent()
''',

    "prompts.py": '''\
# Example prompt template for AI reasoning
CHARTANALYST_PROMPT = """
Analyze the price chart for symbol: {symbol}
Given the latest price {price}, generate a trading signal.
"""
''',

    "test.py": '''\
from backend.agents.chartanalyst.main import analyze_market_event
from datetime import datetime

def test_analyze():
    sample_event = {
        "symbol": "AAPL",
        "price": 150.24,
        "timestamp": datetime.utcnow().isoformat(),
    }
    result = analyze_market_event(sample_event)
    print("Test result:", result)

if __name__ == "__main__":
    test_analyze()
'''
}

def create_agent_scaffold(base_dir, files_dict):
    os.makedirs(base_dir, exist_ok=True)
    for filename, content in files_dict.items():
        path = os.path.join(base_dir, filename)
        with open(path, "w") as f:
            f.write(content)
        print(f"Created {path}")

if __name__ == "__main__":
    create_agent_scaffold(BASE_DIR, FILES_CONTENT)

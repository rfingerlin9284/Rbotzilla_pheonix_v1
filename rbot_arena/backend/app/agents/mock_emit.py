import asyncio
import random
from app.core.bus import bus_publish

async def run_mock(symbol="BTC-USD"):
    """Mock agent emitting signals for testing"""
    await bus_publish({
        "source": "arena",
        "type": "heartbeat",
        "symbol": symbol,
        "payload": {"up": True}
    })
    
    while True:
        conf = round(random.uniform(0.55, 0.88), 2)
        
        await bus_publish({
            "source": "agent.strategy",
            "type": "signal",
            "symbol": symbol,
            "payload": {
                "side": "long",
                "confidence": conf,
                "quality": int(conf * 100),
                "reasons": [
                    {"name": "fvg", "value": True},
                    {"name": "fib", "value": "0.618"}
                ]
            }
        })
        
        await bus_publish({
            "source": "risk.manager",
            "type": "risk_update",
            "symbol": symbol,
            "payload": {
                "risk_pct": 0.7,
                "sl_new": "66400->64650",
                "trail": "on"
            }
        })
        
        await bus_publish({
            "source": "pnl",
            "type": "pnl",
            "symbol": symbol,
            "payload": {
                "unrealized": round(random.uniform(-50, 120), 2),
                "day_pnl": round(random.uniform(-100, 250), 2)
            }
        })
        
        await asyncio.sleep(2.0)

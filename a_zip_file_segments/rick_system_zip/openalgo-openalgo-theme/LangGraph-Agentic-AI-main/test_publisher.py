import asyncio
import json
import redis.asyncio as aioredis
from datetime import datetime

async def publish_test_message():
    redis = aioredis.from_url("redis://localhost:6380")
    event = {
        "signal_type": "BUY",
        "symbol": "BTC/USD",
        "price": 69000,
        "confidence": 0.9,
        "timestamp": datetime.utcnow().isoformat(),
        "analysis": "Test analysis from publisher",
        "source": "test_publisher"
    }
    await redis.publish("chartanalyst_out", json.dumps(event))
    print("Published test message to chartanalyst_out")
    await redis.close()

if __name__ == "__main__":
    asyncio.run(publish_test_message())
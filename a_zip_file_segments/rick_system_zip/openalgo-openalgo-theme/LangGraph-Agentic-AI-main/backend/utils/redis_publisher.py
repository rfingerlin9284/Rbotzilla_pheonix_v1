import redis
import json
import logging
from datetime import datetime # Added this import
from config import settings

logger = logging.getLogger(__name__)

class RedisPublisher:
    def __init__(self):
        self.redis_client = self._get_redis_client()

    def _get_redis_client(self):
        try:
            client = redis.from_url(settings.redis_url)
            client.ping()
            logger.info("Successfully connected to Redis.")
            return client
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Could not connect to Redis: {e}")
            raise

    async def publish_event(self, channel: str, event_type: str, payload: dict):
        message = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload
        }
        try:
            self.redis_client.publish(channel, json.dumps(message))
            logger.info(f"Published to {channel}: {event_type}")
        except Exception as e:
            logger.error(f"Error publishing to Redis channel {channel}: {e}")

# Initialize a global publisher instance
redis_publisher = RedisPublisher()

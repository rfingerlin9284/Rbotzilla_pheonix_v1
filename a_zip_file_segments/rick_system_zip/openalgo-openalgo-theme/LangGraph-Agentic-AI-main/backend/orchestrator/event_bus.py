import asyncio
import redis.asyncio as aioredis
import json
import logging
from typing import Dict, Any, Callable, List
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class EventBus:
    """Redis-based event bus for agent communication"""
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
        return cls._instance

    def __init__(self, redis_url: str = None):
        if not hasattr(self, '_initialized'):
            self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis = None
            self.pubsub = None
            self.subscribers: Dict[str, List[Callable]] = {}
            self.running = False
            self._subscribed_channels = set()
            self._listen_task = None
            self._initialized = True

    async def connect(self):
        """Connect to Redis and set up pubsub"""
        try:
            if not self.redis:
                self.redis = aioredis.Redis.from_url(self.redis_url, decode_responses=False)
                await self.redis.ping()  # Test connection
                self.pubsub = self.redis.pubsub()
                logger.info(f"Connected to Redis event bus at {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Redis"""
        self.running = False
        
        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass

        if self.pubsub:
            await self.pubsub.close()
        if self.redis:
            await self.redis.close()
        logger.info("Disconnected from Redis")

    async def publish(self, channel: str, message: Dict[str, Any]):
        """Publish message to channel"""
        try:
            if not self.redis:
                await self.connect()
            
            enriched_message = {
                **message,
                "timestamp": datetime.now().isoformat(),
                "channel": channel
            }
            
            message_json = json.dumps(enriched_message, default=str)
            result = await self.redis.publish(channel, message_json)
            logger.debug(f"Published to {channel}: {message} (subscribers: {result})")
            return result
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")
            raise

    async def subscribe(self, channel: str, callback: Callable):
        """Subscribe to a Redis channel with a callback"""
        try:
            if not self.pubsub:
                await self.connect()
            
            # Add callback to subscribers
            if channel not in self.subscribers:
                self.subscribers[channel] = []
            self.subscribers[channel].append(callback)
            
            # Only subscribe to Redis if we haven't already
            if channel not in self._subscribed_channels:
                await self.pubsub.subscribe(channel)
                self._subscribed_channels.add(channel)
                logger.info(f"Subscribed to channel: {channel}")
            else:
                logger.info(f"Added callback to existing subscription: {channel}")
                
        except Exception as e:
            logger.error(f"Failed to subscribe to {channel}: {e}")
            raise

    async def unsubscribe(self, channel: str, callback: Callable = None):
        """Unsubscribe from a channel"""
        try:
            if channel in self.subscribers:
                if callback:
                    # Remove specific callback
                    if callback in self.subscribers[channel]:
                        self.subscribers[channel].remove(callback)
                    # If no more callbacks, unsubscribe from Redis
                    if not self.subscribers[channel]:
                        del self.subscribers[channel]
                        if channel in self._subscribed_channels:
                            await self.pubsub.unsubscribe(channel)
                            self._subscribed_channels.remove(channel)
                            logger.info(f"Unsubscribed from channel: {channel}")
                else:
                    # Remove all callbacks for this channel
                    del self.subscribers[channel]
                    if channel in self._subscribed_channels:
                        await self.pubsub.unsubscribe(channel)
                        self._subscribed_channels.remove(channel)
                        logger.info(f"Unsubscribed from channel: {channel}")
        except Exception as e:
            logger.error(f"Failed to unsubscribe from {channel}: {e}")

    async def start_listening(self):
        """Start listening for published messages"""
        if not self.pubsub:
            await self.connect()
        
        # Check if we have any subscriptions
        if not self._subscribed_channels:
            logger.warning("No channels subscribed. Call subscribe() before start_listening()")
            return
        
        self.running = True
        logger.info(f"Started listening for events on channels: {list(self._subscribed_channels)}")
        
        try:
            while self.running:
                try:
                    message = await self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                    if message and message['type'] == 'message':
                        await self._handle_message(message)
                except asyncio.TimeoutError:
                    # This is normal - just continue the loop
                    continue
                except Exception as e:
                    logger.error(f"Error getting message: {e}")
                    # Small delay before retrying
                    await asyncio.sleep(0.1)
                    
        except asyncio.CancelledError:
            logger.info("Event listening cancelled")
        except Exception as e:
            logger.error(f"Error in event loop: {e}")
        finally:
            logger.info("Stopped listening for events")

    async def _handle_message(self, message):
        """Handle an incoming message"""
        try:
            channel = message['channel'].decode('utf-8') if isinstance(message['channel'], bytes) else message['channel']
            data_str = message['data'].decode('utf-8') if isinstance(message['data'], bytes) else message['data']
            data = json.loads(data_str)
            
            logger.debug(f"Received message on {channel}: {data}")
            
            if channel in self.subscribers:
                # Execute all callbacks for this channel
                for callback in self.subscribers[channel]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(channel, data)
                        else:
                            callback(channel, data)
                    except Exception as e:
                        logger.error(f"Error in callback for channel {channel}: {e}")
            else:
                logger.warning(f"No subscribers for channel {channel}")
                        
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def stop_listening(self):
        """Stop the event loop"""
        self.running = False

    def start_background_listener(self):
        """Start listening in the background"""
        if self._listen_task is None or self._listen_task.done():
            self._listen_task = asyncio.create_task(self.start_listening())
        return self._listen_task

event_bus = EventBus()

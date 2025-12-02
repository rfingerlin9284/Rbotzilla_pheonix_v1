import asyncio
import logging
from typing import List, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, subscribe_channels: List[str] = None, publish_channel: str = None):
        self.name = name
        self.subscribe_channels = subscribe_channels or []
        self.publish_channel = publish_channel
        self.running = False
        self.event_bus = None
        
    async def initialize(self, event_bus):
        """Initialize the agent with event bus"""
        self.event_bus = event_bus
        
        # Subscribe to channels
        for channel in self.subscribe_channels:
            await self.event_bus.subscribe(channel, self.process_message)
            logger.info(f"{self.name} subscribed to {channel}")
    
    async def start(self, event_bus=None):
        """Start the agent"""
        if event_bus:
            await self.initialize(event_bus)
        
        self.running = True
        logger.info(f"Started agent: {self.name}")
        
        # Keep the agent running
        try:
            while self.running:
                await asyncio.sleep(1) # Keep the agent alive
        except asyncio.CancelledError:
            logger.info(f"Agent {self.name} cancelled")
        finally:
            await self.cleanup()
    
    async def stop(self):
        """Stop the agent"""
        self.running = False
        logger.info(f"Stopped agent: {self.name}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.event_bus:
            for channel in self.subscribe_channels:
                await self.event_bus.unsubscribe(channel, self.process_message)
    
    async def publish(self, message: Dict[str, Any]):
        """Publish a message"""
        if self.event_bus and self.publish_channel:
            await self.event_bus.publish(self.publish_channel, message)
        else:
            logger.warning(f"Cannot publish: event_bus={self.event_bus}, publish_channel={self.publish_channel}")
    
    @abstractmethod
    async def process_message(self, channel: str, message: Dict[str, Any]):
        """Process incoming messages - must be implemented by subclasses"""
        pass

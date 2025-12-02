#!/usr/bin/env python3
"""
Event Publisher for ChartAnalyst
Publishes market events and listens for ChartAnalyst signals
"""

import os
import json
import asyncio
import redis
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EventPublisher')

class EventPublisher:
    """Publishes market events and listens for agent responses"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.pubsub = None
        self._connect_redis()
    
    def _connect_redis(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def publish_market_event(self, symbol: str, price: float, volume: float = None, 
                            news: str = None) -> bool:
        """Publish a market event to trigger analysis"""
        try:
            event = {
                "type": "market_event",
                "symbol": symbol,
                "price": price,
                "volume": volume or 1000000,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "news": news or f"Price update for {symbol}",
                "source": "event_publisher"
            }
            
            message = json.dumps(event)
            result = self.redis_client.publish("market_events", message)
            
            if result > 0:
                logger.info(f"Published market event for {symbol} at ${price}")
                return True
            else:
                logger.warning(f"No subscribers for market_events channel")
                return False
                
        except Exception as e:
            logger.error(f"Failed to publish market event: {e}")
            return False
    
    def publish_analysis_request(self, symbol: str, timeframe: str = "1h") -> bool:
        """Publish direct analysis request"""
        try:
            request = {
                "type": "analysis_request",
                "symbol": symbol,
                "timeframe": timeframe,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "requester": "event_publisher"
            }
            
            message = json.dumps(request)
            result = self.redis_client.publish("analysis_requests", message)
            
            if result > 0:
                logger.info(f"Published analysis request for {symbol} ({timeframe})")
                return True
            else:
                logger.warning("No subscribers for analysis_requests channel")
                return False
                
        except Exception as e:
            logger.error(f"Failed to publish analysis request: {e}")
            return False
    
    def listen_for_signals(self, channels: List[str] = None):
        """Listen for ChartAnalyst signals"""
        if channels is None:
            channels = ["chartanalyst_out", "agent_out", "final_signals"]
        
        try:
            self.pubsub = self.redis_client.pubsub()
            self.pubsub.subscribe(*channels)
            
            logger.info(f"Listening for signals on channels: {channels}")
            
            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    self._handle_signal(message['channel'], message['data'])
                    
        except KeyboardInterrupt:
            logger.info("Stopping signal listener...")
        except Exception as e:
            logger.error(f"Error listening for signals: {e}")
        finally:
            if self.pubsub:
                self.pubsub.close()
    
    def _handle_signal(self, channel: str, data: str):
        """Handle received signal"""
        try:
            signal = json.loads(data)
            
            logger.info(f"?? Received signal from {channel}")
            print(f"\n{'='*50}")
            print(f"?? SIGNAL RECEIVED FROM {channel.upper()}")
            print(f"{'='*50}")
            print(f"Agent: {signal.get('agent', 'Unknown')}")
            print(f"Symbol: {signal.get('symbol', 'N/A')}")
            print(f"Pattern: {signal.get('pattern', 'N/A')}")
            print(f"Confidence: {signal.get('confidence', 0)}%")
            print(f"Trend: {signal.get('trend', 'N/A')}")
            print(f"Volatility: {signal.get('volatility', 'N/A')}")
            print(f"Support Zone: {signal.get('support_zone', [])}")
            print(f"Resistance Zone: {signal.get('resistance_zone', [])}")
            print(f"Timestamp: {signal.get('timestamp', 'N/A')}")
            
            # Print additional data if available
            if 'additional_data' in signal:
                print(f"\n?? Additional Data:")
                additional = signal['additional_data']
                for key, value in additional.items():
                    if key == 'candlestick_patterns' and value:
                        print(f"  Candlestick Patterns ({len(value)}):")
                        for pattern, strength in list(value.items())[:5]:  # Show first 5
                            print(f"    {pattern}: {strength}")
                    else:
                        print(f"  {key}: {value}")
            
            print(f"{'='*50}\n")
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from {channel}: {data}")
        except Exception as e:
            logger.error(f"Error handling signal from {channel}: {e}")

class MarketSimulator:
    """Simulates market events for testing"""
    
    def __init__(self, publisher: EventPublisher):
        self.publisher = publisher
        self.symbols = [
            "BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT",
            "AAPL", "TSLA", "GOOGL", "MSFT", "AMZN",
            "EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "XAGUSD"
        ]
        
        # Sample price data for simulation
        self.base_prices = {
            "BTCUSDT": 43000, "ETHUSDT": 2600, "ADAUSDT": 0.48,
            "AAPL": 195, "TSLA": 248, "GOOGL": 141,
            "EURUSD": 1.0856, "GBPUSD": 1.2731, "XAUUSD": 2034
        }
    
    async def simulate_market_activity(self, duration_minutes: int = 30):
        """Simulate market activity by publishing periodic events"""
        logger.info(f"Starting market simulation for {duration_minutes} minutes")
        
        import random
        end_time = datetime.now().timestamp() + (duration_minutes * 60)
        
        while datetime.now().timestamp() < end_time:
            # Pick random symbol
            symbol = random.choice(self.symbols)
            
            # Generate price movement
            base_price = self.base_prices.get(symbol, 100)
            price_change = random.uniform(-0.05, 0.05)  # ±5% change
            new_price = base_price * (1 + price_change)
            
            # Generate volume
            volume = random.uniform(500000, 2000000)
            
            # Generate news event occasionally
            news = None
            if random.random() < 0.1:  # 10% chance of news
                news_events = [
                    f"Breaking: {symbol} shows strong technical signal",
                    f"Market update: {symbol} reaches key resistance level",
                    f"Alert: High volume detected in {symbol}",
                    f"Analysis: {symbol} forming bullish pattern"
                ]
                news = random.choice(news_events)
            
            # Publish event
            success = self.publisher.publish_market_event(symbol, new_price, volume, news)
            if success:
                logger.debug(f"Published event: {symbol} @ ${new_price:.4f}")
            
            # Wait before next event
            await asyncio.sleep(random.uniform(5, 30))  # 5-30 seconds
        
        logger.info("Market simulation completed")
    
    async def trigger_specific_analysis(self, symbols: List[str], timeframe: str = "1h"):
        """Trigger analysis for specific symbols"""
        logger.info(f"Triggering analysis for {len(symbols)} symbols")
        
        for symbol in symbols:
            success = self.publisher.publish_analysis_request(symbol, timeframe)
            if success:
                print(f"✅ Analysis requested for {symbol} ({timeframe})")
            else:
                print(f"❌ Failed to request analysis for {symbol}")
            
            await asyncio.sleep(2)  # Small delay between requests

async def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="ChartAnalyst Event Publisher")
    parser.add_argument("--redis-url", default="redis://localhost:6379",
                       help="Redis connection URL")
    parser.add_argument("--command", choices=["publish", "listen", "simulate", "analyze"],
                       default="listen", help="Command to execute")
    parser.add_argument("--symbol", help="Symbol to analyze (for analyze command)")
    parser.add_argument("--timeframe", default="1h", help="Timeframe for analysis")
    parser.add_argument("--duration", type=int, default=30,
                       help="Duration in minutes for simulation")
    
    args = parser.parse_args()
    
    try:
        publisher = EventPublisher(args.redis_url)
        
        if args.command == "publish":
            # Publish a single market event
            symbol = args.symbol or "BTCUSDT"
            price = 43250.50  # Example price
            success = publisher.publish_market_event(symbol, price)
            if success:
                print(f"✅ Published market event for {symbol}")
            else:
                print(f"❌ Failed to publish market event")
                
        elif args.command == "listen":
            # Listen for signals
            print("?? Listening for ChartAnalyst signals...")
            print("Press Ctrl+C to stop")
            publisher.listen_for_signals()
            
        elif args.command == "simulate":
            # Simulate market activity
            simulator = MarketSimulator(publisher)
            print(f"?? Starting market simulation for {args.duration} minutes...")
            print("Press Ctrl+C to stop early")
            
            # Start listening in background
            listen_task = asyncio.create_task(
                asyncio.to_thread(publisher.listen_for_signals)
            )
            
            # Start simulation
            sim_task = asyncio.create_task(
                simulator.simulate_market_activity(args.duration)
            )
            
            try:
                await sim_task
                listen_task.cancel()
            except KeyboardInterrupt:
                print("\n?? Stopping simulation...")
                sim_task.cancel()
                listen_task.cancel()
                
        elif args.command == "analyze":
            # Request specific analysis
            if args.symbol:
                symbols = [args.symbol]
            else:
                symbols = ["BTCUSDT", "ETHUSDT", "AAPL", "TSLA"]
            
            simulator = MarketSimulator(publisher)
            
            print(f"?? Requesting analysis for {len(symbols)} symbols...")
            
            # Start listening for responses
            listen_task = asyncio.create_task(
                asyncio.to_thread(publisher.listen_for_signals)
            )
            
            # Trigger analysis
            await simulator.trigger_specific_analysis(symbols, args.timeframe)
            
            print("Listening for responses... Press Ctrl+C to stop")
            try:
                await asyncio.sleep(60)  # Listen for 1 minute
            except KeyboardInterrupt:
                pass
            finally:
                listen_task.cancel()
    
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    exit_code = asyncio.run(main())
    exit(exit_code)

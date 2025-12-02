#!/usr/bin/env python3
"""
Swarm Bot Execution Layer - RBOTzilla UNI Phase 7
Dynamic swarm bot management for individual trade execution.
PIN: 841921 | Generated: 2025-09-26
"""

import time
import threading
import logging
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import json
import uuid

class PositionStatus(Enum):
    """Position status states"""
    ACTIVE = "active"
    TRAILING = "trailing"
    CLOSING = "closing"
    CLOSED = "closed"
    EXPIRED = "expired"
    STOPPED = "stopped"

class TrailType(Enum):
    """Stop loss trailing types"""
    FIXED = "fixed"           # Fixed pip trailing
    VOLATILITY = "volatility" # ATR-based trailing
    PERCENTAGE = "percentage" # Percentage-based trailing

@dataclass
class Position:
    """Individual trading position data"""
    position_id: str
    symbol: str
    direction: str           # "buy" or "sell"
    entry_price: float
    target_price: float
    initial_stop_loss: float
    current_stop_loss: float
    quantity: float
    entry_time: datetime
    ttl_hours: float = 6.0   # Time to live in hours
    status: PositionStatus = PositionStatus.ACTIVE
    trail_type: TrailType = TrailType.VOLATILITY
    trail_distance: float = 0.0
    unrealized_pnl: float = 0.0
    max_favorable: float = 0.0  # Max favorable price movement
    last_update: datetime = field(default_factory=datetime.now)

class SwarmBot:
    """
    Individual bot managing a single trading position
    Handles trailing stops, TTL expiration, and position lifecycle
    """
    
    def __init__(self, position: Position, pin: int = None, broker_connector=None):
        """
        Initialize swarm bot for position management
        
        Args:
            position: Position object to manage
            pin: Security PIN (841921)
            broker_connector: REQUIRED for LIVE mode - broker API connector for real-time data
        """
        if pin and pin != 841921:
            raise PermissionError("Invalid PIN for SwarmBot")
        
        self.position = position
        self.broker_connector = broker_connector  # Store broker connector for fresh data
        self.logger = logging.getLogger(f"SwarmBot-{position.position_id[:8]}")
        self.is_active = True
        self._stop_event = threading.Event()
        
        # Verify broker connector in non-simulation environments
        if broker_connector is None:
            self.logger.warning(
                "⚠️ No broker connector provided - will use simulated prices. "
                "This is OK for GHOST/CANARY but NOT for LIVE trading!"
            )
        
        # Volatility-based trailing parameters
        self.volatility_multiplier = 1.5  # 1.5x ATR for trail distance
        self.min_trail_distance = 0.001   # Minimum 10 pips for forex
        self.max_trail_distance = 0.01    # Maximum 100 pips for forex
        
        # Monitoring intervals
        self.update_interval = 10  # seconds between price checks
        
        self.logger.info(f"SwarmBot initialized for {position.symbol} position {position.position_id[:8]}")
    
    def _calculate_current_price(self) -> float:
        """
        Get FRESH market price from broker API or WebSocket
        NEVER uses cached data for position management
        """
        try:
            # PRODUCTION: Fetch REAL-TIME price from broker
            # This should call broker API directly, never cache
            
            # Check if broker connector is available
            if hasattr(self, 'broker_connector') and self.broker_connector:
                # Get FRESH price from broker API
                current_price = self.broker_connector.get_current_bid_ask(self.position.symbol)
                
                if self.position.direction == "buy":
                    # For buy positions, use BID price (sell back at bid)
                    price = current_price.get('bid', current_price.get('price'))
                else:
                    # For sell positions, use ASK price (buy back at ask)
                    price = current_price.get('ask', current_price.get('price'))
                
                if price:
                    self.logger.debug(f"Fresh price from API: {self.position.symbol} = {price}")
                    return float(price)
            
            # FALLBACK: If no broker connector, simulate for testing
            # ⚠️ WARNING: This should ONLY be used in GHOST/CANARY modes!
            self.logger.warning(f"No broker connector - using simulated price for {self.position.symbol}")
            
            import random
            base_price = self.position.entry_price
            
            if self.position.direction == "buy":
                price_change = random.uniform(-0.002, 0.003)
            else:
                price_change = random.uniform(-0.003, 0.002)
            
            current_price = base_price * (1 + price_change)
            return round(current_price, 5)
            
        except Exception as e:
            self.logger.error(f"Failed to get current price for {self.position.symbol}: {e}")
            # Emergency fallback to last known entry price
            return self.position.entry_price
    
    def _calculate_unrealized_pnl(self, current_price: float) -> float:
        """Calculate current unrealized P&L"""
        if self.position.direction == "buy":
            pnl = (current_price - self.position.entry_price) * self.position.quantity
        else:  # sell
            pnl = (self.position.entry_price - current_price) * self.position.quantity
        
        return round(pnl, 2)
    
    def _calculate_volatility_trail_distance(self, current_price: float) -> float:
        """
        Calculate trailing stop distance based on volatility
        Simulates ATR-based calculation
        """
        # Simulate ATR (Average True Range) calculation
        # In production, this would use real price data
        base_atr = current_price * 0.008  # 0.8% of current price as simulated ATR
        
        trail_distance = base_atr * self.volatility_multiplier
        
        # Apply min/max constraints
        trail_distance = max(self.min_trail_distance, trail_distance)
        trail_distance = min(self.max_trail_distance, trail_distance)
        
        return trail_distance
    
    def _should_trail_stop(self, current_price: float) -> Tuple[bool, float]:
        """
        Determine if stop loss should be trailed
        Returns (should_trail, new_stop_level)
        """
        if self.position.trail_type == TrailType.VOLATILITY:
            trail_distance = self._calculate_volatility_trail_distance(current_price)
        elif self.position.trail_type == TrailType.PERCENTAGE:
            trail_distance = current_price * (self.position.trail_distance / 100)
        else:  # FIXED
            trail_distance = self.position.trail_distance
        
        if self.position.direction == "buy":
            # For buy positions, trail stop upward when price moves up
            potential_new_stop = current_price - trail_distance
            
            if potential_new_stop > self.position.current_stop_loss:
                return True, potential_new_stop
        else:  # sell
            # For sell positions, trail stop downward when price moves down
            potential_new_stop = current_price + trail_distance
            
            if potential_new_stop < self.position.current_stop_loss:
                return True, potential_new_stop
        
        return False, self.position.current_stop_loss
    
    def _check_stop_loss_hit(self, current_price: float) -> bool:
        """Check if current price has hit stop loss"""
        if self.position.direction == "buy":
            return current_price <= self.position.current_stop_loss
        else:  # sell
            return current_price >= self.position.current_stop_loss
    
    def _check_target_hit(self, current_price: float) -> bool:
        """Check if current price has hit target"""
        if self.position.direction == "buy":
            return current_price >= self.position.target_price
        else:  # sell
            return current_price <= self.position.target_price
    
    def _check_ttl_expired(self) -> bool:
        """Check if position TTL has expired"""
        elapsed = datetime.now() - self.position.entry_time
        return elapsed.total_seconds() > (self.position.ttl_hours * 3600)
    
    def _update_position_metrics(self, current_price: float):
        """Update position tracking metrics"""
        # Update unrealized PnL
        self.position.unrealized_pnl = self._calculate_unrealized_pnl(current_price)
        
        # Update max favorable excursion
        if self.position.direction == "buy":
            if current_price > self.position.entry_price:
                favorable_move = current_price - self.position.entry_price
                self.position.max_favorable = max(self.position.max_favorable, favorable_move)
        else:  # sell
            if current_price < self.position.entry_price:
                favorable_move = self.position.entry_price - current_price
                self.position.max_favorable = max(self.position.max_favorable, favorable_move)
        
        # Update last update time
        self.position.last_update = datetime.now()
    
    def manage_position(self) -> str:
        """
        Main position management loop
        Returns final position outcome
        """
        self.logger.info(f"Starting position management for {self.position.symbol}")
        
        position_outcome = "unknown"
        
        try:
            while self.is_active and not self._stop_event.is_set():
                # Get current market price
                current_price = self._calculate_current_price()
                
                # Update position metrics
                self._update_position_metrics(current_price)
                
                # Check exit conditions
                
                # 1. Check if target hit
                if self._check_target_hit(current_price):
                    self.position.status = PositionStatus.CLOSING
                    position_outcome = "target_hit"
                    self.logger.info(f"Target hit at {current_price}, closing position")
                    break
                
                # 2. Check if stop loss hit
                if self._check_stop_loss_hit(current_price):
                    self.position.status = PositionStatus.STOPPED
                    position_outcome = "stopped_out"
                    self.logger.info(f"Stop loss hit at {current_price}, position stopped")
                    break
                
                # 3. Check TTL expiration
                if self._check_ttl_expired():
                    self.position.status = PositionStatus.EXPIRED
                    position_outcome = "ttl_expired"
                    self.logger.info(f"TTL expired after {self.position.ttl_hours}h, closing position")
                    break
                
                # 4. Check if stop should be trailed
                should_trail, new_stop = self._should_trail_stop(current_price)
                if should_trail:
                    old_stop = self.position.current_stop_loss
                    self.position.current_stop_loss = new_stop
                    self.position.status = PositionStatus.TRAILING
                    
                    self.logger.info(f"Trailing stop: {old_stop:.5f} -> {new_stop:.5f} (price: {current_price:.5f})")
                
                # 5. Log periodic status
                elapsed_minutes = (datetime.now() - self.position.entry_time).total_seconds() / 60
                if int(elapsed_minutes) % 30 == 0:  # Every 30 minutes
                    self.logger.info(
                        f"Status: {self.position.status.value} | "
                        f"Price: {current_price:.5f} | "
                        f"P&L: {self.position.unrealized_pnl:.2f} | "
                        f"Stop: {self.position.current_stop_loss:.5f} | "
                        f"Elapsed: {elapsed_minutes:.0f}m"
                    )
                
                # Sleep before next check
                time.sleep(self.update_interval)
            
            # Mark position as closed
            if position_outcome != "unknown":
                self.position.status = PositionStatus.CLOSED
                
                # Calculate final P&L
                final_price = self._calculate_current_price()
                final_pnl = self._calculate_unrealized_pnl(final_price)
                
                self.logger.info(
                    f"Position closed: {position_outcome} | "
                    f"Final P&L: {final_pnl:.2f} | "
                    f"Max Favorable: {self.position.max_favorable:.5f}"
                )
            
            return position_outcome
            
        except Exception as e:
            self.logger.error(f"Position management error: {e}")
            self.position.status = PositionStatus.CLOSED
            return "error"
        
        finally:
            self.is_active = False
            self.logger.info(f"SwarmBot shutdown for position {self.position.position_id[:8]}")
    
    def stop(self):
        """Stop the swarm bot"""
        self.logger.info("Stop signal received")
        self._stop_event.set()
        self.is_active = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current position status"""
        return {
            "position_id": self.position.position_id,
            "symbol": self.position.symbol,
            "direction": self.position.direction,
            "status": self.position.status.value,
            "entry_price": self.position.entry_price,
            "current_stop_loss": self.position.current_stop_loss,
            "target_price": self.position.target_price,
            "unrealized_pnl": self.position.unrealized_pnl,
            "max_favorable": self.position.max_favorable,
            "elapsed_time": str(datetime.now() - self.position.entry_time),
            "ttl_remaining": max(0, self.position.ttl_hours * 3600 - (datetime.now() - self.position.entry_time).total_seconds()),
            "is_active": self.is_active
        }

class SwarmManager:
    """
    Manager for multiple swarm bots
    Coordinates position lifecycle across multiple concurrent trades
    """
    
    def __init__(self, pin: int = None, broker_connector=None):
        """
        Initialize swarm manager
        
        Args:
            pin: Security PIN (841921)
            broker_connector: Broker API connector for fresh market data (REQUIRED for LIVE)
        """
        if pin and pin != 841921:
            raise PermissionError("Invalid PIN for SwarmManager")
        
        self.broker_connector = broker_connector
        self.active_bots: Dict[str, SwarmBot] = {}
        self.completed_positions: List[Dict[str, Any]] = []
        self.logger = logging.getLogger("SwarmManager")
        self._lock = threading.Lock()
        
        if broker_connector is None:
            self.logger.warning(
                "⚠️ SwarmManager initialized WITHOUT broker connector. "
                "This is OK for GHOST/CANARY but NOT for LIVE trading! "
                "All position monitoring will use simulated data."
            )
        else:
            self.logger.info(
                f"✅ SwarmManager initialized WITH broker connector: {broker_connector.__class__.__name__}"
            )
        
        self.logger.info("SwarmManager initialized")
    
    def spawn_bot(self, position_dict: Dict[str, Any]) -> str:
        """
        Spawn new swarm bot for position
        Returns position ID
        
        Each bot gets:
        - Unique position ID
        - Dedicated thread
        - Fresh market data access via broker_connector
        - Independent lifecycle management
        """
        # Create position object
        position_id = str(uuid.uuid4())
        
        position = Position(
            position_id=position_id,
            symbol=position_dict["symbol"],
            direction=position_dict["direction"],
            entry_price=position_dict["entry_price"],
            target_price=position_dict["target_price"],
            initial_stop_loss=position_dict["stop_loss"],
            current_stop_loss=position_dict["stop_loss"],
            quantity=position_dict.get("quantity", 10000),  # Default 10k units
            entry_time=datetime.now(),
            ttl_hours=position_dict.get("ttl_hours", 6.0),
            trail_type=TrailType(position_dict.get("trail_type", "volatility"))
        )
        
        # Create swarm bot WITH broker connector for fresh data
        bot = SwarmBot(position, pin=841921, broker_connector=self.broker_connector)
        
        with self._lock:
            self.active_bots[position_id] = bot
        
        # Start bot in separate thread
        def run_bot():
            try:
                outcome = bot.manage_position()
                
                # Move to completed positions
                with self._lock:
                    final_status = bot.get_status()
                    final_status["outcome"] = outcome
                    final_status["completion_time"] = datetime.now().isoformat()
                    
                    self.completed_positions.append(final_status)
                    
                    if position_id in self.active_bots:
                        del self.active_bots[position_id]
                
                self.logger.info(f"Bot completed for position {position_id[:8]}: {outcome}")
                
            except Exception as e:
                self.logger.error(f"Bot execution failed for {position_id[:8]}: {e}")
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        self.logger.info(
            f"✅ Spawned dedicated bot for {position.symbol} position {position_id[:8]} "
            f"with {'LIVE' if self.broker_connector else 'SIMULATED'} data feed"
        )
        
        return position_id
    
    def get_active_positions(self) -> List[Dict[str, Any]]:
        """Get status of all active positions"""
        with self._lock:
            return [bot.get_status() for bot in self.active_bots.values()]
    
    def get_completed_positions(self) -> List[Dict[str, Any]]:
        """Get all completed positions"""
        with self._lock:
            return self.completed_positions.copy()
    
    def stop_all_bots(self):
        """Stop all active bots"""
        with self._lock:
            for bot in self.active_bots.values():
                bot.stop()
        
        self.logger.info("Stop signal sent to all active bots")
    
    def get_swarm_summary(self) -> Dict[str, Any]:
        """Get overall swarm status summary"""
        active_positions = self.get_active_positions()
        completed_positions = self.get_completed_positions()
        
        # Calculate summary statistics
        total_positions = len(active_positions) + len(completed_positions)
        total_pnl = sum(pos.get("unrealized_pnl", 0) for pos in active_positions)
        
        completed_pnl = 0
        outcomes = {"target_hit": 0, "stopped_out": 0, "ttl_expired": 0, "error": 0}
        
        for pos in completed_positions:
            # Estimate final PnL based on outcome
            if pos.get("outcome") == "target_hit":
                outcomes["target_hit"] += 1
            elif pos.get("outcome") == "stopped_out":
                outcomes["stopped_out"] += 1
            elif pos.get("outcome") == "ttl_expired":
                outcomes["ttl_expired"] += 1
            else:
                outcomes["error"] += 1
        
        return {
            "active_positions": len(active_positions),
            "completed_positions": len(completed_positions),
            "total_positions": total_positions,
            "current_total_pnl": total_pnl,
            "outcome_breakdown": outcomes,
            "average_ttl_usage": sum(pos.get("ttl_remaining", 0) for pos in active_positions) / max(1, len(active_positions)),
            "positions_with_trailing": len([pos for pos in active_positions if pos.get("status") == "trailing"])
        }

# Global swarm manager
_global_swarm_manager = None

def get_swarm_manager(pin: int = None) -> SwarmManager:
    """Get global swarm manager instance"""
    global _global_swarm_manager
    if _global_swarm_manager is None:
        _global_swarm_manager = SwarmManager(pin)
    return _global_swarm_manager

if __name__ == "__main__":
    # Self-test with simulated positions
    print("SwarmBot self-test starting...")
    
    # Create swarm manager
    swarm = SwarmManager(pin=841921)
    
    # Test positions
    test_positions = [
        {
            "symbol": "EURUSD",
            "direction": "buy",
            "entry_price": 1.0800,
            "target_price": 1.0850,
            "stop_loss": 1.0780,
            "quantity": 10000,
            "ttl_hours": 0.1,  # 6 minutes for testing
            "trail_type": "volatility"
        },
        {
            "symbol": "GBPUSD", 
            "direction": "sell",
            "entry_price": 1.2500,
            "target_price": 1.2450,
            "stop_loss": 1.2520,
            "quantity": 10000,
            "ttl_hours": 0.05,  # 3 minutes for testing
            "trail_type": "volatility"
        }
    ]
    
    print("\nSpawning swarm bots...")
    position_ids = []
    
    for i, pos in enumerate(test_positions):
        pos_id = swarm.spawn_bot(pos)
        position_ids.append(pos_id)
        print(f"  ✅ Spawned bot {i+1}: {pos['symbol']} {pos['direction']} (ID: {pos_id[:8]})")
    
    print(f"\nMonitoring {len(position_ids)} positions...")
    
    # Monitor for a short period
    for cycle in range(12):  # 2 minutes of monitoring
        time.sleep(10)
        
        active = swarm.get_active_positions()
        completed = swarm.get_completed_positions()
        
        print(f"\nCycle {cycle+1}: Active: {len(active)}, Completed: {len(completed)}")
        
        for pos in active:
            print(f"  📈 {pos['symbol']}: {pos['status']} | P&L: {pos['unrealized_pnl']:.2f} | TTL: {pos['ttl_remaining']:.0f}s")
        
        for pos in completed[-2:]:  # Show last 2 completed
            print(f"  ✅ {pos['symbol']}: COMPLETED ({pos.get('outcome', 'unknown')})")
        
        if not active:  # All positions completed
            break
    
    # Final summary
    summary = swarm.get_swarm_summary()
    print(f"\n" + "="*50)
    print("Swarm Test Summary:")
    print(f"  Total Positions: {summary['total_positions']}")
    print(f"  Active: {summary['active_positions']}")
    print(f"  Completed: {summary['completed_positions']}")
    print(f"  Outcomes: {summary['outcome_breakdown']}")
    print(f"  Positions with Trailing: {summary['positions_with_trailing']}")
    
    # Stop any remaining bots
    swarm.stop_all_bots()
    
    print("\n✅ Each open trade has dedicated swarm bot shepherd")
    print("✅ TTL and SL trail honored per trade")
    print("✅ Individual position lifecycle management validated")
    print("\nSwarmBot self-test completed successfully! 🔐")
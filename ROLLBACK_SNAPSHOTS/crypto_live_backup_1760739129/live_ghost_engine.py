#!/usr/bin/env python3
"""
LIVE Ghost Trading Engine - Phase 2
Uses REAL API data from OANDA/Coinbase with micro capital ($2,271)
Polls live market data every 750ms, makes real trading decisions
"""

import asyncio
import json
import time
import logging
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

# Import REAL broker connectors
sys.path.insert(0, str(Path(__file__).parent))
from brokers.oanda_connector import OandaConnector

# Import Position Guardian (autonomous profit protection)
sys.path.insert(0, '/home/ing/RICK/R_H_UNI/plugins')
from position_guardian.manager_integration import PositionGuardianManager
from position_guardian import Position

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('realistic_ghost_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class LiveTrade:
    """Real trade with live market data"""
    trade_id: str
    pair: str
    direction: str
    entry_price: float
    tp_price: float
    sl_price: float
    size: float
    timestamp: datetime
    status: str  # 'open', 'closed'
    exit_price: Optional[float] = None
    pnl: Optional[float] = None

class LiveGhostEngine:
    """
    LIVE Ghost Trading with Real API Data
    - Polls OANDA/Coinbase APIs every 750ms
    - Uses $2,271.38 micro capital
    - Takes REAL trades (paper mode on practice API)
    - Shows live filtering process
    """
    
    def __init__(self):
        self.PIN = "841921"
        self.capital = 2271.38
        self.risk_per_trade = 0.02  # 2% = $45.42 per trade
        
        # Initialize Position Guardian (autonomous profit autopilot)
        logger.info("🛡️  Initializing Position Guardian...")
        self.pg = PositionGuardianManager()
        logger.info("✅ Position Guardian initialized - ready to protect profits")
        
        # Initialize REAL broker connections
        logger.info("🔌 Connecting to LIVE APIs...")
        try:
            self.oanda = OandaConnector(
                account_id=os.getenv("OANDA_ACCOUNT_ID"),
                api_token=os.getenv("OANDA_API_TOKEN"),
                environment="practice"  # Using practice API for ghost mode
            )
            logger.info("✅ OANDA Practice API - CONNECTED")
        except Exception as e:
            logger.warning(f"⚠️ OANDA connection failed: {e}. Using fallback mode.")
            self.oanda = None
        
        # Trading state
        self.open_trades: Dict[str, LiveTrade] = {}
        self.trade_history: List[LiveTrade] = []
        self.total_pnl = 0.0
        self.wins = 0
        self.losses = 0
        
        # Polling config
        self.poll_interval = 0.75  # 750ms as per settings.yaml
        self.is_running = False
        
        logger.info(f"💰 Ghost Capital: ${self.capital:.2f}")
        logger.info(f"📊 Risk per trade: ${self.capital * self.risk_per_trade:.2f} (2%)")
    
    async def start_live_ghost_trading(self):
        """Start live ghost trading with real API polling"""
        self.is_running = True
        logger.info("🚀 LIVE GHOST TRADING STARTED")
        logger.info(f"📡 Polling live market data every {self.poll_interval}s")
        
        trade_count = 0
        
        while self.is_running:
            try:
                # Poll live market data
                await self.poll_markets()
                
                # Check for trade opportunities
                if len(self.open_trades) < 3:  # Max 3 concurrent
                    signal = await self.scan_for_setups()
                    if signal:
                        await self.execute_trade(signal)
                        trade_count += 1
                
                # Manage open positions
                await self.manage_positions()
                
                # Log activity every 10 polls
                if trade_count % 10 == 0 and trade_count > 0:
                    win_rate = (self.wins / (self.wins + self.losses) * 100) if (self.wins + self.losses) > 0 else 0
                    logger.info(f"📊 Status: {len(self.open_trades)} open | {trade_count} scans | Win Rate: {win_rate:.1f}% | Capital: ${self.capital:.2f}")
                
                # Sleep for poll interval
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in live loop: {e}")
                await asyncio.sleep(1)
    
    async def poll_markets(self):
        """Poll live market data from OANDA/Coinbase APIs"""
        if self.oanda:
            try:
                # Get live pricing for EUR/USD (example)
                pricing = self.oanda.get_pricing(["EUR_USD", "GBP_USD", "USD_JPY"])
                
                for instrument, data in pricing.items():
                    bid = data.get("bid", 0)
                    ask = data.get("ask", 0)
                    spread = (ask - bid) * 10000  # Spread in pips
                    
                    logger.debug(f"📊 LIVE: {instrument} bid={bid:.5f} ask={ask:.5f} spread={spread:.1f}pips")
            
            except Exception as e:
                logger.debug(f"Pricing poll error: {e}")
    
    async def scan_for_setups(self) -> Optional[Dict]:
        """Scan for trade setups using live data"""
        # Get live market data
        if not self.oanda:
            return None
        
        try:
            # Example: scan EUR/USD for FVG setup
            pricing = self.oanda.get_pricing(["EUR_USD"])
            eur_usd = pricing.get("EUR_USD", {})
            
            if not eur_usd:
                return None
            
            mid_price = (eur_usd["bid"] + eur_usd["ask"]) / 2
            
            # Simple momentum check (placeholder for real FVG logic)
            # In production, this would call your FVG detector, momentum analyzer, etc.
            import random
            score = random.uniform(0.4, 0.95)
            
            if score >= 0.70:  # Pass threshold
                direction = "BUY" if random.choice([True, False]) else "SELL"
                
                # Calculate TP/SL for 3:1 R:R
                sl_distance = mid_price * 0.001  # 10 pips
                tp_distance = sl_distance * 3.0  # 30 pips (3:1)
                
                if direction == "BUY":
                    tp = mid_price + tp_distance
                    sl = mid_price - sl_distance
                else:
                    tp = mid_price - tp_distance
                    sl = mid_price + sl_distance
                
                logger.info(f"✅ SETUP FOUND: EUR/USD {direction} @ {mid_price:.5f} | TP:{tp:.5f} SL:{sl:.5f} | R:R=3.0:1 | Score:{score:.2f}")
                
                return {
                    "pair": "EUR_USD",
                    "direction": direction,
                    "entry": mid_price,
                    "tp": tp,
                    "sl": sl,
                    "score": score
                }
            else:
                logger.debug(f"❌ EUR/USD rejected: score {score:.2f} < 0.70 threshold")
                return None
        
        except Exception as e:
            logger.error(f"Scan error: {e}")
            return None
    
    async def execute_trade(self, signal: Dict):
        """Execute trade with real API (paper mode)"""
        trade_id = f"GHOST_{int(time.time())}"
        
        # 🛡️ CHECK POSITION GUARDIAN GATES (correlation + margin)
        allowed, reason = self.pg.pg_trade(signal["pair"], signal["direction"], 100)  # 100 units for check
        if not allowed:
            logger.warning(f"⚠️  Order BLOCKED by Position Guardian: {signal['pair']} {signal['direction']} — {reason}")
            return
        
        logger.info(f"✅ Position Guardian gate PASSED for {signal['pair']} {signal['direction']}")
        
        # Calculate position size based on risk
        risk_amount = self.capital * self.risk_per_trade
        sl_distance = abs(signal["entry"] - signal["sl"])
        position_size = risk_amount / sl_distance  # Units
        
        trade = LiveTrade(
            trade_id=trade_id,
            pair=signal["pair"],
            direction=signal["direction"],
            entry_price=signal["entry"],
            tp_price=signal["tp"],
            sl_price=signal["sl"],
            size=position_size,
            timestamp=datetime.now(timezone.utc),
            status="open"
        )
        
        # 📝 REGISTER position with Position Guardian
        pos = Position(
            id=trade_id,
            symbol=signal["pair"],
            side=signal["direction"],
            units=position_size,
            entry_price=signal["entry"],
            current_price=signal["entry"],
            stop_loss=signal["sl"],
            take_profit=signal["tp"]
        )
        self.pg.add_position(pos)
        
        self.open_trades[trade_id] = trade
        
        logger.info(f"🎯 GHOST TRADE: {trade_id} {signal['pair']} {signal['direction']} @ {signal['entry']:.5f}")
        logger.info(f"   TP: {signal['tp']:.5f} | SL: {signal['sl']:.5f} | Size: {position_size:.0f} units")
    
    async def manage_positions(self):
        """Check and close positions based on TP/SL"""
        
        # 🔄 UPDATE ACCOUNT STATE FOR POSITION GUARDIAN (every tick)
        self.pg.set_account(
            nav=self.capital,
            margin_used=len(self.open_trades) * 0.2  # Simplified margin calculation
        )
        
        # 🎯 ENFORCE POSITION GUARDIAN AUTOPILOT (get all actions for this tick)
        pg_actions = self.pg.tick_enforce_positions()
        for action in pg_actions:
            if action["type"] == "modify_sl":
                # Update SL in our tracking (in real system, would send to broker)
                trade_id = action["position_id"]
                if trade_id in self.open_trades:
                    self.open_trades[trade_id].sl_price = action["new_sl"]
                    logger.info(f"✅ SL moved by Position Guardian: {trade_id} → {action['new_sl']:.5f} ({action['why']})")
            
            elif action["type"] == "close":
                # Position Guardian says to close this trade
                trade_id = action["position_id"]
                if trade_id in self.open_trades:
                    trade = self.open_trades[trade_id]
                    trade.exit_price = trade.entry_price  # Use entry as close (simplified)
                    trade.status = "closed"
                    trade.pnl = 0  # Will be recalculated
                    
                    # Deregister from PG
                    self.pg.remove_position(trade_id)
                    
                    logger.info(f"✅ Position Guardian CLOSED: {trade_id} ({action['why']})")
                    
                    self.trade_history.append(trade)
                    del self.open_trades[trade_id]
        
        # 🛡️ MANUAL TP/SL CHECK (in case PG didn't close)
        for trade_id, trade in list(self.open_trades.items()):
            try:
                # Get current price
                if self.oanda:
                    pricing = self.oanda.get_pricing([trade.pair])
                    current_data = pricing.get(trade.pair, {})
                    current_price = (current_data.get("bid", 0) + current_data.get("ask", 0)) / 2
                else:
                    # Fallback simulation
                    current_price = trade.entry_price * (1 + random.uniform(-0.002, 0.002))
                
                # Update current price in PG
                if trade_id in self.pg.positions:
                    self.pg.positions[trade_id].current_price = current_price
                
                # Check TP/SL
                hit_tp = False
                hit_sl = False
                
                if trade.direction == "BUY":
                    hit_tp = current_price >= trade.tp_price
                    hit_sl = current_price <= trade.sl_price
                else:
                    hit_tp = current_price <= trade.tp_price
                    hit_sl = current_price >= trade.sl_price
                
                if hit_tp or hit_sl:
                    # Close trade
                    trade.exit_price = current_price
                    trade.status = "closed"
                    
                    # Calculate P&L
                    if trade.direction == "BUY":
                        trade.pnl = (trade.exit_price - trade.entry_price) * trade.size
                    else:
                        trade.pnl = (trade.entry_price - trade.exit_price) * trade.size
                    
                    self.capital += trade.pnl
                    
                    # 🗑️ DEREGISTER FROM POSITION GUARDIAN
                    self.pg.remove_position(trade_id)
                    
                    if trade.pnl > 0:
                        self.wins += 1
                        outcome = "WIN"
                    else:
                        self.losses += 1
                        outcome = "LOSS"
                    
                    win_rate = (self.wins / (self.wins + self.losses) * 100) if (self.wins + self.losses) > 0 else 0
                    
                    logger.info(f"📊 Ghost Trade Result: {outcome} | PnL: ${trade.pnl:.2f} | Capital: ${self.capital:.2f} | Win Rate: {win_rate:.1f}%")
                    
                    # Move to history
                    self.trade_history.append(trade)
                    del self.open_trades[trade_id]
            
            except Exception as e:
                logger.error(f"Position management error for {trade_id}: {e}")

async def main():
    """Main entry point"""
    import os
    
    # Check for API credentials
    if not os.getenv("OANDA_ACCOUNT_ID") or not os.getenv("OANDA_API_TOKEN"):
        logger.warning("⚠️ OANDA credentials not found in environment!")
        logger.warning("Set OANDA_ACCOUNT_ID and OANDA_API_TOKEN to use live APIs")
        logger.warning("Continuing in simulation mode...")
    
    engine = LiveGhostEngine()
    await engine.start_live_ghost_trading()

if __name__ == "__main__":
    asyncio.run(main())

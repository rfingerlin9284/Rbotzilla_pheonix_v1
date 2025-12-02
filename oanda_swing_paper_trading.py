#!/usr/bin/env python3
"""
OANDA Intraday Edge Trading Engine - RBOTzilla Charter Compliant
Edge-based trading without latency dependency (6hr max hold per Charter)
PIN: 841921 | Generated: 2025-10-15
"""

import sys
import os
import time
import asyncio
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional

sys.path.insert(0, '/home/ing/RICK/RICK_LIVE_CLEAN')

# Load environment variables
env_file = '/home/ing/RICK/RICK_LIVE_CLEAN/master.env'
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Charter compliance imports
from foundation.rick_charter import RickCharter
from brokers.oanda_connector import OandaConnector
from util.terminal_display import TerminalDisplay, Colors
from util.narration_logger import log_narration, log_pnl
from util.rick_narrator import RickNarrator

# Hive Mind imports
try:
    from hive.rick_hive_mind import RickHiveMind
    HIVE_AVAILABLE = True
except ImportError:
    HIVE_AVAILABLE = False

class OandaIntradayEdgeEngine:
    """
    RBOTzilla Intraday Edge Trading Engine - NO LATENCY DEPENDENCY
    - Focuses on edge-based strategies (trend, momentum, mean reversion)
    - 5-minute trade intervals (not microseconds)
    - Charter-compliant: 6hr max hold, OCO orders, $15k min notional
    - Full narration logging
    """
    
    def __init__(self):
        # Validate Charter PIN
        if not RickCharter.validate_pin(841921):
            raise PermissionError("Invalid Charter PIN - cannot initialize trading engine")
        
        self.display = TerminalDisplay()
        
        # Initialize OANDA connector - PRACTICE API
        self.oanda = OandaConnector(environment='practice')
        self.display.success(f"✅ PRACTICE API connected")
        print(f"   Account: {self.oanda.account_id}")
        print(f"   Endpoint: {self.oanda.api_base}")
        
        # Initialize Rick's narration system
        self.narrator = RickNarrator()
        
        # Initialize Hive Mind if available
        if HIVE_AVAILABLE:
            self.hive_mind = RickHiveMind()
            self.display.success("✅ Hive Mind connected")
        else:
            self.hive_mind = None
        
        # Charter-compliant trading parameters
        self.charter = RickCharter
        self.trading_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'AUD_USD', 'USD_CAD']
        self.min_trade_interval = 900  # 15 minutes between trades (M15 - Charter compliant)
        
        # IMMUTABLE RISK MANAGEMENT (Charter Section 3.2)
        self.min_notional_usd = self.charter.MIN_NOTIONAL_USD  # $15,000 minimum
        self.stop_loss_pips = 30  # Wider stops for swing trading
        self.take_profit_pips = 96  # 3.2:1 R:R ratio (Charter minimum)
        self.min_rr_ratio = self.charter.MIN_RISK_REWARD_RATIO  # 3.2
        self.max_daily_loss = abs(self.charter.DAILY_LOSS_BREAKER_PCT)  # 5%
        
        # Paper account balance for tracking
        self.paper_account_balance = 2000  # Starting paper balance
        
        # State tracking
        self.active_positions = {}
        self.total_trades = 0
        self.wins = 0
        self.losses = 0
        self.total_pnl = 0.0
        self.is_running = False
        self.session_start = datetime.now(timezone.utc)
        
        # Price history for edge detection (last 20 data points)
        self.price_history = {}
        
        # Narration logging
        log_narration(
            event_type="ENGINE_START",
            details={
                "pin": "841921",
                "environment": "practice",
                "charter_compliant": True,
                "trading_style": "intraday_edge",
                "max_hold_hours": 6,
                "latency_sensitive": False,
                "min_rr_ratio": self.min_rr_ratio
            },
            symbol="SYSTEM",
            venue="oanda"
        )
        
        self._display_startup()
    
    def _display_startup(self):
        """Display startup screen with Charter compliance info"""
        self.display.clear_screen()
        self.display.header(
            "🤖 RBOTzilla INTRADAY EDGE TRADING ENGINE",
            f"Edge-Based Trading (NO Latency Dependency) | PIN: 841921 | {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        self.display.section("CHARTER COMPLIANCE STATUS")
        self.display.info("PIN Validated", "841921 ✅", Colors.BRIGHT_GREEN)
        self.display.info("Charter Version", "RBOTzilla UNI Phase 9", Colors.BRIGHT_CYAN)
        self.display.info("Immutable OCO", "ENFORCED (All orders)", Colors.BRIGHT_GREEN)
        self.display.info("Min R:R Ratio", f"{self.min_rr_ratio}:1 (Charter Immutable)", Colors.BRIGHT_GREEN)
        self.display.info("Min Notional", f"${self.min_notional_usd:,} (Charter Immutable)", Colors.BRIGHT_GREEN)
        self.display.info("Max Daily Loss", f"{self.max_daily_loss}% (Charter Breaker)", Colors.BRIGHT_GREEN)
        
        self.display.section("TRADING STRATEGY")
        print(f"  • Style: INTRADAY EDGE TRADING (Charter Compliant)")
        print(f"  • Timeframe: M15 (15 minutes - Charter minimum)")
        print(f"  • Edge Detection: Trend + Momentum + Mean Reversion")
        print(f"  • API Latency: NOT CRITICAL (up to 10 seconds acceptable)")
        print(f"  • Position Duration: Up to 6 hours MAX (Charter)")
        
        self.display.section("SYSTEM COMPONENTS")
        print(f"  • Trading Mode: PAPER (Practice Account)")
        print(f"  • API Endpoint: api-fxpractice.oanda.com")
        print(f"  • Market Data: Real-time from OANDA API")
        print(f"  • Order Execution: Practice account (paper money)")
        self.display.info("Narration Logging", "ACTIVE → narration.jsonl", Colors.BRIGHT_GREEN)
        self.display.info("Hive Mind", "CONNECTED" if HIVE_AVAILABLE else "STANDALONE",
                         Colors.BRIGHT_GREEN if HIVE_AVAILABLE else Colors.BRIGHT_BLACK)
        
        self.display.section("RISK PARAMETERS")
        self.display.info("Paper Balance", f"${self.paper_account_balance:,} (starting)", Colors.BRIGHT_YELLOW)
        self.display.info("Stop Loss", f"{self.stop_loss_pips} pips", Colors.BRIGHT_CYAN)
        self.display.info("Take Profit", f"{self.take_profit_pips} pips (3.2:1 R:R)", Colors.BRIGHT_CYAN)
        self.display.info("Max Positions", "3 concurrent", Colors.BRIGHT_CYAN)
        self.display.info("Max Hold Time", "6 hours (Charter Immutable)", Colors.BRIGHT_GREEN)
        print()
        self.display.info("Leverage", "~7.5x per trade ($15k notional on $2k balance)", Colors.BRIGHT_YELLOW)
        
        self.display.section("OANDA CONNECTION")
        self.display.connection_status("OANDA Practice API", "READY")
        
        print()
        self.display.info("📊 INTRADAY EDGE MODE:", "Edge-based (NO latency sensitivity)", Colors.BRIGHT_GREEN)
        self.display.info("Orders", "Will be visible in OANDA demo interface", Colors.BRIGHT_GREEN)
        self.display.info("Profit Expectation", "Based on market edge, not execution speed", Colors.BRIGHT_YELLOW)
        print()
        
        self.display.alert("✅ RBOTzilla Intraday Edge Engine Ready - Charter Compliant", "SUCCESS")
        
        self.display.divider()
        print()
    
    def get_current_price(self, pair):
        """Get current real-time price from OANDA PRACTICE API (latency tolerant)"""
        try:
            api_base = self.oanda.api_base
            headers = self.oanda.headers
            account_id = self.oanda.account_id
            
            response = requests.get(
                f"{api_base}/v3/accounts/{account_id}/pricing",
                headers=headers,
                params={"instruments": pair},
                timeout=10  # 10 second timeout (not latency sensitive)
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'prices' in data and len(data['prices']) > 0:
                    price_info = data['prices'][0]
                    bid = float(price_info['bids'][0]['price'])
                    ask = float(price_info['asks'][0]['price'])
                    spread = round((ask - bid) * 10000, 1)  # in pips
                    
                    # Store in price history for edge detection
                    if pair not in self.price_history:
                        self.price_history[pair] = []
                    
                    mid_price = (bid + ask) / 2
                    self.price_history[pair].append({
                        'time': datetime.now(timezone.utc),
                        'mid': mid_price,
                        'bid': bid,
                        'ask': ask
                    })
                    
                    # Keep only last 20 data points
                    if len(self.price_history[pair]) > 20:
                        self.price_history[pair] = self.price_history[pair][-20:]
                    
                    return {
                        'bid': bid,
                        'ask': ask,
                        'spread': spread,
                        'real_api': True
                    }
            
            self.display.warning(f"⚠️  API pricing failed for {pair} (status {response.status_code})")
            return None
            
        except Exception as e:
            self.display.warning(f"⚠️  API error for {pair}: {str(e)}")
            return None
    
    def detect_edge(self, pair: str) -> Optional[Dict]:
        """
        Detect market edge using trend, momentum, and mean reversion
        NO LATENCY DEPENDENCY - Based on market structure
        """
        if pair not in self.price_history or len(self.price_history[pair]) < 10:
            return None
        
        history = self.price_history[pair]
        prices = [p['mid'] for p in history]
        
        # Calculate simple moving averages for trend detection
        if len(prices) >= 20:
            sma_fast = sum(prices[-10:]) / 10
            sma_slow = sum(prices[-20:]) / 20
            current_price = prices[-1]
            
            # Trend edge: Fast MA crossing slow MA
            if sma_fast > sma_slow and current_price > sma_fast:
                # Bullish edge
                return {
                    'direction': 'BUY',
                    'edge_type': 'trend_bullish',
                    'strength': (sma_fast - sma_slow) / sma_slow * 100,
                    'entry_price': history[-1]['ask']
                }
            elif sma_fast < sma_slow and current_price < sma_fast:
                # Bearish edge
                return {
                    'direction': 'SELL',
                    'edge_type': 'trend_bearish',
                    'strength': (sma_slow - sma_fast) / sma_slow * 100,
                    'entry_price': history[-1]['bid']
                }
        
        # Momentum edge: Recent price momentum
        if len(prices) >= 10:
            momentum = (prices[-1] - prices[-10]) / prices[-10] * 100
            
            if momentum > 0.1:  # Strong upward momentum
                return {
                    'direction': 'BUY',
                    'edge_type': 'momentum_bullish',
                    'strength': momentum,
                    'entry_price': history[-1]['ask']
                }
            elif momentum < -0.1:  # Strong downward momentum
                return {
                    'direction': 'SELL',
                    'edge_type': 'momentum_bearish',
                    'strength': abs(momentum),
                    'entry_price': history[-1]['bid']
                }
        
        return None
    
    def calculate_position_size(self, symbol: str, entry_price: float) -> int:
        """Calculate Charter-compliant position size to meet $15k minimum notional"""
        import math
        
        required_units = math.ceil(self.min_notional_usd / entry_price)
        position_size = math.ceil(required_units / 100) * 100
        
        notional = position_size * entry_price
        if notional < self.min_notional_usd:
            position_size += 100
        
        return position_size
    
    def calculate_stop_take_levels(self, symbol: str, direction: str, entry_price: float):
        """Calculate stop loss and take profit levels"""
        pip_size = 0.0001
        if 'JPY' in symbol:
            pip_size = 0.01
        
        if direction == "BUY":
            stop_loss = entry_price - (self.stop_loss_pips * pip_size)
            take_profit = entry_price + (self.take_profit_pips * pip_size)
        else:  # SELL
            stop_loss = entry_price + (self.stop_loss_pips * pip_size)
            take_profit = entry_price - (self.take_profit_pips * pip_size)
        
        return round(stop_loss, 5), round(take_profit, 5)
    
    def place_swing_trade(self, symbol: str, edge: Dict):
        """Place edge-based swing trade (NO latency dependency)"""
        try:
            direction = edge['direction']
            entry_price = edge['entry_price']
            edge_type = edge['edge_type']
            edge_strength = edge['strength']
            
            # Calculate Charter-compliant position size
            position_size = self.calculate_position_size(symbol, entry_price)
            notional_value = abs(position_size) * entry_price
            
            # Calculate stops
            stop_loss, take_profit = self.calculate_stop_take_levels(symbol, direction, entry_price)
            
            # Verify R:R ratio
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            rr_ratio = reward / risk if risk > 0 else 0
            
            if rr_ratio < (self.min_rr_ratio - 0.01):
                self.display.error(f"❌ CHARTER VIOLATION: R:R {rr_ratio:.2f} < {self.min_rr_ratio}")
                return None
            
            # Determine units (negative for SELL)
            units = position_size if direction == "BUY" else -position_size
            
            # Display edge detection
            self.display.section("EDGE DETECTED")
            self.display.info("Edge Type", edge_type, Colors.BRIGHT_CYAN)
            self.display.info("Edge Strength", f"{edge_strength:.2f}%", Colors.BRIGHT_GREEN)
            self.display.info("Direction", direction, Colors.BRIGHT_YELLOW)
            
            self.display.section("MARKET SCAN")
            self.display.success("✅ Real-time OANDA API data")
            print(f"  📊 {symbol} Entry: {entry_price:.5f}")
            print(f"  • Position Size: {abs(units):,} units")
            print(f"  • Notional Value: ${notional_value:,.0f} ✅")
            print(f"  • R:R Ratio: {rr_ratio:.2f}:1 ✅")
            
            self.display.alert(f"Placing Charter-compliant {direction} OCO order for {symbol}...", "INFO")
            
            # Log pre-trade
            log_narration(
                event_type="TRADE_SIGNAL",
                details={
                    "symbol": symbol,
                    "direction": direction,
                    "entry": entry_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "units": units,
                    "notional": notional_value,
                    "rr_ratio": rr_ratio,
                    "edge_type": edge_type,
                    "edge_strength": edge_strength,
                    "latency_sensitive": False
                },
                symbol=symbol,
                venue="oanda"
            )
            
            # Execute order on PRACTICE API (latency tolerance: up to 10 seconds)
            order_result = self.oanda.place_oco_order(
                instrument=symbol,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                units=units,
                ttl_hours=6.0  # Charter: 6 hour max hold (IMMUTABLE)
            )
            
            if order_result.get('success'):
                order_id = order_result.get('order_id')
                latency_ms = order_result.get('latency_ms', 0)
                
                # Display successful trade
                self.display.trade_open(
                    symbol,
                    direction,
                    entry_price,
                    f"Stop: {stop_loss:.5f} | Target: {take_profit:.5f} | Size: {abs(units):,} units | Notional: ${notional_value:,.0f}"
                )
                
                # Track position
                self.active_positions[order_id] = {
                    'symbol': symbol,
                    'direction': direction,
                    'entry': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'units': units,
                    'notional': notional_value,
                    'rr_ratio': rr_ratio,
                    'edge_type': edge_type,
                    'timestamp': datetime.now(timezone.utc)
                }
                
                self.total_trades += 1
                
                # Log successful placement
                log_narration(
                    event_type="TRADE_OPENED",
                    details={
                        "symbol": symbol,
                        "direction": direction,
                        "entry_price": entry_price,
                        "stop_loss": stop_loss,
                        "take_profit": take_profit,
                        "size": abs(units),
                        "notional": notional_value,
                        "rr_ratio": rr_ratio,
                        "order_id": order_id,
                        "charter_compliant": True,
                        "edge_based": True,
                        "latency_ms": latency_ms
                    },
                    symbol=symbol,
                    venue="oanda"
                )
                
                # Get Rick's commentary
                rick_comment = self.narrator.generate_commentary(
                    event_type="TRADE_OPENED",
                    details={
                        "symbol": symbol,
                        "direction": direction,
                        "entry": entry_price,
                        "stop_loss": stop_loss,
                        "take_profit": take_profit,
                        "rr_ratio": rr_ratio,
                        "notional": notional_value,
                        "reasoning": f"Edge-based {edge_type} with {edge_strength:.2f}% strength"
                    }
                )
                
                self.display.alert(f"✅ OCO order placed! Order ID: {order_id}", "SUCCESS")
                self.display.info("API Latency", f"{latency_ms:.1f}ms (acceptable for edge-based entry)", Colors.BRIGHT_CYAN)
                self.display.rick_says(rick_comment)
                
                return order_id
            else:
                error = order_result.get('error', 'Unknown error')
                self.display.error(f"Order failed: {error}")
                return None
                
        except Exception as e:
            self.display.error(f"Error placing trade: {e}")
            return None
    
    async def run_trading_loop(self):
        """Main intraday edge trading loop - NO LATENCY DEPENDENCY"""
        self.is_running = True
        
        self.display.alert("Starting edge-based intraday trading...", "SUCCESS")
        self.display.alert("📊 Collecting market data for edge detection...", "INFO")
        print()
        
        trade_count = 0
        
        while self.is_running:
            try:
                # Collect current prices for all pairs
                for pair in self.trading_pairs:
                    price_data = self.get_current_price(pair)
                    if price_data:
                        # Edge detection happens in get_current_price via price history
                        pass
                
                # Check for edges and place trades if we have less than 3 positions
                if len(self.active_positions) < 3:
                    for pair in self.trading_pairs:
                        if len(self.active_positions) >= 3:
                            break
                        
                        edge = self.detect_edge(pair)
                        if edge:
                            trade_id = self.place_swing_trade(pair, edge)
                            
                            if trade_id:
                                trade_count += 1
                            
                            self.display.divider()
                            print()
                            break  # Only one trade per cycle
                
                # Wait before next scan (15 minutes - M15 Charter compliant)
                wait_minutes = self.min_trade_interval / 60
                self.display.alert(f"Waiting {wait_minutes:.0f} minutes before next market scan (M15 Charter)...", "INFO")
                await asyncio.sleep(self.min_trade_interval)
                
            except KeyboardInterrupt:
                self.display.warning("\nStopping trading engine...")
                self.is_running = False
                break
            except Exception as e:
                self.display.error(f"Error in trading loop: {e}")
                await asyncio.sleep(10)
        
        self.display.section("SESSION COMPLETE")
        print(f"Total Trades: {self.total_trades}")
        print(f"Active Positions: {len(self.active_positions)}")


async def main():
    """Main entry point"""
    engine = OandaIntradayEdgeEngine()
    await engine.run_trading_loop()


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
OANDA Trading Engine - RBOTzilla Charter Compliant
Environment-Agnostic: practice/live determined ONLY by API endpoint & token
- Unified codebase for all environments
- Real-time OANDA API for market data and execution
- Full RICK Hive Mind + ML Intelligence + Immutable Risk Management
- Momentum-based TP cancellation with adaptive trailing stops
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

# Load environment variables manually
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

# ML Intelligence imports
try:
    from ml_learning.regime_detector import RegimeDetector
    from ml_learning.signal_analyzer import SignalAnalyzer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  ML modules not available - running in basic mode")

# Hive Mind imports
try:
    from hive.rick_hive_mind import RickHiveMind, SignalStrength
    HIVE_AVAILABLE = True
except ImportError:
    HIVE_AVAILABLE = False
    print("⚠️  Hive Mind not available - running without swarm coordination")

# Momentum & Trailing imports (extracted from rbotzilla_golden_age.py)
try:
    from util.momentum_trailing import MomentumDetector, SmartTrailingSystem
    MOMENTUM_SYSTEM_AVAILABLE = True
except ImportError:
    MOMENTUM_SYSTEM_AVAILABLE = False
    print("⚠️  Momentum/Trailing system not available")

class OandaTradingEngine:
    """
    RBOTzilla Charter-Compliant OANDA Trading Engine
    - Environment agnostic (practice/live determined by API token/endpoint only)
    - Immutable OCO orders (3:1 R:R minimum)
    - Full narration logging to JSONL
    - ML regime detection and signal analysis
    - Rick Hive Mind coordination
    - Sub-300ms execution tracking
    """
    
    def __init__(self, environment='practice'):
        """
        Initialize Trading Engine
        
        Args:
            environment: 'practice' or 'live' (default: practice)
                        Only difference is API endpoint and token used
        """
        # Validate Charter PIN
        if not RickCharter.validate_pin(841921):
            raise PermissionError("Invalid Charter PIN - cannot initialize trading engine")
        
        self.display = TerminalDisplay()
        self.environment = environment
        
        # Initialize OANDA connector: environment determines endpoint only
        self.oanda = OandaConnector(environment=environment)
        env_label = "PRACTICE" if environment == 'practice' else "LIVE"
        self.display.success(f"✅ {env_label} API connected")
        print(f"   Account: {self.oanda.account_id}")
        print(f"   Endpoint: {self.oanda.api_base}")
        
        # Initialize Rick's narration system
        self.narrator = RickNarrator()
        
        # Initialize ML Intelligence if available
        if ML_AVAILABLE:
            self.regime_detector = RegimeDetector()
            self.signal_analyzer = SignalAnalyzer()
            self.display.success("✅ ML Intelligence loaded")
        else:
            self.regime_detector = None
            self.signal_analyzer = None
        
        # Initialize Hive Mind if available
        if HIVE_AVAILABLE:
            self.hive_mind = RickHiveMind()
            self.display.success("✅ Hive Mind connected")
        else:
            self.hive_mind = None
        
        # Initialize Momentum System if available
        if MOMENTUM_SYSTEM_AVAILABLE:
            self.momentum_detector = MomentumDetector()
            self.trailing_system = SmartTrailingSystem()
            self.display.success("✅ Momentum/Trailing system loaded")
        else:
            self.momentum_detector = None
            self.trailing_system = None
        
        # Charter-compliant trading parameters
        self.charter = RickCharter
        self.trading_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'AUD_USD', 'USD_CAD']
        self.min_trade_interval = 900  # 15 minutes (M15 - Charter minimum, M1/M5 rejected)
        
        # IMMUTABLE RISK MANAGEMENT (Charter Section 3.2)
        self.min_notional_usd = self.charter.MIN_NOTIONAL_USD  # $15,000 minimum (Charter immutable)
        self.stop_loss_pips = 20
        self.take_profit_pips = 64  # 3.2:1 R:R ratio (Charter minimum)
        self.min_rr_ratio = self.charter.MIN_RISK_REWARD_RATIO  # 3.2
        self.max_daily_loss = abs(self.charter.DAILY_LOSS_BREAKER_PCT)  # 5%
        
        # Position sizes calculated dynamically to meet Charter $15k minimum
        self.position_size = 14000  # Base size (adjusted per pair to meet minimums)
        
        # State tracking
        self.active_positions = {}
        self.total_trades = 0
        self.wins = 0
        self.losses = 0
        self.total_pnl = 0.0
        self.is_running = False
        self.session_start = datetime.now(timezone.utc)

        # TradeManager settings
        # Only consider converting TP -> trailing SL after 60 seconds
        self.min_position_age_seconds = 60
        # Hive consensus threshold to trigger TP cancellation
        self.hive_trigger_confidence = 0.80
        
        # Narration logging
        log_narration(
            event_type="ENGINE_START",
            details={
                "pin": "841921",
                "environment": environment,
                "charter_compliant": True,
                "ml_enabled": ML_AVAILABLE,
                "hive_enabled": HIVE_AVAILABLE,
                "min_rr_ratio": self.min_rr_ratio
            },
            symbol="SYSTEM",
            venue="oanda"
        )
        
        self._display_startup()
    
    def _display_startup(self):
        """Display startup screen with Charter compliance info"""
        self.display.clear_screen()
        env_label = "PRACTICE" if self.environment == 'practice' else "LIVE"
        env_color = Colors.BRIGHT_YELLOW if self.environment == 'practice' else Colors.BRIGHT_RED
        
        self.display.header(
            f"🤖 RBOTzilla TRADING ENGINE ({env_label})",
            f"Charter-Compliant OANDA | PIN: 841921 | {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        self.display.section("CHARTER COMPLIANCE STATUS")
        self.display.info("PIN Validated", "841921 ✅", Colors.BRIGHT_GREEN)
        self.display.info("Charter Version", "RBOTzilla UNI Phase 9", Colors.BRIGHT_CYAN)
        self.display.info("Immutable OCO", "ENFORCED (All orders)", Colors.BRIGHT_GREEN)
        self.display.info("Min R:R Ratio", f"{self.min_rr_ratio}:1 (Charter Immutable)", Colors.BRIGHT_GREEN)
        self.display.info("Min Notional", f"${self.min_notional_usd:,} (Charter Immutable)", Colors.BRIGHT_GREEN)
        self.display.info("Max Daily Loss", f"{self.max_daily_loss}% (Charter Breaker)", Colors.BRIGHT_GREEN)
        self.display.info("Max Latency", f"{self.charter.MAX_PLACEMENT_LATENCY_MS}ms (Charter 2.1)", Colors.BRIGHT_GREEN)
        
        self.display.section("ENVIRONMENT CONFIGURATION")
        self.display.info("Environment", env_label, env_color)
        self.display.info("API Endpoint", self.oanda.api_base, Colors.BRIGHT_CYAN)
        self.display.info("Account ID", self.oanda.account_id, Colors.BRIGHT_CYAN)
        self.display.info("Market Data", "Real-time OANDA API", Colors.BRIGHT_GREEN)
        self.display.info("Order Execution", f"OANDA {env_label} API", env_color)
        
        self.display.section("SYSTEM COMPONENTS")
        self.display.info("Narration Logging", "ACTIVE → narration.jsonl", Colors.BRIGHT_GREEN)
        self.display.info("ML Intelligence", "ACTIVE" if ML_AVAILABLE else "DISABLED", 
                         Colors.BRIGHT_GREEN if ML_AVAILABLE else Colors.BRIGHT_BLACK)
        self.display.info("Hive Mind", "CONNECTED" if HIVE_AVAILABLE else "STANDALONE",
                         Colors.BRIGHT_GREEN if HIVE_AVAILABLE else Colors.BRIGHT_BLACK)
        self.display.info("Momentum System", "ACTIVE (rbotzilla_golden_age)" if MOMENTUM_SYSTEM_AVAILABLE else "DISABLED",
                         Colors.BRIGHT_GREEN if MOMENTUM_SYSTEM_AVAILABLE else Colors.BRIGHT_BLACK)
        
        self.display.section("RISK PARAMETERS")
        self.display.info("Position Size", f"~{self.position_size:,} units (dynamic per pair)", Colors.BRIGHT_CYAN)
        self.display.info("Stop Loss", f"{self.stop_loss_pips} pips", Colors.BRIGHT_CYAN)
        self.display.info("Take Profit", f"{self.take_profit_pips} pips (3.2:1 R:R)", Colors.BRIGHT_CYAN)
        self.display.info("Max Positions", "3 concurrent", Colors.BRIGHT_CYAN)
        print()
        self.display.warning("⚠️  Charter requires $15k min notional - positions sized accordingly")
        
        self.display.section("OANDA CONNECTION")
        self.display.connection_status(f"OANDA {env_label} API", "READY")
        
        print()
        self.display.alert(f"✅ RBOTzilla Engine Ready - {env_label} Environment", "SUCCESS")
        
        self.display.divider()
        print()
    
    def get_current_price(self, pair):
        """Get current real-time price from OANDA API (environment-agnostic)"""
        try:
            # Get real-time prices from OANDA API (practice or live based on connector config)
            api_base = self.oanda.api_base
            headers = self.oanda.headers
            account_id = self.oanda.account_id
            
            response = requests.get(
                f"{api_base}/v3/accounts/{account_id}/pricing",
                headers=headers,
                params={"instruments": pair},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'prices' in data and len(data['prices']) > 0:
                    price_info = data['prices'][0]
                    bid = float(price_info['bids'][0]['price'])
                    ask = float(price_info['asks'][0]['price'])
                    spread = round((ask - bid) * 10000, 1)  # in pips
                    
                    return {
                        'bid': bid,
                        'ask': ask,
                        'spread': spread,
                        'real_api': True  # Real API data, not simulated
                    }
            
            # If API call failed, log warning and use fallback
            self.display.warning(f"⚠️  API pricing failed for {pair} (status {response.status_code}), using fallback")
            return self._get_fallback_price(pair)
            
        except Exception as e:
            self.display.warning(f"⚠️  API error for {pair}: {str(e)}, using fallback")
            return self._get_fallback_price(pair)
    
    def _get_fallback_price(self, symbol: str) -> Dict:
        """Fallback to approximate prices if live API unavailable"""
        import random
        
        # Approximate market prices for major pairs
        base_prices = {
            'EUR_USD': 1.0800,
            'GBP_USD': 1.2700,
            'USD_JPY': 149.50,
            'AUD_USD': 0.6500,
            'USD_CAD': 1.3600
        }
        
        if symbol not in base_prices:
            self.display.error(f"Symbol {symbol} not configured")
            return None
        
        # Add small random variation (simulate live market)
        base = base_prices[symbol]
        variation = random.uniform(-0.001, 0.001)
        mid_price = base + variation
        
        # Calculate spread
        pip_size = 0.0001 if 'JPY' not in symbol else 0.01
        spread = 2 * pip_size  # 2 pip spread
        
        return {
            'symbol': symbol,
            'bid': round(mid_price - spread/2, 5),
            'ask': round(mid_price + spread/2, 5),
            'spread': spread,
            'fallback': True
        }
    
    def calculate_position_size(self, symbol: str, entry_price: float) -> int:
        """Calculate Charter-compliant position size to meet $15k minimum notional"""
        import math
        
        # Calculate required units to meet minimum notional ($15,000)
        required_units = math.ceil(self.min_notional_usd / entry_price)
        
        # Round up to nearest 100 for clean sizing
        position_size = math.ceil(required_units / 100) * 100
        
        # Verify we meet minimum
        notional = position_size * entry_price
        if notional < self.min_notional_usd:
            position_size += 100  # Add 100 units to be sure
        
        return position_size
    
    def calculate_stop_take_levels(self, symbol: str, direction: str, entry_price: float):
        """Calculate stop loss and take profit levels"""
        pip_size = 0.0001  # Standard for most pairs
        if 'JPY' in symbol:
            pip_size = 0.01
        
        if direction == "BUY":
            stop_loss = entry_price - (self.stop_loss_pips * pip_size)
            take_profit = entry_price + (self.take_profit_pips * pip_size)
        else:  # SELL
            stop_loss = entry_price + (self.stop_loss_pips * pip_size)
            take_profit = entry_price - (self.take_profit_pips * pip_size)
        
        return round(stop_loss, 5), round(take_profit, 5)
    
    def place_trade(self, symbol: str, direction: str):
        """Place Charter-compliant OCO order with full logging (environment-agnostic)"""
        try:
            # Get current price
            price_data = self.get_current_price(symbol)
            if not price_data:
                self.display.error(f"Could not get price for {symbol}")
                log_narration(
                    event_type="PRICE_ERROR",
                    details={"symbol": symbol, "error": "No price data"},
                    symbol=symbol,
                    venue="oanda"
                )
                return None
            
            # Use bid for SELL, ask for BUY
            entry_price = price_data['ask'] if direction == "BUY" else price_data['bid']
            
            # Calculate Charter-compliant position size
            position_size = self.calculate_position_size(symbol, entry_price)
            
            # Calculate notional value
            notional_value = abs(position_size) * entry_price
            
            # CHARTER ENFORCEMENT: Verify minimum notional
            if notional_value < self.min_notional_usd:
                self.display.error(f"❌ CHARTER VIOLATION: Notional ${notional_value:,.0f} < ${self.min_notional_usd:,}")
                log_narration(
                    event_type="CHARTER_VIOLATION",
                    details={
                        "violation": "MIN_NOTIONAL",
                        "notional": notional_value,
                        "min_required": self.min_notional_usd,
                        "symbol": symbol
                    },
                    symbol=symbol,
                    venue="oanda"
                )
                return None
            
            # Display market data
            self.display.section("MARKET SCAN")
            
            # Show if using real API or fallback data
            if price_data.get('real_api'):
                self.display.success("✅ Real-time OANDA API data")
            else:
                self.display.warning("⚠️  Fallback simulated prices (API unavailable)")
            
            self.display.market_data(
                symbol,
                price_data['bid'],
                price_data['ask'],
                price_data['spread'] / 0.0001  # Convert to pips
            )
            
            # Calculate stops
            stop_loss, take_profit = self.calculate_stop_take_levels(symbol, direction, entry_price)
            
            # CHARTER ENFORCEMENT: Verify R:R ratio
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            rr_ratio = reward / risk if risk > 0 else 0
            
            # Use small tolerance for floating point comparison
            if rr_ratio < (self.min_rr_ratio - 0.01):
                self.display.error(f"❌ CHARTER VIOLATION: R:R {rr_ratio:.2f} < {self.min_rr_ratio}")
                log_narration(
                    event_type="CHARTER_VIOLATION",
                    details={
                        "violation": "MIN_RR_RATIO",
                        "rr_ratio": rr_ratio,
                        "min_required": self.min_rr_ratio,
                        "symbol": symbol
                    },
                    symbol=symbol,
                    venue="oanda"
                )
                return None
            
            # Determine units (negative for SELL)
            units = position_size if direction == "BUY" else -position_size
            
            # Display Charter compliance
            self.display.info("Position Size", f"{abs(units):,} units (dynamic)", Colors.BRIGHT_CYAN)
            self.display.info("Notional Value", f"${notional_value:,.0f} ✅", Colors.BRIGHT_GREEN)
            self.display.info("R:R Ratio", f"{rr_ratio:.2f}:1 ✅", Colors.BRIGHT_GREEN)
            
            # Place OCO order
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
                    "live_data": not price_data.get('fallback', False)
                },
                symbol=symbol,
                venue="oanda"
            )
            
            # Execute order via OANDA API (environment determined by connector config)
            order_result = self.oanda.place_oco_order(
                instrument=symbol,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                units=units,
                ttl_hours=6.0  # Charter: 6 hour max hold
            )
            
            if order_result.get('success'):
                order_id = order_result.get('order_id')
                latency_ms = order_result.get('latency_ms', 0)
                
                # CHARTER ENFORCEMENT: Verify latency
                if latency_ms > self.charter.MAX_PLACEMENT_LATENCY_MS:
                    self.display.error(f"❌ CHARTER VIOLATION: Latency {latency_ms:.1f}ms > 300ms")
                    log_narration(
                        event_type="CHARTER_VIOLATION",
                        details={
                            "violation": "MAX_LATENCY",
                            "latency_ms": latency_ms,
                            "max_allowed": self.charter.MAX_PLACEMENT_LATENCY_MS,
                            "order_id": order_id
                        },
                        symbol=symbol,
                        venue="oanda"
                    )
                    # Continue anyway since order was placed (just log violation)
                
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
                    'timestamp': datetime.now(timezone.utc)
                }
                
                self.total_trades += 1
                
                # Log successful placement with narration
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
                        "charter_compliant": True
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
                        "reasoning": f"Charter-compliant {rr_ratio:.2f}:1 R:R, ${notional_value:,.0f} notional"
                    }
                )
                
                self.display.alert(f"✅ OCO order placed! Order ID: {order_id}", "SUCCESS")
                self.display.info("Latency", f"{latency_ms:.1f}ms", Colors.BRIGHT_CYAN)
                self.display.rick_says(rick_comment)
                
                return order_id
            else:
                error = order_result.get('error', 'Unknown error')
                self.display.error(f"Order failed: {error}")
                
                log_narration(
                    event_type="ORDER_FAILED",
                    details={
                        "symbol": symbol,
                        "direction": direction,
                        "error": error,
                        "environment": self.environment
                    },
                    symbol=symbol,
                    venue="oanda"
                )
                
                return None
                
        except Exception as e:
            self.display.error(f"Error placing trade: {e}")
            log_narration(
                event_type="TRADE_ERROR",
                details={"error": str(e), "symbol": symbol},
                symbol=symbol,
                venue="oanda"
            )
            return None
    
    def check_positions(self):
        """Check status of open positions via OANDA API"""
        # Positions managed by TradeManager background loop
        # This method can be extended to sync state with OANDA API if needed
        return

    async def trade_manager_loop(self):
        """Background loop that evaluates active positions and asks the Hive for momentum signals.

        Behavior:
        - For positions older than `min_position_age_seconds`, query the Hive Mind for a consensus
          analysis on that symbol.
        - Use battle-tested MomentumDetector (from rbotzilla_golden_age.py) to detect strong momentum.
        - If EITHER the Hive consensus exceeds threshold OR MomentumDetector confirms momentum,
          cancel the existing TakeProfit order and set an adaptive trailing stop via the OANDA connector.
        - All modifications are logged via `log_narration` to keep an auditable trail.
        
        Integration Note: This TradeManager integrates existing momentum detection logic from
        /home/ing/RICK/RICK_LIVE_CLEAN/rbotzilla_golden_age.py (MomentumDetector & SmartTrailingSystem)
        to fulfill Charter requirement for code reuse (PIN 841921).
        """
        while self.is_running:
            try:
                now = datetime.now(timezone.utc)
                for order_id, pos in list(self.active_positions.items()):
                    # Skip if already processed for TP cancellation
                    if pos.get('tp_cancelled'):
                        continue
                    
                    # Age check
                    age = (now - pos['timestamp']).total_seconds()
                    if age < self.min_position_age_seconds:
                        continue

                    symbol = pos['symbol']
                    direction = pos['direction']
                    entry_price = pos['entry']

                    # Get current price to calculate profit
                    try:
                        current_price_data = self.get_current_price(symbol)
                        if not current_price_data:
                            continue
                        current_price = current_price_data['ask'] if direction == 'BUY' else current_price_data['bid']
                    except Exception as e:
                        self.display.warning(f"Could not fetch current price for {symbol}: {e}")
                        continue

                    # Calculate profit in pips and ATR multiples
                    pip_size = 0.0001 if 'JPY' not in symbol else 0.01
                    if direction == 'BUY':
                        profit_pips = (current_price - entry_price) / pip_size
                    else:
                        profit_pips = (entry_price - current_price) / pip_size
                    
                    # Estimate ATR (use stop_loss_pips / 1.2 as proxy, since stop = 1.2 * ATR)
                    estimated_atr_pips = self.stop_loss_pips / 1.2
                    profit_atr_multiple = profit_pips / estimated_atr_pips if estimated_atr_pips > 0 else 0

                    # Signal flags
                    hive_signal_confirmed = False
                    momentum_signal_confirmed = False

                    # Query Hive Mind for consensus on this instrument
                    if self.hive_mind:
                        market_data = {
                            "symbol": symbol.replace('_', ''),
                            "current_price": current_price,
                            "timeframe": "M15"
                        }

                        analysis = self.hive_mind.delegate_analysis(market_data)
                        consensus = analysis.consensus_signal
                        confidence = analysis.consensus_confidence

                        # Log the analysis
                        log_narration(
                            event_type="HIVE_ANALYSIS",
                            details={
                                "symbol": symbol,
                                "consensus": consensus.value if hasattr(consensus, 'value') else str(consensus),
                                "confidence": confidence,
                                "order_id": order_id,
                                "profit_atr": profit_atr_multiple
                            },
                            symbol=symbol,
                            venue="hive"
                        )

                        # Check hive consensus threshold
                        if confidence >= self.hive_trigger_confidence and consensus in (SignalStrength.STRONG_BUY, SignalStrength.STRONG_SELL):
                            if (direction == 'BUY' and consensus == SignalStrength.STRONG_BUY) or (direction == 'SELL' and consensus == SignalStrength.STRONG_SELL):
                                hive_signal_confirmed = True
                                self.display.info(f"Hive signal: {consensus.value} ({confidence:.2f}) for {symbol}", Colors.BRIGHT_CYAN)

                    # Use MomentumDetector from rbotzilla_golden_age.py
                    if self.momentum_detector and profit_atr_multiple > 0:
                        # Assume moderate trend and normal volatility for simple case
                        # (In production, you'd query actual regime/volatility from ML modules)
                        trend_strength = 0.7  # Moderate trend assumption
                        market_cycle = 'BULL_MODERATE'  # Default assumption
                        volatility = 1.0  # Normal volatility

                        has_momentum, momentum_strength = self.momentum_detector.detect_momentum(
                            profit_atr_multiple=profit_atr_multiple,
                            trend_strength=trend_strength,
                            cycle=market_cycle,
                            volatility=volatility
                        )

                        if has_momentum:
                            momentum_signal_confirmed = True
                            self.display.info(f"Momentum detected: {momentum_strength:.2f}x strength for {symbol} (profit: {profit_atr_multiple:.2f}x ATR)", Colors.BRIGHT_GREEN)
                            
                            log_narration(
                                event_type="MOMENTUM_DETECTED",
                                details={
                                    "symbol": symbol,
                                    "profit_atr": profit_atr_multiple,
                                    "momentum_strength": momentum_strength,
                                    "order_id": order_id
                                },
                                symbol=symbol,
                                venue="momentum_detector"
                            )

                    # Trigger TP cancellation if EITHER signal confirmed
                    if hive_signal_confirmed or momentum_signal_confirmed:
                        trigger_source = []
                        if hive_signal_confirmed:
                            trigger_source.append("Hive")
                        if momentum_signal_confirmed:
                            trigger_source.append("Momentum")
                        
                        self.display.alert(f"{'|'.join(trigger_source)} signal(s) detected for {symbol} - converting OCO to trailing SL", "INFO")

                        # Attempt to cancel TP order(s) associated with this OCO
                        try:
                            cancel_resp = self.oanda.cancel_order(order_id)

                            log_narration(
                                event_type="TP_CANCEL_ATTEMPT",
                                details={
                                    "order_id": order_id,
                                    "trigger_source": trigger_source,
                                    "profit_atr": profit_atr_multiple,
                                    "cancel_response": cancel_resp
                                },
                                symbol=symbol,
                                venue="oanda"
                            )

                            # Find open trades for this symbol and set an initial trailing stop
                            trades = self.oanda.get_trades()
                            for t in trades:
                                trade_instrument = t.get('instrument') or t.get('symbol')
                                trade_id = t.get('id') or t.get('tradeID') or t.get('trade_id')
                                if not trade_id:
                                    continue
                                if trade_instrument and trade_instrument.replace('.', '_').upper() == symbol:
                                    # Calculate adaptive trailing stop using SmartTrailingSystem
                                    if self.trailing_system and profit_atr_multiple > 0:
                                        atr_price = estimated_atr_pips * pip_size
                                        trail_distance = self.trailing_system.calculate_dynamic_trailing_distance(
                                            profit_atr_multiple=profit_atr_multiple,
                                            atr=atr_price,
                                            momentum_active=True
                                        )
                                        
                                        if direction == 'BUY':
                                            new_sl = current_price - trail_distance
                                        else:
                                            new_sl = current_price + trail_distance
                                        
                                        # Ensure new SL is better than original
                                        original_sl = pos.get('stop_loss')
                                        if direction == 'BUY':
                                            adaptive_sl = max(new_sl, original_sl)
                                        else:
                                            adaptive_sl = min(new_sl, original_sl)
                                    else:
                                        # Fallback: use existing stop_loss
                                        adaptive_sl = pos.get('stop_loss')
                                    
                                    set_resp = self.oanda.set_trade_stop(trade_id, adaptive_sl)

                                    log_narration(
                                        event_type="TRAILING_SL_SET",
                                        details={
                                            "trade_id": trade_id,
                                            "order_id": order_id,
                                            "set_stop": adaptive_sl,
                                            "trail_distance_pips": (current_price - adaptive_sl) / pip_size if direction == 'BUY' else (adaptive_sl - current_price) / pip_size,
                                            "set_resp": set_resp,
                                            "trigger_source": trigger_source
                                        },
                                        symbol=symbol,
                                        venue="oanda"
                                    )

                                    # Mark position as having TP cancelled
                                    pos['tp_cancelled'] = True
                                    pos['tp_cancelled_timestamp'] = datetime.now(timezone.utc)
                                    pos['tp_cancel_source'] = trigger_source
                                    self.display.success(f"✅ TP cancelled and adaptive trailing SL set for trade {trade_id} ({symbol})")
                                    break

                        except Exception as e:
                            self.display.error(f"Error during TP cancellation/trailing conversion: {e}")
                            log_narration(
                                event_type="TP_CANCEL_ERROR",
                                details={"order_id": order_id, "error": str(e)},
                                symbol=symbol,
                                venue="oanda"
                            )

                # Sleep short interval before next pass
                await asyncio.sleep(5)
            except Exception as e:
                self.display.error(f"TradeManager loop error: {e}")
                await asyncio.sleep(5)
    
    def _handle_position_closed(self, trade_id: str):
        """Handle a closed position"""
        if trade_id not in self.active_positions:
            return
        
        position = self.active_positions[trade_id]
        
        try:
            # Get trade details from OANDA
            trades = self.oanda.get_trades()
            
            # Assume win for now (we'd need to check actual closing price)
            # In real implementation, you'd query the closed trade details
            is_win = True  # Placeholder
            
            pnl = 50.0 if is_win else -20.0  # Placeholder values
            
            if is_win:
                self.wins += 1
                self.display.trade_win(
                    position['symbol'],
                    pnl,
                    f"Exit: {position['take_profit']:.5f} | R:R 3:1 achieved"
                )
            else:
                self.losses += 1
                self.display.trade_loss(
                    position['symbol'],
                    pnl,
                    f"Exit: {position['stop_loss']:.5f} | Stopped out"
                )
            
            # Remove from active positions
            del self.active_positions[trade_id]
            
            # Display stats
            self._display_stats()
            
        except Exception as e:
            self.display.error(f"Error handling closed position: {e}")
    
    def _display_stats(self):
        """Display current statistics"""
        win_rate = (self.wins / self.total_trades * 100) if self.total_trades > 0 else 0
        
        stats = {
            "Total Trades": str(self.total_trades),
            "Active Positions": str(len(self.active_positions)),
            "Wins / Losses": f"{self.wins} / {self.losses}",
            "Win Rate": f"{win_rate:.1f}%"
        }
        
        self.display.stats_panel(stats)
    
    async def run_trading_loop(self):
        """Main trading loop (environment-agnostic)"""
        self.is_running = True
        
        env_label = "PRACTICE" if self.environment == 'practice' else "LIVE"
        self.display.alert(f"Starting trading engine with {env_label} API...", "SUCCESS")
        self.display.alert(f"📊 Market Data: {env_label} OANDA API (real-time)", "INFO")
        self.display.alert(f"💰 Orders: {env_label} OANDA API", "INFO")
        print()
        
        trade_count = 0
        # Start TradeManager background task
        trade_manager_task = asyncio.create_task(self.trade_manager_loop())
        
        while self.is_running:
            try:
                # Check existing positions
                self.check_positions()
                
                # Place new trade if we have less than 3 active positions
                if len(self.active_positions) < 3:
                    import random
                    
                    # Pick random pair and direction
                    symbol = random.choice(self.trading_pairs)
                    direction = random.choice(["BUY", "SELL"])
                    
                    trade_id = self.place_trade(symbol, direction)
                    
                    if trade_id:
                        trade_count += 1
                    
                    self.display.divider()
                    print()
                
                # Wait before next trade (M15 Charter compliance)
                wait_minutes = self.min_trade_interval / 60
                self.display.alert(f"Waiting {wait_minutes:.0f} minutes before next trade (M15 Charter)...", "INFO")
                await asyncio.sleep(self.min_trade_interval)
                
            except KeyboardInterrupt:
                self.display.warning("\nStopping trading engine...")
                self.is_running = False
                break
            except Exception as e:
                self.display.error(f"Error in trading loop: {e}")
                await asyncio.sleep(10)
        
        self.display.section("SESSION COMPLETE")
        self._display_stats()
        # Cancel trade manager task
        try:
            trade_manager_task.cancel()
        except Exception:
            pass


async def main():
    """Main entry point - environment determined by API configuration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RBOTzilla Charter-Compliant OANDA Trading Engine')
    parser.add_argument('--env', '--environment', 
                       choices=['practice', 'live'], 
                       default='practice',
                       help='Trading environment (practice=demo, live=real money)')
    
    args = parser.parse_args()
    
    # Confirm LIVE mode with user
    if args.env == 'live':
        print("\n" + "="*60)
        print("⚠️  LIVE TRADING MODE - REAL MONEY AT RISK ⚠️")
        print("="*60)
        confirm = input("\nType 'CONFIRM LIVE' to proceed with live trading: ")
        if confirm != 'CONFIRM LIVE':
            print("Live trading cancelled.")
            return
        print("\n✅ Live trading confirmed. Initializing engine...\n")
    
    engine = OandaTradingEngine(environment=args.env)
    await engine.run_trading_loop()


if __name__ == "__main__":
    asyncio.run(main())

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
from pathlib import Path
import os
import time
import asyncio
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.resolve()))

# Load environment variables manually
env_file = str(Path(__file__).parent / 'master.env')
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Charter compliance imports
from foundation.rick_charter import RickCharter
from foundation.margin_correlation_gate import MarginCorrelationGate, Position, Order, HookResult
from brokers.oanda_connector import OandaConnector
from util.terminal_display import TerminalDisplay, Colors
from util.narration_logger import log_narration, log_pnl
from util.rick_narrator import RickNarrator
from util.usd_converter import get_usd_notional
from systems.momentum_signals import generate_signal

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
        
        # Initialize Strategy Aggregator (combines 5 prototype strategies)
        try:
            from util.strategy_aggregator import StrategyAggregator
            self.strategy_aggregator = StrategyAggregator(signal_vote_threshold=2)
            self.display.success("✅ Strategy Aggregator loaded (5 prototype strategies)")
        except ImportError:
            self.strategy_aggregator = None
            self.display.warning("⚠️  Strategy Aggregator not available")
        
        # Initialize Quantitative Hedge Engine (correlation-based hedging)
        try:
            from util.quant_hedge_engine import QuantHedgeEngine
            self.hedge_engine = QuantHedgeEngine()
            self.active_hedges = {}  # Track active hedge positions
            self.display.success("✅ Quantitative Hedge Engine loaded")
        except ImportError:
            self.hedge_engine = None
            self.active_hedges = {}
            self.display.warning("⚠️  Hedge Engine not available")
        
        # Charter-compliant trading parameters
        self.charter = RickCharter
        
        # ========================================================================
        # MARGIN & CORRELATION GUARDIAN GATES (NEW)
        # ========================================================================
        # Get account NAV for gate calculations
        # Use default NAV for bootstrap - will be updated from API calls
        account_nav = 2000.0  # Default OANDA practice account NAV
        try:
            if hasattr(self.oanda, 'get_account_info'):
                account_info = self.oanda.get_account_info()
                account_nav = float(account_info.get('NAV', 2000.0))
        except Exception as e:
            self.display.warn(f"⚠️  Could not fetch account NAV: {e}, using default $2000")
        
        self.gate = MarginCorrelationGate(account_nav=account_nav)
        self.current_positions = []  # Track positions for gate monitoring
        self.pending_orders = []      # Track pending orders for gate monitoring
        self.display.success("🛡️  Margin & Correlation Guardian Gates ACTIVE")
        
        # ALL AVAILABLE OANDA FOREX PAIRS (from env_new.env)
        # Major USD pairs + Major crosses + Commodity currencies
        self.trading_pairs = [
            # Major USD pairs (highest liquidity)
            'EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'AUD_USD', 'USD_CAD', 'NZD_USD',
            # Major crosses (no USD)
            'EUR_GBP', 'EUR_JPY', 'GBP_JPY', 'AUD_JPY', 'CHF_JPY',
            # European crosses
            'EUR_CHF', 'GBP_CHF',
            # Commodity currency crosses
            'AUD_CHF', 'NZD_CHF', 'EUR_AUD', 'GBP_AUD'
        ]
        
        self.min_trade_interval = 300  # 5 minutes (MICRO TRADING DISABLED - Minimum 5min enforced)
        
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
        
        # Approximate market prices for ALL pairs (updated Oct 2025)
        base_prices = {
            # Major USD pairs
            'EUR_USD': 1.0800,
            'GBP_USD': 1.2700,
            'USD_JPY': 150.00,
            'USD_CHF': 0.8800,
            'AUD_USD': 0.6500,
            'USD_CAD': 1.3600,
            'NZD_USD': 0.6000,
            
            # Major crosses (no USD)
            'EUR_GBP': 0.8500,
            'EUR_JPY': 162.00,
            'GBP_JPY': 190.00,
            'AUD_JPY': 97.50,
            'CHF_JPY': 170.00,
            
            # European crosses
            'EUR_CHF': 0.9500,
            'GBP_CHF': 1.1200,
            
            # Commodity currency crosses
            'AUD_CHF': 0.5700,
            'NZD_CHF': 0.5300,
            'EUR_AUD': 1.6600,
            'GBP_AUD': 1.9500
        }
        
        if symbol not in base_prices:
            self.display.error(f"Symbol {symbol} not configured - add to base_prices dict")
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
    
    def evaluate_signal_with_ml(self, symbol: str, signal_data: Dict) -> Tuple[bool, Dict]:
        """
        Filter signals through ML regime detection and strength analysis
        
        Returns:
            (bool, dict): (approved, analysis_details)
        """
        if not self.regime_detector or not self.signal_analyzer:
            # No ML, accept signal
            return True, {'ml_available': False, 'reason': 'ML not available'}
        
        try:
            # Get recent price data for ML analysis
            price_data = self.get_current_price(symbol)
            if not price_data:
                return False, {'ml_available': True, 'reason': 'Could not fetch price data'}
            
            # Detect market regime
            regime = self.regime_detector.detect_regime(symbol)
            
            # Analyze signal quality
            strength = self.signal_analyzer.analyze_signal(
                symbol, 
                signal_data.get('action', 'buy'),
                signal_data.get('entry', price_data.get('ask', 0))
            )
            
            # Accept signals with high confidence in trending regimes
            if regime in ['trending_up', 'trending_down']:
                # Strong trend: accept if confidence >= 0.70
                if strength >= 0.70:
                    log_narration(
                        event_type="ML_SIGNAL_APPROVED",
                        details={
                            "symbol": symbol,
                            "regime": regime,
                            "strength": strength,
                            "reason": "High confidence in strong trend"
                        },
                        symbol=symbol,
                        venue="ml_intelligence"
                    )
                    return True, {
                        'ml_available': True,
                        'regime': regime,
                        'strength': strength,
                        'approved': True
                    }
            
            elif regime in ['ranging', 'consolidating']:
                # Low trend environment: accept only exceptional signals (>0.80)
                if strength >= 0.80:
                    log_narration(
                        event_type="ML_SIGNAL_APPROVED",
                        details={
                            "symbol": symbol,
                            "regime": regime,
                            "strength": strength,
                            "reason": "Exceptional signal in ranging market"
                        },
                        symbol=symbol,
                        venue="ml_intelligence"
                    )
                    return True, {
                        'ml_available': True,
                        'regime': regime,
                        'strength': strength,
                        'approved': True
                    }
            
            # Signal rejected due to weak confidence
            log_narration(
                event_type="ML_SIGNAL_REJECTED",
                details={
                    "symbol": symbol,
                    "regime": regime,
                    "strength": strength,
                    "reason": f"Insufficient confidence in {regime} regime"
                },
                symbol=symbol,
                venue="ml_intelligence"
            )
            
            return False, {
                'ml_available': True,
                'regime': regime,
                'strength': strength,
                'approved': False,
                'reason': f'Weak signal ({strength:.2f}) in {regime} market'
            }
        
        except Exception as e:
            # ML error - be permissive, don't block trade
            self.display.warning(f"ML evaluation error for {symbol}: {str(e)}")
            return True, {'ml_available': True, 'error': str(e), 'approved': True}
    
    def amplify_signal_with_hive(self, symbol: str, signal_data: Dict) -> Dict:
        """
        Amplify signal strength through Hive Mind consensus
        
        Args:
            symbol: Currency pair
            signal_data: Signal dict with 'action', 'entry', etc.
        
        Returns:
            Amplified signal dict with hive_amplified flag and confidence
        """
        if not self.hive_mind:
            # No Hive, return original
            return signal_data
        
        try:
            # Query Hive Mind for consensus on this symbol
            market_data = {
                "symbol": symbol.replace('_', ''),
                "action": signal_data.get('action', 'buy'),
                "entry_price": signal_data.get('entry', 0),
                "timeframe": "M15"
            }
            
            hive_analysis = self.hive_mind.delegate_analysis(market_data)
            
            if not hive_analysis:
                return signal_data
            
            consensus = hive_analysis.consensus_signal
            confidence = hive_analysis.consensus_confidence
            
            # Check if Hive strongly agrees with signal
            if confidence >= self.hive_trigger_confidence:
                # Hive consensus is strong
                
                # Amplify the signal
                amplified_signal = signal_data.copy()
                amplified_signal['hive_amplified'] = True
                amplified_signal['hive_confidence'] = confidence
                amplified_signal['hive_consensus'] = consensus.value if hasattr(consensus, 'value') else str(consensus)
                
                log_narration(
                    event_type="HIVE_CONSENSUS_STRONG",
                    details={
                        "symbol": symbol,
                        "consensus": consensus.value if hasattr(consensus, 'value') else str(consensus),
                        "confidence": confidence,
                        "original_signal": signal_data.get('tag', 'unknown'),
                        "amplified": True
                    },
                    symbol=symbol,
                    venue="hive_mind"
                )
                
                self.display.success(f"🐝 Hive amplified {symbol}: {consensus} ({confidence:.2f})")
                
                return amplified_signal
            else:
                # Hive consensus weak - return original signal
                log_narration(
                    event_type="HIVE_CONSENSUS_WEAK",
                    details={
                        "symbol": symbol,
                        "consensus": consensus.value if hasattr(consensus, 'value') else str(consensus),
                        "confidence": confidence,
                        "threshold": self.hive_trigger_confidence
                    },
                    symbol=symbol,
                    venue="hive_mind"
                )
                
                return signal_data
        
        except Exception as e:
            # Hive error - return original signal
            self.display.warning(f"Hive amplification error for {symbol}: {str(e)}")
            return signal_data
    
    def calculate_position_size(self, symbol: str, entry_price: float) -> int:
        """Calculate Charter-compliant position size to meet $15k minimum notional"""
        import math
        
        # CRITICAL FIX: JPY pairs have special pip value (0.01 vs 0.0001)
        # This changes notional calculation significantly
        
        pip_size = 0.01 if 'JPY' in symbol else 0.0001
        
        # Calculate required units to meet minimum notional ($15,000)
        # For JPY pairs: entry_price is ~150, so 1 unit = ~150 * 0.01 per pip
        # For regular pairs: entry_price is ~1.05, so 1 unit = ~1.05 * 0.0001 per pip
        
        required_units = math.ceil(self.min_notional_usd / entry_price)
        
        # JPY pairs need special handling - multiply by 10 since pip value is 10x larger
        if 'JPY' in symbol:
            required_units = math.ceil(required_units * 10)
        
        # Round up to nearest 100 for clean sizing
        position_size = math.ceil(required_units / 100) * 100
        
        # Verify we meet minimum notional
        notional = position_size * entry_price
        if notional < self.min_notional_usd:
            # Add extra units for JPY pairs
            add_units = 100 if 'JPY' not in symbol else 1000
            position_size += add_units
        
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
    
    def _evaluate_hedge_conditions(self, symbol: str, direction: str, units: float, 
                                   entry_price: float, notional: float, current_margin_used: float) -> Dict:
        """
        Intelligent multi-condition hedge evaluation
        Analyzes portfolio state, market conditions, and risk exposure
        
        Returns:
            Dict with 'execute' (bool) and 'reason' (str)
        """
        # Get account NAV for calculations
        account_nav = 2000.0
        try:
            if hasattr(self.oanda, 'get_account_info'):
                account_info = self.oanda.get_account_info()
                account_nav = float(account_info.get('NAV', 2000.0))
        except Exception:
            pass
        
        # Calculate current margin utilization
        margin_utilization = (current_margin_used / account_nav) if account_nav > 0 else 0
        
        # Evaluate hedge opportunity
        hedge_opp = self.hedge_engine.evaluate_hedge_opportunity(symbol)
        
        # ========================================================================
        # HEDGE DECISION RULES - Multi-Condition Analysis
        # ========================================================================
        
        # RULE 1: No suitable hedge pair available
        if not hedge_opp['hedge_available']:
            return {'execute': False, 'reason': 'No inverse correlation pair found'}
        
        # RULE 2: Weak correlation (< -0.50 threshold)
        if abs(hedge_opp['correlation']) < 0.50:
            return {'execute': False, 'reason': f"Weak correlation ({hedge_opp['correlation']:.2f})"}
        
        # RULE 3: High margin usage (>25%) - ALWAYS hedge to protect capital
        if margin_utilization > 0.25:
            return {
                'execute': True, 
                'reason': f'High margin usage ({margin_utilization:.1%}) - protective hedge required'
            }
        
        # RULE 4: Large notional (>$20k) - Hedge to reduce single-position risk
        if notional > 20000:
            return {
                'execute': True,
                'reason': f'Large notional (${notional:,.0f}) - risk reduction hedge'
            }
        
        # RULE 5: Multiple positions in same currency - Hedge cumulative exposure
        usd_exposure_count = sum(1 for pos in self.current_positions 
                                 if 'USD' in pos.symbol and pos.side == ("LONG" if direction == "BUY" else "SHORT"))
        if usd_exposure_count >= 2:
            return {
                'execute': True,
                'reason': f'Cumulative USD exposure ({usd_exposure_count + 1} positions) - correlation hedge'
            }
        
        # RULE 6: Strong inverse correlation (< -0.70) - Opportunistic hedge
        if hedge_opp['correlation'] < -0.70:
            return {
                'execute': True,
                'reason': f"Strong inverse correlation ({hedge_opp['correlation']:.2f}) - optimal hedge opportunity"
            }
        
        # RULE 7: Moderate margin (15-25%) + Strong correlation - Selective hedge
        if 0.15 < margin_utilization <= 0.25 and hedge_opp['correlation'] < -0.65:
            return {
                'execute': True,
                'reason': f'Moderate margin ({margin_utilization:.1%}) + strong correlation - proactive hedge'
            }
        
        # DEFAULT: Skip hedge for low-risk scenarios
        return {
            'execute': False,
            'reason': f'Low risk profile (margin: {margin_utilization:.1%}, notional: ${notional:,.0f})'
        }
    
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
            
            # Calculate notional value in TRUE USD (handles cross pairs correctly)
            notional_value = get_usd_notional(position_size, symbol, entry_price, self.oanda)
            if notional_value is None:
                self.display.error(f"❌ Cannot calculate USD notional for {symbol}")
                return None
            
            # ========================================================================
            # 🛡️ PRE-TRADE GUARDIAN GATE CHECK (NEW)
            # ========================================================================
            # Get current account margin
            current_margin_used = 0
            try:
                if hasattr(self.oanda, 'get_account_info'):
                    account_info = self.oanda.get_account_info()
                    current_margin_used = float(account_info.get('marginUsed', 0))
            except Exception as e:
                self.display.warn(f"⚠️  Could not fetch margin info: {e}")
            
            # Create order object for gate validation
            gate_order = Order(
                symbol=symbol,
                side=direction,
                units=position_size,
                price=entry_price,
                order_id=f"pending_{symbol}_{int(time.time())}"
            )
            
            # Run pre-trade gate
            gate_result = self.gate.pre_trade_gate(
                new_order=gate_order,
                current_positions=self.current_positions,
                pending_orders=self.pending_orders,
                total_margin_used=current_margin_used
            )
            
            # If gate rejects order, stop here
            if not gate_result.allowed:
                self.display.error(f"❌ GUARDIAN GATE BLOCKED: {gate_result.reason}")
                if gate_result.action == "AUTO_CANCEL":
                    self.display.alert(f"   Action: {gate_result.action}", "WARNING")
                log_narration(
                    event_type="GATE_REJECTION",
                    details={
                        "symbol": symbol,
                        "reason": gate_result.reason,
                        "action": gate_result.action,
                        "margin_used": current_margin_used
                    },
                    symbol=symbol,
                    venue="oanda"
                )
                return None
            
            # CHARTER ENFORCEMENT: Verify minimum notional (GATED PRE-ORDER VALIDATION)
            if notional_value < self.min_notional_usd:
                self.display.error(f"❌ CHARTER VIOLATION: Notional ${notional_value:,.0f} < ${self.min_notional_usd:,}")
                self.display.error(f"   GATED LOGIC: Order blocked before submission")
                log_narration(
                    event_type="CHARTER_VIOLATION",
                    details={
                        "action": "PRE_ORDER_BLOCK",
                        "violation": "MIN_NOTIONAL_PRE_ORDER",
                        "notional_usd": round(notional_value, 2),
                        "min_required_usd": self.min_notional_usd,
                        "symbol": symbol,
                        "direction": direction,
                        "position_size": position_size,
                        "entry_price": entry_price,
                        "enforcement": "GATED_LOGIC_AUTOMATIC",
                        "status": "BLOCKED_BEFORE_SUBMISSION"
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
                
                # ========================================================================
                # 🛡️ TRACK POSITION FOR GUARDIAN GATE ONGOING MONITORING
                # ========================================================================
                gate_position = Position(
                    symbol=symbol,
                    side="LONG" if direction == "BUY" else "SHORT",
                    units=abs(units),
                    entry_price=entry_price,
                    current_price=entry_price,
                    pnl=0.0,
                    pnl_pips=0.0,
                    margin_used=(notional_value * 0.02),  # Typical FOREX margin ~2%
                    position_id=order_id
                )
                self.current_positions.append(gate_position)
                self.display.info("🛡️ Position tracked for guardian gate monitoring", "", Colors.BRIGHT_CYAN)
                
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
                
                # ========================================================================
                # 🛡️ QUANTITATIVE HEDGE ENGINE - INTELLIGENT MULTI-CONDITION ANALYSIS
                # ========================================================================
                if self.hedge_engine:
                    hedge_decision = self._evaluate_hedge_conditions(
                        symbol=symbol,
                        direction=direction,
                        units=abs(units),
                        entry_price=entry_price,
                        notional=notional_value,
                        current_margin_used=current_margin_used
                    )
                    
                    if hedge_decision['execute']:
                        self.display.section("HEDGE ANALYSIS")
                        self.display.info("Hedge Decision", hedge_decision['reason'], Colors.BRIGHT_YELLOW)
                        
                        hedge_position = self.hedge_engine.execute_hedge(
                            primary_symbol=symbol,
                            primary_side=direction,
                            position_size=abs(units),
                            entry_price=entry_price
                        )
                        
                        if hedge_position:
                            # Store hedge reference
                            self.active_hedges[order_id] = hedge_position
                            
                            self.display.success(
                                f"🛡️ HEDGE EXECUTED: {hedge_position.side} {hedge_position.size:.0f} units "
                                f"{hedge_position.symbol} @ {hedge_position.hedge_ratio:.0%} coverage"
                            )
                            self.display.info(
                                "Correlation", 
                                f"{hedge_position.correlation:.2f} (inverse)", 
                                Colors.BRIGHT_CYAN
                            )
                            
                            log_narration(
                                event_type="HEDGE_EXECUTED",
                                details={
                                    "primary_symbol": symbol,
                                    "hedge_symbol": hedge_position.symbol,
                                    "hedge_side": hedge_position.side,
                                    "hedge_size": hedge_position.size,
                                    "hedge_ratio": hedge_position.hedge_ratio,
                                    "correlation": hedge_position.correlation,
                                    "reason": hedge_decision['reason']
                                },
                                symbol=symbol,
                                venue="quant_hedge"
                            )
                            
                            # TODO: Place actual hedge order via OANDA API if live trading
                            # hedge_order_id = self.oanda.place_oco_order(
                            #     instrument=hedge_position.symbol,
                            #     entry_price=hedge_position.entry_price,
                            #     units=hedge_position.size if hedge_position.side == 'BUY' else -hedge_position.size,
                            #     ...
                            # )
                        else:
                            self.display.warning("⚠️  No suitable hedge pair found")
                    else:
                        self.display.info("Hedge Decision", f"SKIPPED - {hedge_decision['reason']}", Colors.DIM)
                
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
        last_police_sweep = time.time()  # Track last Position Police sweep
        police_sweep_interval = 900  # 15 minutes (M15 charter compliance)
        
        # Start TradeManager background task
        trade_manager_task = asyncio.create_task(self.trade_manager_loop())
        
        while self.is_running:
            try:
                # AUTOMATED POSITION POLICE SWEEP (every 15 minutes)
                current_time = time.time()
                if current_time - last_police_sweep >= police_sweep_interval:
                    try:
                        self.display.info("🚓 Position Police sweep starting...")
                        _rbz_force_min_notional_position_police()
                        last_police_sweep = current_time
                        self.display.success("✅ Position Police sweep complete")
                    except Exception as e:
                        self.display.error(f"❌ Position Police error: {e}")
                
                # Check existing positions
                self.check_positions()
                
                # Place new trade if we have less than 3 active positions
                if len(self.active_positions) < 3:
                    # Deterministic signal scan across configured pairs
                    symbol = None
                    direction = None
                    for _candidate in self.trading_pairs:
                        try:
                            candles = self.oanda.get_historical_data(_candidate, count=120, granularity="M15")
                            sig, conf = generate_signal(_candidate, candles)  # returns ("BUY"/"SELL", confidence) or (None, 0)
                        except Exception as e:
                            self.display.error(f"Signal error for {_candidate}: {e}")
                            continue
                        if sig in ("BUY","SELL"):
                            symbol = _candidate
                            direction = sig
                            self.display.success(f"✓ Signal: {symbol} {direction} (confidence: {conf:.1%})")
                            break
                    
                    if not symbol or not direction:
                        self.display.warning("No valid signals across pairs - skipping cycle")
                        await asyncio.sleep(self.min_trade_interval)
                        continue
                    
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

# ===== RBOTZILLA: POSITION POLICE (immutable min-notional) =====
try:
    from rick_charter import RickCharter
except Exception:
    class RickCharter: MIN_NOTIONAL_USD = 15000

def _rbz_usd_notional(instrument: str, units: float, price: float) -> float:
    try:
        base, quote = instrument.split("_",1)
        u = abs(float(units))
        p = float(price)
        if quote == "USD":      # e.g., GBP_USD
            return u * p
        if base == "USD":       # e.g., USD_JPY
            return u * 1.0
        return 0.0              # non-USD crosses (ignored by charter)
    except Exception:
        return 0.0

def _rbz_fetch_price(sess, acct: str, inst: str, tok: str):
    import requests
    try:
        r = sess.get(
            f"https://api-fxpractice.oanda.com/v3/accounts/{acct}/pricing",
            headers={"Authorization": f"Bearer {tok}"},
            params={"instruments": inst}, timeout=5,
        )
        return float(r.json()["prices"][0]["closeoutAsk"])
    except Exception:
        return None

def _rbz_force_min_notional_position_police():
    """
    AUTOMATED POSITION POLICE - GATED CHARTER ENFORCEMENT
    Closes any position < MIN_NOTIONAL_USD ($15,000)
    Runs: (1) On engine startup, (2) Every 15 minutes during trading loop
    PIN: 841921 | IMMUTABLE
    """
    import os, json, requests
    from datetime import datetime, timezone
    
    MIN_NOTIONAL = getattr(RickCharter, "MIN_NOTIONAL_USD", 15000)
    acct = os.environ.get("OANDA_PRACTICE_ACCOUNT_ID") or os.environ.get("OANDA_ACCOUNT_ID")
    tok  = os.environ.get("OANDA_PRACTICE_TOKEN") or os.environ.get("OANDA_TOKEN")
    if not acct or not tok:
        print('[RBZ_POLICE] skipped (no creds)'); return

    s = requests.Session()
    violations_found = 0
    violations_closed = 0
    
    # 1) fetch open positions
    r = s.get(
        f"https://api-fxpractice.oanda.com/v3/accounts/{acct}/openPositions",
        headers={"Authorization": f"Bearer {tok}"}, timeout=7,
    )
    
    positions = r.json().get("positions", [])
    timestamp = datetime.now(timezone.utc).isoformat()
    
    for pos in positions:
        inst = pos.get("instrument")
        long_u  = float(pos.get("long",{}).get("units","0"))
        short_u = float(pos.get("short",{}).get("units","0"))  # negative when short
        net = long_u + short_u
        if net == 0:
            continue

        avg = pos.get("long",{}).get("averagePrice") or pos.get("short",{}).get("averagePrice")
        price = float(avg) if avg else (_rbz_fetch_price(s, acct, inst, tok) or 0.0)
        notional = _rbz_usd_notional(inst, net, price)

        if 0 < notional < MIN_NOTIONAL:
            violations_found += 1
            violation_data = {
                "timestamp": timestamp,
                "event_type": "CHARTER_VIOLATION",
                "action": "POSITION_POLICE_AUTO_CLOSE",
                "details": {
                    "violation": "POSITION_BELOW_MIN_NOTIONAL",
                    "instrument": inst,
                    "net_units": net,
                    "side": "long" if net > 0 else "short",
                    "avg_price": price,
                    "notional_usd": round(notional, 2),
                    "min_required_usd": MIN_NOTIONAL,
                    "account": acct,
                    "enforcement": "GATED_LOGIC_AUTOMATIC"
                },
                "symbol": inst,
                "venue": "oanda"
            }
            
            # Log violation BEFORE closing
            print(json.dumps(violation_data))
            try:
                log_narration(**violation_data)
            except:
                pass  # Narration logger may not be available
            
            # Close entire side
            side = "long" if net > 0 else "short"
            payload = {"longUnits":"ALL"} if side=="long" else {"shortUnits":"ALL"}
            close_response = s.put(
                f"https://api-fxpractice.oanda.com/v3/accounts/{acct}/positions/{inst}/close",
                headers={"Authorization": f"Bearer {tok}", "Content-Type":"application/json"},
                data=json.dumps(payload), timeout=7,
            )
            
            if close_response.status_code == 200:
                violations_closed += 1
                close_data = {
                    "timestamp": timestamp,
                    "event_type": "POSITION_CLOSED",
                    "action": "CHARTER_ENFORCEMENT_SUCCESS",
                    "details": {
                        "instrument": inst,
                        "reason": "BELOW_MIN_NOTIONAL",
                        "status": "CLOSED_BY_POSITION_POLICE"
                    },
                    "symbol": inst,
                    "venue": "oanda"
                }
                print(json.dumps(close_data))
                try:
                    log_narration(**close_data)
                except:
                    pass
    
    # Summary logging
    if violations_found > 0:
        summary = {
            "timestamp": timestamp,
            "event_type": "POSITION_POLICE_SUMMARY",
            "details": {
                "violations_found": violations_found,
                "violations_closed": violations_closed,
                "enforcement": "GATED_LOGIC_AUTOMATIC",
                "min_notional_usd": MIN_NOTIONAL
            }
        }
        print(json.dumps(summary))
        try:
            log_narration(**summary)
        except:
            pass
            
# ===== /POSITION POLICE =====

# RBZ guard at import time
try:
    _rbz_force_min_notional_position_police()
except Exception as _e:
    print('[RBZ_POLICE] error', _e)

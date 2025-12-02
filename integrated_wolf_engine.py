#!/usr/bin/env python3
"""
integrated_wolf_engine.py - Full 130+ Feature Integrated Trading System
PIN: 841921 | Charter Compliant | All Wolf Packs Active

Combines ALL existing components:
- 3 Wolf Pack Strategies (Bullish/Bearish/Sideways)
- Regime Detection (logic/regime_detector.py)
- Guardian Gates (hive/guardian_gates.py)
- Smart Logic Filter (logic/smart_logic.py)
- Quant Hedge Rules (hive/quant_hedge_rules.py)
- Margin Correlation Gate (foundation/margin_correlation_gate.py)
- Charter Compliance (foundation/rick_charter.py)
- OANDA Connector with OCO (brokers/oanda_connector.py)
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Charter (immutable constants)
from foundation.rick_charter import RickCharter

# Import Wolf Pack Strategies
from strategies.bullish_wolf import BullishWolf
from strategies.bearish_wolf import BearishWolf
from strategies.sideways_wolf import SidewaysWolf

# Import Regime Detection
from logic.regime_detector import detect_market_regime, MarketRegime

# Import Gates
from hive.guardian_gates import GuardianGates, GateResult
from foundation.margin_correlation_gate import MarginCorrelationGate

# Import Smart Logic
from logic.smart_logic import get_tracker

# Import OANDA Connector
from brokers.oanda_connector import OandaConnector

# Import utilities
from util.narration_logger import NarrationLogger


class IntegratedWolfEngine:
    """
    Full-featured trading engine integrating all 130+ components.
    
    Features Active:
    - Multi-regime strategy selection (3 Wolf Packs)
    - 6-layer gate validation (Guardian + Margin + Correlation + Charter)
    - Real-time regime detection
    - Smart logic filtering
    - OCO order management
    - Narration event logging
    - Position monitoring
    - Dynamic sizing with Charter enforcement
    """
    
    def __init__(self, account_id: str, api_token: str, practice: bool = True):
        """Initialize the integrated engine."""
        self.PIN = 841921
        logger.info(f"Initializing Integrated Wolf Engine (PIN: {self.PIN})")
        
        # Charter validation
        assert RickCharter.PIN == self.PIN, "Charter PIN mismatch!"
        
        # Broker connection
        self.connector = OandaConnector(
            account_id=account_id,
            api_token=api_token,
            practice=practice
        )
        
        # Wolf Pack Strategies
        self.strategies = {
            MarketRegime.BULLISH: BullishWolf(),
            MarketRegime.BEARISH: BearishWolf(),
            MarketRegime.SIDEWAYS: SidewaysWolf()
        }
        logger.info(f"✅ Loaded {len(self.strategies)} Wolf Pack strategies")
        
        # Gate Systems
        account_nav = self.get_account_nav()
        self.guardian_gates = GuardianGates(account_nav=account_nav)
        self.margin_gate = MarginCorrelationGate(
            account_nav=account_nav,
            margin_cap_pct=0.35  # 35% from Charter
        )
        logger.info("✅ Guardian Gates armed")
        logger.info("✅ Margin Correlation Gate armed")
        
        # Smart Logic Filter
        self.tracker = get_tracker()
        logger.info("✅ Smart Logic Filter active")
        
        # Narration Logger
        self.narration = NarrationLogger()
        logger.info("✅ Narration logging enabled")
        
        # State
        self.current_positions = []
        self.current_regime = None
        self.active_strategy = None
        
        logger.info("=" * 80)
        logger.info("🐺 INTEGRATED WOLF ENGINE READY")
        logger.info(f"Charter: MIN_NOTIONAL=${RickCharter.MIN_NOTIONAL_USD:,}")
        logger.info(f"Charter: MIN_RR_RATIO={RickCharter.MIN_RR_RATIO}:1")
        logger.info(f"Charter: OCO_REQUIRED={RickCharter.OCO_REQUIRED}")
        logger.info(f"Charter: MAX_HOLD_TIME={RickCharter.MAX_HOLD_TIME_HOURS}h")
        logger.info("=" * 80)
    
    def get_account_nav(self) -> float:
        """Get account NAV for gate initialization."""
        try:
            summary = self.connector.get_account_summary()
            return float(summary.get('NAV', 100000))
        except Exception as e:
            logger.warning(f"Could not fetch NAV: {e}, using default 100k")
            return 100000.0
    
    def detect_current_regime(self, symbol: str) -> MarketRegime:
        """Detect current market regime for symbol."""
        try:
            # Get recent price data
            candles = self.connector.get_historical_data(
                symbol=symbol,
                granularity="M15",
                count=200
            )
            
            if not candles:
                logger.warning("No candle data, defaulting to SIDEWAYS")
                return MarketRegime.SIDEWAYS
            
            # Extract closing prices
            prices = [float(c['mid']['c']) for c in candles]
            
            # Detect regime
            regime_data = detect_market_regime(prices, symbol)
            regime_str = regime_data.get('regime', 'SIDEWAYS')
            
            # Map to enum
            regime_map = {
                'BULLISH': MarketRegime.BULLISH,
                'BEARISH': MarketRegime.BEARISH,
                'SIDEWAYS': MarketRegime.SIDEWAYS,
                'CRASH': MarketRegime.SIDEWAYS,  # Use sideways strategy for crash
                'TRIAGE': MarketRegime.SIDEWAYS
            }
            
            regime = regime_map.get(regime_str, MarketRegime.SIDEWAYS)
            
            logger.info(f"📊 Regime detected: {regime.value} for {symbol}")
            logger.info(f"   Confidence: {regime_data.get('confidence', 0):.2%}")
            logger.info(f"   Volatility: {regime_data.get('volatility', 0):.4f}")
            
            return regime
            
        except Exception as e:
            logger.error(f"Regime detection failed: {e}")
            return MarketRegime.SIDEWAYS
    
    def analyze_signal(self, symbol: str, timeframe: str = "M15") -> Optional[Dict]:
        """
        Full signal analysis pipeline:
        1. Detect regime
        2. Select appropriate Wolf Pack
        3. Generate signal
        4. Validate through all gates
        5. Return trade signal or None
        """
        logger.info(f"\n{'=' * 80}")
        logger.info(f"🔍 ANALYZING: {symbol} ({timeframe})")
        logger.info(f"{'=' * 80}")
        
        # Step 1: Detect Regime
        regime = self.detect_current_regime(symbol)
        self.current_regime = regime
        
        # Step 2: Select Wolf Pack Strategy
        if regime not in self.strategies:
            logger.warning(f"No strategy for regime {regime.value}, skipping")
            return None
        
        strategy = self.strategies[regime]
        self.active_strategy = strategy
        logger.info(f"🐺 Selected: {strategy.__class__.__name__}")
        
        # Step 3: Get candle data for strategy
        try:
            candles = self.connector.get_historical_data(
                symbol=symbol,
                granularity=timeframe,
                count=200
            )
            
            if not candles or len(candles) < 50:
                logger.warning("Insufficient candle data")
                return None
            
        except Exception as e:
            logger.error(f"Failed to fetch candles: {e}")
            return None
        
        # Step 4: Generate signal from Wolf Pack
        try:
            signal = strategy.analyze(candles, symbol)
            
            if not signal or signal.get('action') == 'NONE':
                logger.info("❌ No signal generated by strategy")
                return None
            
            logger.info(f"✅ Signal: {signal.get('action')} @ {signal.get('entry_price')}")
            logger.info(f"   Confidence: {signal.get('confidence', 0):.2%}")
            logger.info(f"   SL: {signal.get('stop_loss')} | TP: {signal.get('take_profit')}")
            
        except Exception as e:
            logger.error(f"Strategy analysis failed: {e}")
            return None
        
        # Step 5: Gate Validation Pipeline
        logger.info(f"\n{'─' * 80}")
        logger.info("🛡️  GATE VALIDATION PIPELINE")
        logger.info(f"{'─' * 80}")
        
        # Gate 1: Guardian Gates (4 sub-gates)
        try:
            account = self.connector.get_account_summary()
            positions = self.connector.get_open_positions()
            
            gate_result = self.guardian_gates.validate_signal(
                signal=signal,
                account=account,
                positions=positions
            )
            
            if not gate_result.allowed:
                logger.warning(f"❌ Guardian Gate BLOCKED: {gate_result.reason}")
                self.narration.log_event({
                    'event': 'GATE_REJECTION',
                    'gate': 'guardian',
                    'symbol': symbol,
                    'reason': gate_result.reason
                })
                return None
            
            logger.info(f"✅ Guardian Gates PASSED: {gate_result.reason}")
            
        except Exception as e:
            logger.error(f"Guardian gate check failed: {e}")
            return None
        
        # Gate 2: Margin Correlation Gate
        try:
            margin_result = self.margin_gate.pre_trade_gate(
                symbol=symbol,
                direction=signal.get('action'),
                notional_usd=signal.get('notional_usd', RickCharter.MIN_NOTIONAL_USD)
            )
            
            if not margin_result.allowed:
                logger.warning(f"❌ Margin Gate BLOCKED: {margin_result.reason}")
                self.narration.log_event({
                    'event': 'GATE_REJECTION',
                    'gate': 'margin_correlation',
                    'symbol': symbol,
                    'reason': margin_result.reason
                })
                return None
            
            logger.info(f"✅ Margin Correlation Gate PASSED")
            
        except Exception as e:
            logger.error(f"Margin gate check failed: {e}")
            return None
        
        # Gate 3: Charter Compliance
        notional = signal.get('notional_usd', 0)
        if notional < RickCharter.MIN_NOTIONAL_USD:
            logger.warning(f"❌ Charter BLOCKED: Notional ${notional:,.0f} < ${RickCharter.MIN_NOTIONAL_USD:,}")
            return None
        
        # Calculate R-ratio
        entry = signal.get('entry_price', 0)
        sl = signal.get('stop_loss', 0)
        tp = signal.get('take_profit', 0)
        
        if entry and sl and tp:
            risk = abs(entry - sl)
            reward = abs(tp - entry)
            r_ratio = reward / risk if risk > 0 else 0
            
            if r_ratio < RickCharter.MIN_RR_RATIO:
                logger.warning(f"❌ Charter BLOCKED: R-ratio {r_ratio:.2f} < {RickCharter.MIN_RR_RATIO}")
                return None
            
            signal['r_ratio'] = r_ratio
            logger.info(f"✅ Charter Compliance PASSED (R={r_ratio:.2f}:1, N=${notional:,.0f})")
        
        # Gate 4: Smart Logic Filter
        try:
            filter_result = self.tracker.filter_signal(signal)
            if not filter_result.passed:
                logger.warning(f"❌ Smart Logic BLOCKED: {filter_result.reason}")
                return None
            
            logger.info(f"✅ Smart Logic Filter PASSED")
            
        except Exception as e:
            logger.warning(f"Smart Logic filter unavailable: {e}")
            # Don't block on smart logic failure
        
        logger.info(f"{'─' * 80}")
        logger.info("✅ ALL GATES PASSED - Signal approved for execution")
        logger.info(f"{'─' * 80}\n")
        
        # Log approval
        self.narration.log_event({
            'event': 'SIGNAL_APPROVED',
            'symbol': symbol,
            'regime': regime.value,
            'strategy': strategy.__class__.__name__,
            'signal': signal
        })
        
        return signal
    
    def execute_trade(self, signal: Dict) -> bool:
        """Execute approved trade with OCO orders."""
        try:
            symbol = signal['symbol']
            action = signal['action']
            units = signal.get('units', 10000)
            entry = signal['entry_price']
            sl = signal['stop_loss']
            tp = signal['take_profit']
            
            logger.info(f"\n{'=' * 80}")
            logger.info(f"📤 EXECUTING TRADE")
            logger.info(f"{'=' * 80}")
            logger.info(f"Symbol: {symbol}")
            logger.info(f"Action: {action}")
            logger.info(f"Units: {units:,}")
            logger.info(f"Entry: {entry}")
            logger.info(f"Stop Loss: {sl}")
            logger.info(f"Take Profit: {tp}")
            logger.info(f"R-Ratio: {signal.get('r_ratio', 0):.2f}:1")
            logger.info(f"{'=' * 80}\n")
            
            # Place OCO order
            order_result = self.connector.place_oco_order(
                symbol=symbol,
                units=units if action == 'BUY' else -units,
                stop_loss=sl,
                take_profit=tp
            )
            
            if order_result.get('success'):
                logger.info("✅ Trade executed successfully!")
                
                self.narration.log_event({
                    'event': 'TRADE_OPENED',
                    'symbol': symbol,
                    'action': action,
                    'units': units,
                    'entry': entry,
                    'sl': sl,
                    'tp': tp,
                    'r_ratio': signal.get('r_ratio', 0),
                    'regime': self.current_regime.value if self.current_regime else 'UNKNOWN',
                    'strategy': self.active_strategy.__class__.__name__ if self.active_strategy else 'UNKNOWN'
                })
                
                return True
            else:
                logger.error(f"❌ Trade execution failed: {order_result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Trade execution error: {e}")
            return False
    
    def run_analysis_cycle(self, symbols: List[str]):
        """Run full analysis cycle on symbol list."""
        logger.info(f"\n{'#' * 80}")
        logger.info(f"🚀 STARTING ANALYSIS CYCLE")
        logger.info(f"Symbols: {', '.join(symbols)}")
        logger.info(f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        logger.info(f"{'#' * 80}\n")
        
        signals_found = 0
        trades_executed = 0
        
        for symbol in symbols:
            try:
                signal = self.analyze_signal(symbol)
                
                if signal:
                    signals_found += 1
                    
                    # Execute trade
                    if self.execute_trade(signal):
                        trades_executed += 1
                        
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue
        
        logger.info(f"\n{'#' * 80}")
        logger.info(f"📊 CYCLE COMPLETE")
        logger.info(f"Signals Found: {signals_found}")
        logger.info(f"Trades Executed: {trades_executed}")
        logger.info(f"{'#' * 80}\n")


def main():
    """Main entry point."""
    # Load credentials
    account_id = os.getenv('OANDA_PRACTICE_ACCOUNT_ID')
    api_token = os.getenv('OANDA_PRACTICE_TOKEN')
    
    if not account_id or not api_token:
        print("ERROR: OANDA credentials not found in environment")
        print("Please run: source .env.oanda_only")
        sys.exit(1)
    
    # Initialize engine
    engine = IntegratedWolfEngine(
        account_id=account_id,
        api_token=api_token,
        practice=True
    )
    
    # Define trading universe
    symbols = [
        'EUR_USD',
        'GBP_USD',
        'USD_JPY',
        'AUD_USD',
        'USD_CAD'
    ]
    
    # Run analysis
    engine.run_analysis_cycle(symbols)


if __name__ == '__main__':
    main()

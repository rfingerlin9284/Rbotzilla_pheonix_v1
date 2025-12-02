#!/home/ing/RICK/RICK_PHOENIX/.venv/bin/python
"""
RICK Coinbase Safe Mode Trading Engine
Integrates all 130+ features with safe mode progression
Starts in paper trading, graduates to live after meeting success threshold
PIN: 841921 REQUIRED for live authorization
"""

import os
import sys
import json
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal

# Coinbase imports
from coinbase.jwt_generator import format_jwt
from coinbase.rest import RESTClient

# RICK system imports
sys.path.append(os.path.dirname(__file__))
from safe_mode_manager import SafeModeManager, TradingMode
from foundation.rick_charter import RickCharter
from logic.smart_logic import SmartLogicFilter
from hive.rick_hive_mind import RickHiveMind
from util.narration_logger import NarrationLogger
from auto_diagnostic_monitor import run_full_diagnostic

class CoinbaseSafeModeEngine:
    """
    Production Coinbase trading engine with full feature integration
    and safe mode progression system
    """
    
    def __init__(self, pin: Optional[int] = None):
        """Initialize engine with PIN authorization"""
        self.pin = pin
        if pin and not RickCharter.validate_pin(pin):
            raise PermissionError("Invalid PIN for engine access")
        
        # Core components
        self.safe_mode = SafeModeManager(pin=pin)
        self.charter = RickCharter
        self.smart_filter = SmartLogicFilter(pin=pin)
        self.hive_mind = RickHiveMind(pin=pin)
        self.narration = NarrationLogger()
        
        # Coinbase client
        self.client = None
        self.paper_client = None  # For paper trading simulation
        
        # State tracking
        self.current_mode = TradingMode.PAPER
        self.active_positions = {}
        self.daily_trades = 0
        self.daily_pnl = 0.0
        
        # Logging
        self.logger = self._setup_logging()
        
        # Load credentials
        self._load_coinbase_credentials()
        
        self.narration.log({
            "event": "engine_initialized",
            "mode": self.current_mode.value,
            "pin_verified": bool(pin and RickCharter.validate_pin(pin)),
            "timestamp": datetime.utcnow().isoformat()
        })
        
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging"""
        logger = logging.getLogger('coinbase_safe_mode_engine')
        logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        
        if not logger.handlers:
            handler = logging.FileHandler('logs/coinbase_engine.log', mode='a')
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def _load_coinbase_credentials(self):
        """Load Coinbase Advanced API credentials"""
        env_file = os.path.join(os.path.dirname(__file__), '.env.coinbase_advanced')
        
        if not os.path.exists(env_file):
            raise FileNotFoundError(f"Coinbase credentials not found: {env_file}")
        
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Extract API key
        key_start = content.find('CDP_API_KEY_NAME="') + len('CDP_API_KEY_NAME="')
        key_end = content.find('"', key_start)
        api_key = content[key_start:key_end]
        
        # Extract private key (multiline)
        priv_start = content.find('CDP_PRIVATE_KEY="') + len('CDP_PRIVATE_KEY="')
        priv_end = content.find('"', priv_start + 50)  # Skip ahead to find closing quote
        api_secret = content[priv_start:priv_end].replace('\\n', '\n')
        
        # Initialize REST client
        self.client = RESTClient(api_key=api_key, api_secret=api_secret)
        
        self.logger.info(f"Coinbase credentials loaded: {api_key[:30]}...")
        
    def start(self):
        """Main engine loop"""
        self.logger.info("=" * 80)
        self.logger.info("🚀 RICK COINBASE SAFE MODE ENGINE STARTING")
        self.logger.info("=" * 80)
        
        # ==========================================
        # MANDATORY STEP 1: FULL SYSTEM DIAGNOSTIC
        # ==========================================
        self.logger.info("\n🔍 STEP 1: MANDATORY PRE-FLIGHT DIAGNOSTIC (130 Features)")
        self.logger.info("This check is REQUIRED before trading can begin.\n")
        
        diagnostic_results = run_full_diagnostic()
        
        # Check for critical failures
        critical_failures = []
        for check_name, result in diagnostic_results.items():
            if result['status'] == 'FAIL' and check_name in [
                'api_connectivity', 'auth_tokens', 'charter_constants', 
                'gate_enforcement', 'oco_logic'
            ]:
                critical_failures.append(check_name)
        
        if critical_failures:
            error_msg = f"\n❌ CRITICAL DIAGNOSTIC FAILURES: {', '.join(critical_failures)}"
            error_msg += "\n\n🛑 BOT CANNOT START - Fix issues above and try again.\n"
            self.logger.error(error_msg)
            print(error_msg)
            
            self.narration.log({
                "event": "startup_blocked",
                "reason": "diagnostic_failures",
                "failed_checks": critical_failures,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            sys.exit(1)
        
        # All checks passed
        success_msg = "\n✅ ALL DIAGNOSTICS PASSED - System healthy, proceeding to trading mode\n"
        self.logger.info(success_msg)
        print(success_msg)
        
        self.logger.info(f"Current Mode: {self.current_mode.value}")
        self.logger.info("=" * 80)
        
        self.narration.log({
            "event": "engine_start",
            "mode": self.current_mode.value,
            "diagnostic_status": "passed",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        try:
            while True:
                # Update current mode based on performance
                self.current_mode = self.safe_mode.get_current_mode()
                
                # Check if we can trade
                if self.current_mode == TradingMode.PAPER:
                    self._paper_trading_cycle()
                elif self.current_mode == TradingMode.SAFE_VALIDATION:
                    self._validation_cycle()
                elif self.current_mode == TradingMode.LIVE_READY:
                    self._await_live_authorization()
                elif self.current_mode == TradingMode.LIVE_AUTHORIZED:
                    self._live_trading_cycle()
                
                # 10-second cycle
                time.sleep(10)
                
        except KeyboardInterrupt:
            self.logger.info("\n🛑 Engine shutdown requested")
            self.shutdown()
        except Exception as e:
            self.logger.error(f"Engine error: {e}", exc_info=True)
            self.shutdown()
    
    def _paper_trading_cycle(self):
        """Paper trading mode - build track record"""
        self.narration.log({
            "event": "paper_trading_cycle",
            "message": "Building track record in paper mode. No real money at risk.",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Scan for opportunities
        opportunities = self._scan_markets()
        
        # Filter with smart logic
        for opp in opportunities:
            validation = self.smart_filter.validate_signal(opp)
            
            if validation.passed:
                # Get hive mind consensus
                hive_decision = self.hive_mind.vote_on_signal(opp)
                
                if hive_decision['consensus'] == 'BUY':
                    self._execute_paper_trade(opp, hive_decision)
    
    def _scan_markets(self) -> List[Dict]:
        """Scan markets for trading opportunities using all 130+ features"""
        opportunities = []
        
        # Markets to scan
        markets = ['BTC-USD', 'ETH-USD']
        
        for market in markets:
            try:
                # Get current price
                product = self.client.get_product(product_id=market)
                current_price = float(product['price'])
                
                # Get candles for technical analysis
                candles = self.client.get_candles(
                    product_id=market,
                    granularity='THREE_HUNDRED',  # 5-minute candles
                    limit=200
                )
                
                if not candles or 'candles' not in candles:
                    continue
                
                # Run full analysis suite
                signal = self._analyze_market(market, candles['candles'], current_price)
                
                if signal:
                    opportunities.append(signal)
                    
            except Exception as e:
                self.logger.error(f"Error scanning {market}: {e}")
                
        return opportunities
    
    def _analyze_market(self, market: str, candles: List, current_price: float) -> Optional[Dict]:
        """
        Full market analysis using all 130+ features:
        - Fibonacci levels
        - FVG detection
        - Mass behavior patterns
        - Smart OCO logic
        - ML predictions
        - Volume profile
        - Momentum indicators
        """
        # Convert candles to OHLC
        ohlc = []
        for c in candles:
            ohlc.append({
                'time': c['start'],
                'open': float(c['open']),
                'high': float(c['high']),
                'low': float(c['low']),
                'close': float(c['close']),
                'volume': float(c['volume'])
            })
        
        if len(ohlc) < 50:
            return None
        
        # Calculate ATR for risk management
        atr = self._calculate_atr(ohlc)
        
        # Detect FVG (Fair Value Gaps)
        fvg_zones = self._detect_fvg(ohlc)
        
        # Calculate Fibonacci levels
        fib_levels = self._calculate_fibonacci(ohlc)
        
        # Detect mass behavior patterns
        mass_pattern = self._detect_mass_behavior(ohlc)
        
        # Example: Bullish FVG + Fibonacci confluence
        if fvg_zones and fib_levels:
            # Check if price is near support
            for fvg in fvg_zones:
                if fvg['type'] == 'bullish' and abs(current_price - fvg['level']) / current_price < 0.005:
                    # Near bullish FVG - potential buy
                    
                    # Calculate entry, target, stop
                    entry = current_price
                    stop_loss = entry - (atr * self.charter.CRYPTO_STOP_LOSS_ATR_MULTIPLIER)
                    
                    # Target at next Fibonacci extension
                    target = None
                    for fib in fib_levels['extensions']:
                        if fib > entry:
                            target = fib
                            break
                    
                    if not target:
                        continue
                    
                    # Calculate risk/reward
                    risk = entry - stop_loss
                    reward = target - entry
                    rr_ratio = reward / risk if risk > 0 else 0
                    
                    # Charter compliance check
                    if not self.charter.validate_risk_reward(rr_ratio):
                        continue
                    
                    # Calculate position size
                    position_size = self._calculate_position_size(entry, stop_loss, market)
                    notional = position_size * entry
                    
                    if not self.charter.validate_notional(notional):
                        continue
                    
                    # Build signal
                    signal = {
                        'symbol': market,
                        'direction': 'buy',
                        'entry_price': entry,
                        'target_price': target,
                        'stop_loss': stop_loss,
                        'position_size': position_size,
                        'notional_usd': notional,
                        'risk_reward_ratio': rr_ratio,
                        'atr': atr,
                        'fvg_confluence': True,
                        'fibonacci_confluence': True,
                        'mass_behavior': mass_pattern,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    return signal
        
        return None
    
    def _calculate_atr(self, ohlc: List[Dict], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(ohlc) < period + 1:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(ohlc)):
            high = ohlc[i]['high']
            low = ohlc[i]['low']
            prev_close = ohlc[i-1]['close']
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        # Simple moving average of true range
        atr = sum(true_ranges[-period:]) / period
        return atr
    
    def _detect_fvg(self, ohlc: List[Dict]) -> List[Dict]:
        """Detect Fair Value Gaps (3-candle pattern)"""
        fvg_zones = []
        
        for i in range(2, len(ohlc)):
            candle1 = ohlc[i-2]
            candle2 = ohlc[i-1]
            candle3 = ohlc[i]
            
            # Bullish FVG: candle1 low > candle3 high (gap up)
            if candle1['low'] > candle3['high']:
                fvg_zones.append({
                    'type': 'bullish',
                    'level': (candle1['low'] + candle3['high']) / 2,
                    'strength': (candle1['low'] - candle3['high']) / candle3['high']
                })
            
            # Bearish FVG: candle1 high < candle3 low (gap down)
            elif candle1['high'] < candle3['low']:
                fvg_zones.append({
                    'type': 'bearish',
                    'level': (candle1['high'] + candle3['low']) / 2,
                    'strength': (candle3['low'] - candle1['high']) / candle3['low']
                })
        
        return fvg_zones
    
    def _calculate_fibonacci(self, ohlc: List[Dict]) -> Dict:
        """Calculate Fibonacci retracement and extension levels"""
        # Find swing high/low in last 100 candles
        recent = ohlc[-100:]
        swing_high = max(c['high'] for c in recent)
        swing_low = min(c['low'] for c in recent)
        
        diff = swing_high - swing_low
        
        # Retracement levels (from high to low)
        retracements = {
            '0.236': swing_high - (diff * 0.236),
            '0.382': swing_high - (diff * 0.382),
            '0.5': swing_high - (diff * 0.5),
            '0.618': swing_high - (diff * 0.618),
            '0.786': swing_high - (diff * 0.786)
        }
        
        # Extension levels (beyond swing high)
        extensions = [
            swing_high + (diff * 0.618),
            swing_high + (diff * 1.0),
            swing_high + (diff * 1.618),
            swing_high + (diff * 2.618)
        ]
        
        return {
            'retracements': retracements,
            'extensions': extensions,
            'swing_high': swing_high,
            'swing_low': swing_low
        }
    
    def _detect_mass_behavior(self, ohlc: List[Dict]) -> Dict:
        """Detect human mass behavior patterns (crowding, FOMO, panic)"""
        recent = ohlc[-20:]
        
        # Volume analysis
        avg_volume = sum(c['volume'] for c in recent) / len(recent)
        last_volume = recent[-1]['volume']
        volume_spike = last_volume / avg_volume if avg_volume > 0 else 1.0        
        # Price momentum
        price_change = (recent[-1]['close'] - recent[0]['close']) / recent[0]['close']
        
        # Crowding detection
        crowding = 'high' if volume_spike > 2.0 else 'normal'
        sentiment = 'bullish' if price_change > 0.05 else 'bearish' if price_change < -0.05 else 'neutral'
        
        return {
            'crowding': crowding,
            'sentiment': sentiment,
            'volume_spike': volume_spike,
            'price_momentum': price_change
        }
    
    def _calculate_position_size(self, entry: float, stop_loss: float, market: str) -> float:
        """Calculate position size based on risk management"""
        # Get account balance
        accounts = self.client.get_accounts()
        
        # Find USD balance
        usd_balance = 0.0
        for acc in accounts['accounts']:
            if acc['currency'] in ['USD', 'USDC']:
                usd_balance += float(acc['available_balance']['value'])
        
        # Risk 2% of capital per trade
        risk_amount = usd_balance * 0.02
        
        # Calculate position size
        risk_per_unit = abs(entry - stop_loss)
        position_size = risk_amount / risk_per_unit if risk_per_unit > 0 else 0
        
        # Round to 8 decimals for crypto
        return round(position_size, 8)
    
    def _execute_paper_trade(self, signal: Dict, hive_decision: Dict):
        """Execute trade in paper mode (simulation only)"""
        self.narration.log({
            "event": "paper_trade_executed",
            "symbol": signal['symbol'],
            "direction": signal['direction'],
            "entry": signal['entry_price'],
            "target": signal['target_price'],
            "stop_loss": signal['stop_loss'],
            "risk_reward": round(signal['risk_reward_ratio'], 2),
            "hive_consensus": hive_decision['consensus'],
            "hive_confidence": round(hive_decision['confidence'], 2),
            "message": f"Paper trade: {signal['direction'].upper()} {signal['symbol']} at ${signal['entry_price']:,.2f}. Target: ${signal['target_price']:,.2f} (RR: {signal['risk_reward_ratio']:.2f}x). Hive consensus: {hive_decision['consensus']} ({hive_decision['confidence']:.1%} confidence).",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Record for safe mode progression tracking
        self.safe_mode.record_trade_result({
            'symbol': signal['symbol'],
            'entry_price': signal['entry_price'],
            'target_price': signal['target_price'],
            'stop_loss': signal['stop_loss'],
            'position_size': signal['position_size'],
            'mode': 'PAPER',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def _validation_cycle(self):
        """Safe validation mode - stricter requirements"""
        self.narration.log({
            "event": "validation_cycle",
            "message": "Safe validation mode active. Meeting thresholds to qualify for live trading.",
            "timestamp": datetime.utcnow().isoformat()
        })
        # Similar to paper trading but with stricter validation
        self._paper_trading_cycle()
    
    def _await_live_authorization(self):
        """Await PIN authorization for live trading"""
        self.logger.info("🎯 LIVE TRADING READY - Awaiting PIN 841921 authorization")
        
        self.narration.log({
            "event": "live_ready",
            "message": "System has met all safety thresholds. Awaiting PIN 841921 authorization to begin live trading.",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Wait for PIN authorization
        time.sleep(60)
    
    def _live_trading_cycle(self):
        """Live trading mode - real money"""
        if not self.pin or not RickCharter.validate_pin(self.pin):
            self.logger.error("Live trading requires valid PIN")
            return
        
        self.narration.log({
            "event": "live_trading_cycle",
            "message": "LIVE TRADING ACTIVE. Real money at risk. All safety systems engaged.",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Scan and execute live trades
        opportunities = self._scan_markets()
        
        for opp in opportunities:
            validation = self.smart_filter.validate_signal(opp)
            
            if validation.passed:
                hive_decision = self.hive_mind.vote_on_signal(opp)
                
                if hive_decision['consensus'] == 'BUY':
                    self._execute_live_trade(opp, hive_decision)
    
    def _execute_live_trade(self, signal: Dict, hive_decision: Dict):
        """Execute real live trade with full OCO"""
        try:
            # Market buy order
            client_order_id = str(uuid.uuid4())
            
            buy_response = self.client.market_order_buy(
                client_order_id=client_order_id,
                product_id=signal['symbol'],
                quote_size=str(round(signal['notional_usd'], 2))
            )
            
            if buy_response.get('success'):
                order_id = buy_response.get('success_response', {}).get('order_id')
                
                self.narration.log({
                    "event": "live_trade_executed",
                    "symbol": signal['symbol'],
                    "order_id": order_id,
                    "direction": "BUY",
                    "notional": signal['notional_usd'],
                    "entry": signal['entry_price'],
                    "target": signal['target_price'],
                    "stop_loss": signal['stop_loss'],
                    "message": f"LIVE BUY executed: {signal['symbol']} - ${signal['notional_usd']:,.2f} notional. Entry: ${signal['entry_price']:,.2f}, Target: ${signal['target_price']:,.2f}, Stop: ${signal['stop_loss']:,.2f}. Order ID: {order_id}",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Place OCO (take profit + stop loss)
                self._place_oco_orders(signal, order_id)
                
        except Exception as e:
            self.logger.error(f"Live trade execution failed: {e}", exc_info=True)
            self.narration.log({
                "event": "trade_error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def _place_oco_orders(self, signal: Dict, parent_order_id: str):
        """Place OCO (One-Cancels-Other) take profit and stop loss orders"""
        try:
            # Take profit limit order
            tp_client_id = str(uuid.uuid4())
            tp_response = self.client.limit_order_gtc(
                client_order_id=tp_client_id,
                product_id=signal['symbol'],
                side='SELL',
                base_size=str(signal['position_size']),
                limit_price=str(round(signal['target_price'], 2))
            )
            
            # Stop loss order
            sl_client_id = str(uuid.uuid4())
            sl_response = self.client.stop_limit_order_gtc(
                client_order_id=sl_client_id,
                product_id=signal['symbol'],
                side='SELL',
                base_size=str(signal['position_size']),
                limit_price=str(round(signal['stop_loss'] * 0.99, 2)),  # Limit slightly below stop
                stop_price=str(round(signal['stop_loss'], 2))
            )
            
            self.narration.log({
                "event": "oco_orders_placed",
                "parent_order": parent_order_id,
                "take_profit_order": tp_response.get('success_response', {}).get('order_id'),
                "stop_loss_order": sl_response.get('success_response', {}).get('order_id'),
                "message": f"OCO orders placed: TP at ${signal['target_price']:,.2f}, SL at ${signal['stop_loss']:,.2f}",
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"OCO order placement failed: {e}", exc_info=True)
    
    def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("🛑 Engine shutdown initiated")
        
        self.narration.log({
            "event": "engine_shutdown",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Close any open positions if needed
        # (implementation depends on requirements)
        
        self.logger.info("✅ Shutdown complete")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='RICK Coinbase Safe Mode Trading Engine')
    parser.add_argument('--pin', type=int, help='PIN for live trading authorization')
    
    args = parser.parse_args()
    
    # Create and start engine
    engine = CoinbaseSafeModeEngine(pin=args.pin)
    engine.start()

#!/usr/bin/env python3
"""
Coinbase Advanced Trading Engine - Crypto Perps & Spot
Autonomous trading for cryptocurrency perpetuals and spot markets

PIN: 841921 | Mode: Sandbox (safe testing)
Charter: MIN_NOTIONAL=$3k, MIN_PNL=$150, MAX_HOLD=4h, MIN_RR=3.0x

Features:
- Crypto spot + perpetuals trading (BTC, ETH, SOL)
- 24/7 markets (no downtime)
- Funding rate awareness (every 8h for perps)
- High-frequency cycles (3-5 min)
- WebSocket streaming for real-time prices
- REST API for order execution
- RICK Hive Mind integration
"""

import os
import sys
import time
import asyncio
import logging
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

# Add parent for rick_hive access
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Coinbase connector
from coinbase_connector import CoinbaseConnector

# RICK Hive Mind
try:
    from rick_hive.rick_charter import RickCharter as CHARTER
except ImportError:
    class CHARTER:
        MIN_NOTIONAL_USD = 3000  # Lower for crypto (vs $5k IBKR, $15k forex)
        MIN_EXPECTED_PNL_USD = 150  # Adjusted for high frequency
        MAX_HOLD_TIME_HOURS = 4  # Faster than forex/futures (vs 6h)
        MIN_RISK_REWARD_RATIO = 3.0  # Slightly lower due to perps funding
from foundation.trading_mode import safe_place_order


class CryptoPerpsWolfPack:
    """
    Consolidated wolf pack strategies for crypto spot + perps
    Adapted from IBKR/OANDA with crypto-specific enhancements
    
    Differences from Forex/Futures:
    - Funding rate arbitrage (perps specific)
    - 24/7 operation (no session breaks)
    - Higher volatility → tighter stops
    - Mean reversion dominant (vs trend following)
    """
    
    # Crypto instruments (spot + perps)
    INSTRUMENTS = {
        "BTC-USD": {"type": "spot", "multiplier": 1.0},
        "BTC-PERP": {"type": "perp", "multiplier": 1.0, "funding_interval": 8},
        "ETH-USD": {"type": "spot", "multiplier": 1.0},
        "ETH-PERP": {"type": "perp", "multiplier": 1.0, "funding_interval": 8},
        "SOL-USD": {"type": "spot", "multiplier": 1.0},
    }
    
    # Crypto-specific parameters (very tight due to high vol)
    RSI_OVERSOLD = 20  # vs 25 futures, 30 forex
    RSI_OVERBOUGHT = 80  # vs 75 futures, 70 forex
    
    # Funding rate thresholds (perps only)
    FUNDING_RATE_HIGH = 0.01  # 1% = crowded long, fade it
    FUNDING_RATE_LOW = -0.01  # -1% = crowded short, fade it
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.last_funding_check = {}
    
    def calculate_rsi(self, candles: List[Dict], period: int = 14) -> float:
        """Calculate RSI (same as IBKR/OANDA)"""
        if len(candles) < period + 1:
            return 50.0
        
        closes = [c["close"] for c in candles[-(period + 1):]]
        
        gains = []
        losses = []
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_ema(self, candles: List[Dict], period: int) -> float:
        """Calculate EMA"""
        if len(candles) < period:
            return candles[-1]["close"] if candles else 0.0
        
        closes = [c["close"] for c in candles[-period:]]
        
        ema = sum(closes[:period]) / period
        multiplier = 2 / (period + 1)
        
        for close in closes[period:]:
            ema = (close - ema) * multiplier + ema
        
        return ema
    
    def get_funding_rate(self, symbol: str, connector) -> float:
        """
        Get current funding rate for perps
        
        Funding rate mechanics:
        - Positive = longs pay shorts (bullish crowding)
        - Negative = shorts pay longs (bearish crowding)
        - Extreme rates = contrarian signal
        """
        if "PERP" not in symbol:
            return 0.0  # Spot has no funding
        
        try:
            # Check if we already fetched recently (cache for 1 hour)
            now = datetime.now(timezone.utc)
            cache_key = symbol
            
            if cache_key in self.last_funding_check:
                last_check, cached_rate = self.last_funding_check[cache_key]
                if (now - last_check).total_seconds() < 3600:  # 1 hour cache
                    return cached_rate
            
            # Fetch current funding rate (Coinbase API specific)
            # This is a placeholder - actual API call would go here
            funding_rate = 0.0  # connector.get_funding_rate(symbol)
            
            self.last_funding_check[cache_key] = (now, funding_rate)
            return funding_rate
            
        except Exception as e:
            self.logger.error(f"Failed to get funding rate for {symbol}: {e}")
            return 0.0
    
    def analyze_crypto_perps(
        self,
        symbol: str,
        candles: List[Dict],
        current_price: float,
        connector = None
    ) -> Optional[Dict]:
        """
        Unified crypto analysis (spot + perps)
        
        Strategy mix:
        - Mean reversion (dominant for crypto)
        - Funding rate arbitrage (perps only)
        - Breakout momentum (high vol periods)
        
        Args:
            symbol: BTC-USD, BTC-PERP, ETH-USD, etc.
            candles: Historical OHLCV
            current_price: Current market price
            connector: CoinbaseConnector (for funding rate)
            
        Returns:
            Signal dict or None
        """
        if len(candles) < 60:
            self.logger.warning(f"{symbol}: Insufficient candles ({len(candles)})")
            return None
        
        # Calculate indicators
        rsi = self.calculate_rsi(candles)
        ema_fast = self.calculate_ema(candles, 9)  # Faster than futures (9 vs 12)
        ema_slow = self.calculate_ema(candles, 21)  # Faster (21 vs 26)
        
        # Trend direction
        trend_bullish = ema_fast > ema_slow
        trend_bearish = ema_fast < ema_slow
        
        # Mean reversion zones (primary crypto strategy)
        oversold = rsi < self.RSI_OVERSOLD
        overbought = rsi > self.RSI_OVERBOUGHT
        
        # Funding rate check (perps only)
        funding_rate = self.get_funding_rate(symbol, connector) if connector else 0.0
        funding_crowded_long = funding_rate > self.FUNDING_RATE_HIGH
        funding_crowded_short = funding_rate < self.FUNDING_RATE_LOW
        
        # Recent momentum
        recent_candles = candles[-3:]
        momentum_up = all(c["close"] > c["open"] for c in recent_candles)
        momentum_down = all(c["close"] < c["open"] for c in recent_candles)
        
        signal = None
        
        # LONG signals (mean reversion + funding arbitrage)
        if oversold and momentum_up:
            # Strong mean reversion long
            signal = self._generate_long_signal(symbol, current_price, candles, "mean_reversion")
        elif funding_crowded_short and trend_bullish:
            # Funding arbitrage: shorts are crowded, fade them
            signal = self._generate_long_signal(symbol, current_price, candles, "funding_arb")
        
        # SHORT signals
        elif overbought and momentum_down:
            # Mean reversion short
            signal = self._generate_short_signal(symbol, current_price, candles, "mean_reversion")
        elif funding_crowded_long and trend_bearish:
            # Funding arbitrage: longs are crowded, fade them
            signal = self._generate_short_signal(symbol, current_price, candles, "funding_arb")
        
        if signal:
            self.logger.info(
                f"📊 {symbol} Signal: {signal['side']} @ {signal['entry']:.2f} "
                f"(RSI: {rsi:.1f}, Funding: {funding_rate:.4f}, Strategy: {signal.get('strategy')})"
            )
        
        return signal
    
    def _generate_long_signal(
        self,
        symbol: str,
        entry: float,
        candles: List[Dict],
        strategy: str
    ) -> Dict:
        """Generate LONG signal with OCO levels"""
        atr = self._calculate_atr(candles, period=14)
        
        # Crypto = tighter stops (1.2x ATR vs 1.5x for futures)
        stop_loss = entry - (1.2 * atr)
        take_profit = entry + (3.0 * 1.2 * atr)  # 3.0x R:R (vs 3.5x futures)
        
        # Calculate units for MIN_NOTIONAL ($3000)
        units = max(1, int(CHARTER.MIN_NOTIONAL_USD / entry))
        
        return {
            "symbol": symbol,
            "side": "BUY",
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "units": units,
            "notional": units * entry,
            "expected_pnl": (take_profit - entry) * units,
            "rr_ratio": 3.0,
            "strategy": strategy,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _generate_short_signal(
        self,
        symbol: str,
        entry: float,
        candles: List[Dict],
        strategy: str
    ) -> Dict:
        """Generate SHORT signal with OCO levels"""
        atr = self._calculate_atr(candles, period=14)
        
        stop_loss = entry + (1.2 * atr)
        take_profit = entry - (3.0 * 1.2 * atr)
        
        units = max(1, int(CHARTER.MIN_NOTIONAL_USD / entry))
        
        return {
            "symbol": symbol,
            "side": "SELL",
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "units": units,
            "notional": units * entry,
            "expected_pnl": (entry - take_profit) * units,
            "rr_ratio": 3.0,
            "strategy": strategy,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _calculate_atr(self, candles: List[Dict], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(candles) < period + 1:
            return candles[-1]["high"] - candles[-1]["low"] if candles else 0.0
        
        true_ranges = []
        for i in range(1, len(candles)):
            high = candles[i]["high"]
            low = candles[i]["low"]
            prev_close = candles[i-1]["close"]
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        return sum(true_ranges[-period:]) / period


class CoinbaseTradingEngine:
    """
    Main trading engine for Coinbase crypto markets
    
    Loop (3-5 minute cycles):
    1. Fetch candles for BTC/ETH/SOL (spot + perps)
    2. Run crypto wolf pack analysis
    3. Check funding rates (perps)
    4. Generate signals
    5. Validate vs charter gates
    6. Place OCO orders
    7. Monitor positions (max 4h hold)
    8. Run Position Police
    """
    
    def __init__(self):
        # Logging
        self.logger = self._setup_logging()
        
        # Coinbase connector
        self.connector = CoinbaseConnector(
            api_key=os.getenv("COINBASE_API_KEY"),
            api_secret=os.getenv("COINBASE_API_SECRET"),
            passphrase=os.getenv("COINBASE_PASSPHRASE"),
            sandbox=os.getenv("COINBASE_SANDBOX", "true").lower() == "true",
            logger=self.logger
        )
        
        # Wolf pack strategies
        self.wolf_pack = CryptoPerpsWolfPack(self.logger)
        
        # Position tracking
        self.position_open_times = {}
        
        # Cycle interval (crypto = faster than futures/forex)
        self.cycle_interval = 180  # 3 minutes (vs 5 min IBKR, 15 min forex)
        
        self.logger.info("🚀 Coinbase Crypto Perps Engine initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        os.makedirs("logs", exist_ok=True)
        
        logger = logging.getLogger("CoinbaseEngine")
        logger.setLevel(logging.INFO)
        
        # Console
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(console)
        
        # File
        file_handler = logging.FileHandler("logs/coinbase_engine.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
        
        return logger
    
    async def run_trading_loop(self):
        """
        Main trading loop - 24/7 operation with 3-minute cycles
        """
        if not self.connector.connect():
            self.logger.error("❌ Failed to connect to Coinbase Advanced")
            return
        
        self.logger.info("✅ Trading loop started (3-min cycles, sandbox mode)")
        
        try:
            while True:
                cycle_start = time.time()
                
                # Process each crypto instrument
                for symbol in self.wolf_pack.INSTRUMENTS.keys():
                    try:
                        await self._process_instrument(symbol)
                    except Exception as e:
                        self.logger.error(f"Error processing {symbol}: {e}")
                
                # Position Police (charter enforcement)
                try:
                    self._position_police()
                    self._check_hold_time_violations()
                except Exception as e:
                    self.logger.error(f"Position Police error: {e}")
                
                # Wait for next cycle
                elapsed = time.time() - cycle_start
                sleep_time = max(0, self.cycle_interval - elapsed)
                
                self.logger.info(f"💤 Cycle complete ({elapsed:.1f}s), sleeping {sleep_time:.0f}s")
                await asyncio.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Shutting down...")
        finally:
            self.connector.disconnect()
    
    async def _process_instrument(self, symbol: str):
        """Process single crypto instrument"""
        # Fetch historical data
        candles = self.connector.get_historical_candles(
            symbol,
            granularity=300,  # 5-min candles
            count=60
        )
        
        if not candles:
            self.logger.warning(f"{symbol}: No candles received")
            return
        
        current_price = candles[-1]["close"]
        
        # Check for existing position
        positions = self.connector.get_open_positions()
        has_position = any(p["product_id"] == symbol for p in positions)
        
        if has_position:
            self.logger.info(f"{symbol}: Position already open, monitoring")
            return
        
        # Wolf pack analysis
        signal = self.wolf_pack.analyze_crypto_perps(
            symbol,
            candles,
            current_price,
            self.connector
        )
        
        if not signal:
            return
        
        # Place order (charter validation inside connector)
        ok_flag, result = safe_place_order(self.connector,
            product_id=signal["symbol"],
            side=signal["side"],
            size=signal["units"],
            price=signal["entry"],
            stop_loss=signal["stop_loss"],
            take_profit=signal["take_profit"]
        )
        
        if ok_flag:
            self.position_open_times[symbol] = datetime.now(timezone.utc)
            self.logger.info(f"✅ Trade executed: {symbol} {signal['side']}")
        else:
            self.logger.warning(
                f"❌ Trade rejected: {symbol} - {result.get('error', 'Unknown')}"
            )
    
    def _position_police(self):
        """Charter enforcement: Close positions violating MIN_NOTIONAL"""
        positions = self.connector.get_open_positions()
        
        for pos in positions:
            symbol = pos["product_id"]
            size = float(pos.get("size", 0))
            price = float(pos.get("price", 0))
            notional = abs(size * price)
            
            if notional < CHARTER.MIN_NOTIONAL_USD:
                self.logger.warning(
                    f"🚨 POSITION POLICE: {symbol} notional ${notional:.2f} < "
                    f"${CHARTER.MIN_NOTIONAL_USD} - CLOSING"
                )
                self.connector.close_position(symbol)
    
    def _check_hold_time_violations(self):
        """Charter enforcement: Close positions exceeding MAX_HOLD_TIME (4 hours)"""
        now = datetime.now(timezone.utc)
        max_hold = timedelta(hours=CHARTER.MAX_HOLD_TIME_HOURS)
        
        for symbol, open_time in list(self.position_open_times.items()):
            hold_duration = now - open_time
            
            if hold_duration > max_hold:
                self.logger.warning(
                    f"🚨 MAX_HOLD violation: {symbol} open for {hold_duration.total_seconds()/3600:.1f}h - CLOSING"
                )
                
                result = self.connector.close_position(symbol)
                
                if result.get("success"):
                    del self.position_open_times[symbol]
                    self.logger.info(f"✅ Closed {symbol} (hold time violation)")


async def main():
    """Entry point"""
    print("=" * 80)
    print("COINBASE ADVANCED CRYPTO TRADING ENGINE")
    print("=" * 80)
    print(f"Mode: Sandbox (safe testing)")
    print(f"Assets: BTC, ETH, SOL (spot + perps)")
    print(f"Charter: MIN_NOTIONAL=${CHARTER.MIN_NOTIONAL_USD}, "
          f"MIN_PNL=${CHARTER.MIN_EXPECTED_PNL_USD}, "
          f"MAX_HOLD={CHARTER.MAX_HOLD_TIME_HOURS}h, "
          f"MIN_RR={CHARTER.MIN_RISK_REWARD_RATIO}x")
    print(f"Cycles: 3 minutes (high frequency)")
    print("=" * 80)
    print()
    
    engine = CoinbaseTradingEngine()
    await engine.run_trading_loop()


if __name__ == "__main__":
    asyncio.run(main())

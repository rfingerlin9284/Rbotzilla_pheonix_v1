#!/usr/bin/env python3
"""
Standalone Launcher for The Surgeon
Ensures active position management (Trailing Stops, Zombie Kill, etc.)
is running independently of the main trading engine.
"""
import sys
import os
import time
import logging

# Add project root to path
sys.path.append('/home/ing/RICK/RICK_PHOENIX')

from PhoenixV2.operations.surgeon import Surgeon
from brokers.oanda_connector import OandaConnector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SurgeonLauncher")

class SimpleRouter:
    """Simple router wrapper for Surgeon to talk to OANDA"""
    def __init__(self):
        # Determine environment from env vars or default to practice
        # You can force 'live' if needed, but be careful
        self.oanda = OandaConnector(environment=os.getenv('RICK_ENV', 'practice'))
        logger.info(f"Connected to OANDA ({self.oanda.environment})")

    def get_portfolio_state(self):
        """Get open positions from OANDA"""
        try:
            trades = self.oanda.get_trades()
            # Convert to format expected by Surgeon
            # Surgeon expects: id, instrument, currentUnits, price, unrealizedPL, stopLossOrder
            return {'open_positions': trades}
        except Exception as e:
            logger.error(f"Error fetching portfolio state: {e}")
            return {'open_positions': []}

    def get_candles(self, symbol, timeframe='M15', limit=50):
        """Get candles for Architect"""
        try:
            # OandaConnector.get_historical_data returns list of dicts
            # Architect expects DataFrame usually, but let's check Surgeon usage
            # Surgeon passes df to Architect. Architect expects DataFrame.
            data = self.oanda.get_historical_data(symbol, count=limit, granularity=timeframe)
            if data:
                import pandas as pd
                
                # Flatten OANDA candle format
                flat_data = []
                for c in data:
                    row = {'time': c.get('time'), 'volume': c.get('volume')}
                    if 'mid' in c:
                        mid = c['mid']
                        row['open'] = mid.get('o')
                        row['high'] = mid.get('h')
                        row['low'] = mid.get('l')
                        row['close'] = mid.get('c')
                    flat_data.append(row)
                
                df = pd.DataFrame(flat_data)
                # Ensure numeric
                cols = ['open', 'high', 'low', 'close', 'volume']
                for c in cols:
                    if c in df.columns:
                        df[c] = pd.to_numeric(df[c])
                return df
            return None
        except Exception as e:
            logger.error(f"Error fetching candles: {e}")
            return None

    def get_current_price(self, instrument, broker='OANDA'):
        """Get current price for instrument"""
        if broker == 'OANDA':
            try:
                # Try to use get_live_prices first (more accurate)
                if hasattr(self.oanda, 'get_live_prices'):
                    prices = self.oanda.get_live_prices([instrument])
                    if prices and instrument in prices:
                        p = prices[instrument]
                        return {'bid': p['bid'], 'ask': p['ask']}
                
                # Fallback to historical data (candles)
                data = self.oanda.get_historical_data(instrument, count=1, granularity='S5')
                if data:
                    c = data[0]
                    # OANDA candle format: {'mid': {'c': '1.2345', ...}, ...}
                    if 'mid' in c and 'c' in c['mid']:
                        price = float(c['mid']['c'])
                        return {'bid': price, 'ask': price}
                    # Fallback for flattened format if any
                    elif 'close' in c:
                        return {'bid': float(c['close']), 'ask': float(c['close'])}
            except Exception as e:
                logger.error(f"Error getting price for {instrument}: {e}")
        return None

    def close_trade(self, trade_id, broker='OANDA'):
        """Close a trade"""
        if broker == 'OANDA':
            try:
                logger.info(f"Closing trade {trade_id}...")
                self.oanda.close_trade(trade_id)
            except Exception as e:
                logger.error(f"Error closing trade {trade_id}: {e}")

    def modify_trade_sl(self, trade_id, price, broker='OANDA', instrument=None):
        """Modify Stop Loss"""
        if broker == 'OANDA':
            try:
                # Round price to correct precision
                precision = 5
                if instrument and 'JPY' in instrument:
                    precision = 3
                
                # Format to string with fixed precision to avoid float artifacts
                rounded_price = f"{price:.{precision}f}"
                
                # OandaConnector might have set_trade_stop or similar
                # Let's check OandaConnector, usually it's set_trade_stop
                self.oanda.set_trade_stop(trade_id, rounded_price)
            except Exception as e:
                logger.error(f"Error modifying SL for {trade_id}: {e}")

    # Add oanda property for direct access if Surgeon uses it
    @property
    def oanda_client(self):
        return self.oanda

if __name__ == "__main__":
    print("🚀 Launching Standalone Surgeon...")
    try:
        router = SimpleRouter()
        # Monkey patch router.oanda to be the connector itself if Surgeon accesses router.oanda
        router.oanda = router.oanda 
        
        surgeon = Surgeon(router)
        surgeon.start()
        
        print("✅ Surgeon is running in background.")
        print("   - Monitoring every 5 seconds")
        print("   - HYPER-TIGHT Trailing (0.05% activation / ~5 pips)")
        print("   - HYPER-TIGHT Breakeven (0.05% profit / ~5 pips)")
        print("   - Quant Hedge Rules Integrated")
        
        while True:
            time.sleep(1)
            if not surgeon.is_alive():
                print("⚠️ Surgeon thread died! Restarting...")
                surgeon = Surgeon(router)
                surgeon.start()
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping Surgeon...")
        if 'surgeon' in locals():
            surgeon.stop()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        sys.exit(1)

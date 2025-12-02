#!/usr/bin/env python3
"""
RBOTzilla FULL Autonomous Trading Entrypoint

This file runs the FULL OandaTradingEngine with ALL advanced features:
- Hive Mind consensus voting
- SmartLogicEngine gated filters
- ML/Regime Detection
- Wolf Pack strategies
- Position Police sweeps
- Momentum & Trailing systems
- Charter compliance enforcement

NOT the simplified ghost/canary engine!
"""

import asyncio
import sys
import time
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
PKG = ROOT / "rick_clean_live"

# Add paths for imports
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(PKG / 'util'))
sys.path.append(str(ROOT))

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

ENGINE_LABEL = None

try:
    # Import the FULL OandaTradingEngine with all advanced features
    from oanda_trading_engine import OandaTradingEngine
    ENGINE_LABEL = "OandaTradingEngine (FULL - Hive Mind, ML, Gated Logic)"
except Exception as e:
    print(f"ERROR: Could not import OandaTradingEngine: {type(e).__name__}: {e}")
    
    # Fallback to canary if full engine fails
    try:
        from canary_trading_engine import CanaryTradingEngine
        OandaTradingEngine = None
        ENGINE_LABEL = "CanaryTradingEngine (FALLBACK - simplified)"
    except Exception as e2:
        print(f"ERROR: Could not import CanaryTradingEngine either: {e2}")
        OandaTradingEngine = None
        CanaryTradingEngine = None
        ENGINE_LABEL = "NO ENGINE AVAILABLE"


async def main() -> None:
    """Main loop: start FULL trading engine with auto-restart."""
    print("=" * 80)
    print(f"🚀 RBOTzilla FULL Autonomous Trading")
    print(f"📦 Engine: {ENGINE_LABEL}")
    print(f"⏰ Started: {datetime.utcnow().isoformat()}")
    print("=" * 80)
    
    if OandaTradingEngine is None and CanaryTradingEngine is None:
        print("FATAL: No trading engine available!")
        return
    
    attempt = 0
    backoff_seconds = 5
    
    while True:
        attempt += 1
        print(f"\n🔄 Engine start attempt #{attempt}")
        
        try:
            if OandaTradingEngine is not None:
                # Use the FULL engine with practice environment
                engine = OandaTradingEngine(environment='practice')
                print("✅ Running FULL OandaTradingEngine with:")
                print("   • Hive Mind consensus voting")
                print("   • SmartLogicEngine gated filters")
                print("   • ML/Regime Detection")
                print("   • Position Police sweeps")
                print("   • Momentum & Trailing systems")
                print("   • Charter compliance enforcement")
                await engine.run_trading_loop()
            else:
                # Fallback to Canary
                engine = CanaryTradingEngine(pin=841921)
                print("⚠️ Running FALLBACK CanaryTradingEngine (simplified)")
                await engine.start_ghost_trading()
            
            print("Engine exited normally; restarting in 5s")
            await asyncio.sleep(5)
            
        except KeyboardInterrupt:
            print("\n🛑 Received KeyboardInterrupt, stopping gracefully")
            raise
        except Exception as e:
            now = datetime.utcnow().isoformat()
            print(f"❌ Engine crashed at {now}: {type(e).__name__}: {e}")
            print(f"🔄 Restarting in {backoff_seconds}s (attempt {attempt})")
            await asyncio.sleep(backoff_seconds)
            backoff_seconds = min(300, int(backoff_seconds * 1.5))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
    except Exception as e:
        print(f"💀 Fatal crash: {type(e).__name__}: {e}")
        raise

import os
import sys
from datetime import datetime, timezone
import dateutil.parser

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Try to load .env.live or .env
env_files = ['.env.live', '.env']
env_loaded = False

for env_file in env_files:
    env_path = os.path.join(os.path.dirname(__file__), '..', env_file)
    if os.path.exists(env_path):
        print(f"Loading environment from {env_path}")
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Don't overwrite existing env vars
                        if key not in os.environ:
                            os.environ[key] = value
            env_loaded = True
            # If we found OANDA keys, we can stop looking
            if 'OANDA_LIVE_ACCOUNT_ID' in os.environ:
                break
        except Exception as e:
            print(f"Error loading {env_file}: {e}")

if not env_loaded:
    print("Warning: No .env file found. Relying on existing environment variables.")

from PhoenixV2.core.auth import AuthManager
from PhoenixV2.execution.router import BrokerRouter

def check_stagnant_trades():
    auth = AuthManager()
    router = BrokerRouter(auth)
    
    if not router.oanda:
        print("❌ OANDA not configured or auth failed.")
        return

    print("--- Checking for Stagnant Winners ---")
    try:
        # We need individual trades to check duration
        if hasattr(router.oanda, 'get_open_trades'):
            trades = router.oanda.get_open_trades()
            print(f"Found {len(trades)} open trades.")
            
            stagnant_count = 0
            for t in trades:
                trade_id = t.get('id')
                instrument = t.get('instrument')
                unrealized_pl = float(t.get('unrealizedPL', 0))
                open_time_str = t.get('openTime')
                
                if open_time_str:
                    open_time = dateutil.parser.isoparse(open_time_str)
                    duration = datetime.now(timezone.utc) - open_time
                    duration_hours = duration.total_seconds() / 3600
                    
                    print(f"Trade {trade_id} ({instrument}): Open {duration_hours:.1f}h, PnL: ${unrealized_pl:.2f}")
                    
                    # Simulate the new rule
                    if duration_hours > 6 and unrealized_pl > 10:
                        print(f"  >>> WOULD BE CLOSED by Stagnant Winner Rule (Age > 6h, PnL > $10)")
                        stagnant_count += 1
                    elif duration_hours > 4 and abs(unrealized_pl) < 5:
                        print(f"  >>> WOULD BE CLOSED by Zombie Rule (Age > 4h, PnL < $5)")
                    else:
                        print(f"  >>> SAFE")
                else:
                    print(f"Trade {trade_id}: No open time found.")
            
            if stagnant_count > 0:
                print(f"\nFound {stagnant_count} stagnant winners that will be harvested by the Surgeon.")
            else:
                print("\nNo stagnant winners found currently.")
                
        else:
            print("Router does not support get_open_trades.")
            
    except Exception as e:
        print(f"Error fetching trades: {e}")

if __name__ == "__main__":
    check_stagnant_trades()

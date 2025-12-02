import json
import os
from datetime import datetime

STATE_FILE = '/home/ing/RICK/RICK_PHOENIX/PhoenixV2/core/phoenix_state.json'

def reset_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            try:
                data = json.load(f)
            except:
                data = {}
        
        print(f"Current State Balance: {data.get('current_balance')}")
        
        # Reset to a clean slate
        new_state = {
            "daily_start_balance": 0.0,
            "current_balance": 0.0, # Reset to 0 or user's actual balance if known
            "daily_pnl_pct": 0.0,
            "daily_peak_pnl": 0.0,
            "open_positions_count": 0, # Reset this as well
            "last_updated_iso": datetime.utcnow().isoformat() + "Z",
            "cooldowns": {},
            "strategy_pnl": {}, # Clear strategy history to start fresh tracking
            "strategy_performance": {}
        }
        
        with open(STATE_FILE, 'w') as f:
            json.dump(new_state, f, indent=2)
        
        print("✅ State has been reset to clean slate.")
    else:
        print("❌ State file not found.")

if __name__ == "__main__":
    reset_state()

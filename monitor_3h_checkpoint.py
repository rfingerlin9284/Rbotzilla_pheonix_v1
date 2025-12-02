#!/usr/bin/env python3
"""
Real-Time 3-Hour Checkpoint Monitor
PIN: 841921

Monitors live positions and alerts when 3-hour checkpoint approaches.
Auto-checks R-ratio and triggers alerts/actions.
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from brokers.oanda_connector import OandaConnector
except ImportError:
    print("⚠️  Could not import OandaConnector - running in monitor-only mode")
    OandaConnector = None


class ThreeHourMonitor:
    """Real-time monitor for 3-hour position checkpoint"""
    
    def __init__(self):
        self.connector = None
        if OandaConnector:
            try:
                self.connector = OandaConnector(
                    account_id=os.environ.get("OANDA_PRACTICE_ACCOUNT_ID"),
                    access_token=os.environ.get("OANDA_PRACTICE_TOKEN"),
                    environment="practice"
                )
            except Exception as e:
                print(f"⚠️  Could not initialize OANDA connector: {e}")
        
        self.alert_log = Path("logs/3h_checkpoint_alerts.jsonl")
        self.alert_log.parent.mkdir(exist_ok=True)
    
    def log_alert(self, alert_type: str, position: dict, details: dict):
        """Log alert to file"""
        alert = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "alert_type": alert_type,
            "position": position,
            "details": details
        }
        with open(self.alert_log, "a") as f:
            f.write(json.dumps(alert) + "\n")
        return alert
    
    def get_open_positions(self):
        """Fetch current open positions from OANDA"""
        if not self.connector:
            return []
        
        try:
            account_info = self.connector.get_account_info()
            positions = []
            
            # Get open trades
            if hasattr(self.connector, 'get_open_trades'):
                trades = self.connector.get_open_trades()
                for trade in trades:
                    positions.append({
                        "id": trade.get("id"),
                        "instrument": trade.get("instrument"),
                        "units": float(trade.get("currentUnits", 0)),
                        "entry_price": float(trade.get("price", 0)),
                        "current_price": float(trade.get("price", 0)),  # Will update with real price
                        "unrealized_pnl": float(trade.get("unrealizedPL", 0)),
                        "open_time": trade.get("openTime")
                    })
            
            return positions
        except Exception as e:
            print(f"❌ Error fetching positions: {e}")
            return []
    
    def calculate_r_ratio(self, position: dict, stop_loss_pips: float = 20):
        """Calculate current R-ratio for position"""
        try:
            entry = position["entry_price"]
            current = position["current_price"]
            
            # Calculate pips moved
            pip_size = 0.01 if "JPY" in position["instrument"] else 0.0001
            pips_moved = (current - entry) / pip_size
            
            # R-ratio = pips moved / risk (stop loss pips)
            r_ratio = pips_moved / stop_loss_pips
            
            return r_ratio
        except Exception as e:
            print(f"⚠️  Could not calculate R-ratio: {e}")
            return 0.0
    
    def parse_open_time(self, time_str: str) -> datetime:
        """Parse OANDA timestamp to datetime"""
        try:
            # Format: 2025-11-05T08:26:35.123456789Z
            # Remove fractional seconds beyond microseconds
            if '.' in time_str:
                main_part, frac_part = time_str.rsplit('.', 1)
                frac_part = frac_part.rstrip('Z')[:6] + 'Z'  # Keep only 6 digits
                time_str = f"{main_part}.{frac_part}"
            
            return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except Exception:
            return datetime.now(timezone.utc)
    
    def check_3h_approaching(self, open_time: datetime) -> tuple[bool, int]:
        """Check if 3-hour mark is approaching
        
        Returns:
            (is_approaching, minutes_remaining)
        """
        now = datetime.now(timezone.utc)
        elapsed = now - open_time
        elapsed_minutes = elapsed.total_seconds() / 60
        
        three_hours = 180  # minutes
        remaining = three_hours - elapsed_minutes
        
        # Alert windows: 15min before, 5min before, at checkpoint
        is_approaching = remaining <= 15 and remaining > 0
        
        return is_approaching, int(remaining)
    
    def monitor_loop(self, check_interval: int = 60):
        """Main monitoring loop"""
        print("=" * 80)
        print("🔍 3-HOUR CHECKPOINT MONITOR")
        print("=" * 80)
        print(f"Checking every {check_interval} seconds")
        print(f"Alert log: {self.alert_log}")
        print("\nPress Ctrl+C to stop\n")
        print("-" * 80)
        
        alert_sent = {}  # Track which alerts we've sent
        
        try:
            while True:
                positions = self.get_open_positions()
                
                if not positions:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] No open positions")
                else:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Monitoring {len(positions)} position(s):")
                    
                    for pos in positions:
                        pos_id = pos["id"]
                        instrument = pos["instrument"]
                        open_time = self.parse_open_time(pos["open_time"])
                        
                        # Check 3-hour status
                        approaching, mins_remaining = self.check_3h_approaching(open_time)
                        
                        # Calculate R-ratio
                        r_ratio = self.calculate_r_ratio(pos)
                        
                        # Status display
                        status = "⏳" if approaching else "✅"
                        print(f"  {status} {instrument} (ID: {pos_id})")
                        print(f"     Time: {mins_remaining}m until 3h checkpoint")
                        print(f"     R-ratio: {r_ratio:.2f}x")
                        print(f"     P&L: ${pos['unrealized_pnl']:.2f}")
                        
                        # Alert logic
                        alert_key = f"{pos_id}_3h"
                        
                        # 15-minute warning
                        if 10 <= mins_remaining <= 15 and f"{alert_key}_15m" not in alert_sent:
                            alert = self.log_alert(
                                "WARNING_15MIN",
                                {"id": pos_id, "instrument": instrument},
                                {"minutes_remaining": mins_remaining, "r_ratio": r_ratio}
                            )
                            print(f"     ⚠️  ALERT: 15-minute warning logged")
                            alert_sent[f"{alert_key}_15m"] = True
                        
                        # 5-minute warning
                        if 1 <= mins_remaining <= 5 and f"{alert_key}_5m" not in alert_sent:
                            alert = self.log_alert(
                                "WARNING_5MIN",
                                {"id": pos_id, "instrument": instrument},
                                {"minutes_remaining": mins_remaining, "r_ratio": r_ratio}
                            )
                            print(f"     🚨 ALERT: 5-minute warning - CRITICAL!")
                            alert_sent[f"{alert_key}_5m"] = True
                        
                        # Checkpoint reached
                        if mins_remaining <= 0 and f"{alert_key}_reached" not in alert_sent:
                            action = "SHOULD_CLOSE" if r_ratio < 0.5 else "CAN_CONTINUE"
                            alert = self.log_alert(
                                "CHECKPOINT_REACHED",
                                {"id": pos_id, "instrument": instrument},
                                {
                                    "r_ratio": r_ratio,
                                    "action": action,
                                    "reason": f"R={r_ratio:.2f} {'<' if r_ratio < 0.5 else '>='} 0.5"
                                }
                            )
                            
                            if action == "SHOULD_CLOSE":
                                print(f"     ❌ CHECKPOINT FAILED: R={r_ratio:.2f} < 0.5 → CLOSE POSITION")
                            else:
                                print(f"     ✅ CHECKPOINT PASSED: R={r_ratio:.2f} ≥ 0.5 → Continue")
                            
                            alert_sent[f"{alert_key}_reached"] = True
                
                # Sleep until next check
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n" + "=" * 80)
            print("🛑 Monitor stopped by user")
            print("=" * 80)
            
            # Summary
            if self.alert_log.exists():
                alerts = list(open(self.alert_log))
                print(f"\nTotal alerts logged: {len(alerts)}")
                print(f"Alert log: {self.alert_log}")


def main():
    """Entry point"""
    # Load environment
    env_file = Path(".env.oanda_only")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")
    
    # Check credentials
    if not os.environ.get("OANDA_PRACTICE_ACCOUNT_ID") or not os.environ.get("OANDA_PRACTICE_TOKEN"):
        print("❌ ERROR: OANDA credentials not found in environment")
        print("   Load .env.oanda_only first or set OANDA_PRACTICE_* env vars")
        sys.exit(1)
    
    # Start monitor
    monitor = ThreeHourMonitor()
    monitor.monitor_loop(check_interval=60)  # Check every 60 seconds


if __name__ == "__main__":
    main()

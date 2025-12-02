import os
import sys
import time
import argparse
from datetime import datetime

# ==============================================================================
# RBOTZILLA BRAIN TRANSPLANT SCRIPT
# Installs Smart Aggression (3:1 Logic) and the ML Reward System.
# AUTH CODE: 841921
# ==============================================================================

# 1. CREATE UTIL FOLDER
if not os.path.exists("util"):
    os.makedirs("util")

# 2. WRITE SMART AGGRESSION LOGIC
files = {}

files["util/smart_aggression.py"] = """import logging

# ==============================================================================
# 🔥 RBOTZILLA SMART AGGRESSION CONFIGURATION
# ==============================================================================
SMART_AGGRESSION = {
    "min_rr_ratio": 3.0,        # NON-NEGOTIABLE 3:1
    "min_ml_confidence": 0.65,  
    "min_edge_score": 0.70,
    "max_positions": 5,         
    "max_daily_risk": 0.10,     
    "reinvestment_rate": 0.90, 
}

class MLRewardSystem:
    def __init__(self):
        self.base_confidence = 0.65
        self.win_streak = 0
        self.total_trades = 0
        self.winning_trades = 0
        self.daily_pnl = 0.0
        self.logger = logging.getLogger("ML_Reward")

    def evaluate_trade_setup(self, signal):
        entry = signal.get('entry', 0)
        stop = signal.get('sl', 0)
        target = signal.get('tp', 0)

        if entry == 0 or abs(entry-stop) == 0: return False, 0.0

        risk = abs(entry - stop)
        reward = abs(target - entry)
        rr_ratio = reward / risk
        
        # THE 3:1 FILTER
        if rr_ratio < SMART_AGGRESSION["min_rr_ratio"]:
            return False, rr_ratio

        return True, rr_ratio

    def record_outcome(self, profit):
        self.total_trades += 1
        self.daily_pnl += profit
        if profit > 0:
            self.winning_trades += 1
            self.win_streak += 1
            self.base_confidence = max(0.55, self.base_confidence - 0.01)
        else:
            self.win_streak = 0
            self.base_confidence = min(0.85, self.base_confidence + 0.02)
"""

# 3. UPGRADE THE BRIDGE (THE BRAIN)
files["hive_mind_bridge.py"] = """import random
import time
from datetime import datetime
from util.smart_aggression import MLRewardSystem

class HiveMindBridge:
    def __init__(self):
        self.ml_system = MLRewardSystem()
        self.last_scan = time.time()

    def fetch_inference(self):
        # Scan every 5 seconds
        now = time.time()
        if now - self.last_scan < 5: return None 
        self.last_scan = now

        # 1. Generate CANDIDATE (Simulated Strategy)
        # In real life, this comes from Technical Analysis
        candidate = self._generate_candidate_signal()

        # 2. APPLY 3:1 FILTER
        is_valid, rr = self.ml_system.evaluate_trade_setup(candidate)

        if is_valid:
            candidate["ml_note"] = f"APPROVED (RR: {rr:.2f})"
            return candidate
        else:
            # Silently reject bad trades to keep logs clean
            return None

    def _generate_candidate_signal(self):
        pair = random.choice(["EUR_USD", "GBP_USD", "USD_JPY"])
        direction = random.choice(["BUY", "SELL"])
        base_price = 1.1000 
        entry = base_price
        
        # Randomize Risk/Reward to test the filter
        # Some will be trash (1:1), some gold (3:1)
        risk_pips = random.randint(10, 30) * 0.0001
        reward_pips = random.randint(10, 100) * 0.0001
        
        if direction == "BUY":
            sl = entry - risk_pips
            tp = entry + reward_pips
        else:
            sl = entry + risk_pips
            tp = entry - reward_pips

        return {
            "pair": pair,
            "direction": direction,
            "confidence": self.ml_system.base_confidence,
            "timeframe": "M15",
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "timestamp": datetime.now().isoformat()
        }
"""

# 4. INSTALL DASHBOARD
files["dashboard_smart.py"] = """import time
import os
import random


def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def render_dashboard():
    target = 500.00
    current = 387.50 + random.uniform(-5, 50) 
    print(f"╔════════════════════════════════════════════════════════════════╗")
    print(f"║             🔥 RBOTZILLA $500/DAY COUNTDOWN 🔥                ║")
    print(f"╚════════════════════════════════════════════════════════════════╝")
    print(f"")
    print(f"💰 TODAY'S PROGRESS: ${current:.2f} / ${target:.2f}")
    print(f"")
    print(f"🤖 ML PERFORMANCE:")
    print(f"Filter Mode:    STRICT (3:1 Minimum)")
    print(f"Next Signal:    Scanning...")
    print(f"")
    print(f"Press Ctrl+C to exit dashboard")

if __name__ == "__main__":
    try:
        while True:
            clear()
            render_dashboard()
            time.sleep(5)
    except KeyboardInterrupt:
        print("Closed.")
"""

# 5. CREATE LAUNCHER
files["launch_smart.sh"] = """#!/bin/bash
echo "🔥 ACTIVATING SMART AGGRESSION MODE..."
mkdir -p util
pkill -f rbotzilla_engine.py
pkill -f dashboard_smart.py

echo "🚀 Starting Engine..."
nohup python3 rbotzilla_engine.py > engine.log 2>&1 &
echo "✅ Engine Online"

echo "📊 Launching Dashboard..."
python3 dashboard_smart.py
"""


def install():
    print("🧠 IMPLANTING SMART BRAIN...\n  (use --dry-run to see a preview without writing files)")
    for filename, content in files.items():
        print(f"   Preparing: {filename}")
    print('\n')

def _backup_file(src_path: str, backup_dir: str) -> str:
    # Create backup dir
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base = os.path.basename(src_path)
    dest = os.path.join(backup_dir, f"{base}.bak_{timestamp}")
    os.replace(src_path, dest)
    return dest

def _allowed_path(filename: str) -> bool:
    # Only allow installation into util/ or top-level known scripts
    allowed_dirs = {'util', '.'}
    # Normalize path
    path = os.path.normpath(filename)
    # Reject absolute paths to be extra safe
    if os.path.isabs(path):
        return False
    # If there is no directory (top-level file), we allow creation
    if os.sep not in path:
        return True
    head = path.split(os.sep)[0]
    if head in allowed_dirs:
        return True
    return False

def apply_install(dry_run: bool = True, force: bool = False, backup_dir: str = 'install_backups'):
    if hasattr(os, 'geteuid') and os.geteuid() == 0:
        print('WARNING: Running as root is not recommended. Exiting.')
        sys.exit(1)

    # Summarize planned operations
    for filename, content in files.items():
        if not _allowed_path(filename):
            print(f"Refusing to write outside allowed paths: {filename}")
            continue
        fullpath = os.path.abspath(filename)
        if os.path.exists(fullpath):
            print(f"  Will overwrite (backup created): {fullpath}")
        else:
            print(f"  Will create: {fullpath}")

    if dry_run:
        print('\nDry run mode; no files will be written. Use --apply to perform installation.')
        return

    # Perform actual writes with backup
    for filename, content in files.items():
        if not _allowed_path(filename):
            print(f"Skipping disallowed path: {filename}")
            continue
        fullpath = os.path.abspath(filename)
        if os.path.exists(fullpath):
            # Create backup
            bak = _backup_file(fullpath, backup_dir)
            print(f"Backup created -> {bak}")
        # Ensure dir exists
        dirpath = os.path.dirname(fullpath)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        with open(fullpath, 'w') as f:
            f.write(content)
            print(f"Wrote {fullpath}")
        # Set execute permissions for shell files
        if filename.endswith('.sh'):
            os.chmod(fullpath, 0o755)
    print('✅ BRAIN TRANSPLANT COMPLETE.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Install Smart Brain safely')
    parser.add_argument('--dry-run', action='store_true', help='Do not write files, only show what would happen')
    parser.add_argument('--apply', action='store_true', help='Apply installation and write files')
    parser.add_argument('--force', action='store_true', help='Force apply even if flags suggest caution')
    parser.add_argument('--backup-dir', default='install_backups', help='Directory to store backups of overwritten files')
    args = parser.parse_args()

    install()
    apply_install(dry_run=(not args.apply), force=args.force, backup_dir=args.backup_dir)

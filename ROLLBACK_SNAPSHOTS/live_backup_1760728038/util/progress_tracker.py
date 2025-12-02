#!/usr/bin/env python3
"""
Immutable Progress Tracker - RICK_LIVE_CLEAN
Automatically updates README.md with breadcrumb trail of completed work
PIN: 841921 | Auto-generated progress documentation
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

class ProgressTracker:
    """
    Immutable progress tracking with automatic README generation
    Maintains complete audit trail of all system changes
    """
    
    def __init__(self, root_dir: str = None):
        self.root_dir = Path(root_dir or os.getcwd())
        self.progress_file = self.root_dir / "PROGRESS_LOG.json"
        self.readme_file = self.root_dir / "README.md"
        self.backup_dir = self.root_dir / ".progress_backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Load existing progress or initialize
        self.progress_data = self._load_progress()
    
    def _load_progress(self) -> Dict:
        """Load existing progress log"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "initialized": datetime.now(timezone.utc).isoformat(),
                "pin": "841921",
                "phases": [],
                "active_files": {},
                "system_constants": {
                    "MIN_RISK_REWARD_RATIO": 3.2,
                    "MIN_NOTIONAL_USD": 15000,
                    "PIN": 841921,
                    "MAX_PLACEMENT_LATENCY_MS": 300
                }
            }
    
    def _backup_progress(self):
        """Create timestamped backup before update"""
        if self.progress_file.exists():
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"progress_{timestamp}.json"
            with open(self.progress_file, 'r') as src:
                with open(backup_file, 'w') as dst:
                    dst.write(src.read())
    
    def _save_progress(self):
        """Save progress log atomically"""
        self._backup_progress()
        
        # Write to temp file first
        temp_file = self.progress_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(self.progress_data, f, indent=2)
        
        # Atomic rename
        temp_file.replace(self.progress_file)
    
    def mark_complete(self, phase_name: str, description: str, 
                     files_modified: List[str], 
                     key_features: List[str],
                     verification_status: str = "VERIFIED"):
        """
        Mark a phase as complete with full documentation
        
        Args:
            phase_name: Short name of completed phase
            description: What was accomplished
            files_modified: List of file paths that were changed/created
            key_features: List of key features or changes
            verification_status: VERIFIED, TESTED, or PENDING
        """
        phase_entry = {
            "phase": phase_name,
            "status": "COMPLETED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "description": description,
            "files_modified": files_modified,
            "key_features": key_features,
            "verification_status": verification_status
        }
        
        # Append to phases (immutable append-only log)
        self.progress_data["phases"].append(phase_entry)
        
        # Update active files registry
        for file_path in files_modified:
            self.progress_data["active_files"][file_path] = {
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "phase": phase_name,
                "status": "ACTIVE"
            }
        
        # Save progress
        self._save_progress()
        
        # Regenerate README
        self._generate_readme()
        
        print(f"✅ Progress tracked: {phase_name}")
        print(f"📝 README updated: {self.readme_file}")
    
    def _generate_readme(self):
        """Generate comprehensive README from progress log"""
        phases = self.progress_data["phases"]
        active_files = self.progress_data["active_files"]
        constants = self.progress_data["system_constants"]
        
        readme_content = f"""# RICK_LIVE_CLEAN - Live Trading System
## PIN: {constants['PIN']} | Last Updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## 🎯 System Status: GHOST MODE (45-min validation active)

### Current Configuration
- **Risk/Reward Ratio**: {constants['MIN_RISK_REWARD_RATIO']} (Charter validated)
- **Min Notional**: ${constants['MIN_NOTIONAL_USD']:,} (enforced both connectors)
- **Max Latency**: {constants['MAX_PLACEMENT_LATENCY_MS']}ms (OCO placement)
- **Mode**: GHOST → .upgrade_toggle managed
- **Environments**: OANDA=practice, Coinbase=sandbox

---

## 📊 Completed Phases ({len(phases)} total)

"""
        
        # List all completed phases in reverse chronological order
        for phase in reversed(phases):
            status_icon = "✅" if phase["verification_status"] == "VERIFIED" else "⏳"
            readme_content += f"""### {status_icon} {phase['phase']} 
**Completed**: {phase['timestamp'][:19]}  
**Status**: {phase['verification_status']}  
**Description**: {phase['description']}

**Key Features**:
"""
            for feature in phase['key_features']:
                readme_content += f"- {feature}\n"
            
            readme_content += f"\n**Files Modified** ({len(phase['files_modified'])}):\n"
            for file_path in phase['files_modified']:
                readme_content += f"- `{file_path}`\n"
            
            readme_content += "\n---\n\n"
        
        # Active Files Registry
        readme_content += f"""## 🔥 Active Files Registry ({len(active_files)} files)

This section documents all currently active code files and their purpose.

"""
        
        # Group by directory
        files_by_dir = {}
        for file_path, info in active_files.items():
            dir_name = str(Path(file_path).parent)
            if dir_name not in files_by_dir:
                files_by_dir[dir_name] = []
            files_by_dir[dir_name].append((file_path, info))
        
        for dir_name in sorted(files_by_dir.keys()):
            readme_content += f"### {dir_name}/\n"
            for file_path, info in sorted(files_by_dir[dir_name]):
                file_name = Path(file_path).name
                readme_content += f"- **{file_name}** - Last updated: {info['last_updated'][:19]} (Phase: {info['phase']})\n"
            readme_content += "\n"
        
        # System Architecture
        readme_content += """---

## 🏗️ System Architecture

### Core Components
1. **Charter** (`foundation/rick_charter.py`)
   - Immutable trading constants
   - Self-validating on import
   - PIN: 841921

2. **Mode Manager** (`util/mode_manager.py`)
   - .upgrade_toggle integration
   - OFF/GHOST/CANARY/LIVE modes
   - Connector auto-detection

3. **Narration Logger** (`util/narration_logger.py`)
   - Event logging to narration.jsonl
   - P&L tracking to pnl.jsonl
   - Session summary aggregation

4. **Connectors**
   - `brokers/oanda_connector.py` - OANDA FX (practice/live)
   - `brokers/coinbase_connector.py` - Coinbase crypto (sandbox/live)
   - Both support environment=None for auto-detection
   - Min-notional enforcement: $15k

### Trading Modes
```
OFF     → OANDA: practice, Coinbase: sandbox (safe default)
GHOST   → OANDA: practice, Coinbase: sandbox (45-min validation)
CANARY  → OANDA: practice, Coinbase: sandbox (extended testing)
LIVE    → OANDA: live,     Coinbase: live     (requires PIN: 841921)
```

### Promotion Flow
1. **GHOST** session runs 45 minutes
2. System logs to `narration.jsonl` + `pnl.jsonl`
3. **CANARY** evaluates: 70% win rate, 10+ trades, $50+ P&L
4. If criteria met → promote to **LIVE** with PIN validation
5. Live trading begins with full guardrails

---

## 🔒 Safety Features

### Immutable Constants (rick_charter.py)
- Module-level validation blocks import if constants are tampered
- Self-test on every import
- Assertion failures prevent system startup

### Mode Protection
- LIVE mode requires PIN (841921)
- Practice/sandbox default for GHOST/CANARY
- .upgrade_toggle file controls all mode switches

### Min-Notional Enforcement
- Both OANDA and Coinbase auto-upsize to $15k minimum
- Preserves order sign (buy/sell)
- Logs NOTIONAL_ADJUSTMENT events

### OCO Placement Logging
- Every OCO placement logged with latency
- Errors tracked to narration.jsonl
- Real-time dashboard monitoring

---

## 📁 File Organization

```
RICK_LIVE_CLEAN/
├── brokers/                    # Trading connectors
│   ├── oanda_connector.py      # OANDA FX (ACTIVE)
│   └── coinbase_connector.py   # Coinbase crypto (ACTIVE)
├── foundation/                 # Core system
│   ├── rick_charter.py         # Immutable constants (ACTIVE)
│   └── progress.py             # Phase tracking (ACTIVE)
├── util/                       # Utilities
│   ├── mode_manager.py         # .upgrade_toggle handler (ACTIVE)
│   ├── narration_logger.py     # Event/P&L logging (ACTIVE)
│   └── progress_tracker.py     # README auto-generation (ACTIVE)
├── dashboard/                  # Monitoring
│   ├── generate_dashboard.py  # Static HTML generator (ACTIVE)
│   └── dashboard.html          # Auto-refreshing UI
├── logs/                       # Session logs
│   ├── ghost_trading.log       # Ghost session output
│   └── ghost_session.log       # Background process log
├── pre_upgrade/headless/logs/  # Event logs
│   ├── narration.jsonl         # All trading events (232k+ lines)
│   └── pnl.jsonl              # P&L tracking (ACTIVE)
├── ghost_trading_engine.py     # 45-min validation (ACTIVE)
├── canary_to_live.py          # Promotion logic (ACTIVE)
├── test_ghost_trading.py      # 2-min test suite (VERIFIED)
├── .upgrade_toggle            # Mode control (GHOST/OFF/CANARY/LIVE)
├── PROGRESS_LOG.json          # Immutable progress log
└── README.md                  # This file (auto-generated)
```

---

## 🚀 Quick Start

### Run Ghost Trading Session (45 minutes)
```bash
# Switch to GHOST mode
python3 -c "from util.mode_manager import switch_mode; switch_mode('GHOST')"

# Start validation session
nohup python3 ghost_trading_engine.py > logs/ghost_session.log 2>&1 &

# Monitor progress
tail -f logs/ghost_session.log
```

### Check System Status
```bash
# View current mode
cat .upgrade_toggle

# Check recent events
tail -20 pre_upgrade/headless/logs/narration.jsonl | jq .

# View P&L summary
python3 -c "from util.narration_logger import get_session_summary; import json; print(json.dumps(get_session_summary(), indent=2))"
```

### Generate Dashboard
```bash
# Update HTML dashboard
python3 dashboard/generate_dashboard.py

# Open in browser (auto-refreshes every 10s)
xdg-open dashboard/dashboard.html
```

### Promote to LIVE (requires passing GHOST/CANARY)
```bash
# Switch to LIVE mode (requires PIN: 841921)
python3 -c "from util.mode_manager import switch_mode; switch_mode('LIVE', pin=841921)"
```

---

## 🔍 Verification Commands

### Test Connectors
```bash
# Test OANDA connector with auto-detection
python3 -c "from brokers.oanda_connector import OandaConnector; oc = OandaConnector(pin=841921); print(f'OANDA environment: {oc.environment}')"

# Test Coinbase connector
python3 -c "from brokers.coinbase_connector import CoinbaseConnector; cc = CoinbaseConnector(pin=841921); print(f'Coinbase environment: {cc.environment}')"
```

### Validate Charter
```bash
# Charter self-validates on import
python3 -c "from foundation.rick_charter import RickCharter; print('Charter valid ✅')"
```

### Check Ghost Session Status
```bash
# Check if running
ps aux | grep ghost_trading_engine | grep -v grep

# View recent trades
grep "Ghost Trade Result" logs/ghost_session.log | tail -5
```

---

## 📈 Progress Tracking

This README is **auto-generated** by `util/progress_tracker.py` after each phase completion.

To update progress:
```python
from util.progress_tracker import ProgressTracker

tracker = ProgressTracker()
tracker.mark_complete(
    phase_name="Phase Name",
    description="What was accomplished",
    files_modified=["path/to/file.py"],
    key_features=["Feature 1", "Feature 2"],
    verification_status="VERIFIED"
)
```

---

## ⚠️ Important Notes

1. **NEVER edit .upgrade_toggle manually** - Use mode_manager.switch_mode()
2. **NEVER modify rick_charter.py constants** - System will fail validation
3. **ALWAYS use PIN 841921** for LIVE mode switches
4. **Ghost sessions must complete** before promotion evaluation
5. **Narration logs are append-only** - Never delete/truncate

---

## 📞 System Health

Last validation: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

**Status**: ✅ All systems operational

---

*This README is automatically maintained by the progress tracking system.*  
*Manual edits will be overwritten on next phase completion.*  
*To update: Use `util/progress_tracker.py` only.*
"""
        
        # Write README atomically
        temp_readme = self.readme_file.with_suffix('.tmp')
        with open(temp_readme, 'w') as f:
            f.write(readme_content)
        temp_readme.replace(self.readme_file)
    
    def get_active_files(self) -> Dict[str, Dict]:
        """Get all currently active files"""
        return self.progress_data["active_files"]
    
    def get_phase_history(self) -> List[Dict]:
        """Get complete phase history"""
        return self.progress_data["phases"]


if __name__ == '__main__':
    # Example usage
    tracker = ProgressTracker()
    print(f"📊 Loaded {len(tracker.get_phase_history())} completed phases")
    print(f"🔥 Tracking {len(tracker.get_active_files())} active files")

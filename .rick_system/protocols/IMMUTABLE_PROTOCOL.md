# 🔐 RICK IMMUTABLE CHANGE PROTOCOL
## Version 1.0 | PIN: 841921 | Effective: 2025-11-25

---

## 📋 PURPOSE

This document establishes **IMMUTABLE STANDARDS** for:
1. When to save/commit changes
2. How to label files and folders
3. Where to store logs and backups
4. How to track dependencies between files

**These rules cannot be bypassed or modified without Charter approval (PIN 841921).**

---

## 🗂️ FOLDER STRUCTURE (IMMUTABLE)

```
/home/ing/RICK/RICK_LIVE_CLEAN/
├── .rick_system/                    # SYSTEM MANAGEMENT (PROTECTED)
│   ├── change_log/                  # Session change logs (JSONL)
│   │   ├── TIMELINE.jsonl           # Master timeline of all sessions
│   │   └── session_YYYYMMDD_HHMMSS.json
│   ├── diffs/                       # Individual file diffs
│   │   └── YYYYMMDD_HHMMSS_filename.diff
│   ├── snapshots/                   # Frozen state snapshots
│   │   └── frozen-v2_YYYYMMDD_HHMMSS/
│   ├── manifests/                   # Active file manifests
│   │   ├── manifest_YYYYMMDD_HHMMSS.md
│   │   └── manifest_YYYYMMDD_HHMMSS.json
│   ├── backups/                     # Auto/manual backups
│   │   └── backup_YYYYMMDD_HHMMSS/
│   └── protocols/                   # Protocol documentation
│       └── IMMUTABLE_PROTOCOL.md    # THIS FILE
│
├── rick_clean_live/                 # ACTIVE TRADING CODE
│   ├── brokers/                     # Broker connectors
│   ├── foundation/                  # Charter + Core rules
│   ├── hive/                        # Swarm intelligence
│   ├── logic/                       # ML + Decision logic
│   ├── strategies/                  # Trading strategies
│   ├── systems/                     # Signal systems
│   ├── util/                        # Utility modules
│   └── oanda_trading_engine.py      # MAIN ENGINE
│
├── _legacy_code/                    # ARCHIVED/DEPRECATED CODE
│   └── L-*.py                       # All legacy files prefixed with L-
│
└── dev_toggle.sh                    # Dev/Live mode switcher
```

---

## 📛 NAMING CONVENTIONS (IMMUTABLE)

### File Naming
| Type | Format | Example |
|------|--------|---------|
| Active module | `snake_case.py` | `oanda_trading_engine.py` |
| Legacy/archived | `L-original_name.py` | `L-oanda_trading_engine.py` |
| Backup | `backup_YYYYMMDD_HHMMSS/` | `backup_20251125_143022/` |
| Diff | `YYYYMMDD_HHMMSS_filename.diff` | `20251125_143022_engine.diff` |
| Manifest | `manifest_YYYYMMDD_HHMMSS.md` | `manifest_20251125_143022.md` |
| Session log | `session_YYYYMMDD_HHMMSS.json` | `session_20251125_143022.json` |

### Branch Naming
| Type | Format | Example |
|------|--------|---------|
| Frozen production | `frozen-v{N}` | `frozen-v2` |
| Development | `dev/{feature}` | `dev/momentum-fix` |
| Copilot session | `copilot/{description}` | `copilot/restore-repo-and-clean-errors` |

---

## 💾 WHEN TO SAVE (IMMUTABLE TRIGGERS)

### AUTOMATIC SAVES (System-Triggered)
1. **Before any file modification** - Cache original content
2. **After successful trade execution** - Log position state
3. **On engine startup** - Snapshot current config
4. **On engine shutdown** - Save session summary
5. **Every 15 minutes** - Auto-checkpoint during active trading

### MANUAL SAVES (User-Triggered)
1. **Before switching modes** (dev ↔ live)
2. **Before major code changes**
3. **After fixing a bug**
4. **Before merging branches**
5. **When creating a new frozen version**

### COMMIT MESSAGE FORMAT
```
[TYPE] Brief description

Detailed changes:
- File 1: What changed
- File 2: What changed

Source files (if extracted):
- Original file → New file

Lines changed: +XX / -YY
```

Types: `[FIX]`, `[FEATURE]`, `[REFACTOR]`, `[DOCS]`, `[FREEZE]`

---

## 📊 FILE DEPENDENCY TRACKING

### When Creating a New File
Log the following in the session record:

```json
{
  "new_file": "util/new_module.py",
  "line_count": 250,
  "source_files": [
    "util/old_module.py (lines 50-150)",
    "systems/signals.py (lines 200-250)"
  ],
  "dependencies": [
    "foundation/rick_charter.py",
    "util/terminal_display.py"
  ],
  "reason": "Extracted momentum logic for reuse"
}
```

### When Modifying a File
Log the following:

```json
{
  "file": "oanda_trading_engine.py",
  "line_count_before": 1752,
  "line_count_after": 1760,
  "changes": [
    {
      "line_range": "1442-1445",
      "type": "FIX",
      "description": "Fixed info() method signature"
    }
  ],
  "diff_file": "20251125_143022_oanda_trading_engine.diff"
}
```

### When Archiving a File
```json
{
  "original_file": "oanda/oanda_trading_engine.py",
  "archived_to": "_legacy_code/L-oanda_oanda_trading_engine.py",
  "line_count": 2430,
  "reason": "Duplicate of rick_clean_live version",
  "replacement": "rick_clean_live/oanda_trading_engine.py"
}
```

---

## 🚫 PROTECTED FILES (CANNOT BE MODIFIED IN LIVE MODE)

These files are LOCKED in production mode:

| File | Reason |
|------|--------|
| `foundation/rick_charter.py` | Charter rules are immutable |
| `.rick_system/*` | System management files |
| `master.env` | Environment configuration |
| `_legacy_code/*` | Archived code (reference only) |

To modify these files:
1. Switch to dev mode: `./dev_toggle.sh dev`
2. Make changes
3. Test thoroughly
4. Create new frozen snapshot
5. Switch to new frozen version

---

## 📝 ACTIVE FILE MANIFEST FORMAT

Every manifest must include:

```markdown
# RICK Active Files Manifest
## Generated: 2025-11-25T20:00:00Z
## Total Files: 45
## Total Lines: 15,234

| File Path | Lines | Size (KB) | Hash | Status |
|-----------|-------|-----------|------|--------|
| `oanda_trading_engine.py` | 1,752 | 68.5 | a1b2c3d4 | ACTIVE |
| `util/momentum_trailing.py` | 250 | 9.8 | e5f6g7h8 | ACTIVE |
...
```

Status values:
- `ACTIVE` - Currently in use by the system
- `STANDBY` - Available but not currently loaded
- `DEPRECATED` - Scheduled for archival
- `LEGACY` - Archived in _legacy_code/

---

## 🔄 DEV → LIVE MERGE PROTOCOL

Before merging dev changes to production:

### 1. Pre-Merge Checklist
- [ ] All tests pass
- [ ] Engine initializes without errors
- [ ] All systems show ACTIVE (Momentum, Hive, ML)
- [ ] No uncommitted changes in dev
- [ ] Manifest generated and reviewed
- [ ] Session log saved

### 2. Merge Steps
```bash
# 1. Create new frozen version
./dev_toggle.sh backup
git checkout -b frozen-v{N+1}

# 2. Merge dev changes
git merge dev/your-feature

# 3. Tag the release
git tag -a v{N+1}.0 -m "Frozen release v{N+1}"

# 4. Push to remote
git push origin frozen-v{N+1}
git push origin --tags

# 5. Update mode
./dev_toggle.sh live
```

### 3. Post-Merge Verification
- [ ] Engine starts successfully
- [ ] Positions sync from OANDA
- [ ] All components report ACTIVE
- [ ] Narration logs flowing to terminal

---

## 📋 CHANGE LOG ENTRY FORMAT

Every change session creates a log entry:

```json
{
  "session_id": "session_20251125_143022",
  "start_time": "2025-11-25T14:30:22Z",
  "end_time": "2025-11-25T15:45:00Z",
  "changes": [
    {
      "timestamp": "2025-11-25T14:32:00Z",
      "file_path": "rick_clean_live/util/__init__.py",
      "change_type": "CREATED",
      "line_count_before": 0,
      "line_count_after": 1,
      "description": "Created package init file",
      "source_files": []
    }
  ],
  "files_modified": ["oanda_trading_engine.py"],
  "files_created": ["util/__init__.py", "hive/__init__.py"],
  "files_deleted": [],
  "total_lines_changed": 15,
  "description": "Fixed package imports and Position Police error"
}
```

---

## ⚠️ VIOLATION HANDLING

If a protocol violation is detected:

1. **WARN** - Log the violation, continue operation
2. **BLOCK** - Prevent the action, require manual override
3. **ALERT** - Notify user immediately via terminal

| Violation | Severity | Action |
|-----------|----------|--------|
| Modifying protected file in live mode | BLOCK | Require dev mode switch |
| Missing session log | WARN | Auto-create empty log |
| Uncommitted changes on mode switch | ALERT | Prompt to stash/commit |
| Direct push to frozen branch | BLOCK | Require merge from dev |

---

## 🔐 CHARTER COMPLIANCE

This protocol operates under RBOTzilla Charter PIN: **841921**

Any modifications to this protocol require:
1. Charter PIN validation
2. Documented justification
3. New protocol version number
4. Notification to all system components

---

*Protocol Version: 1.0 | Effective: 2025-11-25 | Next Review: 2025-12-25*

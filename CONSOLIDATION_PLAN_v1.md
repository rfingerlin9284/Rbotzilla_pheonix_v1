# RBOTZILLA CONSOLIDATION PLAN v1
**PIN**: 841921 | **Date**: Nov 7, 2025 | **Repo**: RICK_LIVE_CLEAN

## 📊 CURRENT STATE
- Python files: 5,509
- Total files: 9,286
- Size: 424MB

## 🎯 TARGET STATE
- **Core Strategy Files**: 4 (Bullish, Bearish, Sideways, Triage)
- **Total Python files**: ~50-100 (95%+ reduction)
- **Folder naming**: `strategy_4F/` (4 Files)
- **Size**: <50MB

---

## 📁 PROPOSED STRUCTURE

```
RICK_LIVE_CLEAN/
├── README_MASTER_v1.md          # THE BIBLE - Full rebuild mega-prompt
├── oanda_trading_engine_v1.py   # Main engine (consolidated)
├── .env                          # Credentials
│
├── strategy_4F/                  # 4 mega-files
│   ├── bullish_wolf_pack_v1.py  # All bullish logic + FVG + aux strategies
│   ├── bearish_wolf_pack_v1.py  # All bearish logic + FVG + aux strategies
│   ├── sideways_wolf_pack_v1.py # All sideways logic + FVG + aux strategies
│   ├── triage_adaptive_v1.py    # Regime detection + routing
│   └── narration_agent_v1.py    # Strategy folder narrator
│
├── hive_3F/                      # RICK + Hive Mind
│   ├── rick_hive_mind_v1.py     # Main orchestrator + closed loop
│   ├── consensus_engine_v1.py   # Probability scoring
│   └── narration_agent_v1.py    # Hive narrator
│
├── ml_2F/                        # Machine Learning
│   ├── ml_models_v1.py          # All ML models (regime, pattern, signal)
│   └── narration_agent_v1.py    # ML narrator
│
├── brokers_2F/                   # API Connectors
│   ├── oanda_connector_v1.py    # OANDA only (Coinbase removed)
│   └── narration_agent_v1.py    # Broker narrator
│
├── foundation_2F/                # Charter + Gates
│   ├── rick_charter_v1.py       # Immutable risk rules
│   └── margin_gate_v1.py        # Correlation + Margin gates
│
├── util_5F/                      # Core utilities
│   ├── central_narrator_v1.py   # JSON→Human translator
│   ├── smart_trailing_v1.py     # Trailing stop logic
│   ├── smart_logic_v1.py        # Trade logic assistant
│   ├── usd_converter_v1.py      # Currency conversion
│   └── terminal_display_v1.py   # Dashboard output
│
├── logs/                         # Per-folder logs
│   ├── strategy/                # Strategy narration
│   ├── hive/                    # Hive decisions
│   ├── ml/                      # ML predictions
│   ├── brokers/                 # API calls
│   └── central_narration.log    # Human-readable consolidated
│
└── _ARCHIVE_LEGACY/             # Everything else (locked, read-only)
    └── [all removed code]
```

---

## 🔥 FILES TO CONSOLIDATE

### Strategy Files → `strategy_4F/`
**INTO bullish_wolf_pack_v1.py:**
- systems/momentum_signals.py (bullish portions)
- systems/fvg_detector.py (bullish FVG)
- systems/mass_behavior_logic.py (bullish sentiment)
- ANY auxiliary strategy tagged "bullish"

**INTO bearish_wolf_pack_v1.py:**
- systems/momentum_signals.py (bearish portions)
- systems/fvg_detector.py (bearish FVG)
- systems/mass_behavior_logic.py (bearish sentiment)
- ANY auxiliary strategy tagged "bearish"

**INTO sideways_wolf_pack_v1.py:**
- Range-bound strategies
- Mean reversion logic
- Consolidation detectors

**INTO triage_adaptive_v1.py:**
- ml_learning/optimizer.py (regime detection)
- Routing logic (which pack to use)

### Hive Files → `hive_3F/`
**INTO rick_hive_mind_v1.py:**
- hive/rick_hive_mind.py
- hive/adaptive_rick.py
- hive/rick_local_ai.py
- hive/rick_hive_browser.py

**INTO consensus_engine_v1.py:**
- hive/hive_mind_processor.py
- Probability scoring logic

### ML Files → `ml_2F/`
**INTO ml_models_v1.py:**
- ml_learning/ml_models.py
- ml_learning/pattern_learner.py
- ml_learning/optimizer.py
- ANY regime detection code

### Broker Files → `brokers_2F/`
**INTO oanda_connector_v1.py:**
- brokers/oanda_connector.py (FIXED version)
- Remove: coinbase_connector.py (not used)

---

## 🗑️ FILES TO DELETE

1. **Duplicates**: Any file with same code
2. **Stubs**: Empty or placeholder files
3. **Broken**: Files with syntax errors
4. **Unused**: Anything not imported by engine
5. **Coinbase**: All Coinbase-related code (user disregards)
6. **Archives**: Old rollback snapshots (move to _ARCHIVE_LEGACY/)

---

## ✅ EXECUTION CHECKLIST

- [ ] Phase 1: Backup current state
- [ ] Phase 2: Create new folder structure
- [ ] Phase 3: Consolidate strategy files (4F)
- [ ] Phase 4: Consolidate hive files (3F)
- [ ] Phase 5: Consolidate ML files (2F)
- [ ] Phase 6: Consolidate broker files (2F)
- [ ] Phase 7: Add narration agents to each folder
- [ ] Phase 8: Create central_narrator_v1.py
- [ ] Phase 9: Wire RICK closed loop (3-5 min re-eval)
- [ ] Phase 10: Create README_MASTER_v1.md (mega-prompt)
- [ ] Phase 11: Move legacy code to _ARCHIVE_LEGACY/
- [ ] Phase 12: Lock critical files (chmod 444)
- [ ] Phase 13: Test engine startup
- [ ] Phase 14: Verify narration output

---

**Ready to execute? Reply: "EXECUTE CONSOLIDATION 841921"**

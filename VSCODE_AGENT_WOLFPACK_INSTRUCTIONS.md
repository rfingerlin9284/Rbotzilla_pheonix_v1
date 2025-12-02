# VSCode Agent Task: Elite Wolf Pack Strategy Assembly

## MISSION OBJECTIVE
Search filesystem comprehensively to find top-performing trading strategies and assemble three specialized Wolf Pack files optimized for different market regimes with embedded performance metrics.

## SEARCH PHASE - Strategy Discovery

### Search Locations (Execute in Order)
```bash
# Primary search locations
/home/ing/                           # WSL user directory
/mnt/c/Users/                       # Windows user directories
/mnt/c/                             # Full C: drive
~/Desktop/                          # User desktop
~/Documents/                        # Documents folder
~/Downloads/                        # Downloads folder
```

### Search Patterns (Use grep/find/semantic_search)
```bash
# Strategy file patterns
**/*strategy*.py
**/*trading*.py
**/*signal*.py
**/*backtest*.py
**/*wolf*.py
**/*pack*.py
**/*regime*.py
**/*momentum*.py
**/*mean_reversion*.py
**/*breakout*.py
**/*scalping*.py

# Configuration patterns
**/config/*.yaml
**/config/*.json
**/*config*.py
**/*settings*.py

# Backtest result patterns
**/*results*.csv
**/*performance*.json
**/*metrics*.txt
**/*sharpe*.csv
**/*drawdown*.log
```

### Performance Ranking Criteria
Search for these metrics in files/comments/results:
```python
# Priority ranking factors:
1. Profitability % (target: >60% win rate)
2. Maximum Drawdown (target: <15%)
3. Sharpe Ratio (target: >1.5)
4. Risk/Reward Ratio (target: >3.0)
5. Number of successful backtests
6. Timeframe compatibility (M15, M30, H1)
7. Regime performance specialization
```

## ANALYSIS PHASE - Strategy Selection

### Extract Top Methods Per Regime
For each strategy file found, analyze for:

**Bullish Regime Indicators:**
- Moving average golden crosses
- RSI momentum breaks (>70)
- MACD bullish divergence
- Breakout confirmations
- Volume surge patterns

**Bearish Regime Indicators:**
- Moving average death crosses
- RSI bearish momentum (<30)
- MACD bearish divergence
- Breakdown confirmations
- Volume distribution patterns

**Sideways Regime Indicators:**
- Bollinger Band mean reversion
- RSI range trading (30-70)
- Support/resistance bounces
- Low ADX readings (<25)
- Oscillator reversals

### Synergistic Method Selection
For each regime, select 4-5 methods that:
1. Complement each other (not redundant)
2. Have proven backtest results
3. Work on different timeframes
4. Have different trigger conditions
5. Share similar risk profiles

## ASSEMBLY PHASE - Wolf Pack Creation

### File Structure Template
```python
# BULLISH_WOLF_PACK.py template structure
"""
Elite Bullish Wolf Pack Strategy
Assembled from top-performing strategies found on filesystem
Performance Metrics: [EMBED ACTUAL RESULTS]
"""

class BullishWolfPack:
    # RICK Charter Compliance
    MAX_HOLD_HOURS = 6
    ALLOWED_TIMEFRAMES = ['M15', 'M30', 'H1']
    MIN_NOTIONAL = 15000
    MIN_RISK_REWARD = 3.2

    # Embedded Performance Metrics (from search results)
    HISTORICAL_PERFORMANCE = {
        'win_rate': 0.0,  # Fill from found results
        'sharpe_ratio': 0.0,
        'max_drawdown': 0.0,
        'avg_return': 0.0,
        'total_trades': 0,
        'source_files': []  # List source files used
    }

    # Method 1: [Name from best found strategy]
    # Method 2: [Name from second best]
    # Method 3: [Name from third best]
    # Method 4: [Name from fourth best]
    # Method 5: [Name from fifth best]
```

### Output Files to Create
Save to Desktop:
1. `BULLISH_WOLF_PACK.py` - Uptrend specialist
2. `BEARISH_WOLF_PACK.py` - Downtrend specialist
3. `SIDEWAYS_WOLF_PACK.py` - Range trading specialist
4. `WOLF_PACK_ASSEMBLY_REPORT.md` - Detailed source documentation

## EXECUTION COMMANDS

### Step 1: Comprehensive Search
```bash
# Search for all strategy files
find /home/ing/ -name "*strategy*.py" -o -name "*trading*.py" 2>/dev/null | head -50
find /mnt/c/ -name "*strategy*.py" -o -name "*trading*.py" 2>/dev/null | head -50

# Search for backtest results
find /home/ing/ -name "*results*.csv" -o -name "*performance*.json" 2>/dev/null | head -20
find /mnt/c/ -name "*results*.csv" -o -name "*performance*.json" 2>/dev/null | head -20

# Search for existing wolf pack files
grep -r "wolf" /home/ing/ --include="*.py" | head -20
grep -r "pack" /mnt/c/ --include="*.py" | head -20
```

### Step 2: Content Analysis
```bash
# Analyze found files for performance metrics
grep -r "win_rate\|sharpe\|drawdown\|profitability" [FOUND_FILES]
grep -r "backtest\|performance\|metrics" [FOUND_FILES]

# Extract strategy methods
grep -r "def.*signal\|def.*entry\|def.*exit" [FOUND_FILES]
grep -r "RSI\|MACD\|EMA\|SMA\|ATR" [FOUND_FILES]
```

### Step 3: Assembly and Validation
```python
# Validate each wolf pack meets RICK requirements
# Ensure 4-5 synergistic methods per pack
# Embed actual performance metrics found
# Include source file references
# Test basic syntax validation
```

## SUCCESS CRITERIA

### Each Wolf Pack Must Include:
- ✅ 4-5 complementary trading methods
- ✅ Embedded historical performance metrics
- ✅ RICK charter compliance checks
- ✅ Regime detection logic
- ✅ Source file documentation
- ✅ Backtest validation results
- ✅ Risk management integration

### Performance Targets:
- Win Rate: >55%
- Sharpe Ratio: >0.8
- Max Drawdown: <30%
- Risk/Reward: >3.0
- Minimum 100+ historical trades

## DELIVERABLES

1. **BULLISH_WOLF_PACK.py** - Complete implementation
2. **BEARISH_WOLF_PACK.py** - Complete implementation
3. **SIDEWAYS_WOLF_PACK.py** - Complete implementation
4. **WOLF_PACK_ASSEMBLY_REPORT.md** - Full documentation:
   - Source files discovered
   - Performance metrics extracted
   - Method selection rationale
   - Synergy analysis
   - RICK compliance verification
   - Recommended next steps

## AGENT EXECUTION NOTES

- Use semantic_search for intelligent strategy discovery
- Prioritize files with actual backtest results
- Extract numerical performance metrics automatically
- Validate Python syntax before saving
- Include error handling in generated code
- Document all source files used
- Preserve original strategy attribution
- Ensure no duplicate methods across packs

## POST-ASSEMBLY VALIDATION

After creation, run these checks:
```bash
python3 -m py_compile BULLISH_WOLF_PACK.py
python3 -m py_compile BEARISH_WOLF_PACK.py
python3 -m py_compile SIDEWAYS_WOLF_PACK.py
```

Execute this task with maximum thoroughness - the Wolf Packs will be the core trading intelligence for the system.
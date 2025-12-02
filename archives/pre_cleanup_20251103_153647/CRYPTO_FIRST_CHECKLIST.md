# 🚀 CRYPTO-FIRST DEPLOYMENT CHECKLIST
# October 17, 2025 | PIN: 841921

## 📋 PRE-DEPLOYMENT CHECKLIST

### Phase 1: API Setup (5-10 minutes)

#### Step 1: Get Coinbase API Credentials
- [ ] Go to https://www.coinbase.com/advancedtrade
- [ ] Settings → API → Create API Key
- [ ] Select "Advanced Trading"
- [ ] Enable: View summary, View details, View trading, Create orders, Cancel orders
- [ ] Copy 3 values:
  - [ ] API Key (public)
  - [ ] API Secret (private)
  - [ ] API Passphrase

#### Step 2: Add to Configuration File
- [ ] Edit `crypto_first.env`
- [ ] Replace `PUT_YOUR_KEY_HERE` with your API key
- [ ] Replace `PUT_YOUR_SECRET_HERE` with your API secret
- [ ] Replace `PUT_YOUR_PASSPHRASE_HERE` with your passphrase
- [ ] Save file

#### Step 3: Load Configuration
```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN
source crypto_first.env
```

- [ ] Verify keys loaded: `echo $COINBASE_API_KEY`
- [ ] Should show your key (not empty)


### Phase 2: Connectivity Test (5 minutes)

#### Step 4: Test Single Iteration
```bash
export ENVIRONMENT=practice
python3 multi_broker_engine.py --iterations 1
```

Expected output:
```
🚀 MULTI-BROKER TRADING ENGINE STARTING
✅ Coinbase connected (Crypto)
📊 Fetching market data from all brokers...
   ✅ Coinbase: 4 pairs
🎯 Running strategy analysis...
   ✅ coinbase   BTC-USD → 2 signals
   ✅ coinbase   ETH-USD → 1 signal
```

- [ ] See "✅ Coinbase connected"?
- [ ] See market data from 4 pairs?
- [ ] See strategy signals generating?
- [ ] No errors in output?

**If YES** → Proceed to Phase 3  
**If NO** → Check troubleshooting below


### Phase 3: Paper Mode (24 hours)

#### Step 5: Start Paper Trading
```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN
export ENVIRONMENT=practice
python3 multi_broker_engine.py
```

- [ ] Process started successfully
- [ ] No "Connection refused" errors
- [ ] Trading loop running (watch for iterations)

#### Step 6: Monitor in Separate Terminal
```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN
tail -f narration.jsonl | grep -E 'execution|signal|coinbase'
```

Expected to see:
- [ ] Execution events (trades being placed)
- [ ] Signal events (strategies firing)
- [ ] Hive Mind consensus voting
- [ ] ML confidence filtering

#### Step 7: Collect Metrics (After 24 hours)

Check trades:
```bash
grep -i 'execution' narration.jsonl | wc -l
# Should see 10-20 trades
```
- [ ] Trades: ______ (target: 10-20)

Check win rate:
```bash
python3 << 'EOF'
import json
wins, losses = 0, 0
with open('narration.jsonl') as f:
    for line in f:
        try:
            evt = json.loads(line)
            text = evt.get('text', '').lower()
            if 'win' in text: wins += 1
            elif 'loss' in text: losses += 1
        except: pass
if wins + losses > 0:
    print(f"Wins: {wins}, Losses: {losses}, Rate: {100*wins/(wins+losses):.0f}%")
EOF
```
- [ ] Win rate: ______ % (target: ≥70%)

Check P&L:
```bash
grep -i 'pnl' narration.jsonl | tail -5
```
- [ ] Total P&L: ______ (target: positive)

#### Phase 3 Success Criteria
- [ ] Win rate ≥70%?
- [ ] At least 10 trades?
- [ ] Total P&L positive?
- [ ] No system crashes?

**If ALL YES** → Proceed to Phase 4 (LIVE)  
**If ANY NO** → Debug issues, run longer paper mode


### Phase 4: Production Deployment (Real Money!)

#### Step 8: Create Backup (CRITICAL!)
```bash
mkdir -p ROLLBACK_SNAPSHOTS
cp -r . ROLLBACK_SNAPSHOTS/crypto_live_backup_$(date +%s)/
```

- [ ] Backup created
- [ ] Verify: `ls -la ROLLBACK_SNAPSHOTS/`
- [ ] Should see directory like `crypto_live_backup_1729189800/`

#### Step 9: Switch to Live Environment
```bash
export ENVIRONMENT=live
```

- [ ] Environment variable set
- [ ] Verify: `echo $ENVIRONMENT` should show `live`

#### Step 10: Start Live Trading (Background)
```bash
nohup python3 multi_broker_engine.py > crypto_trading.log 2>&1 &
sleep 2
ps aux | grep multi_broker_engine
```

- [ ] Process started (see PID)
- [ ] No errors in initial startup
- [ ] Process showing in `ps` output

#### Step 11: Verify Live Trading Active
```bash
tail -20 crypto_trading.log
tail -20 narration.jsonl
```

- [ ] Log file shows trading activity
- [ ] Narration shows live execution
- [ ] Timestamps are current (not old)

#### Step 12: Intensive Monitoring (24 hours)

**Terminal 1: Watch logs**
```bash
tail -f crypto_trading.log
```
- [ ] No error messages
- [ ] Regular activity
- [ ] No crashes

**Terminal 2: Monitor trades**
```bash
tail -f narration.jsonl | grep -i execution
```
- [ ] Trades executing
- [ ] Real money engaged

**Terminal 3: Check P&L every 5 min**
```bash
watch -n 5 'tail -5 narration.jsonl | grep -i pnl'
```
- [ ] P&L growing (target: +0.2% daily)
- [ ] Win rate holding (target: ≥65%)

#### Emergency Stop (If Needed)
```bash
pkill -f multi_broker_engine.py
sleep 2
ps aux | grep multi_broker_engine  # Should show nothing
```

- [ ] Confirmed stopped
- [ ] No lingering processes


### Phase 5: Scale Up (After 1 week success)

Once Coinbase is stable and profitable:

#### Add OANDA Forex (Optional)
- [ ] OANDA credentials already in .env (from Phase 6)
- [ ] Uncomment OANDA lines in crypto_first.env
- [ ] Test in paper mode first
- [ ] Then go live with OANDA enabled
- [ ] Expected: +15-25 additional trades/day

#### Add IBKR Equities (Optional)
- [ ] Start IB Gateway
- [ ] Add IBKR credentials to crypto_first.env
- [ ] Test in paper mode first
- [ ] Then go live with IBKR enabled
- [ ] Expected: +5-10 additional trades/day


---

## 🔴 TROUBLESHOOTING

### Issue: "Coinbase API: Invalid Signature"
**Solution**:
1. Double-check API key format in crypto_first.env
2. Verify exact match from Coinbase UI
3. Reload: `source crypto_first.env`
4. Test: `echo $COINBASE_API_KEY`

### Issue: "Connection refused"
**Solution**:
1. Check internet connection
2. Verify Coinbase API endpoint is accessible
3. Try single iteration first: `python3 multi_broker_engine.py --iterations 1`

### Issue: "No trades executing"
**Solution**:
1. Check market conditions (very quiet market = fewer signals)
2. Verify strategies generating signals: `grep -i signal narration.jsonl`
3. Check Hive Mind voting: `grep -i hive narration.jsonl`
4. Check ML confidence: `grep -i confidence narration.jsonl`

### Issue: "Win rate below 60%"
**Solution**:
1. Market conditions change - extend paper mode
2. Run for another 24 hours to get more samples
3. Verify all 5 strategies are active
4. Check if market is in consolidation (fewer high-probability setups)

### Issue: "Process crashed"
**Solution**:
1. Check error: `tail -100 crypto_trading.log`
2. Stop: `pkill -f multi_broker_engine.py`
3. Restore: `cp ROLLBACK_SNAPSHOTS/crypto_live_backup_*/. .`
4. Restart paper mode to debug

---

## 📊 MONITORING COMMANDS (Copy-Paste Ready)

**Check live process:**
```bash
ps aux | grep multi_broker_engine
```

**View recent trades:**
```bash
tail -20 narration.jsonl | grep -i execution
```

**Calculate current P&L:**
```bash
grep -i 'pnl' narration.jsonl | tail -1
```

**Count total trades:**
```bash
grep -c 'execution' narration.jsonl
```

**View win rate:**
```bash
python3 << 'EOF'
import json
w, l = 0, 0
with open('narration.jsonl') as f:
    for line in f:
        try:
            evt = json.loads(line)
            t = evt.get('text','').lower()
            if 'win' in t: w += 1
            elif 'loss' in t: l += 1
        except: pass
if w+l > 0: print(f"{100*w/(w+l):.0f}% ({w}W {l}L)")
EOF
```

**Emergency stop:**
```bash
pkill -f multi_broker_engine.py
```

**Restore from backup:**
```bash
cp ROLLBACK_SNAPSHOTS/crypto_live_backup_*/. .
```

---

## ✅ DEPLOYMENT SUMMARY

**Status**: 🔴 READY TO START

**Current Phase**: Phase 1 - API Setup

**Next Actions**:
1. [ ] Get Coinbase API key
2. [ ] Add to crypto_first.env
3. [ ] Test connectivity (1 iteration)
4. [ ] Deploy paper mode (24 hours)
5. [ ] Deploy live (if metrics pass)

**Expected Timeline**:
- API Setup: 10 minutes
- Connectivity Test: 5 minutes
- Paper Mode: 24 hours
- Live Trading: Start by tomorrow

**Risk Level**: ✅ MANAGED
- All 50+ guardian rules active
- Backup created before going live
- Emergency stop procedure ready
- Narration logging 100%

---

**Ready to proceed? Start with Step 1: Get Coinbase API credentials**

Generated: October 17, 2025  
PIN: 841921  
Mode: Crypto-First

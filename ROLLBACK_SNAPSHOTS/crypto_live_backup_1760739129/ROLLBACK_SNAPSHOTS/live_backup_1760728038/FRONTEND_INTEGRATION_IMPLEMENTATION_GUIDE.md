# Frontend Integration — Implementation Guide

**Date**: October 17, 2025  
**Target**: Phase 5 Dashboard Polish  
**Status**: Ready for Backend Developer

---

## 🎯 What You're Implementing

Your dashboard frontend has **UI elements that look great** but lack **backend data wiring**. This guide shows exactly what's missing and how to wire it.

**Current State**: 90% UI-ready, 10% data-ready  
**Goal State**: 100% production UI with real-time data  
**Time Estimate**: 6-8 hours total (can be split across multiple sessions)

---

## 📊 Gap Summary

| #  | Issue | Current | Target | Priority | Hours |
|----|-------|---------|--------|----------|-------|
| 1  | Raw JSON in narration | `{"source":"oanda",...}` | "OCO placed @ 1.40382" | 🔴 CRITICAL | 1 |
| 2  | Hive analysis shows nothing | "HIVE_ANALYSIS: USD_CAD" | "GPT 78% BUY\|GROK 72% BUY\|DS 65% HOLD" | 🔴 CRITICAL | 1.5 |
| 3  | Event cards empty | `<div></div>` | "BUY 100 EUR_USD @ 1.1655" | 🟠 HIGH | 1 |
| 4  | No broker status | None | "OANDA: Connected, Balance: $100k" | 🟠 HIGH | 1.5 |
| 5  | 10s narration lag | Polling every 10s | SSE stream (< 500ms) | 🟠 HIGH | 2 |
| 6  | No testing framework | Manual testing | Automated test events | 🟡 MED | 1 |
| 7  | Tabs don't switch | Non-functional | Hive panel populates | 🟡 MED | 1 |

**Total Hours**: 6-8 (pick what matters most for Phase 5)

---

## 🔴 CRITICAL #1: Fix Raw JSON in Narration

### The Problem (What Users See Now)

```
[19:09:26] {"source":"oanda","type":"oco_placed","payload":{"order_id":"paper-oanda-1",...},"ts":"..."}
[19:09:26] {"source":"coinbase","type":"order_placed","payload":{"order_id":"paper-1",...},"ts":"..."}
[01:00:57] 💬 Rick: OCO order placed on USD_CAD @ 1.40382, -10700 units. Execution latency: 197.2ms.
```

**Users should see clean narration, not raw JSON technical data.**

### Why It's Happening

File: `dashboard/app.py` lines 1571-1620

```python
# Current /api/narration endpoint
@app.route('/api/narration', methods=['GET'])
def narration():
    events = get_latest_narration(n=50)  # Gets raw broker events
    
    for event in events:
        if event_type == 'OANDA_CONNECTION':
            event['rick_says'] = "Connected to OANDA..."  # ✅ Has commentary
        # ... more event types ...
        # BUT: No handling for OCO_PLACED, ORDER_PLACED, HEARTBEAT
        # So frontend falls back to displaying raw event.text or JSON
```

### The Fix (1 hour)

**In `dashboard/app.py` around line 1605**, add these handlers:

```python
elif event_type == 'OCO_PLACED':
    symbol = event.get('symbol') or details.get('instrument', 'UNKNOWN')
    side = details.get('side', 'BUY')
    units = details.get('units', '?')
    entry = details.get('entry', '?')
    sl = details.get('sl', '?')
    tp = details.get('tp', '?')
    quality = details.get('quality', '?')
    
    event['rick_says'] = (
        f"OCO order placed on {symbol}: {side} {units} units @ {entry}. "
        f"SL: {sl}, TP: {tp}. Quality: {quality}%."
    )

elif event_type == 'ORDER_PLACED':
    # Coinbase style
    side = details.get('side', 'BUY')
    product = details.get('product_id', 'UNKNOWN')
    size = details.get('size', '?')
    order_id = details.get('order_id', '?')
    
    event['rick_says'] = (
        f"Order opened: {side} {size} {product}. Order ID: {order_id}."
    )

elif event_type == 'HEARTBEAT':
    mode = details.get('mode', 'UNKNOWN')
    status = details.get('status', 'unknown')
    event['rick_says'] = f"(Arena heartbeat — {mode} mode, {status})"

elif event_type == 'TRADE_CLOSED':
    symbol = event.get('symbol', 'UNKNOWN')
    exit_price = details.get('exit_price', '?')
    pnl = details.get('pnl', '?')
    event['rick_says'] = (
        f"Trade closed on {symbol} @ {exit_price}. P&L: ${pnl}."
    )

else:
    # Fallback: generate generic rick_says from event_type
    event['rick_says'] = f"[{event_type}] Event occurred on {venue or 'internal'}."
```

### Verification

1. Open dashboard: http://127.0.0.1:3000
2. Trigger a trade or check `/api/narration` in browser console
3. **Before**: Narration feed shows raw JSON blocks
4. **After**: Narration feed shows "OCO order placed on EUR_USD @ 1.1655"

---

## 🔴 CRITICAL #2: Show Hive Agent Votes

### The Problem

```
[01:01:57] 💬 Rick: HIVE_ANALYSIS: USD_CAD - hive
[01:02:03] 💬 Rick: HIVE_ANALYSIS: USD_CAD - hive
[01:02:09] 💬 Rick: HIVE_ANALYSIS: USD_CAD - hive
```

**Repeated identical messages with ZERO information about WHY the Hive decided.**

### What Users Should See

```
[01:01:57] 💬 Rick: Hive consensus on USD_CAD:
           → GPT (35%): 78% confidence BUY
           → GROK (35%): 72% confidence BUY  
           → DeepSeek (30%): 65% confidence HOLD
           → Final: 72% confidence BUY (2/3 agents agree)
```

### The Fix (1.5 hours)

**Step 1: Expose Hive voting breakdown**

Create new endpoint in `dashboard/app.py`:

```python
@app.route('/api/hive/analyze', methods=['GET'])
def hive_analyze():
    """Get detailed Hive agent votes for a symbol"""
    symbol = request.args.get('symbol', 'EUR_USD')
    
    try:
        # Import hive processor
        from hive.rick_hive_mind import get_hive_consensus_breakdown
        
        # Get voting data (you'll need to expose this function)
        breakdown = get_hive_consensus_breakdown(symbol)
        
        return jsonify({
            'symbol': symbol,
            'agent_votes': {
                'gpt': {
                    'signal': breakdown['gpt_signal'],        # 'BUY', 'SELL', 'HOLD'
                    'confidence': breakdown['gpt_confidence'],  # 0.0-1.0
                    'reasoning': breakdown['gpt_reason']
                },
                'grok': {
                    'signal': breakdown['grok_signal'],
                    'confidence': breakdown['grok_confidence'],
                    'reasoning': breakdown['grok_reason']
                },
                'deepseek': {
                    'signal': breakdown['ds_signal'],
                    'confidence': breakdown['ds_confidence'],
                    'reasoning': breakdown['ds_reason']
                }
            },
            'consensus': {
                'direction': breakdown['final_direction'],      # BUY/SELL/HOLD
                'confidence': breakdown['final_confidence'],    # 0.0-1.0
                'agreement_strength': breakdown['agreement'],   # 1/3, 2/3, 3/3
                'weights': {
                    'gpt': 0.35,
                    'grok': 0.35,
                    'deepseek': 0.30
                }
            },
            'timestamp': breakdown['timestamp']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**Step 2: Update narration formatter**

In `dashboard/app.py` around line 1615, add:

```python
elif event_type == 'HIVE_ANALYSIS':
    symbol = event.get('symbol', 'UNKNOWN')
    hive_details = details.get('breakdown', {})
    
    gpt_conf = (hive_details.get('gpt_confidence', 0.5) * 100)
    grok_conf = (hive_details.get('grok_confidence', 0.5) * 100)
    ds_conf = (hive_details.get('ds_confidence', 0.5) * 100)
    
    gpt_sig = hive_details.get('gpt_signal', '?')
    grok_sig = hive_details.get('grok_signal', '?')
    ds_sig = hive_details.get('ds_signal', '?')
    
    consensus_conf = (hive_details.get('final_confidence', 0.5) * 100)
    consensus_dir = hive_details.get('final_direction', '?')
    
    event['rick_says'] = (
        f"Hive consensus on {symbol}: "
        f"GPT {gpt_conf:.0f}% {gpt_sig} | "
        f"GROK {grok_conf:.0f}% {grok_sig} | "
        f"DeepSeek {ds_conf:.0f}% {ds_sig} → "
        f"Final: {consensus_conf:.0f}% {consensus_dir}"
    )
    
    # Add breakdown for modal/detail view
    event['hive_breakdown'] = hive_details
```

**Step 3: Add frontend modal for details**

In `dashboard.html`, add click listener:

```javascript
// Add to document event listeners
document.addEventListener('click', function(e) {
    if (e.target.closest('.narration-line[data-event-type="HIVE_ANALYSIS"]')) {
        const line = e.target.closest('.narration-line');
        const symbol = line.dataset.symbol;
        
        // Fetch detailed breakdown
        fetch(`/api/hive/analyze?symbol=${symbol}`)
            .then(r => r.json())
            .then(data => showHiveModal(data));
    }
});

function showHiveModal(data) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Hive Consensus: ${data.symbol}</h2>
            <div class="agent-votes">
                <div class="agent">
                    <strong>GPT (35% weight)</strong>
                    ${data.agent_votes.gpt.signal} @ ${(data.agent_votes.gpt.confidence*100).toFixed(0)}%
                    <p style="opacity: 0.7; font-size: 0.9em;">${data.agent_votes.gpt.reasoning}</p>
                </div>
                <div class="agent">
                    <strong>GROK (35% weight)</strong>
                    ${data.agent_votes.grok.signal} @ ${(data.agent_votes.grok.confidence*100).toFixed(0)}%
                    <p style="opacity: 0.7; font-size: 0.9em;">${data.agent_votes.grok.reasoning}</p>
                </div>
                <div class="agent">
                    <strong>DeepSeek (30% weight)</strong>
                    ${data.agent_votes.deepseek.signal} @ ${(data.agent_votes.deepseek.confidence*100).toFixed(0)}%
                    <p style="opacity: 0.7; font-size: 0.9em;">${data.agent_votes.deepseek.reasoning}</p>
                </div>
            </div>
            <div class="consensus">
                <strong>Consensus</strong>: ${data.consensus.direction} @ ${(data.consensus.confidence*100).toFixed(0)}%
            </div>
            <button onclick="this.parentElement.parentElement.remove()">Close</button>
        </div>
    `;
    document.body.appendChild(modal);
}
```

### Verification

1. Trigger a Hive analysis on the system
2. Open dashboard narration feed
3. **Before**: "HIVE_ANALYSIS: USD_CAD - hive" (repeated)
4. **After**: "Hive consensus on USD_CAD: GPT 78% BUY | GROK 72% BUY | DeepSeek 65% HOLD → Final: 72% BUY"
5. Click the message to see detailed modal

---

## 🟠 HIGH #3: Non-Critical But Useful Implementations

### Quick Wins (30 min each)

**A. Event Card Descriptions**

Current: Empty `<div></div>` in event cards  
Target: "BUY 100 EUR_USD @ 1.1655"

In frontend `formatNarrationLine()`, add case for card details:

```javascript
const eventDescriptions = {
    'OCO_PLACED': (evt) => 
        `${evt.details.side} ${evt.details.units}u @ ${evt.details.entry} | SL: ${evt.details.sl}`,
    'ORDER_PLACED': (evt) =>
        `${evt.details.side} ${evt.details.size} ${evt.details.product_id}`,
    'DUAL_CONNECTOR_INIT': (evt) =>
        `Mode: ${evt.details.mode} | Live: ${evt.details.live_available}`,
};

// When rendering event card:
const desc = eventDescriptions[eventType];
if (desc) cardDiv.innerHTML = desc(event);
```

**B. Broker Status Cards**

Create `/api/brokers/status` endpoint returning connection state, balance, positions.

**C. SSE Streaming**

Replace polling with real-time Server-Sent Events:

```python
@app.route('/api/narration/stream')
def narration_stream():
    def generate():
        while True:
            events = get_latest_narration(n=1)  # Get newest only
            if events:
                yield f"data: {json.dumps(events[0])}\n\n"
            time.sleep(0.5)  # Check every 500ms
    
    return Response(generate(), mimetype='text/event-stream')
```

Frontend:

```javascript
const eventSource = new EventSource('/api/narration/stream');
eventSource.onmessage = (e) => {
    const event = JSON.parse(e.data);
    // Render immediately (< 500ms latency)
};
```

---

## 📋 Implementation Checklist

- [ ] **Phase A (Critical)** — 2-3 hours
  - [ ] Add broker event `rick_says` formatters (OCO_PLACED, ORDER_PLACED, HEARTBEAT)
  - [ ] Implement `/api/hive/analyze` endpoint
  - [ ] Test narration feed shows formatted text, not JSON

- [ ] **Phase B (High)** — 3-4 hours
  - [ ] Add event card description templates
  - [ ] Create `/api/brokers/status` endpoint
  - [ ] Implement SSE narration streaming

- [ ] **Phase C (Medium)** — 2 hours
  - [ ] Create test event generator
  - [ ] Wire up tab switching for Hive panel

---

## 🚀 Quick Start Commands

```bash
# Test narration endpoint
curl http://127.0.0.1:5000/api/narration | jq

# Test hive endpoint (once implemented)
curl http://127.0.0.1:5000/api/hive/analyze?symbol=EUR_USD | jq

# Open dashboard
open http://127.0.0.1:3000

# Watch dashboard logs
tail -f logs/dashboard.log
```

---

## 📞 Key Files Reference

| File | Purpose | Key Function |
|------|---------|--------------|
| `dashboard/app.py` | Flask backend | `/api/narration` endpoint (line 1571) |
| `dashboard.html` | Frontend UI | `formatNarrationLine()` (line 1006) |
| `hive/rick_hive_mind.py` | Hive voting | Needs export of breakdown function |
| `util/narration_logger.py` | Event storage | `get_latest_narration()` |

---

**Status**: Ready for implementation  
**Next Step**: Start with Phase A Critical fixes  
**Questions**: See FRONTEND_INTEGRATION_CHECKLIST.md for details


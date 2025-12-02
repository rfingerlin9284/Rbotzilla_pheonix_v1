# RICK Dashboard Frontend Snapshot — Integration Review Package

Purpose: This bundle captures the exact UI fragments you selected (HTML/CSS) and a clear summary so another AI agent can quickly see what’s rendering and what still isn’t wired to the backend.

Use: Share this file together with the screenshot noted below. It contains selectors, raw DOM fragments, and observed states pointing to missing backend connections.

---

## 1) Screenshot (attach alongside this doc)

- File placeholder: assets/snapshots/rick_dashboard_snapshot_2025-10-16.png
- If you have the screenshot saved locally, drop it at the path above so it’s versioned with this doc. If the path differs, just update this line so the reviewing agent can find it.

What the screenshot shows at a glance:
- RICK Companion panel open with Chat/Hive/Narrator tabs
- Narration feed streaming with Rick messages
- Multiple raw JSON lines for Arena/OANDA/Coinbase events (not plain-English formatted)

---

## 2) UI selectors you highlighted

These are the exact elements you selected; an agent can use them to bind listeners, populate content, or toggle UI state.

- div
- button#tabNarrator.companion-btn
- button#tabHive.companion-btn
- button#tabChat.companion-btn
- div.companion-title
- div
- div#companionLog.companion-log
- div.companion-header
- div.header
- div.controls
- div.stat
- div.stat-1
- div.stat-2
- div.stat-3
- div.stat-4
- div.card
- html

---

## 3) Narration feed — raw HTML fragment (as rendered)

This is the narration stream div with its current child lines exactly as seen in your selection.

```html
<div class="narration-feed" id="narration-feed">
  <div class="narration-empty" id="narration-empty" style="display: none;">
      ⏳ Waiting for trade activity...
  </div>
  <div class="narration-line new"><span class="narration-timestamp">19:09:26</span><span class="narration-text"> {"source":"arena","type":"heartbeat","payload":{"status":"started","mode":"true"},"ts":"2025-10-16T11:39:49.386111Z"}</span></div>
  <div class="narration-line new"><span class="narration-timestamp">19:09:26</span><span class="narration-text"> {"source":"oanda","type":"oco_placed","payload":{"order_id":"paper-oanda-1","instrument":"EUR_USD","side":"BUY","units":100,"entry":1.1655,"sl":1.16,"tp":1.17,"quality":75,"mode":"paper","ttl_min":360},"ts":"2025-10-16T11:41:45.607529Z"}</span></div>
  <div class="narration-line new"><span class="narration-timestamp">19:09:26</span><span class="narration-text"> {"source":"coinbase","type":"order_placed","payload":{"order_id":"paper-1","product_id":"BTC-USD","side":"BUY","size":0.001,"mode":"paper"},"ts":"2025-10-16T11:42:13.182297Z"}</span></div>
  <div class="narration-line new"><span class="narration-timestamp">19:09:26</span><span class="narration-text"> {"source":"oanda","type":"oco_placed","payload":{"order_id":"paper-oanda-2","instrument":"EUR_USD","side":"BUY","units":100,"entry":1.1655,"sl":1.16,"tp":1.17,"quality":75,"mode":"paper","ttl_min":360},"ts":"2025-10-16T11:54:53.461353Z"}</span></div>
  <div class="narration-line new"><span class="narration-timestamp">19:09:26</span><span class="narration-text"> {"source":"oanda","type":"oco_placed","payload":{"order_id":"paper-oanda-3","instrument":"EUR_USD","side":"BUY","units":100,"entry":1.1655,"sl":1.16,"tp":1.17,"quality":75,"mode":"paper","ttl_min":360},"ts":"2025-10-16T11:55:27.021050Z"}</span></div>
  <div class="narration-line new"><span class="narration-timestamp">19:09:26</span><span class="narration-text"> {"source":"coinbase","type":"order_placed","payload":{"order_id":"paper-2","product_id":"BTC-USD","side":"BUY","size":0.001,"mode":"paper"},"ts":"2025-10-16T11:55:27.026738Z"}</span></div>
  <div class="narration-line new"><span class="narration-timestamp">01:00:56</span><span class="narration-text">💬 <strong>Rick:</strong> ENGINE_START: SYSTEM - oanda</span></div>
  <div class="narration-line new"><span class="narration-timestamp">01:00:57</span><span class="narration-text">💬 <strong>Rick:</strong> TRADE_SIGNAL: USD_CAD - oanda</span></div>
  <div class="narration-line new"><span class="narration-timestamp">01:00:57</span><span class="narration-text">💬 <strong>Rick:</strong> OCO order placed on USD_CAD @ 1.40382, -10700 units. Execution latency: 197.2ms.</span></div>
  <div class="narration-line new"><span class="narration-timestamp">01:00:57</span><span class="narration-text">💬 <strong>Rick:</strong> Trade opened: SELL USD_CAD @ 1.40382. Position is live, stops are set.</span></div>
  <div class="narration-line new"><span class="narration-timestamp">01:01:57</span><span class="narration-text">💬 <strong>Rick:</strong> HIVE_ANALYSIS: USD_CAD - hive</span></div>
  <!-- Many repeated HIVE_ANALYSIS lines -->
  <div class="narration-line new"><span class="narration-timestamp">09:21:24</span><span class="narration-text">💬 <strong>Rick:</strong> DASHBOARD_TEST: TEST_USD - internal</span></div>
  <div class="narration-line new"><span class="narration-timestamp">09:38:24</span><span class="narration-text">💬 <strong>Rick:</strong> Dual-connector initialized: live market data + practice execution. Live available: True. Ready for action.</span></div>
  <div class="narration-line new"><span class="narration-timestamp">09:38:24</span><span class="narration-text">💬 <strong>Rick:</strong> Order via dual-source: using live prices, executing on practice. Entry: 1.08500. Market data separate from execution - clean separation.</span></div>
  <div class="narration-line new"><span class="narration-timestamp">09:39:33</span><span class="narration-text">💬 <strong>Rick:</strong> Dual-connector initialized: practice market data + practice execution. Live available: False. Ready for action.</span></div>
</div>
```

---

## 4) CSS rules (as captured with your selection)

The following are the rule excerpts you selected. They help another agent quickly reproduce the styling context.

```css
/* Matched Rule from user-agent */
div { display: block; }

/* Matched Rule from user-agent */
address, blockquote, center, div, figure, figcaption, footer, form, header, hr, legend, listing, main, p, plaintext, pre, summary, xmp, article, aside, h1, h2, h3, h4, h5, h6, hgroup, nav, section, search, table, caption, colgroup, col, thead, tbody, tfoot, tr, td, th, dir, dd, dl, dt, menu, ol, ul, li, bdi, output, [dir="ltr" i], [dir="rtl" i], [dir="auto" i] {
  unicode-bidi: isolate;
}

/* Matched Rule from regular */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* Matched Rule from regular */
.narration-feed {
  height: 500px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 0.95em;
  line-height: 1.6;
  padding: 15px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  border: 1px solid rgba(255, 215, 0, 0.2);
}

/* Inherited styles from page */
.narration-stream {
  background: rgba(0, 0, 0, 0.4);
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 30px;
  border: 2px solid rgba(255, 215, 0, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.container { max-width: 1400px; margin: 0 auto; }
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; padding: 20px; }
html { display: block; }
```

---

## 5) Event card — raw HTML fragment (as rendered)

Two copies were selected; they’re identical and show an empty description area.

```html
<div class="event">
  <span class="event-type">DUAL_CONNECTOR_INIT</span>
  <span style="opacity: 0.6;"> @ internal</span>
  <div class="event-time">2025-10-16T09:39:33.060631+00:00</div>
  <div style="margin-top: 5px; opacity: 0.7; font-size: 0.85em;"></div>
</div>
```

Associated styles:

```css
.event {
  background: rgba(0,0,0,0.2);
  padding: 10px;
  margin-bottom: 8px;
  border-radius: 8px;
  font-size: 0.9em;
}
.events-list { max-height: 300px; overflow-y: auto; margin-top: 15px; }
.card {
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  border: 1px solid rgba(255,255,255,0.18);
}
```

---

## 6) Quick backend-connection inference (from what’s visible)

This section is to guide the reviewing agent; it’s based solely on the UI fragments above.

- Raw JSON log lines are showing in the narration-feed for Arena/OANDA/Coinbase events.
  - Likely missing a formatter layer that converts structured events into plain-English display for non-"Rick:" messages.
  - Actionable: implement/utilize a `rick_narration_formatter` in the `/api/narration` response.
- Repeated `HIVE_ANALYSIS: USD_CAD - hive` with no deeper detail.
  - Suggests a placeholder message rather than live consensus details (confidence, agent breakdown).
  - Actionable: expose a `/api/hive/analyze` endpoint or WebSocket stream and render agent/confidence results.
- Event cards (e.g., DUAL_CONNECTOR_INIT) have an empty description div.
  - Indicates the card body isn’t populated from event payload (missing mapping/templating function).
  - Actionable: map event types → description templates in the frontend or in the API.
- The presence of Coinbase and OANDA events implies the dashboard does receive multi-source messages, but UX still shows some raw structures instead of human-friendly summaries.

Optional endpoints the backend may need to expose (if not already):
- GET `/api/narration` → return both raw and formatted text for each event
- GET `/api/hive/analyze?symbol=...` → return consensus + agent breakdown
- GET `/api/brokers/status` → per-broker connected/balance/positions
- WebSocket/SSE bridge to Hive Mind if using a separate port

---

## 7) How to hand off

- Share this Markdown file and the screenshot file together.
- The reviewing agent can recreate the exact DOM/CSS context and compare with your running dashboard at http://127.0.0.1:3000/.
- If they need live data, point them to `dashboard/app.py` and the narration JSON endpoints already in your project.

---

If you want, I can also create a compact JSON hand-off (selectors + fragments) for automated ingestion by another agent.

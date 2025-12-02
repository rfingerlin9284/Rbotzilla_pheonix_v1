from flask import Flask, render_template_string, request, redirect, url_for, jsonify, Response, stream_with_context
import subprocess
import os
import sys
import logging
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from util.mode_manager import get_mode_info, switch_mode
from util.narration_logger import get_latest_narration, get_session_summary
from util.rick_narrator import get_latest_rick_narration
from util.rick_live_monitor import get_active_bots_snapshot, get_live_monitor

app = Flask(__name__)
logger = logging.getLogger(__name__)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SESSION = 'rbot_headless'

# --- Arena SSE proxy (same-origin) and simple viewer ---
@app.route('/arena/events')
def arena_events_proxy():
    """Proxy RBOT Arena SSE stream (8787) through Flask (8080) to avoid CORS issues.

    Important: we set a finite connect-timeout and no read-timeout so the
    long-lived SSE connection doesn't drop periodically.
    """
    arena_url = os.environ.get('ARENA_EVENTS_URL', 'http://127.0.0.1:8787/events')

    def generate():
        try:
            # Connect timeout 3s, read timeout None (stream stays open)
            with requests.get(
                arena_url,
                stream=True,
                timeout=(3, None),
                headers={
                    'Accept': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'User-Agent': 'rick-dashboard-sse-proxy'
                }
            ) as r:
                r.raise_for_status()
                # Iterate line-by-line to preserve SSE frame boundaries
                for line in r.iter_lines(chunk_size=1024, decode_unicode=False):
                    if line is None:
                        continue
                    # Forward exactly as received (bytes); add trailing newline back
                    yield line + b"\n"
                # If the upstream closes cleanly, end the stream
                return
        except GeneratorExit:
            # Client disconnected; stop generating
            return
        except Exception as e:
            # Emit one error event then close
            payload = {"error": str(e), "source": "arena_proxy"}
            msg = f"data: {payload}\n\n".encode('utf-8')
            yield msg

    headers = {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',  # disable buffering on some proxies
    }
    return Response(stream_with_context(generate()), headers=headers)


@app.route('/arena-test')
def arena_test_page():
    """Minimal page to verify Arena SSE stream in the browser."""
    return render_template_string(
        """
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>Arena SSE Test</title>
            <style>
                body { font-family: Segoe UI, sans-serif; background:#111827; color:#d1d5db; padding:20px; }
                pre { background:#0b1220; padding:12px; border-radius:8px; max-height:70vh; overflow:auto; }
                .ok { color:#10b981 }
                .err { color:#ef4444 }
            </style>
        </head>
        <body>
            <h2>RBOT Arena SSE viewer</h2>
            <p>Connecting to <code>/arena/events</code> (proxy to 8787)...</p>
            <pre id="out"></pre>
            <script>
                const out = document.getElementById('out');
                function log(line, cls) {
                    const span = document.createElement('div');
                    if (cls) span.className = cls;
                    span.textContent = line;
                    out.appendChild(span);
                    out.scrollTop = out.scrollHeight;
                }
                try {
                    const es = new EventSource('/arena/events');
                    es.onopen = () => log('[open] connected', 'ok');
                    es.onerror = (e) => log('[error] ' + (e?.message || 'SSE error'), 'err');
                    es.onmessage = (e) => log(e.data);
                } catch (e) {
                    log('Failed to connect: ' + e, 'err');
                }
            </script>
        </body>
        </html>
        """
    )

INDEX_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>RICK Trading Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid rgba(255,255,255,0.2);
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .mode-badge {
            display: inline-block;
            padding: 8px 20px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.1em;
            margin-top: 10px;
        }
        .mode-off { background: #6c757d; }
        .mode-ghost { background: #17a2b8; }
        .mode-canary { background: #ffc107; color: #000; }
        .mode-live { background: #dc3545; animation: pulse 2s infinite; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255,255,255,0.18);
        }
        .card h2 {
            font-size: 1.3em;
            margin-bottom: 15px;
            color: #ffd700;
        }
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .stat:last-child { border-bottom: none; }
        .stat-label { opacity: 0.8; }
        .stat-value {
            font-weight: bold;
            font-size: 1.1em;
        }
        .positive { color: #28a745; }
        .negative { color: #dc3545; }
        .events-list {
            max-height: 300px;
            overflow-y: auto;
            margin-top: 15px;
        }
        .event {
            background: rgba(0,0,0,0.2);
            padding: 10px;
            margin-bottom: 8px;
            border-radius: 8px;
            font-size: 0.9em;
        }
        .event-type {
            font-weight: bold;
            color: #ffd700;
        }
        .event-time {
            opacity: 0.6;
            font-size: 0.85em;
        }
        .controls {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .refresh-notice {
            text-align: center;
            opacity: 0.7;
            font-size: 0.9em;
            margin-top: 20px;
        }
        /* RICK LIVE NARRATION STREAM */
        .narration-stream {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            border: 2px solid rgba(255, 215, 0, 0.3);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        }
        .narration-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255, 215, 0, 0.3);
        }
        .narration-title {
            font-size: 1.4em;
            color: #ffd700;
            font-weight: bold;
        }
        .narration-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #28a745;
            font-size: 0.9em;
        }
        .live-dot {
            width: 10px;
            height: 10px;
            background: #28a745;
            border-radius: 50%;
            animation: blink 1.5s ease-in-out infinite;
        }
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
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
        .narration-feed::-webkit-scrollbar {
            width: 8px;
        }
        .narration-feed::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
        }
        .narration-feed::-webkit-scrollbar-thumb {
            background: rgba(255, 215, 0, 0.5);
            border-radius: 10px;
        }
        .narration-feed::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 215, 0, 0.7);
        }
        .narration-line {
            margin-bottom: 12px;
            padding: 8px;
            border-radius: 5px;
            transition: background 0.3s ease;
        }
        .narration-line:hover {
            background: rgba(255, 215, 0, 0.1);
        }
        .narration-line.new {
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .narration-timestamp {
            color: #007bff;
            margin-right: 10px;
            font-weight: bold;
        }
        .narration-event {
            color: #ffd700;
            font-weight: bold;
            margin-right: 10px;
        }
        .narration-text {
            color: #e0e0e0;
        }
        .narration-symbol {
            color: #28a745;
            font-weight: bold;
        }
        .narration-venue {
            color: #dc3545;
            font-style: italic;
        }
        .narration-empty {
            text-align: center;
            padding: 40px;
            color: #6c757d;
            font-size: 1.1em;
        }
        
        /* RICK COMPANION SIDEBAR & OVERLAY */
        .companion-sidebar {
            position: fixed;
            top: 50%;
            right: 0;
            transform: translateY(-50%);
            z-index: 9999;
            background: linear-gradient(180deg, rgba(57, 255, 20, 0.8), rgba(0, 92, 180, 0.8));
            border-radius: 15px 0 0 15px;
            padding: 15px 8px;
            box-shadow: -4px 0 20px rgba(0, 0, 0, 0.5);
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .companion-sidebar:hover {
            padding-right: 15px;
            box-shadow: -8px 0 30px rgba(57, 255, 20, 0.4);
        }
        
        .companion-sidebar-icon {
            writing-mode: vertical-rl;
            text-orientation: mixed;
            font-size: 16px;
            font-weight: bold;
            color: white;
            letter-spacing: 2px;
            text-shadow: 0 0 10px rgba(0, 0, 0, 0.8);
        }
        
        .companion-overlay {
            position: fixed;
            top: 80px;
            right: 20px;
            width: 450px;
            height: 600px;
            background: linear-gradient(135deg, rgba(20, 22, 35, 0.75), rgba(30, 32, 50, 0.65));
            backdrop-filter: blur(12px) saturate(150%);
            border: 2px solid rgba(57, 255, 20, 0.3);
            border-radius: 20px;
            box-shadow: 0 15px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(57, 255, 20, 0.2);
            display: none;
            flex-direction: column;
            z-index: 10000;
            opacity: 1;
            transition: opacity 0.4s ease, transform 0.3s ease;
            resize: both;
            overflow: hidden;
            min-width: 320px;
            min-height: 400px;
        }
        
        .companion-overlay.visible {
            display: flex;
        }
        
        .companion-overlay.faded {
            opacity: 0.15;
        }
        
        .companion-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background: linear-gradient(90deg, rgba(57, 255, 20, 0.15), rgba(0, 92, 180, 0.15));
            border-bottom: 2px solid rgba(57, 255, 20, 0.3);
            cursor: move;
            user-select: none;
            border-radius: 18px 18px 0 0;
        }
        
        .companion-title {
            font-size: 18px;
            font-weight: bold;
            color: #39ff14;
            text-shadow: 0 0 10px rgba(57, 255, 20, 0.5);
        }
        
        .companion-controls {
            display: flex;
            gap: 8px;
        }
        
        .companion-btn {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 6px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s ease;
        }
        
        .companion-btn:hover {
            background: rgba(57, 255, 20, 0.2);
            border-color: #39ff14;
            transform: scale(1.05);
        }
        
        .companion-settings {
            padding: 10px 16px;
            background: rgba(0, 0, 0, 0.3);
            border-bottom: 1px solid rgba(57, 255, 20, 0.2);
            display: flex;
            gap: 12px;
            align-items: center;
            flex-wrap: wrap;
            font-size: 12px;
        }
        
        .companion-settings label {
            display: flex;
            align-items: center;
            gap: 5px;
            color: #e0e0e0;
        }
        
        .companion-settings select {
            background: rgba(0, 0, 0, 0.5);
            color: white;
            border: 1px solid rgba(57, 255, 20, 0.3);
            border-radius: 5px;
            padding: 4px 8px;
        }
        
        .companion-log {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: rgba(0, 0, 0, 0.2);
        }
        
        .companion-log::-webkit-scrollbar {
            width: 8px;
        }
        
        .companion-log::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
        }
        
        .companion-log::-webkit-scrollbar-thumb {
            background: rgba(57, 255, 20, 0.5);
            border-radius: 10px;
        }
        
        .companion-log::-webkit-scrollbar-thumb:hover {
            background: rgba(57, 255, 20, 0.7);
        }
        
        .companion-message {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 15px;
            word-wrap: break-word;
            font-weight: bold;
            font-size: 14px;
            line-height: 1.4;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .companion-message.user {
            align-self: flex-end;
            background: #39ff14;
            color: #111;
            text-align: right;
            border: 1px solid rgba(57, 255, 20, 0.5);
            box-shadow: 0 4px 15px rgba(57, 255, 20, 0.3);
        }
        
        .companion-message.rick {
            align-self: flex-start;
            background: #005CB4;
            color: white;
            text-align: left;
            border: 1px solid rgba(0, 92, 180, 0.5);
            box-shadow: 0 4px 15px rgba(0, 92, 180, 0.3);
        }
        
        .companion-composer {
            padding: 16px;
            background: rgba(0, 0, 0, 0.3);
            border-top: 2px solid rgba(57, 255, 20, 0.3);
            display: flex;
            gap: 10px;
            border-radius: 0 0 18px 18px;
        }
        
        .companion-input {
            flex: 1;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(57, 255, 20, 0.3);
            border-radius: 10px;
            padding: 10px;
            color: white;
            font-size: 14px;
            resize: vertical;
            min-height: 40px;
            max-height: 120px;
        }
        
        .companion-input:focus {
            outline: none;
            border-color: #39ff14;
            box-shadow: 0 0 15px rgba(57, 255, 20, 0.3);
        }
        
        .companion-send {
            background: linear-gradient(135deg, #39ff14, #005CB4);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            transition: all 0.2s ease;
            box-shadow: 0 4px 15px rgba(57, 255, 20, 0.3);
        }
        
        .companion-send:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(57, 255, 20, 0.5);
        }
        
        .companion-send:active {
            transform: translateY(0);
        }
        
        .companion-empty {
            text-align: center;
            padding: 40px 20px;
            color: #6c757d;
            font-size: 14px;
            font-style: italic;
        }
    </style>
    <script>
        let lastEventId = 0;
        
        // RICK COMPANION STATE
        let companionState = {
            visible: false,
            faded: false,
            messages: [],
            idleTimeout: 10000,
            fadeOnClick: true,
            retractOnClick: false,
            position: { x: null, y: null },
            size: { w: 450, h: 600 }
        };
        
        // Load companion state from localStorage
        function loadCompanionState() {
            const saved = localStorage.getItem('rickCompanionState');
            if (saved) {
                try {
                    Object.assign(companionState, JSON.parse(saved));
                } catch (e) {}
            }
        }
        
        // Save companion state
        function saveCompanionState() {
            localStorage.setItem('rickCompanionState', JSON.stringify(companionState));
        }
        
        // Initialize companion
        function initCompanion() {
            loadCompanionState();
            const overlay = document.getElementById('companionOverlay');
            const sidebar = document.getElementById('companionSidebar');
            const log = document.getElementById('companionLog');
            const hivePane = document.getElementById('hivePane');
            const narratorPane = document.getElementById('narratorPane');
            const input = document.getElementById('companionInput');
            const sendBtn = document.getElementById('companionSend');
            const closeBtn = document.getElementById('companionClose');
            const minBtn = document.getElementById('companionMin');
            const idleSelect = document.getElementById('idleTimeout');
            const fadeCheck = document.getElementById('fadeOnClick');
            const retractCheck = document.getElementById('retractOnClick');
            const tabChat = document.getElementById('tabChat');
            const tabHive = document.getElementById('tabHive');
            const tabNarrator = document.getElementById('tabNarrator');
            const confirmComms = document.getElementById('confirmComms');
            const provGPT = document.getElementById('provGPT');
            const provGrok = document.getElementById('provGrok');
            const provDeepSeek = document.getElementById('provDeepSeek');
            const provGitHub = document.getElementById('provGitHub');
            
            if (!overlay || !sidebar) return;
            
            // Restore state
            if (companionState.position.x && companionState.position.y) {
                overlay.style.left = companionState.position.x + 'px';
                overlay.style.top = companionState.position.y + 'px';
            }
            overlay.style.width = companionState.size.w + 'px';
            overlay.style.height = companionState.size.h + 'px';
            idleSelect.value = companionState.idleTimeout;
            fadeCheck.checked = companionState.fadeOnClick;
            retractCheck.checked = companionState.retractOnClick;
            
            // Restore messages
            companionState.messages.forEach(msg => {
                appendCompanionMessage(msg.role, msg.text, false);
            });
            
            if (companionState.visible) {
                overlay.classList.add('visible');
            }
            
            // Sidebar toggle
            sidebar.addEventListener('click', () => {
                companionState.visible = !companionState.visible;
                overlay.classList.toggle('visible');
                overlay.classList.remove('faded');
                companionState.faded = false;
                saveCompanionState();
                resetIdleTimer();
            });
            
            // Close button
            closeBtn?.addEventListener('click', () => {
                companionState.visible = false;
                overlay.classList.remove('visible');
                saveCompanionState();
            });
            
            // Minimize button
            minBtn?.addEventListener('click', () => {
                companionState.visible = false;
                overlay.classList.remove('visible');
                saveCompanionState();
            });
            
            // Tabs
            function showPane(which) {
                [log, hivePane, narratorPane].forEach(el => el.style.display = 'none');
                if (which === 'chat') log.style.display = '';
                if (which === 'hive') hivePane.style.display = '';
                if (which === 'narrator') narratorPane.style.display = '';
                companionState.activePane = which;
                saveCompanionState();
            }
            tabChat?.addEventListener('click', () => showPane('chat'));
            tabHive?.addEventListener('click', () => showPane('hive'));
            tabNarrator?.addEventListener('click', () => showPane('narrator'));
            showPane(companionState.activePane || 'chat');

            // Confirm comms (mock signal)
            confirmComms?.addEventListener('click', () => {
                const providers = [];
                if (provGPT?.checked) providers.push('GPT');
                if (provGrok?.checked) providers.push('Grok');
                if (provDeepSeek?.checked) providers.push('DeepSeek');
                if (provGitHub?.checked) providers.push('GitHub');
                appendCompanionMessage('rick', `Confirm comms team: ${providers.join(', ')}`);
                // Mock provider echoes shown in hive pane
                const msg = document.createElement('div');
                msg.className = 'companion-message rick';
                msg.textContent = providers.map(p => `${p}: comms confirmed!`).join('  ·  ');
                hivePane.appendChild(msg);
                hivePane.scrollTop = hivePane.scrollHeight;
                resetIdleTimer();
            });

            // Send message
            function sendMessage() {
                const text = input.value.trim();
                if (!text) return;
                
                appendCompanionMessage('user', text);
                input.value = '';
                resetIdleTimer();
                
                // Mock Rick response (replace with actual API call)
                setTimeout(() => {
                    const rickReply = getRickReply(text);
                    appendCompanionMessage('rick', rickReply);
                    // Also reflect dispatch in hive pane (mocked)
                    const hp = document.createElement('div');
                    hp.className = 'companion-message user';
                    hp.textContent = `Dispatch → ${text}`;
                    hivePane.appendChild(hp);
                    hivePane.scrollTop = hivePane.scrollHeight;
                    resetIdleTimer();
                }, 500);
            }
            
            sendBtn?.addEventListener('click', sendMessage);
            input?.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
            
            // Settings
            idleSelect?.addEventListener('change', () => {
                companionState.idleTimeout = parseInt(idleSelect.value);
                saveCompanionState();
                resetIdleTimer();
            });
            
            fadeCheck?.addEventListener('change', () => {
                companionState.fadeOnClick = fadeCheck.checked;
                saveCompanionState();
            });
            
            retractCheck?.addEventListener('change', () => {
                companionState.retractOnClick = retractCheck.checked;
                saveCompanionState();
            });
            
            // Dragging
            let isDragging = false;
            let dragOffset = { x: 0, y: 0 };
            
            const header = overlay.querySelector('.companion-header');
            header?.addEventListener('mousedown', (e) => {
                if (e.target.tagName === 'BUTTON' || e.target.tagName === 'SELECT') return;
                isDragging = true;
                const rect = overlay.getBoundingClientRect();
                dragOffset.x = e.clientX - rect.left;
                dragOffset.y = e.clientY - rect.top;
                overlay.style.cursor = 'move';
            });
            
            document.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                const x = e.clientX - dragOffset.x;
                const y = e.clientY - dragOffset.y;
                overlay.style.left = Math.max(0, x) + 'px';
                overlay.style.top = Math.max(0, y) + 'px';
                companionState.position.x = x;
                companionState.position.y = y;
            });
            
            document.addEventListener('mouseup', () => {
                if (isDragging) {
                    isDragging = false;
                    overlay.style.cursor = '';
                    saveCompanionState();
                }
            });
            
            // Outside click handling
            document.addEventListener('click', (e) => {
                if (!overlay.classList.contains('visible')) return;
                if (overlay.contains(e.target) || sidebar.contains(e.target)) {
                    // Clicked inside - unfade and reset timer
                    overlay.classList.remove('faded');
                    companionState.faded = false;
                    resetIdleTimer();
                } else {
                    // Clicked outside
                    if (companionState.retractOnClick) {
                        companionState.visible = false;
                        overlay.classList.remove('visible');
                        saveCompanionState();
                    } else if (companionState.fadeOnClick) {
                        overlay.classList.add('faded');
                        companionState.faded = true;
                        saveCompanionState();
                    }
                }
            });
            
            // Idle timer
            let idleTimer = null;
            function resetIdleTimer() {
                clearTimeout(idleTimer);
                overlay.classList.remove('faded');
                companionState.faded = false;
                
                if (companionState.idleTimeout > 0 && overlay.classList.contains('visible')) {
                    idleTimer = setTimeout(() => {
                        overlay.classList.add('faded');
                        companionState.faded = true;
                        saveCompanionState();
                    }, companionState.idleTimeout);
                }
            }
            
            // Start idle timer
            resetIdleTimer();
        }
        
        // Append message to companion log
        function appendCompanionMessage(role, text, save = true) {
            const log = document.getElementById('companionLog');
            if (!log) return;
            
            const empty = document.getElementById('companionEmpty');
            if (empty) empty.style.display = 'none';
            
            const msg = document.createElement('div');
            msg.className = `companion-message ${role}`;
            msg.textContent = text;
            log.appendChild(msg);
            log.scrollTop = log.scrollHeight;
            
            if (save) {
                companionState.messages.push({ role, text });
                saveCompanionState();
            }
        }
        
        // Mock Rick AI response (replace with actual API)
        function getRickReply(userText) {
            const replies = [
                "Copy that. We hustle clean, we hustle smart.",
                "I like your ambition. Tight stops, looser ego.",
                "Neon green means go, blue means think—today we do both.",
                "You type fast; I trade faster. Buckle up.",
                "Risk first, glory second. That's the code.",
                "Chart's looking spicy. Let's see if she follows through.",
                "Your capital, my rules. We protect both.",
                "Market's talking. Question is, you listening?",
                "Clean entry, cleaner exit. That's the RBOTzilla way.",
                "Patience pays dividends. Panic pays the market."
            ];
            const hash = userText.split('').reduce((a, c) => ((a << 5) - a) + c.charCodeAt(0), 0);
            return replies[Math.abs(hash) % replies.length];
        }
        
        // Load narration events
        async function loadNarration() {
            try {
                const response = await fetch('/api/narration');
                const events = await response.json();
                
                const feed = document.getElementById('narration-feed');
                if (!feed) return;
                
                // Add sequential IDs if not present
                events.forEach((event, idx) => {
                    if (!event.id) {
                        event.id = idx + 1;
                    }
                });
                
                // Check if we have new events
                if (events.length > 0) {
                    const newestId = Math.max(...events.map(e => e.id || 0));
                    
                    if (newestId !== lastEventId) {
                        const wasAtBottom = feed.scrollHeight - feed.scrollTop <= feed.clientHeight + 50;
                        
                        // Add new events
                        events.forEach(event => {
                            if ((event.id || 0) > lastEventId) {
                                const line = document.createElement('div');
                                line.className = 'narration-line new';
                                line.innerHTML = formatNarrationLine(event);
                                feed.appendChild(line);
                            }
                        });
                        
                        lastEventId = newestId;
                        
                        // Auto-scroll if user was at bottom
                        if (wasAtBottom) {
                            feed.scrollTop = feed.scrollHeight;
                        }
                        
                        // Update empty state
                        const empty = document.getElementById('narration-empty');
                        if (empty) empty.style.display = 'none';
                    }
                }
            } catch (error) {
                console.error('Failed to load narration:', error);
            }
        }
        
        // Connect to Arena SSE and listen for broker events
        function initArenaEventStream() {
            try {
                const es = new EventSource('/arena/events');
                
                es.onopen = () => {
                    console.log('[Arena SSE] Connected');
                };
                
                es.onerror = (e) => {
                    console.error('[Arena SSE] Connection error:', e);
                };
                
                es.onmessage = (e) => {
                    try {
                        const event = JSON.parse(e.data);
                        handleArenaEvent(event);
                    } catch (err) {
                        console.error('[Arena SSE] Parse error:', err, 'data=', e.data);
                    }
                };
                
                return es;
            } catch (err) {
                console.error('[Arena SSE] Failed to connect:', err);
                return null;
            }
        }
        
        // Handle broker/order events from Arena
        function handleArenaEvent(event) {
            const feed = document.getElementById('narration-feed');
            if (!feed) return;
            
            const source = event.source || 'unknown';
            const type = event.type || 'unknown';
            const payload = event.payload || {};
            
            // Only handle broker-related events
            if (!['oanda', 'coinbase'].includes(source)) {
                return;
            }
            
            // Format and display the event
            const line = document.createElement('div');
            line.className = 'narration-line new';
            
            const timestamp = new Date().toLocaleTimeString();
            let html = `<span class="narration-timestamp">${timestamp}</span>`;
            
            // Format event based on type
            if (type === 'oco_placed') {
                const instrument = payload.instrument || payload.product_id || '?';
                const side = payload.side || '?';
                const units = payload.units || payload.size || '?';
                const sl = payload.sl || payload.stop_loss_price || '?';
                const tp = payload.tp || payload.take_profit_price || '?';
                const mode = payload.mode || 'unknown';
                const status = payload.status || 'PENDING';
                
                html += `<span class="narration-event">📊 OCO Placed</span>`;
                html += `<span class="narration-symbol">${instrument}</span>`;
                html += ` <span class="narration-text">${side} ${units} units | SL: ${sl}, TP: ${tp} | Mode: <strong>${mode}</strong> | Status: <strong>${status}</strong></span>`;
            } else if (type === 'order_filled') {
                const instrument = payload.instrument || payload.product_id || '?';
                const units = payload.units || payload.size || '?';
                const fill_price = payload.fill_price || payload.price || '?';
                
                html += `<span class="narration-event">✓ Order Filled</span>`;
                html += `<span class="narration-symbol">${instrument}</span>`;
                html += ` <span class="narration-text">${units} units @ ${fill_price}</span>`;
            } else if (type === 'order_cancelled') {
                const order_id = payload.order_id || '?';
                const instrument = payload.instrument || payload.product_id || '?';
                
                html += `<span class="narration-event">✕ Order Cancelled</span>`;
                html += `<span class="narration-symbol">${instrument}</span>`;
                html += ` <span class="narration-text">Order ID: ${order_id}</span>`;
            } else {
                // Generic event - plain English fallback (NO JSON)
                const instrument = payload.instrument || payload.product_id || payload.symbol || '';
                const description = payload.description || payload.message || `${type} event`;
                html += `<span class="narration-event">[${source.toUpperCase()}]</span>`;
                if (instrument) html += `<span class="narration-symbol"> ${instrument}</span>`;
                html += ` <span class="narration-text"> ${description}</span>`;
            }
            
            line.innerHTML = html;
            feed.appendChild(line);
            
            // Auto-scroll to bottom
            feed.scrollTop = feed.scrollHeight;
            
            // Update empty state
            const empty = document.getElementById('narration-empty');
            if (empty) empty.style.display = 'none';
        }
        
        function formatNarrationLine(event) {
            // Format timestamp in EST timezone
            const estOptions = { timeZone: 'America/New_York', hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' };
            const estTime = new Date().toLocaleTimeString('en-US', estOptions);
            let html = `<span class="narration-timestamp">${estTime}</span>`;
            
            // Check if Rick has conversational commentary
            if (event.rick_says) {
                // RICK'S CONVERSATIONAL NARRATION (Priority display)
                html += `<span class="narration-text">💬 <strong>Rick:</strong> ${event.rick_says}</span>`;
            } else {
                // Fallback to technical details if no Rick commentary
                html += `<span class="narration-event">[${event.event_type}]</span>`;
                
                if (event.symbol) {
                    html += `<span class="narration-symbol">${event.symbol}</span> `;
                }
                
                if (event.venue) {
                    html += `<span class="narration-venue">@${event.venue}</span> `;
                }
                
                // Add details based on event type
                if (event.details) {
                    if (event.event_type === 'OCO_PLACED') {
                        html += `<span class="narration-text">Entry: ${event.details.entry_price.toFixed(5)} | Units: ${event.details.units} | Latency: ${event.details.latency_ms.toFixed(1)}ms</span>`;
                    } else if (event.event_type === 'NOTIONAL_ADJUSTMENT') {
                        html += `<span class="narration-text">${event.details.original_units} → ${event.details.adjusted_units} units</span>`;
                    } else if (event.event_type === 'GHOST_SESSION_END') {
                        html += `<span class="narration-text">Trades: ${event.details.total_trades} | Win Rate: ${event.details.win_rate.toFixed(1)}% | P&L: $${event.details.net_pnl.toFixed(2)}</span>`;
                    } else if (event.event_type === 'TRADE_CLOSED') {
                        html += `<span class="narration-text">Exit: ${event.details.exit_price ? event.details.exit_price.toFixed(5) : 'N/A'} | P&L: $${event.details.net_pnl ? event.details.net_pnl.toFixed(2) : '0.00'}</span>`;
                    }
                }
            }
            
            return html;
        }
        
        // Refresh OANDA performance stats every 1 minute (real-time update)
        function refreshPerformanceStats() {
            try {
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {
                        // Update performance card with real OANDA data
                        document.querySelectorAll('[data-stat="total-trades"]').forEach(el => el.textContent = data.total_trades || '-');
                        document.querySelectorAll('[data-stat="win-rate"]').forEach(el => el.textContent = (data.win_rate || 0).toFixed(1) + '%');
                        document.querySelectorAll('[data-stat="net-pnl"]').forEach(el => {
                            el.textContent = '$' + (data.net_pnl || 0).toFixed(2);
                            el.className = data.net_pnl > 0 ? 'stat-value positive' : 'stat-value negative';
                        });
                        console.log('[Dashboard] Performance stats updated from OANDA');
                    })
                    .catch(err => console.warn('[Dashboard] Performance stats update failed:', err));
            } catch (e) {
                console.warn('[Dashboard] refreshPerformanceStats error:', e);
            }
        }
        
        // Rick Live Narration auto-refresh (1min & 5min options, separate from page refresh)
        let narrationRefreshInterval = 60000; // Default 1 minute
        let narrationRefreshTimer = null;
        
        // Update clock to Eastern Standard Time
        function updateClock() {
            const now = new Date();
            const estTime = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }));
            const hours = String(estTime.getHours()).padStart(2, '0');
            const minutes = String(estTime.getMinutes()).padStart(2, '0');
            const seconds = String(estTime.getSeconds()).padStart(2, '0');
            const timeStr = `${hours}:${minutes}:${seconds} EST`;
            
            const clockEl = document.getElementById('page-clock');
            if (clockEl) {
                clockEl.textContent = timeStr;
            }
        }
        updateClock();
        setInterval(updateClock, 1000);
        
        // Handle Rick Live Narration refresh rate change (1min, 5min)
        document.addEventListener('DOMContentLoaded', function() {
            const narrationRefreshSelect = document.getElementById('narration-refresh-rate');
            if (narrationRefreshSelect) {
                narrationRefreshSelect.addEventListener('change', function() {
                    const rate = parseInt(this.value) * 1000;
                    narrationRefreshInterval = rate;
                    
                    // Clear existing timer
                    if (narrationRefreshTimer) {
                        clearTimeout(narrationRefreshTimer);
                    }
                    
                    // Set new timer for narration only
                    if (rate > 0) {
                        narrationRefreshTimer = setTimeout(function() {
                            loadNarration();
                            // Schedule next refresh
                            if (narrationRefreshInterval > 0) {
                                narrationRefreshTimer = setTimeout(arguments.callee, narrationRefreshInterval);
                            }
                        }, rate);
                        console.log(`Narration refresh set to ${rate/1000}s`);
                    }
                });
            }
            
            // Refresh performance stats every 1 minute (separate from narration)
            setInterval(refreshPerformanceStats, 60000);
            
            // Initial narration load with auto-play
            loadNarration();
            startArenaSSE();
            initCompanion();
        });
        
        // Live Arena SSE → handle broker & order events with rich formatting
        function startArenaSSE() {
            try {
                const es = new EventSource('/arena/events');
                es.onopen = () => {
                    console.log('[Dashboard] Arena SSE connected (broker events enabled)');
                };
                es.onerror = (e) => {
                    console.warn('[Dashboard] Arena SSE error', e);
                };
                es.onmessage = (e) => {
                    try {
                        const event = JSON.parse(e.data);
                        handleArenaEvent(event);
                    } catch (err) {
                        // Keep UI human-friendly: drop non-JSON messages instead of dumping raw text
                        console.warn('[Dashboard] Dropped non-JSON SSE message to avoid tech jargon on UI');
                    }
                };
            } catch (e) {
                console.warn('[Dashboard] Failed to start Arena SSE', e);
            }
        }

        // Poll for new narration every 3 seconds (fallback)
        setInterval(loadNarration, 3000);
        
        // Load initial narration and initialize companion
        window.addEventListener('DOMContentLoaded', function() {
            startArenaSSE();
            loadNarration();
            initCompanion();
        });
    </script>
</head>
<body>
    <!-- RICK COMPANION SIDEBAR TAB -->
    <div class="companion-sidebar" id="companionSidebar" title="Toggle RICK Companion">
        <div class="companion-sidebar-icon">RICK AI</div>
    </div>
    
    <!-- RICK COMPANION OVERLAY -->
    <div class="companion-overlay" id="companionOverlay">
        <div class="companion-header">
            <div class="companion-title">🤖 RICK Companion</div>
            <div class="companion-controls">
                <button class="companion-btn" id="companionMin" title="Minimize">—</button>
                <button class="companion-btn" id="companionClose" title="Close">✕</button>
            </div>
        </div>
        
        <div class="companion-settings">
            <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
                <label>
                    Idle fade:
                    <select id="idleTimeout">
                        <option value="10000">10s</option>
                        <option value="30000">30s</option>
                        <option value="60000">60s</option>
                        <option value="120000">2m</option>
                        <option value="300000">5m</option>
                        <option value="0">Never</option>
                    </select>
                </label>
                <label>
                    <input type="checkbox" id="fadeOnClick" checked>
                    Fade on outside click
                </label>
                <label>
                    <input type="checkbox" id="retractOnClick">
                    Retract on outside click
                </label>
                <div style="flex-basis:100%; height:0;"></div>
                <div style="display:flex; gap:8px; align-items:center;">
                    <strong>Hive Providers:</strong>
                    <label><input type="checkbox" id="provGPT" checked> GPT</label>
                    <label><input type="checkbox" id="provGrok" checked> Grok</label>
                    <label><input type="checkbox" id="provDeepSeek" checked> DeepSeek</label>
                    <label><input type="checkbox" id="provGitHub" checked> GitHub</label>
                    <button class="companion-btn" id="confirmComms">Confirm Comms</button>
                </div>
                <div style="display:flex; gap:8px; margin-top:6px;">
                    <button class="companion-btn" id="tabChat">Chat</button>
                    <button class="companion-btn" id="tabHive">Hive</button>
                    <button class="companion-btn" id="tabNarrator">Narrator</button>
                </div>
            </div>
        </div>
        
        <div class="companion-log" id="companionLog" aria-label="Chat Log">
            <div class="companion-empty" id="companionEmpty">
                💬 Start chatting with Rick...
            </div>
        </div>

        <!-- Hive pane (read-only visualization of provider prompts) -->
        <div class="companion-log" id="hivePane" aria-label="Hive Pane" style="display:none;">
            <div class="companion-empty">🐝 Hive is quiet. Ask Rick something to dispatch to providers.</div>
        </div>

        <!-- Narrator pane (plain English running commentary) -->
        <div class="companion-log" id="narratorPane" aria-label="Narrator Pane" style="display:none;">
            <div class="companion-empty">📻 Rick will narrate system activity here.</div>
        </div>
        
        <div class="companion-composer">
            <textarea class="companion-input" id="companionInput" placeholder="Type to Rick..." rows="2"></textarea>
            <button class="companion-send" id="companionSend">Send</button>
        </div>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>🤖 RICK Trading Dashboard</h1>
            <div class="mode-badge mode-{{ mode_class }}">
                {{ mode_info.mode }} MODE
            </div>
            <p style="margin-top: 10px; opacity: 0.8;">{{ mode_info.description }}</p>
        </div>
        
        <div class="grid">
            <!-- Performance Card -->
            <div class="card">
                <h2>📊 Performance (Live OANDA)</h2>
                <div class="stat">
                    <span class="stat-label">Total Trades</span>
                    <span class="stat-value" data-stat="total-trades">{{ pnl_summary.total_trades }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Win Rate</span>
                    <span class="stat-value" data-stat="win-rate">{{ "%.1f"|format(pnl_summary.win_rate) }}%</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Wins / Losses</span>
                    <span class="stat-value" data-stat="wins-losses">{{ pnl_summary.wins }} / {{ pnl_summary.losses }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Net P&L</span>
                    <span class="stat-value {{ 'positive' if pnl_summary.net_pnl > 0 else 'negative' }}" data-stat="net-pnl">
                        ${{ "%.2f"|format(pnl_summary.net_pnl) }}
                    </span>
                </div>
                <div class="stat">
                    <span class="stat-label">Total Fees</span>
                    <span class="stat-value" data-stat="total-fees">${{ "%.2f"|format(pnl_summary.total_fees) }}</span>
                </div>
            </div>
            
            <!-- Environment Card -->
            <div class="card">
                <h2>🔧 Environment</h2>
                <div class="stat">
                    <span class="stat-label">OANDA</span>
                    <span class="stat-value">{{ mode_info.oanda_environment }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Coinbase</span>
                    <span class="stat-value">{{ mode_info.coinbase_environment }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Live Trading</span>
                    <span class="stat-value {{ 'negative' if mode_info.is_live else 'positive' }}">
                        {{ 'ACTIVE' if mode_info.is_live else 'OFF' }}
                    </span>
                </div>
                <div class="stat">
                    <span class="stat-label">Tmux Session</span>
                    <span class="stat-value">{{ tmux_status }}</span>
                </div>
            </div>
            
            <!-- Controls Card -->
            <div class="card">
                <h2>⚙️ Controls</h2>
                <div class="controls">
                    <form method="post" action="/mode/ghost" style="display: inline;">
                        <button type="submit" class="btn-primary">GHOST Mode</button>
                    </form>
                    <form method="post" action="/mode/canary" style="display: inline;">
                        <button type="submit" class="btn-success">CANARY Mode</button>
                    </form>
                    <form method="post" action="/mode/off" style="display: inline;">
                        <button type="submit" class="btn-secondary">OFF</button>
                    </form>
                </div>
                <div class="controls" style="margin-top: 15px;">
                    <form method="post" action="/start" style="display: inline;">
                        <button type="submit" class="btn-success">Start Tmux</button>
                    </form>
                    <form method="post" action="/stop" style="display: inline;">
                        <button type="submit" class="btn-danger">Stop Tmux</button>
                    </form>
                </div>
            </div>
        </div>
        
        <!-- RICK LIVE NARRATION STREAM -->
        <div class="narration-stream">
            <div class="narration-header">
                <div class="narration-title">🎙️ RICK LIVE NARRATION</div>
                <div class="narration-indicator">
                    <div class="live-dot"></div>
                    <span>STREAMING</span>
                </div>
                <!-- Refresh Control for Narration Only (1min / 5min) -->
                <div style="display: flex; gap: 10px; align-items: center;">
                    <label style="font-size: 0.9em;">Auto-refresh:</label>
                    <select id="narration-refresh-rate" style="padding: 5px; border-radius: 5px; background: rgba(0,0,0,0.3); color: white; border: 1px solid rgba(255,215,0,0.3);">
                        <option value="60" selected>1 min</option>
                        <option value="300">5 min</option>
                        <option value="0">Manual</option>
                    </select>
                </div>
                <div style="font-size: 0.85em; color: #a0a0a0;">⏰ Eastern Time</div>
            </div>
            <div class="narration-feed" id="narration-feed">
                <div class="narration-empty" id="narration-empty">
                    ⏳ Waiting for trade activity...
                </div>
            </div>
        </div>
        
        <!-- Recent Activity -->
        <div class="card">
            <h2>📝 Recent Activity (Rick's Plain English Commentary)</h2>
            <div class="events-list">
                {% for event in recent_events %}
                <div class="event">
                    {% if event.rick_says %}
                        <!-- Rick's conversational commentary (plain English) -->
                        <span class="event-type">💬 Rick says:</span>
                        <span style="color: #ffd700; font-weight: bold;"> {{ event.rick_says }}</span>
                    {% else %}
                        <!-- Fallback to technical details -->
                        <span class="event-type">{{ event.event_type }}</span>
                        {% if event.symbol %}
                        <span style="opacity: 0.8;"> | {{ event.symbol }}</span>
                        {% endif %}
                        <span style="opacity: 0.6;"> @ {{ event.venue }}</span>
                    {% endif %}
                    <div class="event-time">{{ event.timestamp }}</div>
                    {% if event.details and not event.rick_says %}
                    <div style="margin-top: 5px; opacity: 0.7; font-size: 0.85em;">
                        {% if event.event_type == 'OCO_PLACED' %}
                            Entry: {{ "%.5f"|format(event.details.entry_price) }} | 
                            Units: {{ event.details.units }} | 
                            Latency: {{ "%.1f"|format(event.details.latency_ms) }}ms
                        {% elif event.event_type == 'NOTIONAL_ADJUSTMENT' %}
                            {{ event.details.original_units }} → {{ event.details.adjusted_units }} units
                        {% elif event.event_type == 'GHOST_SESSION_END' %}
                            Trades: {{ event.details.total_trades }} | 
                            Win Rate: {{ "%.1f"|format(event.details.win_rate) }}% | 
                            P&L: ${{ "%.2f"|format(event.details.net_pnl) }}
                        {% endif %}
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="refresh-notice">
            🔄 Dashboard auto-refreshes every 10 seconds
        </div>
    </div>
</body>
</html>
'''

def tmux_running():
    try:
        subprocess.check_output(['tmux', 'has-session', '-t', SESSION], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False

@app.route('/')
def index():
    # Get current mode info
    mode_info = get_mode_info()
    
    # Get P&L summary
    pnl_summary = get_session_summary()
    
    # Get recent events
    recent_events = get_latest_narration(n=10)
    recent_events.reverse()  # Show newest first
    
    # Determine mode CSS class
    mode_class = mode_info['mode'].lower()
    
    # Tmux status
    tmux_status = 'running' if tmux_running() else 'stopped'
    
    return render_template_string(
        INDEX_HTML,
        mode_info=mode_info,
        mode_class=mode_class,
        pnl_summary=pnl_summary,
        recent_events=recent_events,
        tmux_status=tmux_status
    )

@app.route('/mode/<new_mode>', methods=['POST'])
def change_mode(new_mode):
    """Change system mode"""
    new_mode = new_mode.upper()
    if new_mode in ['OFF', 'GHOST', 'CANARY']:
        switch_mode(new_mode)
    return redirect(url_for('index'))

@app.route('/api/status')
def api_status():
    """API endpoint for status (for external monitoring)"""
    mode_info = get_mode_info()
    pnl_summary = get_session_summary()
    
    return jsonify({
        "mode": mode_info['mode'],
        "is_live": mode_info['is_live'],
        "oanda_env": mode_info['oanda_environment'],
        "coinbase_env": mode_info['coinbase_environment'],
        "total_trades": pnl_summary['total_trades'],
        "win_rate": pnl_summary['win_rate'],
        "net_pnl": pnl_summary['net_pnl'],
        "tmux_running": tmux_running()
    })

@app.route('/api/live_monitor', methods=['GET'])
def live_monitor():
    """API endpoint to fetch live trading monitor data"""
    try:
        monitor_data = get_live_monitor()
        return jsonify({"status": "success", "data": monitor_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/narration', methods=['GET'])
def narration():
    """API endpoint to fetch latest narration with Rick's plain English commentary"""
    try:
        from util.narration_logger import get_latest_narration
        
        # Get raw events
        events = get_latest_narration(n=50)
        
        # Add Rick's human commentary to each event
        for event in events:
            event_type = event.get('event_type', 'UNKNOWN')
            details = event.get('details', {})
            symbol = event.get('symbol')
            venue = event.get('venue')
            
            # Generate plain English based on event type
            if event_type == 'IB_CONNECTION':
                status = details.get('status', 'unknown')
                account = details.get('account', 'N/A')
                env = details.get('environment', 'unknown')
                event['rick_says'] = f"Connected to Interactive Brokers {env} account {account}. System is live and monitoring markets."
            
            elif event_type == 'OANDA_CONNECTION':
                status = details.get('status', 'unknown')
                env = details.get('environment', 'unknown')
                event['rick_says'] = f"OANDA {env} environment connected. Ready to scan FX pairs for opportunities."
            
            elif event_type == 'SCAN_START':
                pair_count = details.get('pair_count', 0)
                event['rick_says'] = f"Starting market scan across {pair_count} currency pairs. Looking for high-probability setups."
            
            elif event_type == 'PAIR_CHECK':
                price = details.get('price', 0)
                spread = details.get('spread_pips', 0)
                event['rick_says'] = f"Checking {symbol}: Price {price:.5f}, spread {spread:.1f} pips. Analyzing chart structure..."
            
            elif event_type == 'PATTERN_DETECTION':
                patterns = details.get('patterns', [])
                confidence = details.get('confidence', 0) * 100
                pattern_str = ', '.join(patterns) if patterns else 'multiple patterns'
                event['rick_says'] = f"Detected {pattern_str} on {symbol} with {confidence:.0f}% confidence. Pattern looks solid."
            
            elif event_type == 'ML_ANALYSIS':
                direction = details.get('direction', 'N/A')
                confidence = details.get('confidence', 0) * 100
                regime = details.get('regime', 'unknown')
                event['rick_says'] = f"ML analysis: {direction} signal at {confidence:.0f}% confidence. Market regime: {regime}."
            
            elif event_type == 'FILTER_CHECK':
                filter_name = details.get('filter_name', 'unknown')
                passed = details.get('passed', False)
                result = "passed" if passed else "failed"
                event['rick_says'] = f"Filter check '{filter_name}': {result}. {'Good to go.' if passed else 'Signal rejected.'}"
            
            elif event_type == 'RR_CALCULATION':
                rr = details.get('rr_ratio', 0)
                passes = details.get('passes_charter', False)
                event['rick_says'] = f"Risk/reward calculated: {rr:.1f}:1. {'Meets charter requirements.' if passes else 'Below charter minimum.'}"
            
            elif event_type == 'OCO_PLACED':
                entry = details.get('entry_price', 0)
                units = details.get('units', 0)
                latency = details.get('latency_ms', 0)
                event['rick_says'] = f"OCO order placed on {symbol} @ {entry:.5f}, {units} units. Execution latency: {latency:.1f}ms."
            
            elif event_type == 'TRADE_OPENED':
                entry = details.get('entry_price', 0)
                direction = details.get('direction', 'N/A')
                event['rick_says'] = f"Trade opened: {direction} {symbol} @ {entry:.5f}. Position is live, stops are set."
            
            elif event_type == 'TRADE_CLOSED':
                exit_price = details.get('exit_price', 0)
                net_pnl = details.get('net_pnl', 0)
                outcome = "Win" if net_pnl > 0 else "Loss"
                event['rick_says'] = f"Trade closed: {symbol} @ {exit_price:.5f}. {outcome} ${net_pnl:.2f}. On to the next one."
            
            elif event_type == 'GHOST_SESSION_START':
                mode = details.get('mode', 'ghost')
                event['rick_says'] = f"Ghost session started. Running in simulation mode - no real capital at risk."
            
            elif event_type == 'GHOST_SESSION_END':
                total_trades = details.get('total_trades', 0)
                win_rate = details.get('win_rate', 0)
                net_pnl = details.get('net_pnl', 0)
                event['rick_says'] = f"Ghost session complete: {total_trades} trades, {win_rate:.1f}% win rate, ${net_pnl:.2f} simulated P&L."
            
            elif event_type == 'CANARY_PROMOTION':
                event['rick_says'] = "System promoted to CANARY mode. Now trading with paper accounts - real market data, no real money."
            
            elif event_type == 'LIVE_ACTIVATION':
                event['rick_says'] = "⚠️ LIVE MODE ACTIVATED. Real capital is now at risk. All systems armed and operational."
            
            elif event_type == 'DAILY_LOSS_BREAKER':
                loss_pct = details.get('loss_pct', 0)
                event['rick_says'] = f"Daily loss limit hit ({loss_pct:.1f}%). Shutting down trading for today. We live to fight another day."
            
            elif event_type == 'NOTIONAL_ADJUSTMENT':
                original = details.get('original_units', 0)
                adjusted = details.get('adjusted_units', 0)
                event['rick_says'] = f"Position size adjusted: {original} → {adjusted} units to meet $15K minimum notional."
            
            elif event_type == 'HEDGE_ACTIVATED':
                hedge_type = details.get('hedge_type', 'unknown')
                event['rick_says'] = f"Defensive hedge activated: {hedge_type}. Protecting capital in volatile conditions."
            
            elif event_type == 'ERROR':
                error_msg = details.get('message', 'Unknown error')
                event['rick_says'] = f"System error encountered: {error_msg}. Investigating and recovering."
            
            else:
                # Fallback for unknown event types
                event['rick_says'] = f"{event_type}: {symbol or 'system'} - {venue or 'internal'}"
        
        return jsonify(events)
    
    except Exception as e:
        logger.error(f"Narration API error: {e}")
        return jsonify([])

@app.route('/api/swarmbots')
def api_swarmbots():
    """API endpoint for active SwarmBot positions"""
    try:
        bots = get_active_bots_snapshot()
        return jsonify(bots)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/regime')
def api_regime():
    """API endpoint for current market regime"""
    try:
        monitor = get_live_monitor()
        regime_data = {
            "regime": monitor.current_regime,
            "confidence": monitor.regime_confidence,
            "last_change": monitor.last_regime_change.isoformat() if monitor.last_regime_change else None,
            "active_positions": len(monitor.active_swarm_bots),
            "total_pnl_today": monitor.total_realized_pnl,
            "trades_today": monitor.total_trades_today,
            "win_rate": (monitor.wins_today / monitor.total_trades_today * 100) if monitor.total_trades_today > 0 else 0
        }
        return jsonify(regime_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/start', methods=['POST'])
def start():
    # start headless session
    start_script = os.path.join(ROOT, 'scripts', 'headless_start.sh')
    if os.path.exists(start_script):
        subprocess.Popen([start_script])
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop():
    try:
        subprocess.check_call(['tmux', 'kill-session', '-t', SESSION])
    except subprocess.CalledProcessError:
        pass
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Optional health endpoint for quick checks
    @app.route('/health')
    def health():
        try:
            mode_info = get_mode_info()
            return jsonify({
                'status': 'ok',
                'mode': mode_info.get('mode'),
                'is_live': mode_info.get('is_live')
            })
        except Exception:
            return jsonify({'status': 'ok'})

    # Alias for previous sidecar tester path (redirect to arena_test_page)
    @app.route('/sidecar_test.html')
    def sidecar_test_alias():
        return redirect(url_for('arena_test_page'))

    # Allow overriding the port via env var (DASHBOARD_PORT or PORT)
    port = int(os.environ.get('DASHBOARD_PORT', os.environ.get('PORT', '8080')))
    app.run(host='0.0.0.0', port=port, debug=True)


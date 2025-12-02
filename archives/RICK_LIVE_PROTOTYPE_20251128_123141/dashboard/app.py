from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import subprocess
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from util.mode_manager import get_mode_info, switch_mode
from util.narration_logger import get_latest_narration, get_session_summary

app = Flask(__name__)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SESSION = 'rbot_headless'

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
                
                // Check if we have new events
                if (events.length > 0 && events[0].id !== lastEventId) {
                    const wasAtBottom = feed.scrollHeight - feed.scrollTop <= feed.clientHeight + 50;
                    
                    // Add new events
                    events.forEach(event => {
                        if (event.id > lastEventId) {
                            const line = document.createElement('div');
                            line.className = 'narration-line new';
                            line.innerHTML = formatNarrationLine(event);
                            feed.appendChild(line);
                        }
                    });
                    
                    lastEventId = events[0].id;
                    
                    // Auto-scroll if user was at bottom
                    if (wasAtBottom) {
                        feed.scrollTop = feed.scrollHeight;
                    }
                    
                    // Update empty state
                    const empty = document.getElementById('narration-empty');
                    if (empty) empty.style.display = 'none';
                }
            } catch (error) {
                console.error('Failed to load narration:', error);
            }
        }
        
        function formatNarrationLine(event) {
            let html = `<span class="narration-timestamp">${event.timestamp}</span>`;
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
            
            return html;
        }
        
        // Auto-refresh page every 10 seconds
        setTimeout(function(){ location.reload(); }, 10000);
        
        // Poll for new narration every 3 seconds
        setInterval(loadNarration, 3000);
        
        // Load initial narration and initialize companion
        window.addEventListener('DOMContentLoaded', function() {
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
                <h2>📊 Performance</h2>
                <div class="stat">
                    <span class="stat-label">Total Trades</span>
                    <span class="stat-value">{{ pnl_summary.total_trades }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Win Rate</span>
                    <span class="stat-value">{{ "%.1f"|format(pnl_summary.win_rate) }}%</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Wins / Losses</span>
                    <span class="stat-value">{{ pnl_summary.wins }} / {{ pnl_summary.losses }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Net P&L</span>
                    <span class="stat-value {{ 'positive' if pnl_summary.net_pnl > 0 else 'negative' }}">
                        ${{ "%.2f"|format(pnl_summary.net_pnl) }}
                    </span>
                </div>
                <div class="stat">
                    <span class="stat-label">Total Fees</span>
                    <span class="stat-value">${{ "%.2f"|format(pnl_summary.total_fees) }}</span>
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
            </div>
            <div class="narration-feed" id="narration-feed">
                <div class="narration-empty" id="narration-empty">
                    ⏳ Waiting for trade activity...
                </div>
            </div>
        </div>
        
        <!-- Recent Activity -->
        <div class="card">
            <h2>📝 Recent Activity (Last 10 Events)</h2>
            <div class="events-list">
                {% for event in recent_events %}
                <div class="event">
                    <span class="event-type">{{ event.event_type }}</span>
                    {% if event.symbol %}
                    <span style="opacity: 0.8;"> | {{ event.symbol }}</span>
                    {% endif %}
                    <span style="opacity: 0.6;"> @ {{ event.venue }}</span>
                    <div class="event-time">{{ event.timestamp }}</div>
                    {% if event.details %}
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

@app.route('/api/narration')
def api_narration():
    """API endpoint for live narration feed"""
    try:
        events = get_latest_narration(n=100)  # Get last 100 events
        
        # Add IDs to events for tracking
        for i, event in enumerate(events):
            event['id'] = i
        
        return jsonify(events)
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
    app.run(host='127.0.0.1', port=8080, debug=True)


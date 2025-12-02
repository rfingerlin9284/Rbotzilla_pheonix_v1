// Phase 36: Draggable Widget Manager
import interact from 'interactjs';

class WidgetManager {
    constructor() {
        this.widgets = new Map();
        this.zIndexCounter = 100;
        this.websocket = null;
        this.initializeWebSocket();
        this.initializeWidgets();
    }

    // Initialize WebSocket connection for live data
    initializeWebSocket() {
        try {
            this.websocket = new WebSocket('ws://localhost:8887');
            
            this.websocket.onopen = () => {
                console.log('🔌 Widget Manager connected to WebSocket');
                this.updateConnectionStatus(true);
            };

            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            this.websocket.onclose = () => {
                console.log('🔌 Widget Manager WebSocket disconnected');
                this.updateConnectionStatus(false);
                // Attempt reconnection after 3 seconds
                setTimeout(() => this.initializeWebSocket(), 3000);
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.updateConnectionStatus(false);
        }
    }

    // Handle incoming WebSocket messages
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'tmux_output':
                this.updateTerminalOutput(data.data);
                break;
            case 'system_message':
                this.updateTerminalOutput(`\n🔔 ${data.message}\n`);
                break;
            case 'rick_command':
                this.addRickMessage(data.prompt, 'user');
                this.addRickMessage(data.response, 'ai');
                break;
            case 'strategy_data':
                this.updateStrategyWidget(data.data);
                break;
            case 'ml_prediction':
                this.updateMLWidget(data.data);
                break;
            case 'pnl_update':
                this.updatePnLWidget(data.data);
                break;
            case 'latency_data':
                this.updateLatencyWidget(data.data);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    // Initialize all widgets
    initializeWidgets() {
        // Create default widget layout
        this.createWidget('terminal', 'TMUX Terminal', 50, 100, 600, 300);
        this.createWidget('rick', 'Rick AI', 680, 100, 400, 300);
        this.createWidget('strategy', 'Strategy Monitor', 50, 420, 300, 250);
        this.createWidget('ml', 'ML Predictions', 370, 420, 300, 250);
        this.createWidget('pnl', 'P&L Tracker', 690, 420, 300, 250);
        this.createWidget('latency', 'Latency Monitor', 1010, 420, 280, 250);

        // Make all widgets draggable and resizable
        this.widgets.forEach((widget, id) => {
            this.makeDraggable(id);
            this.makeResizable(id);
        });

        // Initialize widget content
        this.initializeWidgetContent();
    }

    // Create a new widget
    createWidget(id, title, x, y, width, height) {
        const widget = document.createElement('div');
        widget.id = id;
        widget.className = `widget ${id}-widget`;
        widget.style.left = `${x}px`;
        widget.style.top = `${y}px`;
        widget.style.width = `${width}px`;
        widget.style.height = `${height}px`;
        widget.style.zIndex = this.zIndexCounter++;

        widget.innerHTML = `
            <div class="widget-header">
                <div class="widget-title">${title}</div>
                <div class="widget-controls">
                    <div class="widget-btn" onclick="widgetManager.minimizeWidget('${id}')" title="Minimize">−</div>
                    <div class="widget-btn" onclick="widgetManager.maximizeWidget('${id}')" title="Maximize">□</div>
                    <div class="widget-btn" onclick="widgetManager.closeWidget('${id}')" title="Close">×</div>
                </div>
            </div>
            <div class="widget-content" id="${id}-content">
                ${this.getWidgetContent(id)}
            </div>
        `;

        document.querySelector('.widget-workspace').appendChild(widget);
        this.widgets.set(id, {
            element: widget,
            title: title,
            minimized: false,
            originalSize: { width, height }
        });

        return widget;
    }

    // Get initial content for different widget types
    getWidgetContent(id) {
        switch (id) {
            case 'terminal':
                return `
                    <div class="terminal-output" id="terminal-output"></div>
                    <div class="command-input">
                        <input type="text" id="terminal-input" placeholder="Enter command..." 
                               onkeypress="if(event.key==='Enter') widgetManager.sendTerminalCommand()">
                        <button onclick="widgetManager.sendTerminalCommand()">Send</button>
                        <button onclick="widgetManager.clearTerminal()">Clear</button>
                    </div>
                `;
            case 'rick':
                return `
                    <div class="rick-chat" id="rick-chat"></div>
                    <div class="rick-input">
                        <input type="text" id="rick-input" placeholder="Ask Rick AI..." 
                               onkeypress="if(event.key==='Enter') widgetManager.sendRickCommand()">
                        <button onclick="widgetManager.sendRickCommand()">Send</button>
                    </div>
                `;
            case 'strategy':
                return `
                    <div class="strategy-metric">
                        <span>Active Strategies:</span>
                        <span class="strategy-value" id="active-strategies">3</span>
                    </div>
                    <div class="strategy-metric">
                        <span>Win Rate:</span>
                        <span class="strategy-value positive" id="win-rate">72.4%</span>
                    </div>
                    <div class="strategy-metric">
                        <span>Total Signals:</span>
                        <span class="strategy-value" id="total-signals">156</span>
                    </div>
                    <div class="strategy-metric">
                        <span>Confidence:</span>
                        <span class="strategy-value positive" id="strategy-confidence">85.2%</span>
                    </div>
                    <div class="strategy-metric">
                        <span>Risk Level:</span>
                        <span class="strategy-value" id="risk-level">Medium</span>
                    </div>
                `;
            case 'ml':
                return `
                    <div class="ml-prediction">
                        <span>EUR/USD</span>
                        <span>BUY</span>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: 75%"></div>
                        </div>
                    </div>
                    <div class="ml-prediction">
                        <span>BTC/USD</span>
                        <span>SELL</span>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: 60%"></div>
                        </div>
                    </div>
                    <div class="ml-prediction">
                        <span>GBP/USD</span>
                        <span>HOLD</span>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: 45%"></div>
                        </div>
                    </div>
                `;
            case 'pnl':
                return `
                    <div class="pnl-summary">
                        <div class="pnl-item">
                            <div>Total P&L</div>
                            <div class="pnl-value pnl-positive" id="total-pnl">+$1,247.83</div>
                        </div>
                        <div class="pnl-item">
                            <div>Today</div>
                            <div class="pnl-value pnl-positive" id="daily-pnl">+$156.42</div>
                        </div>
                    </div>
                    <div class="pnl-item">
                        <div>Open Positions: <span id="open-positions">3</span></div>
                    </div>
                    <div class="pnl-item">
                        <div>Floating P&L: <span class="pnl-positive" id="floating-pnl">+$23.14</span></div>
                    </div>
                `;
            case 'latency':
                return `
                    <div class="latency-grid">
                        <div class="latency-item">
                            <div>OANDA</div>
                            <div class="latency-value latency-good" id="oanda-latency">45ms</div>
                        </div>
                        <div class="latency-item">
                            <div>Coinbase</div>
                            <div class="latency-value latency-good" id="coinbase-latency">38ms</div>
                        </div>
                        <div class="latency-item">
                            <div>WebSocket</div>
                            <div class="latency-value latency-good" id="ws-latency">12ms</div>
                        </div>
                        <div class="latency-item">
                            <div>API Health</div>
                            <div class="latency-value latency-good" id="api-health">✓</div>
                        </div>
                    </div>
                `;
            default:
                return '<div>Loading...</div>';
        }
    }

    // Make widget draggable
    makeDraggable(id) {
        interact(`#${id}`)
            .draggable({
                allowFrom: '.widget-header',
                listeners: {
                    start: (event) => {
                        event.target.classList.add('dragging');
                        event.target.style.zIndex = this.zIndexCounter++;
                    },
                    move: (event) => {
                        const target = event.target;
                        const x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
                        const y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;
                        
                        target.style.transform = `translate(${x}px, ${y}px)`;
                        target.setAttribute('data-x', x);
                        target.setAttribute('data-y', y);
                    },
                    end: (event) => {
                        event.target.classList.remove('dragging');
                    }
                }
            });
    }

    // Make widget resizable
    makeResizable(id) {
        interact(`#${id}`)
            .resizable({
                edges: { left: true, right: true, bottom: true, top: true },
                listeners: {
                    move: (event) => {
                        const target = event.target;
                        let x = parseFloat(target.getAttribute('data-x')) || 0;
                        let y = parseFloat(target.getAttribute('data-y')) || 0;

                        target.style.width = event.rect.width + 'px';
                        target.style.height = event.rect.height + 'px';

                        x += event.deltaRect.left;
                        y += event.deltaRect.top;

                        target.style.transform = `translate(${x}px, ${y}px)`;
                        target.setAttribute('data-x', x);
                        target.setAttribute('data-y', y);
                    }
                },
                modifiers: [
                    interact.modifiers.restrictSize({
                        min: { width: 200, height: 150 }
                    })
                ]
            });
    }

    // Widget control functions
    minimizeWidget(id) {
        const widget = this.widgets.get(id);
        if (!widget) return;

        if (widget.minimized) {
            widget.element.style.height = widget.originalSize.height + 'px';
            widget.element.querySelector('.widget-content').style.display = 'block';
            widget.minimized = false;
        } else {
            widget.element.style.height = '50px';
            widget.element.querySelector('.widget-content').style.display = 'none';
            widget.minimized = true;
        }
    }

    maximizeWidget(id) {
        const widget = this.widgets.get(id);
        if (!widget) return;

        const element = widget.element;
        if (element.classList.contains('maximized')) {
            // Restore
            element.classList.remove('maximized');
            element.style.width = widget.originalSize.width + 'px';
            element.style.height = widget.originalSize.height + 'px';
            element.style.top = '100px';
            element.style.left = '50px';
        } else {
            // Maximize
            element.classList.add('maximized');
            element.style.width = '90vw';
            element.style.height = '80vh';
            element.style.top = '10vh';
            element.style.left = '5vw';
            element.style.zIndex = this.zIndexCounter++;
        }
    }

    closeWidget(id) {
        const widget = this.widgets.get(id);
        if (widget) {
            widget.element.remove();
            this.widgets.delete(id);
        }
    }

    // Terminal functions
    sendTerminalCommand() {
        const input = document.getElementById('terminal-input');
        const command = input.value.trim();
        if (!command || !this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
            return;
        }

        this.updateTerminalOutput(`$ ${command}`);
        this.websocket.send(JSON.stringify({
            type: 'command',
            command: command
        }));
        input.value = '';
    }

    updateTerminalOutput(text) {
        const output = document.getElementById('terminal-output');
        if (output) {
            output.textContent += text + '\n';
            output.scrollTop = output.scrollHeight;
        }
    }

    clearTerminal() {
        const output = document.getElementById('terminal-output');
        if (output) {
            output.textContent = '';
        }
    }

    // Rick AI functions
    sendRickCommand() {
        const input = document.getElementById('rick-input');
        const prompt = input.value.trim();
        if (!prompt) return;

        this.addRickMessage(prompt, 'user');
        input.value = '';

        fetch('/prompt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: prompt,
                context: { timestamp: Date.now(), source: 'widget' }
            })
        }).then(response => response.json()).then(data => {
            if (data.response) {
                this.addRickMessage(data.response, 'ai');
            }
        }).catch(error => {
            this.addRickMessage(`Error: ${error.message}`, 'ai');
        });
    }

    addRickMessage(message, sender) {
        const chat = document.getElementById('rick-chat');
        if (chat) {
            const div = document.createElement('div');
            div.className = `rick-message ${sender}`;
            div.textContent = `${sender === 'user' ? '👤' : '🤖'} ${message}`;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
    }

    // Data update functions
    updateStrategyWidget(data) {
        document.getElementById('active-strategies').textContent = data.activeStrategies || '3';
        document.getElementById('win-rate').textContent = data.winRate || '72.4%';
        document.getElementById('total-signals').textContent = data.totalSignals || '156';
        document.getElementById('strategy-confidence').textContent = data.confidence || '85.2%';
        document.getElementById('risk-level').textContent = data.riskLevel || 'Medium';
    }

    updateMLWidget(data) {
        // Update ML predictions dynamically
        console.log('ML Widget updated:', data);
    }

    updatePnLWidget(data) {
        if (data.totalPnL) {
            const element = document.getElementById('total-pnl');
            element.textContent = `$${data.totalPnL}`;
            element.className = `pnl-value ${data.totalPnL >= 0 ? 'pnl-positive' : 'pnl-negative'}`;
        }
        if (data.dailyPnL) {
            const element = document.getElementById('daily-pnl');
            element.textContent = `$${data.dailyPnL}`;
            element.className = `pnl-value ${data.dailyPnL >= 0 ? 'pnl-positive' : 'pnl-negative'}`;
        }
    }

    updateLatencyWidget(data) {
        if (data.oanda) {
            document.getElementById('oanda-latency').textContent = `${data.oanda}ms`;
        }
        if (data.coinbase) {
            document.getElementById('coinbase-latency').textContent = `${data.coinbase}ms`;
        }
        if (data.websocket) {
            document.getElementById('ws-latency').textContent = `${data.websocket}ms`;
        }
    }

    updateConnectionStatus(connected) {
        const status = document.getElementById('connectionStatus');
        if (status) {
            status.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
            status.textContent = connected ? '🔗 Connected' : '🔌 Disconnected';
        }
    }

    // Initialize widget content after DOM is loaded
    initializeWidgetContent() {
        // Add initial Rick message
        setTimeout(() => {
            this.addRickMessage('Rick AI is ready! Ask me anything about the trading system.', 'ai');
        }, 1000);

        // Start simulated data updates
        this.startSimulatedData();
    }

    // Start simulated data updates for demo
    startSimulatedData() {
        setInterval(() => {
            // Update strategy metrics
            this.updateStrategyWidget({
                winRate: (70 + Math.random() * 10).toFixed(1) + '%',
                totalSignals: Math.floor(150 + Math.random() * 20),
                confidence: (80 + Math.random() * 15).toFixed(1) + '%'
            });

            // Update P&L
            this.updatePnLWidget({
                totalPnL: (1200 + (Math.random() - 0.5) * 100).toFixed(2),
                dailyPnL: (150 + (Math.random() - 0.5) * 50).toFixed(2)
            });

            // Update latency
            this.updateLatencyWidget({
                oanda: Math.floor(40 + Math.random() * 20),
                coinbase: Math.floor(35 + Math.random() * 25),
                websocket: Math.floor(10 + Math.random() * 15)
            });
        }, 5000);
    }
}

// Initialize widget manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing Phase 36 Widget Manager');
    window.widgetManager = new WidgetManager();
});

export default WidgetManager;
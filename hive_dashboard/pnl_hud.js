// RBOTzilla UNI - Animated P&L HUD Overlay
class PnLHUD {
    constructor() {
        this.currentPnL = 0;
        this.dailyPnL = 0;
        this.positions = [];
        this.isVisible = true;
        this.init();
    }
    
    init() {
        this.createHUD();
        this.startAnimation();
        this.loadMockData();
    }
    
    createHUD() {
        const hud = document.createElement('div');
        hud.id = 'pnl-hud';
        hud.style.cssText = `
            position: fixed;
            top: 50px;
            right: 10px;
            width: 280px;
            background: rgba(0,0,0,0.9);
            border: 2px solid #0f0;
            border-radius: 10px;
            padding: 15px;
            z-index: 1000;
            font-family: 'Orbitron', monospace;
            font-size: 12px;
            color: #0f0;
            box-shadow: 0 0 20px rgba(0,255,0,0.3);
            transition: all 0.3s;
        `;
        
        hud.innerHTML = `
            <div class="hud-header" style="text-align: center; margin-bottom: 10px; color: #ffaa00; font-weight: bold;">
                📊 LIVE P&L HUD
                <button onclick="pnlHUD.toggle()" style="float: right; background: none; border: none; color: #0f0; cursor: pointer;">📐</button>
            </div>
            <div class="hud-content">
                <div class="pnl-current">
                    <span>Current P&L:</span>
                    <span id="current-pnl" style="float: right; font-weight: bold;">$0.00</span>
                </div>
                <div class="pnl-daily" style="margin: 5px 0;">
                    <span>Daily P&L:</span>
                    <span id="daily-pnl" style="float: right; font-weight: bold;">$0.00</span>
                </div>
                <div class="pnl-positions" style="margin-top: 10px; border-top: 1px solid #333; padding-top: 10px;">
                    <div style="color: #888; margin-bottom: 5px;">Open Positions:</div>
                    <div id="positions-list"></div>
                </div>
                <div class="pnl-stats" style="margin-top: 10px; border-top: 1px solid #333; padding-top: 10px; font-size: 10px;">
                    <div>Win Rate: <span id="win-rate">0%</span></div>
                    <div>Trades Today: <span id="trades-count">0</span></div>
                    <div>Best Trade: <span id="best-trade">$0</span></div>
                </div>
            </div>
        `;
        
        document.body.appendChild(hud);
    }
    
    updatePnL(currentPnL, dailyPnL) {
        this.currentPnL = currentPnL;
        this.dailyPnL = dailyPnL;
        
        const currentEl = document.getElementById('current-pnl');
        const dailyEl = document.getElementById('daily-pnl');
        
        if (currentEl) {
            currentEl.textContent = `$${currentPnL.toFixed(2)}`;
            currentEl.style.color = currentPnL >= 0 ? '#0f0' : '#f44';
            
            // Animation flash
            currentEl.style.textShadow = currentPnL >= 0 ? '0 0 10px #0f0' : '0 0 10px #f44';
            setTimeout(() => currentEl.style.textShadow = 'none', 500);
        }
        
        if (dailyEl) {
            dailyEl.textContent = `$${dailyPnL.toFixed(2)}`;
            dailyEl.style.color = dailyPnL >= 0 ? '#0f0' : '#f44';
        }
    }
    
    updatePositions(positions) {
        this.positions = positions;
        const listEl = document.getElementById('positions-list');
        if (!listEl) return;
        
        if (positions.length === 0) {
            listEl.innerHTML = '<div style="color: #666;">No open positions</div>';
            return;
        }
        
        listEl.innerHTML = positions.map(pos => `
            <div style="margin: 2px 0; display: flex; justify-content: space-between;">
                <span>${pos.symbol}</span>
                <span style="color: ${pos.pnl >= 0 ? '#0f0' : '#f44'};">
                    ${pos.pnl >= 0 ? '+' : ''}$${pos.pnl.toFixed(0)}
                </span>
            </div>
        `).join('');
    }
    
    updateStats(winRate, tradesCount, bestTrade) {
        const winRateEl = document.getElementById('win-rate');
        const tradesEl = document.getElementById('trades-count');
        const bestTradeEl = document.getElementById('best-trade');
        
        if (winRateEl) winRateEl.textContent = `${winRate}%`;
        if (tradesEl) tradesEl.textContent = tradesCount;
        if (bestTradeEl) bestTradeEl.textContent = `$${bestTrade}`;
    }
    
    toggle() {
        const hud = document.getElementById('pnl-hud');
        if (hud) {
            this.isVisible = !this.isVisible;
            hud.style.display = this.isVisible ? 'block' : 'none';
        }
    }
    
    startAnimation() {
        // Subtle breathing animation for the HUD
        setInterval(() => {
            const hud = document.getElementById('pnl-hud');
            if (hud && this.isVisible) {
                hud.style.boxShadow = `0 0 ${15 + Math.sin(Date.now() / 1000) * 5}px rgba(0,255,0,0.3)`;
            }
        }, 100);
    }
    
    loadMockData() {
        // Simulate live P&L updates
        setInterval(() => {
            const variance = (Math.random() - 0.5) * 100;
            this.updatePnL(
                this.currentPnL + variance,
                this.dailyPnL + variance * 0.1
            );
            
            // Mock positions
            const mockPositions = [
                { symbol: 'EUR/USD', pnl: 450 + variance },
                { symbol: 'BTC/USD', pnl: -120 + variance * 0.5 },
                { symbol: 'GBP/USD', pnl: 230 + variance * 0.3 }
            ].filter(() => Math.random() > 0.3); // Randomly show/hide positions
            
            this.updatePositions(mockPositions);
            this.updateStats(72, 8, 1250);
        }, 2000);
    }
}

// Global P&L HUD instance
const pnlHUD = new PnLHUD();

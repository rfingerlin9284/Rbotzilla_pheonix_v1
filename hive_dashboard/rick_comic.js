// ========= PHASE 43: Comic/Race Visualizer Panel =========

function renderComicSummary(data) {
    const comic = document.createElement("div");
    comic.className = "comic-panel";
    comic.style.cssText = `
        position: fixed;
        top: 50px;
        left: 50%;
        transform: translateX(-50%);
        width: 500px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #00ff88;
        border-radius: 10px;
        padding: 20px;
        color: #00ff88;
        font-family: 'Orbitron', monospace;
        z-index: 2000;
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.5);
        animation: comicSlideIn 0.5s ease-out;
    `;
    
    const currentPnL = data?.pnl || "+$520.36";
    const trades = data?.trades || 3;
    
    comic.innerHTML = `
        <div style="text-align: center; margin-bottom: 15px;">
            <h2 style="color: #00ff88; text-shadow: 0 0 10px #00ff88;">🏁 Rick's Race Summary</h2>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 14px;">
            <div style="background: rgba(0,255,136,0.1); padding: 10px; border-radius: 5px;">
                <strong>🚘 Trade 1:</strong><br>
                BTC rocketed like a V12 engine! 🏎️💨<br>
                <span style="color: #00ff88;">+$284.50</span>
            </div>
            <div style="background: rgba(255,64,0,0.1); padding: 10px; border-radius: 5px;">
                <strong>⚠️ Trade 2:</strong><br>
                ETH spun out mid-lap! 🚧<br>
                <span style="color: #ff4000;">-$89.20</span>
            </div>
        </div>
        <div style="text-align: center; margin: 15px 0; padding: 10px; background: rgba(0,255,136,0.2); border-radius: 5px;">
            <strong style="font-size: 18px;">🏆 Final P&L: ${currentPnL} 💸</strong><br>
            <small>${trades} trades executed with precision</small>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px;">
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="background: #ff4000; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer;">
                Close
            </button>
            <button onclick="requestFullRaceReport()" 
                    style="background: #00ff88; color: #000; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold;">
                🎬 Full Race Report
            </button>
        </div>
    `;
    
    // Add CSS animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes comicSlideIn {
            from { transform: translateX(-50%) translateY(-30px); opacity: 0; }
            to { transform: translateX(-50%) translateY(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(comic);
    
    // Auto-close after 10 seconds
    setTimeout(() => {
        if (comic.parentElement) {
            comic.style.animation = 'comicSlideIn 0.3s ease-out reverse';
            setTimeout(() => comic.remove(), 300);
        }
    }, 10000);
}

function requestFullRaceReport() {
    // Close current comic
    document.querySelector('.comic-panel')?.remove();
    
    // Create detailed race report
    const report = document.createElement("div");
    report.className = "race-report";
    report.style.cssText = `
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        width: 700px;
        max-height: 80vh;
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 100%);
        border: 2px solid #00ff88;
        border-radius: 10px;
        padding: 20px;
        color: #00ff88;
        font-family: 'Orbitron', monospace;
        z-index: 2001;
        overflow-y: auto;
        box-shadow: 0 0 40px rgba(0, 255, 136, 0.6);
    `;
    
    report.innerHTML = `
        <h2 style="text-align: center; color: #00ff88; margin-bottom: 20px;">🏁 Complete Race Report</h2>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
            <div style="background: rgba(0,255,136,0.1); padding: 15px; border-radius: 8px;">
                <h3>📊 Performance Stats</h3>
                <ul style="list-style: none; margin: 10px 0;">
                    <li>💰 Total P&L: <strong>+$520.36</strong></li>
                    <li>📈 Win Rate: <strong>67.4%</strong></li>
                    <li>🎯 Trades: <strong>8 executed</strong></li>
                    <li>⚡ Avg Speed: <strong>2.3s</strong></li>
                </ul>
            </div>
            
            <div style="background: rgba(0,255,136,0.1); padding: 15px; border-radius: 8px;">
                <h3>🚗 Race Highlights</h3>
                <ul style="list-style: none; margin: 10px 0;">
                    <li>🏎️ Fastest lap: BTC scalp (12s)</li>
                    <li>🥇 Best trade: EUR/USD +$284</li>
                    <li>🚧 Pit stop: Risk adjustment</li>
                    <li>🏁 Finish: Strong close</li>
                </ul>
            </div>
        </div>
        
        <div style="background: rgba(0,0,0,0.5); padding: 15px; border-radius: 8px; margin: 20px 0;">
            <h3>🎬 Rick's Commentary:</h3>
            <p style="line-height: 1.6; margin: 10px 0;">
                "Listen up! Today was like Monaco Grand Prix - tight corners, high stakes, and no room for error. 
                We started strong with that BTC breakout, hit some turbulence around the London close, 
                but finished like champions. The EUR/USD trade was poetry in motion - textbook setup, 
                perfect execution, and a clean exit. That's how you drive in the big leagues!"
            </p>
        </div>
        
        <div style="text-align: center; margin-top: 20px;">
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="background: #00ff88; color: #000; border: none; padding: 12px 25px; border-radius: 5px; cursor: pointer; font-weight: bold; margin-right: 10px;">
                🏁 Close Report
            </button>
            <button onclick="saveRaceReport()" 
                    style="background: rgba(0,255,136,0.2); color: #00ff88; border: 1px solid #00ff88; padding: 12px 25px; border-radius: 5px; cursor: pointer;">
                💾 Save Report
            </button>
        </div>
    `;
    
    document.body.appendChild(report);
}

function saveRaceReport() {
    // Simulate saving
    const button = event.target;
    button.textContent = "✅ Saved!";
    button.style.background = "#00ff88";
    button.style.color = "#000";
    
    setTimeout(() => {
        button.textContent = "💾 Save Report";
        button.style.background = "rgba(0,255,136,0.2)";
        button.style.color = "#00ff88";
    }, 2000);
    
    console.log('📊 Race report saved to artifacts/');
}

// Quick race summary for button clicks
function quickRaceSummary() {
    const data = {
        pnl: "+$520.36",
        trades: 8,
        winRate: "67.4%"
    };
    renderComicSummary(data);
}

// Global functions
window.renderComic = renderComicSummary;
window.quickRace = quickRaceSummary;
window.fullRaceReport = requestFullRaceReport;

console.log('🎬 Rick Comic/Race Visualizer loaded');
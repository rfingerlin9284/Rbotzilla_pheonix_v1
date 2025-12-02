// RBOTzilla UNI - Race Comic Strip Renderer
class ComicRenderer {
    constructor() {
        this.frames = [];
        this.currentFrame = 0;
        this.isPlaying = false;
    }
    
    renderComicStrip(data) {
        const frameBox = document.getElementById("comic-frame");
        if (!frameBox) {
            console.error("Comic frame container not found");
            return;
        }
        
        frameBox.innerHTML = ""; // Reset
        this.frames = data;
        
        data.forEach((frame, i) => {
            const panel = document.createElement("div");
            panel.className = "comic-panel";
            panel.style.cssText = `
                background: rgba(0,255,0,0.1);
                border: 2px solid #0f0;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
                position: relative;
                cursor: pointer;
                transition: all 0.3s;
            `;
            
            panel.innerHTML = `
                <div class="comic-header" style="color: #ffaa00; font-weight: bold; margin-bottom: 10px;">
                    📍 Frame ${i + 1} - ${frame.timestamp || 'Live'}
                </div>
                <div class="comic-content" style="font-size: 14px; line-height: 1.4;">
                    ${frame.text}
                </div>
                ${frame.pnl ? `<div class="comic-pnl" style="color: ${frame.pnl > 0 ? '#0f0' : '#f44'}; font-weight: bold; margin-top: 10px;">
                    P&L: ${frame.pnl > 0 ? '+' : ''}$${frame.pnl}
                </div>` : ''}
            `;
            
            panel.onclick = () => this.highlightFrame(i);
            frameBox.appendChild(panel);
        });
    }
    
    highlightFrame(index) {
        document.querySelectorAll('.comic-panel').forEach((panel, i) => {
            panel.style.borderColor = i === index ? '#ffaa00' : '#0f0';
            panel.style.transform = i === index ? 'scale(1.02)' : 'scale(1)';
        });
        this.currentFrame = index;
    }
    
    playAnimation() {
        if (this.isPlaying) return;
        this.isPlaying = true;
        
        let frame = 0;
        const interval = setInterval(() => {
            if (frame >= this.frames.length) {
                clearInterval(interval);
                this.isPlaying = false;
                return;
            }
            this.highlightFrame(frame);
            frame++;
        }, 1500);
    }
}

// Global comic renderer instance
const comicRenderer = new ComicRenderer();

function runRaceMode() {
    console.log('🎬 Generating race comic summary...');
    
    // Simulate fetching real trading data
    const mockData = [
        { 
            text: "BTC slammed into resistance at $67,200. Rick analyzed the rejection candle with laser focus.", 
            timestamp: "09:15 UTC", 
            pnl: 0 
        },
        { 
            text: "Short entry triggered. Rick's voice steady: 'Position size: 2.5% risk. Stop at $67,350.'", 
            timestamp: "09:16 UTC", 
            pnl: 0 
        },
        { 
            text: "Price wicked up $50, testing resolve. Rick held firm. Hands steady. Mind clear.", 
            timestamp: "09:18 UTC", 
            pnl: -125 
        },
        { 
            text: "Breakdown confirmed. Price crashed through $66,800. Rick smiled. Plan executed perfectly.", 
            timestamp: "09:22 UTC", 
            pnl: 850 
        },
        { 
            text: "Take profit hit at $66,200. P&L flashed green: +$2,390. Rick nodded. 'War won.'", 
            timestamp: "09:28 UTC", 
            pnl: 2390 
        },
        { 
            text: "ETH lined up next. Rick whispered: 'The hunt continues...' Eyes on $2,650 resistance.", 
            timestamp: "09:30 UTC", 
            pnl: 2390 
        }
    ];
    
    comicRenderer.renderComicStrip(mockData);
    
    // Auto-play animation after 1 second
    setTimeout(() => comicRenderer.playAnimation(), 1000);
}

function runDailySummary() {
    console.log('📊 Generating daily summary comic...');
    
    const dailyData = [
        { text: "Market opened volatile. Rick stayed patient, waiting for setups.", timestamp: "Session Start", pnl: 0 },
        { text: "First trade: EUR/USD long at 1.0845. Clean breakout above resistance.", timestamp: "10:30", pnl: 450 },
        { text: "BTC short from $67K. Perfect timing on the rejection.", timestamp: "14:15", pnl: 1250 },
        { text: "Session close: 3 wins, 1 scratch. Risk managed perfectly.", timestamp: "Session End", pnl: 3200 }
    ];
    
    comicRenderer.renderComicStrip(dailyData);
}

// RBOTzilla UNI - Rick Voice + Live Narrator
class RickVoiceNarrator {
    constructor() {
        this.isEnabled = 'speechSynthesis' in window;
        this.voice = null;
        this.isNarrating = false;
        this.queue = [];
        this.init();
    }
    
    init() {
        if (!this.isEnabled) {
            console.warn('🎤 Text-to-speech not supported');
            return;
        }
        
        // Wait for voices to load
        if (speechSynthesis.getVoices().length === 0) {
            speechSynthesis.addEventListener('voiceschanged', () => this.selectVoice());
        } else {
            this.selectVoice();
        }
        
        this.createControls();
    }
    
    selectVoice() {
        const voices = speechSynthesis.getVoices();
        // Prefer deep, authoritative voices for Rick
        this.voice = voices.find(v => 
            v.name.includes('Alex') || 
            v.name.includes('Daniel') || 
            v.name.includes('Male') ||
            v.lang.startsWith('en')
        ) || voices[0];
        
        console.log(`🎤 Rick voice selected: ${this.voice?.name}`);
    }
    
    speak(text, priority = false) {
        if (!this.isEnabled || !this.voice) return;
        
        if (priority) {
            speechSynthesis.cancel(); // Clear queue for urgent messages
            this.queue = [];
        }
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.voice = this.voice;
        utterance.rate = 0.9;
        utterance.pitch = 0.8;
        utterance.volume = 0.7;
        
        utterance.onstart = () => {
            this.isNarrating = true;
            this.updateStatus('🎤 Rick Speaking...');
        };
        
        utterance.onend = () => {
            this.isNarrating = false;
            this.updateStatus('🎤 Rick Ready');
            this.processQueue();
        };
        
        if (this.isNarrating && !priority) {
            this.queue.push(text);
        } else {
            speechSynthesis.speak(utterance);
        }
    }
    
    processQueue() {
        if (this.queue.length > 0 && !this.isNarrating) {
            const next = this.queue.shift();
            this.speak(next);
        }
    }
    
    narrateTrade(action, symbol, pnl) {
        const phrases = {
            entry: [
                `Entering ${symbol}. Position locked and loaded.`,
                `${symbol} setup confirmed. Engaging trade.`,
                `Lock and load. ${symbol} position active.`
            ],
            exit: [
                `${symbol} closed. P and L: ${pnl > 0 ? 'profit' : 'loss'} ${Math.abs(pnl)} dollars.`,
                `Trade complete. ${symbol} delivered ${pnl > 0 ? 'gains' : 'losses'} of ${Math.abs(pnl)}.`,
                `${symbol} exit confirmed. ${pnl > 0 ? 'Victory' : 'Regroup'} achieved.`
            ],
            alert: [
                `Alert. Market condition detected.`,
                `Attention. Price action requires analysis.`,
                `Warning. Setup developing.`
            ]
        };
        
        const options = phrases[action] || phrases.alert;
        const phrase = options[Math.floor(Math.random() * options.length)];
        this.speak(phrase, action === 'alert');
    }
    
    narrateSession(session) {
        const sessionPhrases = {
            'LONDON': 'London session active. High volatility expected.',
            'NEWYORK': 'New York session in progress. Major volume incoming.',
            'ASIAN': 'Asian session detected. Patient analysis mode.',
            'WEEKEND': 'Weekend crypto alpha mode. Enhanced opportunity window.'
        };
        
        if (sessionPhrases[session]) {
            this.speak(sessionPhrases[session]);
        }
    }
    
    createControls() {
        const controls = document.createElement('div');
        controls.id = 'rick-voice-controls';
        controls.style.cssText = `
            position: fixed;
            bottom: 120px;
            right: 10px;
            background: rgba(0,0,0,0.9);
            border: 1px solid #0f0;
            border-radius: 5px;
            padding: 10px;
            z-index: 1000;
            font-family: monospace;
            font-size: 12px;
            color: #0f0;
        `;
        
        controls.innerHTML = `
            <div style="margin-bottom: 5px; font-weight: bold; color: #ffaa00;">🎤 Rick Voice</div>
            <div id="voice-status" style="margin-bottom: 10px;">🎤 Rick Ready</div>
            <button onclick="rickVoice.testVoice()" style="padding: 5px; margin: 2px; background: #0f0; color: #000; border: none; border-radius: 3px;">
                Test Voice
            </button>
            <button onclick="rickVoice.toggle()" style="padding: 5px; margin: 2px; background: #666; color: #fff; border: none; border-radius: 3px;">
                ${this.isEnabled ? 'Disable' : 'Enable'}
            </button>
        `;
        
        document.body.appendChild(controls);
    }
    
    updateStatus(status) {
        const statusEl = document.getElementById('voice-status');
        if (statusEl) statusEl.textContent = status;
    }
    
    testVoice() {
        this.speak("Rick reporting. All systems operational. Ready for battle.", true);
    }
    
    toggle() {
        this.isEnabled = !this.isEnabled;
        if (!this.isEnabled) {
            speechSynthesis.cancel();
            this.queue = [];
        }
        this.updateControls();
    }
    
    updateControls() {
        const controls = document.getElementById('rick-voice-controls');
        if (controls) {
            controls.querySelector('button:last-child').textContent = this.isEnabled ? 'Disable' : 'Enable';
        }
    }
}

// Global Rick voice narrator
const rickVoice = new RickVoiceNarrator();

// Auto-narrate events from socket feeds
if (window.ioClient) {
    ioClient.on('trading-signal', (signal) => {
        rickVoice.narrateTrade('alert', signal.symbol);
    });
    
    ioClient.on('session-update', (data) => {
        rickVoice.narrateSession(data.session);
    });
}

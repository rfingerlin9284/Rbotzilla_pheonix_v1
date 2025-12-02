// ========= PHASE 42: Rick Text-to-Speech Personality =========

function speakRick(text) {
    const msg = new SpeechSynthesisUtterance(text);
    msg.pitch = 0.8;
    msg.rate = 1.05;
    
    // Try to find a good voice for Rick
    const voices = speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => 
        v.name.includes("Google") || 
        v.name.includes("Male") ||
        v.name.includes("UK English Male") ||
        v.lang.startsWith('en')
    );
    
    if (preferredVoice) {
        msg.voice = preferredVoice;
    }
    
    speechSynthesis.speak(msg);
}

// Rick's personality-driven voice responses
window.rickReply = (msg) => {
    // Add to terminal/chat
    const terminalOutput = document.getElementById("terminalOutput");
    const rickMessageList = document.getElementById("rickMessageList");
    
    if (terminalOutput) {
        terminalOutput.textContent += "\n🤖 Rick: " + msg + "\n";
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    }
    
    if (rickMessageList) {
        const div = document.createElement('div');
        div.className = 'ai-response';
        div.innerHTML = `🤖 <strong>Rick:</strong> ${msg}`;
        rickMessageList.appendChild(div);
        rickMessageList.scrollTop = rickMessageList.scrollHeight;
    }
    
    // Speak it with Rick's personality
    speakRick(msg);
}

// Enhanced Rick personality responses
window.getRickResponse = (input) => {
    const responses = {
        'daily': "Alright, let me break down today's action for you. We crushed it on EUR/USD, got schooled by crypto volatility, but still came out swinging with +$247 profit. Not bad for a Tuesday!",
        'pnl': "Looking at the books... We're sitting pretty at +$1,247 total. Today alone brought in +$156. Got 3 positions still cooking. The house always wins when Rick's running the show!",
        'session': "Time check! London session is heating up, NY overlap coming in hot. Perfect time to scalp some pips. Weekend crypto mode is OFF, so we're playing it smart on the forex side.",
        'risk': "Risk management 101: Never bet the farm, always have an exit plan, and trust the process. Current exposure is looking healthy at 2.3% portfolio risk. We're good to go!",
        'futures': "Crypto futures are where the real alpha lives! BTC futures showing bullish divergence, ETH futures got that weekend pump energy. Just remember - futures can wreck you faster than a Formula 1 crash!",
        'help': "I got your back! I can check P&L, analyze sessions, run backtests, give you market updates, or just chat about trading strategies. What's on your mind, partner?"
    };
    
    const lowerInput = input.toLowerCase();
    
    for (const [key, response] of Object.entries(responses)) {
        if (lowerInput.includes(key)) {
            return response;
        }
    }
    
    return "I hear you! Let me process that and get back to you with some solid intel...";
}

// Initialize voices when they're ready
if (speechSynthesis.onvoiceschanged !== undefined) {
    speechSynthesis.onvoiceschanged = () => {
        console.log('🔊 Rick voice system initialized');
    };
}

console.log('🎤 Rick Text-to-Speech Personality loaded');
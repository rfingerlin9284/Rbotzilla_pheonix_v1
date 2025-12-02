// RBOTzilla UNI Theme Engine
const THEMES = {
    stealth: {
        name: "🖤 Stealth Ops",
        css: `
            body { background: #000; color: #0f0; font-family: 'Orbitron', monospace; }
            .widget { background: rgba(0,255,0,0.1); border: 1px solid #0f0; }
            .glow { color: #0f0; text-shadow: 0 0 10px #0f0; }
            input, button { background: #111; color: #0f0; border: 1px solid #0f0; }
        `
    },
    tron: {
        name: "💙 Tron Grid", 
        css: `
            body { background: #001122; color: #33ccff; font-family: 'Share Tech Mono', monospace; }
            .widget { background: rgba(51,204,255,0.1); border: 1px solid #33ccff; }
            .glow { color: #33ccff; text-shadow: 0 0 10px #33ccff; }
            input, button { background: #002244; color: #33ccff; border: 1px solid #33ccff; }
        `
    },
    core: {
        name: "💚 Core Green",
        css: `
            body { background: #000; color: #00ffcc; font-family: 'Courier New', monospace; }
            .widget { background: rgba(0,255,204,0.1); border: 1px solid #00ffcc; }
            .glow { color: #00ffcc; text-shadow: 0 0 10px #00ffcc; }
            input, button { background: #003322; color: #00ffcc; border: 1px solid #00ffcc; }
        `
    },
    crimson: {
        name: "❤️ Crimson War",
        css: `
            body { background: #220000; color: #ff4444; font-family: 'Orbitron', monospace; }
            .widget { background: rgba(255,68,68,0.1); border: 1px solid #ff4444; }
            .glow { color: #ff4444; text-shadow: 0 0 10px #ff4444; }
            input, button { background: #440000; color: #ff4444; border: 1px solid #ff4444; }
        `
    }
};

function switchTheme(themeKey) {
    const theme = THEMES[themeKey];
    if (!theme) return;
    
    let styleElement = document.getElementById('dynamic-theme-style');
    if (!styleElement) {
        styleElement = document.createElement('style');
        styleElement.id = 'dynamic-theme-style';
        document.head.appendChild(styleElement);
    }
    
    styleElement.innerHTML = theme.css;
    localStorage.setItem('rbotzilla-theme', themeKey);
    
    console.log(`🎨 Theme switched to: ${theme.name}`);
    
    // Broadcast theme change to socket if available
    if (window.ioClient) {
        window.ioClient.emit('theme-change', { theme: themeKey, timestamp: Date.now() });
    }
}

function loadSavedTheme() {
    const savedTheme = localStorage.getItem('rbotzilla-theme') || 'stealth';
    switchTheme(savedTheme);
}

// Auto-load theme on page load
document.addEventListener('DOMContentLoaded', loadSavedTheme);

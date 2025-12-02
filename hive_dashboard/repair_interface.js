// RBOTzilla UNI - Self-Repair Web Interface
class RepairInterface {
    constructor() {
        this.isVisible = false;
        this.createInterface();
    }
    
    createInterface() {
        const interface = document.createElement('div');
        interface.id = 'repair-interface';
        interface.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 400px;
            background: rgba(0,0,0,0.95);
            border: 2px solid #ffaa00;
            border-radius: 10px;
            padding: 20px;
            z-index: 2000;
            font-family: 'Orbitron', monospace;
            color: #ffaa00;
            display: none;
            box-shadow: 0 0 30px rgba(255,170,0,0.5);
        `;
        
        interface.innerHTML = `
            <div class="repair-header" style="text-align: center; margin-bottom: 20px; font-weight: bold; font-size: 16px;">
                🔧 SYSTEM REPAIR CONSOLE
            </div>
            
            <div class="repair-status" style="background: #111; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-size: 12px; height: 100px; overflow-y: auto;" id="repair-log">
                System ready for diagnostics...
            </div>
            
            <div class="repair-actions" style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                <button onclick="repairInterface.runDiagnostics()" style="padding: 10px; background: #0f0; color: #000; border: none; border-radius: 5px; font-weight: bold;">
                    🔍 Diagnostics
                </button>
                <button onclick="repairInterface.autoRepair()" style="padding: 10px; background: #ffaa00; color: #000; border: none; border-radius: 5px; font-weight: bold;">
                    🔧 Auto Repair
                </button>
                <button onclick="repairInterface.createBackup()" style="padding: 10px; background: #33ccff; color: #000; border: none; border-radius: 5px; font-weight: bold;">
                    📦 Backup
                </button>
                <button onclick="repairInterface.emergencyReset()" style="padding: 10px; background: #ff4444; color: #fff; border: none; border-radius: 5px; font-weight: bold;">
                    🚨 Emergency
                </button>
            </div>
            
            <div class="repair-close" style="text-align: center;">
                <button onclick="repairInterface.toggle()" style="padding: 8px 16px; background: #666; color: #fff; border: none; border-radius: 5px;">
                    Close
                </button>
            </div>
        `;
        
        document.body.appendChild(interface);
    }
    
    toggle() {
        this.isVisible = !this.isVisible;
        const interface = document.getElementById('repair-interface');
        interface.style.display = this.isVisible ? 'block' : 'none';
    }
    
    log(message) {
        const logEl = document.getElementById('repair-log');
        const timestamp = new Date().toLocaleTimeString();
        logEl.innerHTML += `[${timestamp}] ${message}\n`;
        logEl.scrollTop = logEl.scrollHeight;
    }
    
    runDiagnostics() {
        this.log('🔍 Running system diagnostics...');
        
        // Check socket connection
        if (window.ioClient && window.ioClient.connected) {
            this.log('✅ Socket.IO connection active');
        } else {
            this.log('⚠️ Socket.IO connection lost');
        }
        
        // Check critical components
        const components = [
            { name: 'Theme Engine', check: () => window.switchTheme },
            { name: 'P&L HUD', check: () => window.pnlHUD },
            { name: 'Rick Voice', check: () => window.rickVoice },
            { name: 'Override Controls', check: () => window.overrideControls },
            { name: 'Comic Renderer', check: () => window.comicRenderer }
        ];
        
        components.forEach(comp => {
            if (comp.check()) {
                this.log(`✅ ${comp.name} operational`);
            } else {
                this.log(`❌ ${comp.name} missing or failed`);
            }
        });
        
        this.log('🔍 Diagnostics complete');
    }
    
    autoRepair() {
        this.log('🔧 Initiating auto-repair sequence...');
        
        // Attempt to reconnect socket
        if (!window.ioClient || !window.ioClient.connected) {
            this.log('🔄 Attempting socket reconnection...');
            try {
                window.ioClient = io('http://localhost:5056');
                this.log('✅ Socket reconnection initiated');
            } catch (error) {
                this.log('❌ Socket reconnection failed');
            }
        }
        
        // Reload missing components
        const scripts = [
            'theme_engine.js',
            'pnl_hud.js', 
            'rick_voice_narrator.js',
            'override_controls.js',
            'race_comic.js'
        ];
        
        scripts.forEach(script => {
            if (!document.querySelector(`script[src="${script}"]`)) {
                this.log(`🔄 Reloading ${script}...`);
                const scriptEl = document.createElement('script');
                scriptEl.src = script;
                document.head.appendChild(scriptEl);
            }
        });
        
        this.log('🔧 Auto-repair completed');
    }
    
    createBackup() {
        this.log('📦 Creating system backup...');
        
        // Save current state to localStorage
        const backupData = {
            timestamp: Date.now(),
            theme: localStorage.getItem('rbotzilla-theme'),
            overrideState: localStorage.getItem('rbotzilla-override-state'),
            version: 'phases-46-52'
        };
        
        localStorage.setItem(`rbotzilla-backup-${Date.now()}`, JSON.stringify(backupData));
        this.log('✅ Backup created in localStorage');
    }
    
    emergencyReset() {
        const confirm = prompt('Emergency reset will clear all data. Type "EMERGENCY" to confirm:');
        if (confirm === 'EMERGENCY') {
            this.log('🚨 EMERGENCY RESET INITIATED');
            
            // Clear all localStorage
            localStorage.clear();
            
            // Reload page
            setTimeout(() => {
                this.log('🔄 Reloading system...');
                window.location.reload();
            }, 2000);
        } else {
            this.log('❌ Emergency reset cancelled');
        }
    }
}

// Global repair interface
const repairInterface = new RepairInterface();

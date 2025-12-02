// RBOTzilla UNI - Manual Override + LLM Fuse Lock System
class OverrideControls {
    constructor() {
        this.isLocked = false;
        this.overrideActive = false;
        this.llmEnabled = true;
        this.emergencyMode = false;
        this.init();
    }
    
    init() {
        this.createOverridePanel();
        this.loadSavedState();
    }
    
    createOverridePanel() {
        const panel = document.createElement('div');
        panel.id = 'override-panel';
        panel.style.cssText = `
            position: fixed;
            top: 120px;
            left: 10px;
            width: 250px;
            background: rgba(0,0,0,0.95);
            border: 2px solid #ff4444;
            border-radius: 8px;
            padding: 15px;
            z-index: 1000;
            font-family: 'Orbitron', monospace;
            font-size: 11px;
            color: #ff4444;
            box-shadow: 0 0 15px rgba(255,68,68,0.3);
        `;
        
        panel.innerHTML = `
            <div class="override-header" style="text-align: center; margin-bottom: 15px; color: #ffaa00; font-weight: bold;">
                ⚡ MANUAL OVERRIDE CONTROLS
            </div>
            
            <div class="control-section" style="margin-bottom: 15px;">
                <div style="margin-bottom: 8px; font-weight: bold;">🔒 LLM Fuse Lock</div>
                <button id="llm-toggle" onclick="overrideControls.toggleLLM()" 
                        style="width: 100%; padding: 8px; margin-bottom: 5px; background: #0f0; color: #000; border: none; border-radius: 3px; font-weight: bold;">
                    LLM ENABLED
                </button>
                <div style="font-size: 9px; color: #888;">Disable to prevent AI decisions</div>
            </div>
            
            <div class="control-section" style="margin-bottom: 15px;">
                <div style="margin-bottom: 8px; font-weight: bold;">🎮 Manual Override</div>
                <button id="override-toggle" onclick="overrideControls.toggleOverride()" 
                        style="width: 100%; padding: 8px; margin-bottom: 5px; background: #666; color: #fff; border: none; border-radius: 3px; font-weight: bold;">
                    AUTO MODE
                </button>
                <div style="font-size: 9px; color: #888;">Switch to manual control</div>
            </div>
            
            <div class="control-section" style="margin-bottom: 15px;">
                <div style="margin-bottom: 8px; font-weight: bold;">🚨 Emergency</div>
                <button id="emergency-toggle" onclick="overrideControls.emergencyStop()" 
                        style="width: 100%; padding: 8px; margin-bottom: 5px; background: #ff4444; color: #fff; border: none; border-radius: 3px; font-weight: bold;">
                    EMERGENCY STOP
                </button>
                <div style="font-size: 9px; color: #888;">Immediate halt all operations</div>
            </div>
            
            <div class="control-section">
                <div style="margin-bottom: 8px; font-weight: bold;">🔐 Master Lock</div>
                <input type="password" id="lock-password" placeholder="Enter lock code" 
                       style="width: calc(100% - 60px); padding: 5px; background: #111; color: #0f0; border: 1px solid #333; border-radius: 3px;">
                <button onclick="overrideControls.masterLock()" 
                        style="width: 50px; padding: 5px; background: #ffaa00; color: #000; border: none; border-radius: 3px; font-weight: bold;">
                    LOCK
                </button>
                <div style="font-size: 9px; color: #888; margin-top: 3px;">Lock all controls</div>
            </div>
            
            <div class="status-section" style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #333;">
                <div id="override-status" style="font-size: 10px; color: #888;">
                    Status: All systems operational
                </div>
            </div>
        `;
        
        document.body.appendChild(panel);
    }
    
    toggleLLM() {
        if (this.isLocked) {
            this.showLockedMessage();
            return;
        }
        
        this.llmEnabled = !this.llmEnabled;
        const button = document.getElementById('llm-toggle');
        
        if (this.llmEnabled) {
            button.textContent = 'LLM ENABLED';
            button.style.background = '#0f0';
            button.style.color = '#000';
            this.updateStatus('LLM system active - AI decisions enabled');
        } else {
            button.textContent = 'LLM DISABLED';
            button.style.background = '#ff4444';
            button.style.color = '#fff';
            this.updateStatus('LLM system disabled - Manual mode only');
        }
        
        this.saveState();
        this.broadcastState();
    }
    
    toggleOverride() {
        if (this.isLocked) {
            this.showLockedMessage();
            return;
        }
        
        this.overrideActive = !this.overrideActive;
        const button = document.getElementById('override-toggle');
        
        if (this.overrideActive) {
            button.textContent = 'MANUAL MODE';
            button.style.background = '#ffaa00';
            button.style.color = '#000';
            this.updateStatus('Manual override active - Operator control');
        } else {
            button.textContent = 'AUTO MODE';
            button.style.background = '#666';
            button.style.color = '#fff';
            this.updateStatus('Automatic mode - System control');
        }
        
        this.saveState();
        this.broadcastState();
    }
    
    emergencyStop() {
        if (this.isLocked) {
            this.showLockedMessage();
            return;
        }
        
        this.emergencyMode = !this.emergencyMode;
        const button = document.getElementById('emergency-toggle');
        
        if (this.emergencyMode) {
            button.textContent = 'EMERGENCY ACTIVE';
            button.style.background = '#ff0000';
            this.updateStatus('🚨 EMERGENCY STOP ACTIVE - All trading halted');
            
            // Trigger emergency stop across all systems
            if (window.ioClient) {
                window.ioClient.emit('emergency-stop', { timestamp: Date.now(), user: 'manual' });
            }
            
            if (window.rickVoice) {
                window.rickVoice.speak('Emergency stop activated. All operations halted.', true);
            }
        } else {
            button.textContent = 'EMERGENCY STOP';
            button.style.background = '#ff4444';
            this.updateStatus('Emergency cleared - Systems ready');
            
            if (window.rickVoice) {
                window.rickVoice.speak('Emergency cleared. Systems restored.', true);
            }
        }
        
        this.saveState();
        this.broadcastState();
    }
    
    masterLock() {
        const password = document.getElementById('lock-password').value;
        const correctPassword = 'RBOT2025'; // Simple lock code
        
        if (password === correctPassword) {
            this.isLocked = !this.isLocked;
            
            if (this.isLocked) {
                this.updateStatus('🔒 Controls locked - Enter code to unlock');
                document.getElementById('override-panel').style.borderColor = '#888';
            } else {
                this.updateStatus('🔓 Controls unlocked - Manual operation available');
                document.getElementById('override-panel').style.borderColor = '#ff4444';
            }
            
            document.getElementById('lock-password').value = '';
        } else {
            this.updateStatus('❌ Invalid lock code');
            setTimeout(() => this.updateStatus('Status: Ready'), 2000);
        }
    }
    
    showLockedMessage() {
        this.updateStatus('🔒 Controls locked - Enter unlock code first');
        setTimeout(() => this.updateStatus('Status: Locked'), 1000);
    }
    
    updateStatus(message) {
        const statusEl = document.getElementById('override-status');
        if (statusEl) statusEl.textContent = `Status: ${message}`;
    }
    
    saveState() {
        const state = {
            llmEnabled: this.llmEnabled,
            overrideActive: this.overrideActive,
            emergencyMode: this.emergencyMode,
            isLocked: this.isLocked
        };
        localStorage.setItem('rbotzilla-override-state', JSON.stringify(state));
    }
    
    loadSavedState() {
        const saved = localStorage.getItem('rbotzilla-override-state');
        if (saved) {
            const state = JSON.parse(saved);
            this.llmEnabled = state.llmEnabled !== false; // Default to true
            this.overrideActive = state.overrideActive || false;
            this.emergencyMode = state.emergencyMode || false;
            this.isLocked = state.isLocked || false;
            
            // Update UI to match loaded state
            setTimeout(() => {
                if (!this.llmEnabled) this.toggleLLM();
                if (this.overrideActive) this.toggleOverride();
                if (this.emergencyMode) this.emergencyStop();
            }, 100);
        }
    }
    
    broadcastState() {
        if (window.ioClient) {
            window.ioClient.emit('override-state', {
                llmEnabled: this.llmEnabled,
                overrideActive: this.overrideActive,
                emergencyMode: this.emergencyMode,
                timestamp: Date.now()
            });
        }
    }
}

// Global override controls
const overrideControls = new OverrideControls();

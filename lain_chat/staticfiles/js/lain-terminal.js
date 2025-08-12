/**
 * Lain Chat - Terminal Interface & Anonymization System
 * Present Day, Present Time
 */

class LainTerminal {
    constructor() {
        this.currentLayer = null;
        this.anonymizationLevel = 1;
        this.isGodKnowsMode = false;
        this.isNobodyMode = false;
        this.chatSocket = null;
        this.corruptionLevel = 0;
        this.commands = this.initializeCommands();
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeTerminalEffects();
        this.loadSystemStatus();
        this.startBackgroundProcesses();
        
        console.log('%c[LAIN_TERMINAL] System initialized', 'color: #00ff00');
        console.log('%cPresent day, present time...', 'color: #00ffff');
    }
    
    setupEventListeners() {
        // Gestion des commandes
        document.addEventListener('keydown', this.handleGlobalKeydown.bind(this));
        
        // Formulaires de chat
        const messageForm = document.getElementById('message-form');
        if (messageForm) {
            messageForm.addEventListener('submit', this.handleMessageSubmit.bind(this));
        }
        
        // Navigation des layers
        document.addEventListener('click', this.handleLayerNavigation.bind(this));
        
        // Gestion du curseur custom
        document.addEventListener('mousemove', this.updateCustomCursor.bind(this));
    }
    
    initializeCommands() {
        return {
            '/layer': {
                'create': this.createLayer.bind(this),
                'switch': this.switchLayer.bind(this),
                'burn': this.burnLayer.bind(this),
                'fragment': this.fragmentIdentity.bind(this),
                'list': this.listLayers.bind(this),
                'status': this.layerStatus.bind(this)
            },
            '/present_day': this.presentDay.bind(this),
            '/present_time': this.presentTime.bind(this),
            '/close_the_world': this.closeTheWorld.bind(this),
            '/open_the_nExt': this.openTheNext.bind(this),
            '/nobody': this.nobodyMode.bind(this),
            '/god_knows': this.godKnowsMode.bind(this),
            '/cyberia': this.enterCyberia.bind(this),
            '/wired': this.enterWired.bind(this),
            '/emergency_burn': this.emergencyBurn.bind(this),
            '/help': this.showHelp.bind(this),
            '/status': this.systemStatus.bind(this),
            '/corrupt': this.corruptDisplay.bind(this),
            '/clean': this.cleanDisplay.bind(this)
        };
    }
    
    handleMessageSubmit(event) {
        event.preventDefault();
        const input = event.target.querySelector('input[type="text"]');
        const message = input.value.trim();
        
        if (!message) return;
        
        if (message.startsWith('/')) {
            this.executeCommand(message);
        } else {
            this.sendChatMessage(message);
        }
        
        input.value = '';
    }
    
    executeCommand(commandString) {
        const [command, ...args] = commandString.split(' ');
        
        // Effet de typing pour les commandes
        this.typewriterEffect(`> ${commandString}`, 'prompt');
        
        if (this.commands[command]) {
            if (typeof this.commands[command] === 'function') {
                this.commands[command](args);
            } else if (args.length > 0 && this.commands[command][args[0]]) {
                this.commands[command][args[0]](args.slice(1));
            } else {
                this.displayError(`Unknown subcommand: ${args[0]}`);
            }
        } else {
            this.displayError(`Command not found: ${command}`);
            this.displayInfo('Type /help for available commands');
        }
    }
    
    // ========== LAYER MANAGEMENT ==========
    
    async createLayer(args) {
        const layerName = args.join(' ') || `layer_${Date.now()}`;
        
        this.displayInfo(`Creating anonymous layer: ${layerName}`);
        this.addLoadingEffect();
        
        try {
            const response = await this.secureRequest('/anonymization/create/', {
                layer_name: layerName,
                anonymization_level: this.anonymizationLevel
            });
            
            if (response.success) {
                this.currentLayer = response.layer;
                this.displaySuccess(`Layer "${layerName}" created successfully`);
                this.displayInfo(`Layer ID: ${response.layer.id.substring(0, 8)}...`);
                this.updateLayerDisplay();
            } else {
                this.displayError('Failed to create layer');
            }
        } catch (error) {
            this.displayError('Network error during layer creation');
        }
        
        this.removeLoadingEffect();
    }
    
    async switchLayer(args) {
        const layerName = args.join(' ');
        if (!layerName) {
            this.displayError('Usage: /layer switch <layer_name>');
            return;
        }
        
        this.displayInfo(`Switching to layer: ${layerName}`);
        
        try {
            const response = await this.secureRequest('/anonymization/switch/', {
                layer_name: layerName
            });
            
            if (response.success) {
                this.currentLayer = response.layer;
                this.displaySuccess(`Switched to layer: ${layerName}`);
                this.updateLayerDisplay();
                this.triggerLayerSwitchEffect();
            } else {
                this.displayError('Layer not found or access denied');
            }
        } catch (error) {
            this.displayError('Failed to switch layer');
        }
    }
    
    async burnLayer(args) {
        const layerName = args.join(' ') || 'current';
        
        // Confirmation pour destruction
        if (!confirm(`Are you sure you want to burn layer "${layerName}"? This action is irreversible.`)) {
            return;
        }
        
        this.displayWarning(`Burning layer: ${layerName}`);
        this.displayWarning('This layer will be destroyed permanently');
        
        try {
            const response = await this.secureRequest('/anonymization/burn/', {
                layer_name: layerName
            });
            
            if (response.success) {
                this.displaySuccess(`Layer "${layerName}" burned successfully`);
                this.displayInfo('All traces have been destroyed');
                this.triggerBurnEffect();
                
                if (layerName === 'current' || this.currentLayer?.name === layerName) {
                    this.currentLayer = null;
                    this.updateLayerDisplay();
                }
            } else {
                this.displayError('Failed to burn layer');
            }
        } catch (error) {
            this.displayError('Burn operation failed');
        }
    }
    
    async fragmentIdentity(args) {
        this.displayInfo('Fragmenting identity...');
        this.displayInfo('Creating multiple disconnected layers');
        
        const fragmentCount = parseInt(args[0]) || 3;
        
        try {
            const response = await this.secureRequest('/anonymization/fragment/', {
                fragment_count: fragmentCount
            });
            
            if (response.success) {
                this.displaySuccess(`Identity fragmented into ${fragmentCount} layers`);
                this.displayInfo('Each fragment is completely isolated');
                this.triggerFragmentationEffect();
            } else {
                this.displayError('Fragmentation failed');
            }
        } catch (error) {
            this.displayError('Network error during fragmentation');
        }
    }
    
    // ========== LAIN SPECIAL COMMANDS ==========
    
    presentDay() {
        this.displaySystem('Present day, present time.');
        this.resetToDefaultMode();
        this.triggerPresentDayEffect();
    }
    
    presentTime() {
        const now = new Date();
        this.displaySystem(`Current time: ${now.toLocaleString()}`);
        this.displaySystem('Time synchronization with the Wired: ACTIVE');
        this.triggerTimeEffect();
    }
    
    closeTheWorld() {
        this.displaySystem('Closing connection to the real world...');
        this.displaySystem('Entering isolated mode');
        
        // Effet visuel de fermeture
        document.body.classList.add('isolated-mode');
        this.triggerCloseWorldEffect();
        
        // Désactiver temporairement certaines fonctionnalités
        setTimeout(() => {
            this.displaySystem('Real world connection: CLOSED');
            this.displayInfo('You are now in the Wired only');
        }, 2000);
    }
    
    openTheNext() {
        this.displaySystem('Opening the nExt layer of reality...');
        this.displaySystem('Expanding consciousness boundaries');
        
        this.triggerOpenNextEffect();
        
        setTimeout(() => {
            this.displaySystem('Welcome to the nExt level');
            this.displayInfo('Reality borders are now fluid');
        }, 3000);
    }
    
    nobodyMode() {
        this.isNobodyMode = !this.isNobodyMode;
        
        if (this.isNobodyMode) {
            this.displaySystem('Nobody mode: ACTIVATED');
            this.displayInfo('All users are now "nobody"');
            document.body.classList.add('nobody-mode');
        } else {
            this.displaySystem('Nobody mode: DEACTIVATED');
            this.displayInfo('Individual identities restored');
            document.body.classList.remove('nobody-mode');
        }
        
        this.updateLayerDisplay();
    }
    
    godKnowsMode(args) {
        const duration = parseInt(args[0]) || 300; // 5 minutes par défaut
        
        this.isGodKnowsMode = true;
        this.displaySystem('God knows mode: ACTIVATED');
        this.displayWarning('All messages will be ephemeral');
        this.displayInfo(`Duration: ${duration} seconds`);
        
        document.body.classList.add('god-knows-mode');
        
        // Auto-désactivation
        setTimeout(() => {
            this.isGodKnowsMode = false;
            document.body.classList.remove('god-knows-mode');
            this.displaySystem('God knows mode: DEACTIVATED');
            this.displayInfo('Ephemeral mode ended');
        }, duration * 1000);
    }
    
    enterCyberia() {
        this.displaySystem('Connecting to CYBERIA...');
        this.displaySystem('Digital nightclub protocol: ACTIVE');
        
        // Redirection vers la room cyberia avec effets
        window.location.href = '/chat/cyberia/';
    }
    
    enterWired() {
        this.displaySystem('Full connection to the Wired established');
        this.displaySystem('Reality boundaries: DISSOLVED');
        this.triggerWiredEffect();
    }
    
    async emergencyBurn() {
        if (!confirm('EMERGENCY BURN: This will destroy ALL layers and data. Are you absolutely sure?')) {
            return;
        }
        
        if (!confirm('This action cannot be undone. Type "BURN" to confirm.')) {
            return;
        }
        
        this.displayError('EMERGENCY BURN INITIATED');
        this.displayError('Destroying all traces...');
        
        try {
            const response = await this.secureRequest('/anonymization/emergency_burn/', {
                confirmation: 'BURN'
            });
            
            if (response.success) {
                this.displayError('EMERGENCY BURN COMPLETE');
                this.displayInfo('All data destroyed');
                this.triggerEmergencyBurnEffect();
                
                // Redirection après burn
                setTimeout(() => {
                    window.location.href = '/';
                }, 3000);
            }
        } catch (error) {
            this.displayError('Emergency burn failed');
        }
    }
    
    // ========== VISUAL EFFECTS ==========
    
    triggerLayerSwitchEffect() {
        const terminal = document.querySelector('.terminal');
        terminal.style.filter = 'hue-rotate(120deg)';
        
        setTimeout(() => {
            terminal.style.filter = '';
        }, 500);
    }
    
    triggerBurnEffect() {
        const elements = document.querySelectorAll('.output p:last-child');
        elements.forEach(el => {
            el.classList.add('burn-effect');
        });
    }
    
    triggerFragmentationEffect() {
        const terminal = document.querySelector('.terminal');
        terminal.classList.add('glitch');
        
        setTimeout(() => {
            terminal.classList.remove('glitch');
        }, 2000);
    }
    
    triggerPresentDayEffect() {
        document.body.style.filter = 'brightness(1.2) contrast(1.1)';
        setTimeout(() => {
            document.body.style.filter = '';
        }, 1000);
    }
    
    triggerTimeEffect() {
        const now = new Date();
        const timeDisplay = document.createElement('div');
        timeDisplay.textContent = now.toLocaleTimeString();
        timeDisplay.style.position = 'fixed';
        timeDisplay.style.top = '20px';
        timeDisplay.style.right = '20px';
        timeDisplay.style.color = '#00ffff';
        timeDisplay.style.fontSize = '24px';
        timeDisplay.style.textShadow = '0 0 10px currentColor';
        
        document.body.appendChild(timeDisplay);
        
        setTimeout(() => {
            timeDisplay.remove();
        }, 3000);
    }
    
    corruptDisplay() {
        document.body.classList.add('glitch');
        this.corruptionLevel++;
        this.displayWarning(`Corruption level: ${this.corruptionLevel}`);
    }
    
    cleanDisplay() {
        document.body.classList.remove('glitch', 'corrupted-text');
        this.corruptionLevel = 0;
        this.displaySuccess('Display cleaned');
    }
    
    // ========== UTILITY FUNCTIONS ==========
    
    typewriterEffect(text, className = 'system-message') {
        const outputDiv = document.querySelector('.output');
        const messageDiv = document.createElement('div');
        messageDiv.className = className;
        outputDiv.appendChild(messageDiv);
        
        let i = 0;
        const timer = setInterval(() => {
            if (i < text.length) {
                messageDiv.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(timer);
            }
        }, 30);
        
        this.scrollToBottom();
    }
    
    displayMessage(message, type = 'info') {
        const outputDiv = document.querySelector('.output');
        const messageDiv = document.createElement('div');
        messageDiv.className = `${type}-message`;
        messageDiv.textContent = message;
        outputDiv.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    displayInfo(message) { this.displayMessage(message, 'info'); }
    displaySuccess(message) { this.displayMessage(message, 'success'); }
    displayError(message) { this.displayMessage(message, 'error'); }
    displayWarning(message) { this.displayMessage(message, 'warning'); }
    displaySystem(message) { this.displayMessage(message, 'system'); }
    
    scrollToBottom() {
        const outputDiv = document.querySelector('.output');
        outputDiv.scrollTop = outputDiv.scrollHeight;
    }
    
    updateCustomCursor(event) {
        const cursor = document.body;
        cursor.style.setProperty('--cursor-x', event.clientX + 'px');
        cursor.style.setProperty('--cursor-y', event.clientY + 'px');
    }
    
    async secureRequest(url, data) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(data),
            credentials: 'same-origin'
        });
        
        return await response.json();
    }
    
    showHelp() {
        const helpText = `
Available commands:

LAYER MANAGEMENT:
/layer create <name>     - Create new anonymous layer
/layer switch <name>     - Switch to existing layer  
/layer burn <name>       - Destroy layer permanently
/layer fragment [count]  - Fragment identity into multiple layers
/layer list              - List available layers
/layer status            - Show current layer status

LAIN PROTOCOLS:
/present_day            - Reset to present day mode
/present_time           - Show current time sync
/close_the_world        - Enter isolated mode
/open_the_nExt          - Expand reality boundaries
/cyberia                - Connect to CYBERIA
/wired                  - Full Wired connection

ANONYMIZATION:
/nobody                 - Toggle nobody mode
/god_knows [duration]   - Ephemeral mode (auto-destruction)
/emergency_burn         - Destroy ALL data (use with caution)

SYSTEM:
/status                 - System status
/corrupt                - Corrupt display
/clean                  - Clean display
/help                   - Show this help

Remember: The border between the real world and the Wired is becoming more ambiguous.
        `;
        
        this.typewriterEffect(helpText, 'info');
    }
}

// Initialiser le terminal quand la page est chargée
document.addEventListener('DOMContentLoaded', () => {
    window.lainTerminal = new LainTerminal();
});
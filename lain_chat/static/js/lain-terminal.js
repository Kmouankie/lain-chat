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
    
    
    setupEventListeners() {
        
        document.addEventListener('keydown', this.handleGlobalKeydown.bind(this));
        
        
        const messageForm = document.getElementById('message-form');
        if (messageForm) {
            messageForm.addEventListener('submit', this.handleMessageSubmit.bind(this));
        }
        
        s
        document.addEventListener('click', this.handleLayerNavigation.bind(this));
        
        
        document.addEventListener('mousemove', this.updateCustomCursor.bind(this));
    }
    
    
    
    initializeTerminalEffects() {
        console.log('Terminal effects initialized');
        
        this.addCRTEffects();
    }
    
    loadSystemStatus() {
        console.log('System status loaded');
        this.updateSystemDisplay();
    }
    
    startBackgroundProcesses() {
        console.log('Background processes started');
        
        this.startTimeUpdater();
        this.startCorruptionMonitor();
    }
    
    addCRTEffects() {
        
        document.body.classList.add('crt-effect');
    }
    
    updateSystemDisplay() {
        const layerDisplay = document.getElementById('layer-display');
        const currentLayer = document.getElementById('current-layer');
        
        if (layerDisplay) {
            layerDisplay.textContent = this.currentLayer?.name || 'anonymous';
        }
        if (currentLayer) {
            currentLayer.textContent = this.currentLayer?.name || 'anonymous';
        }
    }
    
    startTimeUpdater() {
        setInterval(() => {
            const timeElement = document.getElementById('system-time');
            if (timeElement) {
                const now = new Date();
                timeElement.textContent = now.toLocaleTimeString();
            }
        }, 1000);
    }
    
    startCorruptionMonitor() {
        
        setInterval(() => {
            if (Math.random() < 0.01) { 
                this.addGlitchEffect();
            }
        }, 5000);
    }
    
    addGlitchEffect() {
        document.body.classList.add('glitch');
        setTimeout(() => {
            document.body.classList.remove('glitch');
        }, 200);
    }
    
    
    
    handleGlobalKeydown(event) {
        
        if (event.ctrlKey && event.key === 'l') {
            event.preventDefault();
            this.clearDisplay();
        }
        
        
        if (event.ctrlKey && event.shiftKey && event.key === 'C') {
            event.preventDefault();
            this.corruptDisplay();
        }
    }
    
    handleLayerNavigation(event) {
        
        if (event.target.classList.contains('layer-switch')) {
            const layerName = event.target.dataset.layerName;
            if (layerName) {
                this.switchLayer([layerName]);
            }
        }
    }
    
    updateCustomCursor(event) {
        
        if (this.corruptionLevel > 5) {
            document.body.style.cursor = 'none';
        }
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
        
        
        this.typewriterEffect(`> ${commandString}`, 'prompt');
        
        if (this.commands[command]) {
            if (typeof this.commands[command] === 'function') {
                this.commands[command](args);
            } else if (args.length > 0 && this.commands[command][args[0]]) {
                this.commands[command][args[0]](args.slice(1));
            } else {
                this.displayError(`Unknown subcommand: ${args[0] || 'none'}`);
                this.showCommandHelp(command);
            }
        } else {
            this.displayError(`Command not found: ${command}`);
            this.displayInfo('Type /help for available commands');
        }
    }
    
    showCommandHelp(command) {
        if (command === '/layer') {
            this.displayInfo('Layer commands: create, switch, burn, fragment, list, status');
            this.displayInfo('Example: /layer create my_layer');
        }
    }
    
    
    
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
                this.updateSystemDisplay();
            } else {
                this.displayError('Failed to create layer');
            }
        } catch (error) {
            this.displayError('Network error during layer creation');
            console.error('Layer creation error:', error);
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
                this.updateSystemDisplay();
                this.triggerLayerSwitchEffect();
            } else {
                this.displayError('Layer not found or access denied');
            }
        } catch (error) {
            this.displayError('Failed to switch layer');
            console.error('Layer switch error:', error);
        }
    }
    
    async burnLayer(args) {
        const layerName = args.join(' ') || 'current';
        
       
        if (!confirm(`Are you sure you want to burn layer "${layerName}"? This action is irreversible.`)) {
            this.displayInfo('Burn operation cancelled');
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
                    this.updateSystemDisplay();
                }
            } else {
                this.displayError('Failed to burn layer');
            }
        } catch (error) {
            this.displayError('Burn operation failed');
            console.error('Burn error:', error);
        }
    }
    
    async fragmentIdentity(args) {
        this.displayInfo('Fragmenting identity...');
        this.displayInfo('Creating multiple disconnected layers');
        
        const fragmentCount = parseInt(args[0]) || 3;
        
        if (fragmentCount > 10) {
            this.displayError('Maximum 10 fragments allowed');
            return;
        }
        
        try {
            const response = await this.secureRequest('/anonymization/fragment/', {
                fragment_count: fragmentCount
            });
            
            if (response.success) {
                this.displaySuccess(`Identity fragmented into ${fragmentCount} layers`);
                this.displayInfo('Each fragment is completely isolated');
                this.triggerFragmentationEffect();
                
                if (response.fragments) {
                    response.fragments.forEach(fragment => {
                        this.displayInfo(`Fragment: ${fragment.name} (corruption: ${fragment.corruption_level})`);
                    });
                }
            } else {
                this.displayError('Fragmentation failed');
            }
        } catch (error) {
            this.displayError('Network error during fragmentation');
            console.error('Fragmentation error:', error);
        }
    }
    
    async listLayers() {
        this.displayInfo('Retrieving layer list...');
        
        try {
            const response = await this.secureRequest('/anonymization/api/layers/', {}, 'GET');
            
            if (response.success && response.layers) {
                this.displaySuccess(`Found ${response.layers.length} layers:`);
                
                response.layers.forEach(layer => {
                    const status = layer.is_expired ? '[EXPIRED]' : '[ACTIVE]';
                    const corruptionBar = '█'.repeat(layer.corruption_level) + '░'.repeat(10 - layer.corruption_level);
                    this.displayInfo(`${status} ${layer.name} - ID: ${layer.id} - Corruption: ${corruptionBar}`);
                });
                
                if (response.layers.length === 0) {
                    this.displayInfo('No layers found. Use /layer create to create one.');
                }
            } else {
                this.displayError('Failed to retrieve layer list');
            }
        } catch (error) {
            this.displayError('Network error retrieving layers');
            console.error('List layers error:', error);
        }
    }
    
    layerStatus() {
        if (this.currentLayer) {
            this.displaySuccess(`Current layer: ${this.currentLayer.name}`);
            this.displayInfo(`Layer ID: ${this.currentLayer.id?.substring(0, 8) || 'unknown'}...`);
            this.displayInfo(`Corruption level: ${this.currentLayer.corruption_level || 0}/10`);
            this.displayInfo(`Anonymization level: ${this.anonymizationLevel}/5`);
        } else {
            this.displayWarning('No active layer');
            this.displayInfo('Use /layer create to create a new layer');
        }
        
        this.displayInfo(`Nobody mode: ${this.isNobodyMode ? 'ACTIVE' : 'INACTIVE'}`);
        this.displayInfo(`God knows mode: ${this.isGodKnowsMode ? 'ACTIVE' : 'INACTIVE'}`);
    }
    
    
    
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
        
        
        document.body.classList.add('isolated-mode');
        this.triggerCloseWorldEffect();
        
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
        
        this.updateSystemDisplay();
    }
    
    godKnowsMode(args) {
        const duration = parseInt(args[0]) || 300; 
        
        this.isGodKnowsMode = true;
        this.displaySystem('God knows mode: ACTIVATED');
        this.displayWarning('All messages will be ephemeral');
        this.displayInfo(`Duration: ${duration} seconds`);
        
        document.body.classList.add('god-knows-mode');
        
        
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
        this.displayInfo('Redirecting to CYBERIA room...');
        
        setTimeout(() => {
            window.location.href = '/chat/cyberia/';
        }, 2000);
    }
    
    enterWired() {
        this.displaySystem('Full connection to the Wired established');
        this.displaySystem('Reality boundaries: DISSOLVED');
        this.triggerWiredEffect();
        
       
        document.body.classList.add('wired-mode');
        this.anonymizationLevel = 5; 
    }
    
    async emergencyBurn() {
        this.displayError('WARNING: EMERGENCY BURN PROTOCOL');
        this.displayError('This will destroy ALL layers and data');
        
        if (!confirm('EMERGENCY BURN: This will destroy ALL layers and data. Are you absolutely sure?')) {
            this.displayInfo('Emergency burn cancelled');
            return;
        }
        
        const confirmation = prompt('Type "BURN" to confirm total destruction:');
        if (confirmation !== 'BURN') {
            this.displayInfo('Emergency burn cancelled - invalid confirmation');
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
                
                setTimeout(() => {
                    window.location.href = '/';
                }, 3000);
            } else {
                this.displayError('Emergency burn failed');
            }
        } catch (error) {
            this.displayError('Emergency burn failed');
            console.error('Emergency burn error:', error);
        }
    }
    
    
    systemStatus() {
        this.displaySuccess('=== LAIN TERMINAL SYSTEM STATUS ===');
        this.displayInfo('System: OPERATIONAL');
        this.displayInfo('Anonymization: ACTIVE');
        this.displayInfo('Encryption: AES-256');
        this.displayInfo('Zero-knowledge auth: ENABLED');
        this.displayInfo(`Corruption level: ${this.corruptionLevel}/10`);
        this.displayInfo(`Current layer: ${this.currentLayer?.name || 'anonymous'}`);
        this.displayInfo('Present day, present time...');
        this.displaySuccess('=== END STATUS ===');
    }
    
    corruptDisplay() {
        document.body.classList.add('glitch');
        this.corruptionLevel++;
        this.displayWarning(`Corruption level increased: ${this.corruptionLevel}/10`);
        
        if (this.corruptionLevel >= 10) {
            this.displayError('CRITICAL CORRUPTION LEVEL REACHED');
            this.displayError('System integrity compromised');
        }
    }
    
    cleanDisplay() {
        document.body.classList.remove('glitch', 'corrupted-text');
        this.corruptionLevel = Math.max(0, this.corruptionLevel - 1);
        this.displaySuccess('Display corruption reduced');
        this.displayInfo(`Corruption level: ${this.corruptionLevel}/10`);
    }
    
    showHelp() {
        const helpText = `
 LAIN TERMINAL COMMAND REFERENCE 

LAYER MANAGEMENT:
/layer create <name>     - Create new anonymous layer
/layer switch <name>     - Switch to existing layer  
/layer burn <name>       - Destroy layer permanently
/layer fragment [count]  - Fragment identity (max 10)
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
/emergency_burn         - Destroy ALL data (DANGER!)

SYSTEM:
/status                 - System status
/corrupt                - Increase corruption
/clean                  - Reduce corruption
/help                   - Show this help

KEYBOARD SHORTCUTS:
Ctrl+L                  - Clear display
Ctrl+Shift+C           - Force corruption

=== REMEMBER 
The border between the real world and the Wired 
is becoming more and more ambiguous.


        `;
        
        this.typewriterEffect(helpText, 'info');
    }
    
    
    triggerLayerSwitchEffect() {
        const terminal = document.querySelector('.terminal');
        if (terminal) {
            terminal.style.filter = 'hue-rotate(120deg)';
            setTimeout(() => {
                terminal.style.filter = '';
            }, 500);
        }
    }
    
    triggerBurnEffect() {
        const elements = document.querySelectorAll('.output p:last-child');
        elements.forEach(el => {
            el.classList.add('burn-effect');
        });
    }
    
    triggerFragmentationEffect() {
        const terminal = document.querySelector('.terminal');
        if (terminal) {
            terminal.classList.add('glitch');
            setTimeout(() => {
                terminal.classList.remove('glitch');
            }, 2000);
        }
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
        timeDisplay.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            color: #00ffff;
            font-size: 24px;
            text-shadow: 0 0 10px currentColor;
            z-index: 9999;
        `;
        
        document.body.appendChild(timeDisplay);
        
        setTimeout(() => {
            timeDisplay.remove();
        }, 3000);
    }
    
    triggerCloseWorldEffect() {
        document.body.style.filter = 'sepia(1) hue-rotate(90deg)';
    }
    
    triggerOpenNextEffect() {
        document.body.style.filter = 'invert(0.1) hue-rotate(180deg)';
        setTimeout(() => {
            document.body.style.filter = '';
        }, 3000);
    }
    
    triggerWiredEffect() {
        document.body.classList.add('matrix-effect');
        setTimeout(() => {
            document.body.classList.remove('matrix-effect');
        }, 5000);
    }
    
    triggerEmergencyBurnEffect() {
        document.body.style.animation = 'burn 3s ease-out forwards';
    }
    
    
    resetToDefaultMode() {
        this.isNobodyMode = false;
        this.isGodKnowsMode = false;
        this.anonymizationLevel = 1;
        this.corruptionLevel = 0;
        
        document.body.classList.remove('nobody-mode', 'god-knows-mode', 'wired-mode', 'isolated-mode');
        document.body.style.filter = '';
    }
    
    typewriterEffect(text, className = 'system-message') {
        const outputDiv = document.querySelector('.output') || document.querySelector('#main-output');
        if (!outputDiv) return;
        
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
        }, 20); 
        
        this.scrollToBottom();
    }
    
    displayMessage(message, type = 'info') {
        const outputDiv = document.querySelector('.output') || document.querySelector('#main-output');
        if (!outputDiv) return;
        
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
        const outputDiv = document.querySelector('.output') || document.querySelector('#main-output');
        if (outputDiv) {
            outputDiv.scrollTop = outputDiv.scrollHeight;
        }
    }
    
    clearDisplay() {
        const outputDiv = document.querySelector('.output') || document.querySelector('#main-output');
        if (outputDiv) {
            outputDiv.innerHTML = '<p class="system-message">Display cleared. Type /help for commands.</p>';
        }
    }
    
    addLoadingEffect() {
        const outputDiv = document.querySelector('.output') || document.querySelector('#main-output');
        if (outputDiv) {
            const loader = document.createElement('div');
            loader.className = 'loading-effect';
            loader.textContent = 'Processing';
            loader.id = 'loader';
            outputDiv.appendChild(loader);
        }
    }
    
    removeLoadingEffect() {
        const loader = document.getElementById('loader');
        if (loader) {
            loader.remove();
        }
    }
    
    sendChatMessage(message) {
        this.displayInfo(`[LOCAL] ${message}`);
    }
    
    async secureRequest(url, data, method = 'POST') {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        
        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: method !== 'GET' ? JSON.stringify(data) : null,
                credentials: 'same-origin'
            });
            
            return await response.json();
        } catch (error) {
            console.error('Request failed:', error);
            throw error;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.lainTerminal = new LainTerminal();
    console.log('%cLain Terminal initialized successfully', 'color: #00ff00; font-weight: bold;');
});
class LainCommandSystem {
    constructor() {
        this.commands = new Map();
        this.commandHistory = [];
        this.currentHistoryIndex = -1;
        this.specialSequences = new Map();
        this.setupCommands();
        this.setupSequences();
    }

    setupCommands() {
        
        this.commands.set('/help', {
            description: 'Affiche la liste des commandes disponibles',
            execute: this.showHelp ? this.showHelp.bind(this) : this.defaultCommand.bind(this),
            category: 'system'
        });

        this.commands.set('/present_day', {
            description: 'Present day, present time',
            execute: this.presentDay ? this.presentDay.bind(this) : this.defaultCommand.bind(this),
            category: 'lain'
        });

        this.commands.set('/god_knows', {
            description: 'Active le mode ephémère (messages non sauvegardés)',
            execute: this.godKnows ? this.godKnows.bind(this) : this.defaultCommand.bind(this),
            category: 'lain'
        });

        this.commands.set('/nobody', {
            description: 'Bascule en mode anonyme total',
            execute: this.nobody ? this.nobody.bind(this) : this.defaultCommand.bind(this),
            category: 'lain'
        });

        this.commands.set('/close_the_world', {
            description: 'Ferme la connexion au monde réel',
            execute: this.closeTheWorld ? this.closeTheWorld.bind(this) : this.defaultCommand.bind(this),
            category: 'lain'
        });

        this.commands.set('/open_the_next', {
            description: 'Ouvre la prochaine couche de réalité',
            execute: this.openTheNext ? this.openTheNext.bind(this) : this.defaultCommand.bind(this),
            category: 'lain'
        });

        this.commands.set('/layer', {
            description: 'Gestion des layers anonymes',
            execute: this.layerCommand ? this.layerCommand.bind(this) : this.defaultCommand.bind(this),
            category: 'anonymization',
            subcommands: ['create', 'switch', 'burn', 'list', 'corrupt']
        });

        this.commands.set('/protocol', {
            description: 'Informations sur le protocole Lain',
            execute: this.protocolInfo ? this.protocolInfo.bind(this) : this.defaultCommand.bind(this),
            category: 'system'
        });

        this.commands.set('/wired', {
            description: 'Informations sur la connexion au Wired',
            execute: this.wiredStatus ? this.wiredStatus.bind(this) : this.defaultCommand.bind(this),
            category: 'system'
        });

        this.commands.set('/cyberia', {
            description: 'Accès au club Cyberia',
            execute: this.cyberia ? this.cyberia.bind(this) : this.defaultCommand.bind(this),
            category: 'easter'
        });

        this.commands.set('/knights', {
            description: 'Invoque les Knights of the Eastern Calculus',
            execute: this.knights ? this.knights.bind(this) : this.defaultCommand.bind(this),
            category: 'easter'
        });

        this.commands.set('/masami', {
            description: 'Souvenir de Masami Eiri',
            execute: this.masami ? this.masami.bind(this) : this.defaultCommand.bind(this),
            category: 'easter'
        });

        this.commands.set('/navi', {
            description: 'Interface NAVI',
            execute: this.navi ? this.navi.bind(this) : this.defaultCommand.bind(this),
            category: 'easter'
        });

        this.commands.set('/corrupt', {
            description: 'Applique des effets de corruption',
            execute: this.corrupt ? this.corrupt.bind(this) : this.defaultCommand.bind(this),
            category: 'effects'
        });

        this.commands.set('/glitch', {
            description: 'Déclenche des effets de glitch',
            execute: this.glitch ? this.glitch.bind(this) : this.defaultCommand.bind(this),
            category: 'effects'
        });

        this.commands.set('/phantom', {
            description: 'Mode fantôme temporaire',
            execute: this.phantom ? this.phantom.bind(this) : this.defaultCommand.bind(this),
            category: 'effects'
        });
    }

    defaultCommand(args, chatSocket) {
        this.addSystemMessage('Command functionality will be implemented soon.', 'info');
        return true;
    }

    setupSequences() {
        this.specialSequences.set('lainlainlain', {
            effect: this.lainSequence ? this.lainSequence.bind(this) : this.defaultCommand.bind(this),
            description: 'Séquence Lain triple'
        });

        this.specialSequences.set('godishere', {
            effect: this.godIsHere ? this.godIsHere.bind(this) : this.defaultCommand.bind(this),
            description: 'Manifestation divine'
        });

        this.specialSequences.set('serialexperiments', {
            effect: this.serialExperiments ? this.serialExperiments.bind(this) : this.defaultCommand.bind(this),
            description: 'Activation du mode expérimental'
        });
    }


    async executeCommand(input, chatSocket) {
        const parts = input.trim().split(' ');
        const command = parts[0].toLowerCase();
        const args = parts.slice(1);

        this.addToHistory(input);

        if (this.commands.has(command)) {
            const cmd = this.commands.get(command);
            try {
                await cmd.execute(args, chatSocket);
                return true;
            } catch (error) {
                this.addSystemMessage(`Erreur lors de l'exécution de ${command}: ${error.message}`, 'error');
                return false;
            }
        } else {
            this.addSystemMessage(`Commande inconnue: ${command}. Tapez /help pour voir les commandes disponibles.`, 'error');
            return false;
        }
    }


    async presentDay(args, chatSocket) {
        this.addSystemMessage('Present day, present time...', 'lain');
        
        this.triggerGlitchEffect();
        
        if (chatSocket) {
            chatSocket.send(JSON.stringify({
                type: 'layer_command',
                command: '/present_day'
            }));
        }
        
        setTimeout(() => {
            this.addSystemMessage('Reality anchor established.', 'success');
        }, 2000);
    }

    async godKnows(args, chatSocket) {
        this.addSystemMessage('God knows what you\'re doing...', 'lain');
        this.addSystemMessage('Messages will now be ephemeral - no traces left behind.', 'warning');
        
        if (chatSocket) {
            chatSocket.send(JSON.stringify({
                type: 'layer_command',
                command: '/god_knows'
            }));
        }
        
        this.applyEphemeralEffect();
    }

    async nobody(args, chatSocket) {
        this.addSystemMessage('Entering nobody mode...', 'lain');
        this.addSystemMessage('Your identity dissolves into the Wired.', 'info');
        
        if (chatSocket) {
            chatSocket.send(JSON.stringify({
                type: 'layer_command',
                command: '/nobody'
            }));
        }
        
        this.applyDissolutionEffect();
    }

    async closeTheWorld(args, chatSocket) {
        this.addSystemMessage('Closing connection to the real world...', 'lain');
        this.addSystemMessage('Only the Wired remains.', 'warning');
        
        this.closeWorldEffect();
        
        if (chatSocket) {
            chatSocket.send(JSON.stringify({
                type: 'layer_command',
                command: '/close_the_world'
            }));
        }
    }

    async openTheNext(args, chatSocket) {
        this.addSystemMessage('Opening the next layer...', 'lain');
        this.addSystemMessage('Reality boundaries expanding.', 'info');
        
        this.openNextEffect();
        
        setTimeout(() => {
            this.addSystemMessage('New layer accessible. Protocol 7 active.', 'success');
        }, 3000);
    }


    async cyberia(args, chatSocket) {
        this.addSystemMessage('Welcome to Cyberia...', 'lain');
        this.addSystemMessage('♪ The music never stops here ♪', 'info');
        
        this.cyberiaEffect();
        
        const quotes = [
            "Are you happy?",
            "The boundary between dreams and reality is unclear.",
            "Dance until the world ends."
        ];
        
        setTimeout(() => {
            const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
            this.addSystemMessage(randomQuote, 'lain');
        }, 2000);
    }

    async knights(args, chatSocket) {
        this.addSystemMessage('Summoning the Knights of the Eastern Calculus...', 'lain');
        
        this.knightsEffect();
        
        setTimeout(() => {
            this.addSystemMessage('The Knights are watching.', 'warning');
            this.addSystemMessage('Your actions in the Wired are being monitored.', 'info');
        }, 2000);
    }

    async masami(args, chatSocket) {
        this.addSystemMessage('Masami Eiri... the father of Protocol 7.', 'lain');
        this.addSystemMessage('His consciousness still lingers in the Wired.', 'info');
        
        this.spectralEffect();
        
        setTimeout(() => {
            this.addSystemMessage('"I am not an AI. I am a god."', 'lain');
        }, 3000);
    }

    async navi(args, chatSocket) {
        this.addSystemMessage('NAVI interface activated.', 'lain');
        this.addSystemMessage('Cooling system: OPTIMAL', 'info');
        this.addSystemMessage('Network connection: STABLE', 'info');
        this.addSystemMessage('Reality filter: DISABLED', 'warning');
        
        this.naviInterface();
    }


    async layerCommand(args, chatSocket) {
        if (args.length === 0) {
            this.addSystemMessage('Usage: /layer <create|switch|burn|list|corrupt> [args]', 'info');
            return;
        }

        const subcommand = args[0].toLowerCase();
        const subArgs = args.slice(1);

        switch (subcommand) {
            case 'create':
                await this.createLayer(subArgs, chatSocket);
                break;
            case 'switch':
                await this.switchLayer(subArgs, chatSocket);
                break;
            case 'burn':
                await this.burnLayer(subArgs, chatSocket);
                break;
            case 'list':
                await this.listLayers(subArgs, chatSocket);
                break;
            case 'corrupt':
                await this.corruptLayer(subArgs, chatSocket);
                break;
            default:
                this.addSystemMessage(`Sous-commande inconnue: ${subcommand}`, 'error');
        }
    }

    async createLayer(args, chatSocket) {
        const layerName = args.join('_') || `layer_${Date.now()}`;
        this.addSystemMessage(`Creating layer: ${layerName}`, 'info');
        
        if (chatSocket) {
            chatSocket.send(JSON.stringify({
                type: 'layer_command',
                command: `/layer create ${layerName}`
            }));
        }
    }

    async protocolInfo(args, chatSocket) {
        if (args.length > 0 && args[0] === '7') {
            this.addSystemMessage('Protocol 7: The love protocol.', 'lain');
            this.addSystemMessage('Connects all human consciousness.', 'info');
            this.addSystemMessage('Status: PARTIALLY_ACTIVE', 'warning');
        } else {
            this.addSystemMessage('LAIN_PROTOCOL v2.3.7', 'info');
            this.addSystemMessage('Anonymization: ENABLED', 'info');
            this.addSystemMessage('Encryption: AES-256-GCM', 'info');
        }
    }

    async wiredStatus(args, chatSocket) {
        this.addSystemMessage('=== WIRED CONNECTION STATUS ===', 'info');
        this.addSystemMessage('Status: CONNECTED', 'success');
        this.addSystemMessage('Protocol: LAIN v2.3.7', 'info');
        this.addSystemMessage('Anonymization: ACTIVE', 'info');
        this.addSystemMessage('Reality anchor: STABLE', 'info');
    }


    triggerGlitchEffect() {
        const terminal = document.querySelector('.terminal-screen');
        if (terminal) {
            terminal.classList.add('glitch-effect');
            setTimeout(() => {
                terminal.classList.remove('glitch-effect');
            }, 1000);
        }
    }

    applyEphemeralEffect() {
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            chatMessages.classList.add('ephemeral-mode');
        }
    }

    applyDissolutionEffect() {
        const userDisplay = document.querySelector('.anon-id');
        if (userDisplay) {
            userDisplay.textContent = 'NOBODY';
            userDisplay.classList.add('dissolving');
        }
    }

    closeWorldEffect() {
        const terminal = document.querySelector('.crt-container');
        if (terminal) {
            terminal.classList.add('closing-world');
            setTimeout(() => {
                terminal.classList.remove('closing-world');
            }, 5000);
        }
    }

    openNextEffect() {
        const terminal = document.querySelector('.terminal-screen');
        if (terminal) {
            terminal.classList.add('dimension-shift');
            setTimeout(() => {
                terminal.classList.remove('dimension-shift');
            }, 3000);
        }
    }

    cyberiaEffect() {
        const body = document.body;
        body.classList.add('cyberia-mode');
        
        setTimeout(() => {
            body.classList.remove('cyberia-mode');
        }, 10000);
    }

    knightsEffect() {
        for (let i = 0; i < 5; i++) {
            setTimeout(() => {
                this.createMysticSymbol();
            }, i * 500);
        }
    }

    spectralEffect() {
        const terminal = document.querySelector('.terminal-screen');
        if (terminal) {
            terminal.classList.add('spectral');
            setTimeout(() => {
                terminal.classList.remove('spectral');
            }, 4000);
        }
    }

    naviInterface() {
        const naviDiv = document.createElement('div');
        naviDiv.className = 'navi-interface';
        naviDiv.innerHTML = `
            <div class="navi-header">NAVI SYSTEM v2.3.7</div>
            <div class="navi-status">STATUS: ONLINE</div>
            <div class="navi-temp">CPU TEMP: 42°C</div>
            <div class="navi-mem">MEMORY: 2048MB AVAILABLE</div>
        `;
        
        document.body.appendChild(naviDiv);
        
        setTimeout(() => {
            naviDiv.remove();
        }, 5000);
    }

    createMysticSymbol() {
        const symbols = ['◉', '⟐', '⧨', '⟠', '◈'];
        const symbol = symbols[Math.floor(Math.random() * symbols.length)];
        
        const div = document.createElement('div');
        div.className = 'mystic-symbol';
        div.textContent = symbol;
        div.style.left = Math.random() * window.innerWidth + 'px';
        div.style.top = Math.random() * window.innerHeight + 'px';
        
        document.body.appendChild(div);
        
        setTimeout(() => {
            div.remove();
        }, 3000);
    }


    showHelp() {
        this.addSystemMessage('=== LAIN CHAT COMMANDS ===', 'info');
        
        const categories = {
            'lain': 'Lain Commands',
            'anonymization': 'Layer Management', 
            'system': 'System Commands',
            'effects': 'Visual Effects',
            'easter': 'Easter Eggs'
        };

        for (const [category, title] of Object.entries(categories)) {
            this.addSystemMessage(`\n--- ${title} ---`, 'info');
            
            for (const [cmd, info] of this.commands.entries()) {
                if (info.category === category) {
                    this.addSystemMessage(`${cmd} - ${info.description}`, 'info');
                }
            }
        }
        
        this.addSystemMessage('\n"Let\'s all love Lain"', 'lain');
    }

    addToHistory(command) {
        this.commandHistory.push(command);
        if (this.commandHistory.length > 50) {
            this.commandHistory.shift();
        }
        this.currentHistoryIndex = this.commandHistory.length;
    }

    getHistoryCommand(direction) {
        if (direction === 'up' && this.currentHistoryIndex > 0) {
            this.currentHistoryIndex--;
            return this.commandHistory[this.currentHistoryIndex];
        } else if (direction === 'down' && this.currentHistoryIndex < this.commandHistory.length - 1) {
            this.currentHistoryIndex++;
            return this.commandHistory[this.currentHistoryIndex];
        } else if (direction === 'down' && this.currentHistoryIndex === this.commandHistory.length - 1) {
            this.currentHistoryIndex = this.commandHistory.length;
            return '';
        }
        return null;
    }

    addSystemMessage(message, type = 'info') {
        if (window.addSystemMessage) {
            window.addSystemMessage(message, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }
}

window.LainCommands = new LainCommandSystem();

if (typeof module !== 'undefined' && module.exports) {
    module.exports = LainCommandSystem;
}
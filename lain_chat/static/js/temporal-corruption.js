class TemporalCorruptionSystem {
    constructor() {
        this.corruptionTimers = new Map();
        this.countdownTimers = new Map();  
        this.corruptionChars = ['█', '▓', '▒', '░', '▄', '▀', '▐', '▌', '▬', '■', '□', '▪', '▫'];
        this.isActive = true;
        
        console.log('[CORRUPTION] Temporal corruption system initialized');
    }
    
    
    startMessageCorruption(messageElement, metadata) {
        if (!this.isActive || !metadata) {
            console.log('[CORRUPTION] System inactive or no metadata');
            return;
        }
        
        const corruptionLevel = metadata.corruption_level || 0;
        const corruptionDelay = metadata.corruption_delay || 0;
        const messageId = metadata.message_id;
        
        console.log(`[CORRUPTION] Processing message ${messageId?.substring(0, 8)} - Level: ${corruptionLevel}, Delay: ${corruptionDelay}s`);
        
        
        if (corruptionLevel === 0 || corruptionDelay === 0) {
            console.log('[CORRUPTION] No corruption needed (level 0)');
            return;
        }
        
        
        this.startCountdown(messageElement, messageId, corruptionDelay);
        
        
        if (metadata.is_ephemeral) {
            console.log('[CORRUPTION] Ephemeral mode - fast corruption');
            this.scheduleCorruption(messageElement, messageId, 5000); // 5 secondes
            return;
        }
        
        
        const delayMs = corruptionDelay * 1000;
        console.log(`[CORRUPTION] Scheduling corruption in ${delayMs}ms`);
        this.scheduleCorruption(messageElement, messageId, delayMs);
    }
    
    
    startCountdown(messageElement, messageId, totalSeconds) {
        const indicator = messageElement.querySelector('.corruption-indicator');
        if (!indicator) return;
        
        let remainingSeconds = totalSeconds;
        
        
        const updateDisplay = () => {
            if (remainingSeconds <= 0) {
                indicator.textContent = '0';
                indicator.className = 'corruption-indicator corrupting';
                return;
            }
            
            indicator.textContent = remainingSeconds.toString();
            
            
            const percentage = remainingSeconds / totalSeconds;
            indicator.className = 'corruption-indicator countdown';
            
            if (percentage > 0.7) {
                indicator.classList.add('high-time');
            } else if (percentage > 0.4) {
                indicator.classList.add('medium-time');
            } else if (percentage > 0.2) {
                indicator.classList.add('low-time');
            } else {
                indicator.classList.add('critical-time');
            }
        };
        
        
        updateDisplay();
        
       
        const countdownInterval = setInterval(() => {
            remainingSeconds--;
            updateDisplay();
            
            if (remainingSeconds <= 0) {
                clearInterval(countdownInterval);
                this.countdownTimers.delete(messageId);
            }
        }, 1000);
        
       
        this.countdownTimers.set(messageId, countdownInterval);
        
        console.log(`[COUNTDOWN] Started countdown for message ${messageId?.substring(0, 8)} - ${totalSeconds}s`);
    }
    
    
    scheduleCorruption(messageElement, messageId, delayMs) {
        
        if (this.corruptionTimers.has(messageId)) {
            clearTimeout(this.corruptionTimers.get(messageId));
        }
        
        
        const timer = setTimeout(() => {
            this.corruptMessage(messageElement, messageId);
            this.corruptionTimers.delete(messageId);
        }, delayMs);
        
        this.corruptionTimers.set(messageId, timer);
    }
    
    
    corruptMessage(messageElement, messageId) {
        if (!messageElement || !messageElement.isConnected) {
            console.log(`[CORRUPTION] Message ${messageId?.substring(0, 8)} element not found or disconnected`);
            return;
        }
        
        const messageTextElement = messageElement.querySelector('.message-text');
        if (!messageTextElement) {
            console.log(`[CORRUPTION] Message text element not found for ${messageId?.substring(0, 8)}`);
            return;
        }
        
        const originalText = messageTextElement.textContent;
        
        
        messageElement.classList.add('corrupting');
        
        
        this.progressiveCorruption(messageTextElement, originalText, 0);
        
        console.log(`[CORRUPTION]  Started corrupting message ${messageId?.substring(0, 8)}: "${originalText.substring(0, 20)}..."`);
    }
    
    
    progressiveCorruption(textElement, originalText, step) {
        const totalSteps = 3;  
        const stepDelay = 100;  
        
        if (step >= totalSteps) {
            
            textElement.textContent = this.generateCorruptedText(originalText.length);
            textElement.parentElement.classList.add('fully-corrupted');
            textElement.parentElement.classList.remove('corrupting');
            console.log(`[CORRUPTION]  Message fully corrupted: "${originalText.substring(0, 20)}..." → "${textElement.textContent.substring(0, 20)}..."`);
            return;
        }
        
        
        const corruptionPercent = (step + 1) / totalSteps;
        const partiallyCorrupted = this.applyPartialCorruption(originalText, corruptionPercent);
        textElement.textContent = partiallyCorrupted;
        
        
        setTimeout(() => {
            this.progressiveCorruption(textElement, originalText, step + 1);
        }, stepDelay);
    }
    
   
    applyPartialCorruption(text, percent) {
        return text.split('').map(char => {
            if (char === ' ') return ' '; 
            
            if (Math.random() < percent) {
                return this.getRandomCorruptionChar();
            }
            return char;
        }).join('');
    }
    
    
    generateCorruptedText(length) {
        let corrupted = '';
        for (let i = 0; i < length; i++) {
            if (Math.random() < 0.2) {
                corrupted += ' '; 
            } else {
                corrupted += this.getRandomCorruptionChar();
            }
        }
        return corrupted;
    }
    
    
    getRandomCorruptionChar() {
        return this.corruptionChars[Math.floor(Math.random() * this.corruptionChars.length)];
    }
    
    
    instantCorruption(messageElement, level = 10) {
        const messageTextElement = messageElement.querySelector('.message-text');
        if (!messageTextElement) return;
        
        const originalText = messageTextElement.textContent;
        const corruptionPercent = Math.min(level / 10, 1);
        
        messageElement.classList.add('instant-corruption');
        
        
        let step = 0;
        const animate = () => {
            if (step >= 10) {
                messageTextElement.textContent = this.generateCorruptedText(originalText.length);
                messageElement.classList.add('fully-corrupted');
                messageElement.classList.remove('instant-corruption');
                return;
            }
            
            const corrupted = this.applyPartialCorruption(originalText, (step + 1) / 10 * corruptionPercent);
            messageTextElement.textContent = corrupted;
            step++;
            
            setTimeout(animate, 50);
        };
        
        animate();
    }
    
    
    toggleCorruption(active = null) {
        this.isActive = active !== null ? active : !this.isActive;
        
        if (!this.isActive) {
            
            this.corruptionTimers.forEach(timer => clearTimeout(timer));
            this.corruptionTimers.clear();
            console.log('[CORRUPTION] System deactivated');
        } else {
            console.log('[CORRUPTION] System activated');
        }
        
        return this.isActive;
    }
    
    cancelMessageCorruption(messageId) {
        if (this.corruptionTimers.has(messageId)) {
            clearTimeout(this.corruptionTimers.get(messageId));
            this.corruptionTimers.delete(messageId);
            console.log(`[CORRUPTION] Cancelled corruption for message ${messageId?.substring(0, 8)}`);
        }
    }
    
  
    cleanup() {
        this.corruptionTimers.forEach(timer => clearTimeout(timer));
        this.corruptionTimers.clear();
        console.log('[CORRUPTION] System cleaned up');
    }
    
    
    getStats() {
        return {
            active: this.isActive,
            activeTimers: this.corruptionTimers.size,
            corruptionChars: this.corruptionChars.length
        };
    }
}


window.TemporalCorruption = new TemporalCorruptionSystem();


window.addEventListener('beforeunload', () => {
    if (window.TemporalCorruption) {
        window.TemporalCorruption.cleanup();
    }
});


if (typeof module !== 'undefined' && module.exports) {
    module.exports = TemporalCorruptionSystem;
}

console.log('Temporal Corruption System loaded - Present day, present time...');
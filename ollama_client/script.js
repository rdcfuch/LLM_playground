class OllamaChat {
    constructor() {
        this.settings = {
            serverUrl: 'http://localhost:11434',
            model: 'qwen3:8b',
            temperature: 0.7
        };
        
        this.chatHistory = [];
        this.isGenerating = false;
        
        this.initializeElements();
        this.bindEvents();
        this.loadSettings();
        this.setupMarkdown();
    }
    
    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.settingsBtn = document.getElementById('settingsBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.settingsPanel = document.getElementById('settingsPanel');
        this.serverUrlInput = document.getElementById('serverUrl');
        this.modelSelect = document.getElementById('modelSelect');
        this.temperatureSlider = document.getElementById('temperature');
        this.temperatureValue = document.getElementById('temperatureValue');
        this.saveSettingsBtn = document.getElementById('saveSettings');
        this.loadingOverlay = document.getElementById('loadingOverlay');
    }
    
    bindEvents() {
        // Send message events
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => this.autoResizeTextarea());
        
        // Settings events
        this.settingsBtn.addEventListener('click', () => this.toggleSettings());
        this.saveSettingsBtn.addEventListener('click', () => this.saveSettings());
        this.temperatureSlider.addEventListener('input', (e) => {
            this.temperatureValue.textContent = e.target.value;
        });
        
        // Clear chat
        this.clearBtn.addEventListener('click', () => this.clearChat());
        
        // Close settings when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.settingsPanel.contains(e.target) && !this.settingsBtn.contains(e.target)) {
                this.settingsPanel.classList.remove('open');
            }
        });
    }
    
    setupMarkdown() {
        // Configure marked for better rendering
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                breaks: true,
                gfm: true,
                sanitize: false
            });
        }
    }
    
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    toggleSettings() {
        this.settingsPanel.classList.toggle('open');
    }
    
    loadSettings() {
        const saved = localStorage.getItem('ollamaSettings');
        if (saved) {
            this.settings = { ...this.settings, ...JSON.parse(saved) };
        }
        
        this.serverUrlInput.value = this.settings.serverUrl;
        this.modelSelect.value = this.settings.model;
        this.temperatureSlider.value = this.settings.temperature;
        this.temperatureValue.textContent = this.settings.temperature;
    }
    
    saveSettings() {
        this.settings = {
            serverUrl: this.serverUrlInput.value,
            model: this.modelSelect.value,
            temperature: parseFloat(this.temperatureSlider.value)
        };
        
        localStorage.setItem('ollamaSettings', JSON.stringify(this.settings));
        this.settingsPanel.classList.remove('open');
        this.showNotification('Settings saved successfully!');
    }
    
    showNotification(message) {
        // Simple notification - you could enhance this
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4caf50;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            z-index: 1001;
            animation: fadeInUp 0.3s ease;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    clearChat() {
        this.chatHistory = [];
        this.chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">
                    <span class="material-icons">waving_hand</span>
                </div>
                <h2>Welcome to Ollama Chat</h2>
                <p>Start a conversation with your local AI model. Type your message below and press Enter or click Send.</p>
            </div>
        `;
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isGenerating) return;
        
        // Clear input and disable send button
        this.messageInput.value = '';
        this.autoResizeTextarea();
        this.isGenerating = true;
        this.sendButton.disabled = true;
        
        // Remove welcome message if it exists
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        // Add user message to UI only (not to history yet)
        this.addMessageToUI(message, 'user');
        
        // Show loading
        this.showLoading(true);
        
        try {
            // Send to Ollama
            const response = await this.callOllama(message);
            
            // Now add both messages to history
            this.chatHistory.push({ role: 'user', content: message });
            this.chatHistory.push({ role: 'assistant', content: response });
            
            this.addMessageToUI(response, 'assistant');
        } catch (error) {
            console.error('Error calling Ollama:', error);
            this.addMessageToUI('Sorry, I encountered an error while processing your request. Please check your Ollama server connection and try again.', 'assistant', true);
        } finally {
            this.showLoading(false);
            this.isGenerating = false;
            this.sendButton.disabled = false;
            this.messageInput.focus();
        }
    }
    
    addMessageToUI(content, sender, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? 
            '<span class="material-icons">person</span>' : 
            '<span class="material-icons">smart_toy</span>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        if (isError) {
            bubble.style.background = '#ffebee';
            bubble.style.color = '#c62828';
            bubble.style.border = '1px solid #ffcdd2';
        }
        
        // Render markdown for assistant messages, plain text for user messages
        if (sender === 'assistant' && typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
            const html = marked.parse(content);
            bubble.innerHTML = DOMPurify.sanitize(html);
        } else {
            bubble.textContent = content;
        }
        
        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = new Date().toLocaleTimeString();
        
        messageContent.appendChild(bubble);
        messageContent.appendChild(time);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    // Keep the old method for backward compatibility if needed elsewhere
    addMessage(content, sender, isError = false) {
        this.addMessageToUI(content, sender, isError);
        this.chatHistory.push({ role: sender, content });
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    showLoading(show) {
        if (show) {
            this.loadingOverlay.classList.add('show');
        } else {
            this.loadingOverlay.classList.remove('show');
        }
    }
    
    async callOllama(message) {
        const url = `${this.settings.serverUrl}/api/generate`;
        
        // Prepare context from chat history
        let context = '';
        const recentHistory = this.chatHistory.slice(-10); // Last 10 messages for context
        
        for (const msg of recentHistory) {
            if (msg.role === 'user') {
                context += `Human: ${msg.content}\n`;
            } else {
                context += `Assistant: ${msg.content}\n`;
            }
        }
        
        const prompt = context + `Human: ${message}\nAssistant:`;
        
        const requestBody = {
            model: this.settings.model,
            prompt: prompt,
            stream: false,
            options: {
                temperature: this.settings.temperature
            }
        };
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            const data = await response.json();
            return data.response || 'No response received';
            
        } catch (error) {
            console.error('Ollama API Error:', error);
            
            // Check for specific error types
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('Cannot connect to Ollama server. Please ensure:\n\n1. Ollama is running (try: ollama serve)\n2. Server is accessible at ' + this.settings.serverUrl + '\n3. CORS is enabled (try: OLLAMA_ORIGINS=* ollama serve)');
            } else if (error.message.includes('CORS')) {
                throw new Error('CORS error detected. Please start Ollama with CORS enabled:\n\nOLLAMA_ORIGINS=* ollama serve');
            } else {
                throw error;
            }
        }
    }
}

// Initialize the chat application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new OllamaChat();
});

// Add some utility functions for better UX
window.addEventListener('beforeunload', (e) => {
    // Warn user if they're in the middle of a conversation
    const chat = document.querySelector('.message');
    if (chat) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Handle offline/online status
window.addEventListener('online', () => {
    console.log('Connection restored');
});

window.addEventListener('offline', () => {
    console.log('Connection lost');
});
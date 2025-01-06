class ChatApp {
    constructor() {
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.chatMessages = document.getElementById('chat-messages');
        this.toolButtons = document.querySelectorAll('.action-btn');
        this.modelSelect = document.querySelector('select[aria-label="Select AI Model"]');
        this.translateButton = document.querySelector('[data-tool="translate"]');
        
        this.API_URL = 'http://127.0.0.1:8080';
        this.isProcessing = false;
        
        this.setupEventListeners();
        this.testConnection();
    }

    async testConnection() {
        try {
            const response = await fetch(`${this.API_URL}/health`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log('Backend health check:', data);
        } catch (error) {
            console.error('Backend connection failed:', error);
            this.addMessageToChat('Error: Cannot connect to the AI service. Please make sure the backend server is running.', 'system');
        }
    }

    setupEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });

        // Add translate button event listener
        if (this.translateButton) {
            console.log('Adding translate button listener');
            this.translateButton.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('Translate button clicked');
                this.translateText();
            });
        } else {
            console.error('Translate button not found');
        }
    }

    async sendMessage() {
        const content = this.messageInput.value.trim();
        if (!content || this.isProcessing) return;

        this.isProcessing = true;
        this.sendButton.disabled = true;

        // Add user message to chat
        this.addMessageToChat(content, 'user');
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';

        try {
            // Get the selected model and choose endpoint
            const selectedModel = this.modelSelect.value;
            const endpoint = selectedModel === 'kimi' ? '/chat/kimi' : '/chat/gpt4o';

            const response = await fetch(`${this.API_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    role: 'user'
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || `HTTP error! status: ${response.status}`);
            }

            this.addMessageToChat(data.content, 'assistant');
        } catch (error) {
            console.error('Error:', error);
            this.addMessageToChat(`Error: ${error.message}`, 'system');
        } finally {
            this.isProcessing = false;
            this.sendButton.disabled = false;
        }
    }

    async translateText() {
        const content = this.messageInput.value.trim();
        if (!content || this.isProcessing) return;

        this.isProcessing = true;
        this.translateButton.disabled = true;

        try {
            const selectedModel = this.modelSelect.value;
            const response = await fetch(`${this.API_URL}/chat/translate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    role: selectedModel
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Add original text and translation to chat
            this.addMessageToChat(content, 'user');
            // Ensure we're only displaying the translation content
            if (data && typeof data.content === 'string') {
                this.addMessageToChat(data.content.trim(), 'assistant');
            } else {
                throw new Error('Invalid translation response format');
            }
            
            // Clear input after successful translation
            this.messageInput.value = '';
            this.messageInput.style.height = 'auto';

        } catch (error) {
            console.error('Translation Error:', error);
            this.addMessageToChat(`Translation Error: ${error.message}`, 'system');
        } finally {
            this.isProcessing = false;
            this.translateButton.disabled = false;
        }
    }

    addMessageToChat(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        const iconDiv = document.createElement('div');
        iconDiv.className = 'message-icon';
        
        // Set appropriate icon based on role
        if (role === 'user') {
            iconDiv.innerHTML = '<span class="material-icons">person</span>';
        } else if (role === 'assistant') {
            iconDiv.innerHTML = '<span class="material-icons">smart_toy</span>';
        } else {
            iconDiv.innerHTML = '<span class="material-icons">warning</span>';
        }
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Handle markdown or code blocks if present
        if (typeof content === 'string' && content.includes('```')) {
            contentDiv.innerHTML = this.formatCodeBlocks(content);
        } else {
            // Ensure content is treated as plain text
            contentDiv.textContent = content;
        }
        
        // Add elements in the correct order based on role
        if (role === 'user') {
            messageDiv.appendChild(contentDiv);
            messageDiv.appendChild(iconDiv);
        } else {
            messageDiv.appendChild(iconDiv);
            messageDiv.appendChild(contentDiv);
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    formatCodeBlocks(content) {
        const parts = content.split('```');
        let formatted = '';
        parts.forEach((part, index) => {
            if (index % 2 === 0) {
                // Regular text
                formatted += part;
            } else {
                // Code block
                formatted += `<pre><code>${part}</code></pre>`;
            }
        });
        return formatted;
    }
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});

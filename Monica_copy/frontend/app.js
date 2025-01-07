class ChatApp {
    constructor() {
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.chatMessages = document.getElementById('chat-messages');
        this.toolButtons = document.querySelectorAll('.action-btn');
        this.modelSelect = document.querySelector('select[aria-label="Select AI Model"]');
        this.translateButton = document.querySelector('[data-tool="translate"]');
        this.fileInput = document.getElementById('file-input');
        this.attachButton = document.getElementById('attach-button');
        this.knowledgeToggle = document.getElementById('knowledge-toggle');
        
        this.API_URL = 'http://127.0.0.1:8080';
        this.isProcessing = false;
        this.useKnowledgeBase = false;
        
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

        // Add file upload functionality
        if (this.attachButton && this.fileInput) {
            this.attachButton.addEventListener('click', () => {
                this.fileInput.click();
            });

            this.fileInput.addEventListener('change', async (e) => {
                const file = e.target.files[0];
                if (file) {
                    await this.uploadFile(file);
                }
            });
        }

        if (this.knowledgeToggle) {
            this.knowledgeToggle.addEventListener('change', (e) => {
                this.useKnowledgeBase = e.target.checked;
                this.addMessageToChat(`Knowledge base ${this.useKnowledgeBase ? 'enabled' : 'disabled'}`, 'system');
            });
        }
    }

    async sendMessage() {
        if (this.isProcessing) return;

        const message = this.messageInput.value.trim();
        if (!message) return;

        this.isProcessing = true;
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        
        try {
            this.addMessageToChat(message, 'user');
            
            const endpoint = this.useKnowledgeBase ? '/knowledge/query' : `/chat/${this.modelSelect.value}`;
            const response = await fetch(`${this.API_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    content: message,
                    role: this.modelSelect.value 
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.addMessageToChat(data.response || data.content, 'assistant');
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessageToChat(`Error: ${error.message}`, 'system');
        } finally {
            this.isProcessing = false;
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

    async uploadFile(file) {
        try {
            this.addMessageToChat(`Uploading file: ${file.name}...`, 'system');
            
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${this.API_URL}/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.addMessageToChat(`File "${file.name}" has been successfully uploaded and added to the knowledge base. Added ${result.chunks} chunks to the database.`, 'system');
            
            // Clear the file input for next upload
            this.fileInput.value = '';
        } catch (error) {
            console.error('Error uploading file:', error);
            this.addMessageToChat(`Error uploading file: ${error.message}`, 'system');
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

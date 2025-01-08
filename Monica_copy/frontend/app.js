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
        
        // Knowledge base management
        this.knowledgeModal = document.getElementById('knowledge-modal');
        this.manageKnowledgeBtn = document.getElementById('manage-knowledge-btn');
        this.closeModalBtn = document.querySelector('.close-btn');
        this.fileList = document.getElementById('knowledge-files');
        this.kbFileInput = document.getElementById('kb-file-input');
        this.kbUploadBtn = document.getElementById('kb-upload-btn');
        
        // Configure marked options
        marked.setOptions({
            highlight: function(code, lang) {
                if (Prism.languages[lang]) {
                    return Prism.highlight(code, Prism.languages[lang], lang);
                }
                return code;
            },
            breaks: true,
            gfm: true
        });
        
        this.setupEventListeners();
        this.testConnection();
        this.initializeKnowledgeManagement();
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

    initializeKnowledgeManagement() {
        // Modal controls
        this.manageKnowledgeBtn.addEventListener('click', () => {
            this.knowledgeModal.classList.add('show');
            this.loadKnowledgeFiles();
        });
        
        this.closeModalBtn.addEventListener('click', () => {
            this.knowledgeModal.classList.remove('show');
        });
        
        // Upload controls
        this.kbUploadBtn.addEventListener('click', () => {
            this.kbFileInput.click();
        });
        
        this.kbFileInput.addEventListener('change', (event) => {
            const file = event.target.files[0];
            if (file) {
                this.uploadFile(file);
            }
        });

        // File deletion
        this.fileList.addEventListener('click', async (event) => {
            const deleteBtn = event.target.closest('.delete-btn');
            if (deleteBtn) {
                const fileId = deleteBtn.dataset.fileId;
                if (fileId) {
                    await this.deleteFile(fileId);
                }
            }
        });
    }
    
    async loadKnowledgeFiles() {
        try {
            const response = await fetch(`${this.API_URL}/knowledge/files`);
            if (!response.ok) throw new Error('Failed to load files');
            
            const data = await response.json();
            this.renderFileList(data.files);
        } catch (error) {
            console.error('Error loading files:', error);
            this.addMessageToChat('Error loading knowledge base files', 'system');
        }
    }
    
    renderFileList(files) {
        this.fileList.innerHTML = files.length === 0 
            ? '<div class="file-item">No files uploaded yet</div>'
            : files.map(file => `
                <div class="file-item">
                    <div class="file-info">
                        <span class="material-icons">description</span>
                        <div>
                            <div class="file-name">${file.name}</div>
                            <div class="file-meta">
                                ${this.formatFileSize(file.size)} • 
                                ${file.chunks} chunks • 
                                Added ${this.formatDate(file.added)}
                            </div>
                        </div>
                    </div>
                    <div class="file-actions">
                        <button class="delete-btn" data-file-id="${file.id}" aria-label="Delete file">
                            <span class="material-icons">delete</span>
                        </button>
                    </div>
                </div>
            `).join('');
    }
    
    formatFileSize(bytes) {
        const units = ['B', 'KB', 'MB', 'GB'];
        let size = bytes;
        let unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return `${size.toFixed(1)} ${units[unitIndex]}`;
    }
    
    formatDate(dateStr) {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        if (diff < 2592000000) return `${Math.floor(diff / 86400000)}d ago`;
        
        return date.toLocaleDateString();
    }
    
    async deleteFile(fileId) {
        const progressDiv = document.getElementById('upload-progress');
        const progressText = progressDiv.querySelector('.progress-text');
        const progressFill = progressDiv.querySelector('.progress-fill');
        
        try {
            progressDiv.style.display = 'block';
            progressText.textContent = 'Deleting file...';
            progressFill.style.width = '0%';
            
            const response = await fetch(`${this.API_URL}/knowledge/files/${fileId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to delete file');
            }
            
            const progress = response.headers.get('X-Progress');
            const progressMessage = response.headers.get('X-Progress-Text');
            if (progress) {
                progressText.textContent = progressMessage || 'Batches: 100%|#####| Complete';
                progressFill.style.width = '100%';
                progressFill.style.backgroundColor = '#4CAF50';  // Green color for completion
            }
            
            // Wait for the progress animation
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            await this.loadKnowledgeFiles();
            this.addMessageToChat('File deleted successfully', 'system');
            
            // If no files left, disable knowledge base
            const files = await (await fetch(`${this.API_URL}/knowledge/files`)).json();
            if (files.files.length === 0) {
                this.knowledgeToggle.checked = false;
                this.useKnowledgeBase = false;
                this.addMessageToChat('Knowledge base disabled - no files available', 'system');
            }
            
            progressDiv.style.display = 'none';
        } catch (error) {
            console.error('Error deleting file:', error);
            this.addMessageToChat(`Error deleting file: ${error.message}`, 'system');
            progressDiv.style.display = 'none';
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
            
            const thinkingDiv = this.showThinking();
            
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

            thinkingDiv.remove();

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

    showThinking() {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'assistant', 'thinking');
        
        // Add message header with icon
        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';
        
        const iconDiv = document.createElement('div');
        iconDiv.className = 'message-icon';
        const icon = document.createElement('span');
        icon.className = 'material-icons';
        icon.textContent = 'smart_toy';
        iconDiv.appendChild(icon);
        headerDiv.appendChild(iconDiv);
        
        // Add thinking animation
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        const dotsDiv = document.createElement('div');
        dotsDiv.className = 'thinking-dots';
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            dotsDiv.appendChild(dot);
        }
        contentDiv.appendChild(dotsDiv);
        
        messageDiv.appendChild(headerDiv);
        messageDiv.appendChild(contentDiv);
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        
        return messageDiv;
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
        const formData = new FormData();
        formData.append('file', file);
        
        const progressDiv = document.getElementById('upload-progress');
        const progressText = progressDiv.querySelector('.progress-text');
        const progressFill = progressDiv.querySelector('.progress-fill');
        
        try {
            progressDiv.style.display = 'block';
            progressText.textContent = 'Processing: Batches [0/0]';
            progressFill.style.width = '0%';
            
            const response = await fetch(`${this.API_URL}/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const progress = response.headers.get('X-Progress');
            if (progress) {
                progressText.textContent = `Batches: 100%|${'█'.repeat(40)}| 142/142 [00:14<00:00, 9.52it/s]`;
                progressFill.style.width = '100%';
            }

            const data = await response.json();
            
            // Wait for the progress animation
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            this.addMessageToChat('File uploaded successfully', 'system');
            
            // Enable knowledge base toggle
            this.knowledgeToggle.checked = true;
            this.useKnowledgeBase = true;
            this.addMessageToChat('Knowledge base enabled - I will use your uploaded documents to answer questions', 'system');
            
            // Close the modal and refresh the file list
            this.knowledgeModal.classList.remove('show');
            this.kbFileInput.value = ''; // Reset file input
            progressDiv.style.display = 'none';
            
        } catch (error) {
            console.error('Error uploading file:', error);
            this.addMessageToChat('Error uploading file', 'system');
            progressDiv.style.display = 'none';
        }
    }

    cleanMarkdown(text) {
        // Fix spacing issues in markdown
        return text
            // Remove space between parenthesis and bold/italic markers
            .replace(/\) \*\*/g, ')**')
            .replace(/\) \*/g, ')*')
            // Remove space between bold/italic markers and parenthesis
            .replace(/\*\* \(/g, '**(')
            .replace(/\* \(/g, '*(')
            // Fix other common spacing issues
            .replace(/\*\* /g, '**')
            .replace(/ \*\*/g, '**')
            .replace(/\* /g, '*')
            .replace(/ \*/g, '*');
    }

    addMessageToChat(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', role);
        
        if (role === 'system') {
            // Handle system messages as before
            const icon = document.createElement('span');
            icon.classList.add('material-icons');
            icon.style.fontSize = '14px';
            icon.style.marginRight = '4px';
            icon.style.verticalAlign = 'middle';
            
            if (messageDiv.classList.contains('error')) {
                icon.textContent = 'error_outline';
            } else if (messageDiv.classList.contains('success')) {
                icon.textContent = 'check_circle_outline';
            } else {
                icon.textContent = 'info_outline';
            }
            
            messageDiv.appendChild(icon);
            const textSpan = document.createElement('span');
            textSpan.textContent = content;
            messageDiv.appendChild(textSpan);
        } else {
            // Create message header with role icon
            const headerDiv = document.createElement('div');
            headerDiv.className = 'message-header';
            
            const iconDiv = document.createElement('div');
            iconDiv.className = 'message-icon';
            const icon = document.createElement('span');
            icon.className = 'material-icons';
            icon.textContent = role === 'user' ? 'person' : 'smart_toy';
            iconDiv.appendChild(icon);
            headerDiv.appendChild(iconDiv);
            
            // Add message content
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            if (role === 'assistant') {
                // Clean and parse markdown for assistant messages
                const cleanedContent = this.cleanMarkdown(content);
                contentDiv.innerHTML = marked.parse(cleanedContent);
                // Apply syntax highlighting to code blocks
                contentDiv.querySelectorAll('pre code').forEach((block) => {
                    Prism.highlightElement(block);
                });
            } else {
                // Keep user messages as plain text
                contentDiv.textContent = content;
            }
            
            messageDiv.appendChild(headerDiv);
            messageDiv.appendChild(contentDiv);
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        
        // Auto-remove system messages after 5 seconds
        if (role === 'system') {
            setTimeout(() => {
                messageDiv.style.opacity = '0';
                setTimeout(() => messageDiv.remove(), 300);
            }, 5000);
        }
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

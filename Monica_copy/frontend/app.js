class ChatApp {
    constructor() {
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.chatMessages = document.getElementById('chat-messages');
        this.modelSelect = document.querySelector('select[aria-label="Select AI Model"]');
        this.kbToggle = document.getElementById('kb-toggle');
        
        // Knowledge base management
        this.kbModal = document.getElementById('knowledge-modal');
        this.manageKbBtn = document.getElementById('manage-kb-btn');
        this.closeModalBtn = document.querySelector('.close-btn');
        this.fileList = document.getElementById('knowledge-files');
        this.kbFileInput = document.getElementById('kb-file-input');
        this.kbUploadBtn = document.getElementById('kb-upload-btn');
        
        // Initialize state
        this.isProcessing = false;
        this.useKnowledgeBase = false;
        this.API_URL = 'http://127.0.0.1:8080';
        
        // Event listeners
        this.setupEventListeners();
        this.initializeKnowledgeManagement();
    }
    
    setupEventListeners() {
        // Send message on button click
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Send message on Enter (but Shift+Enter for new line)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Knowledge base toggle
        this.kbToggle.addEventListener('change', async (e) => {
            const isChecked = e.target.checked;
            
            if (isChecked) {
                try {
                    const response = await fetch(`${this.API_URL}/knowledge/files`);
                    const data = await response.json();
                    
                    if (!data.files || data.files.length === 0) {
                        e.target.checked = false;
                        this.useKnowledgeBase = false;
                        this.addMessageToChat('Cannot enable knowledge base: No files available. Please upload files first.', 'system');
                        return;
                    }
                    
                    this.useKnowledgeBase = true;
                    this.addMessageToChat('Knowledge base enabled', 'system');
                } catch (error) {
                    console.error('Error checking knowledge base:', error);
                    e.target.checked = false;
                    this.useKnowledgeBase = false;
                    this.addMessageToChat('Error checking knowledge base. Please try again.', 'system');
                }
            } else {
                this.useKnowledgeBase = false;
                this.addMessageToChat('Knowledge base disabled', 'system');
            }
        });
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });
    }
    
    initializeKnowledgeManagement() {
        // Modal controls
        this.manageKbBtn.addEventListener('click', () => {
            this.kbModal.style.display = 'block';
            this.loadKnowledgeFiles();
        });
        
        this.closeModalBtn.addEventListener('click', () => {
            this.kbModal.style.display = 'none';
        });
        
        // File upload
        this.kbUploadBtn.addEventListener('click', () => {
            this.kbFileInput.click();
        });
        
        this.kbFileInput.addEventListener('change', async (e) => {
            const files = Array.from(e.target.files);
            if (files.length > 0) {
                const formData = new FormData();
                files.forEach(file => {
                    formData.append('files', file);
                });
                
                const progressDiv = document.getElementById('upload-progress');
                progressDiv.style.display = 'block';
                progressDiv.textContent = 'Uploading files...';
                
                try {
                    const response = await fetch(`${this.API_URL}/upload`, {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'Upload failed');
                    }
                    
                    const data = await response.json();
                    await this.loadKnowledgeFiles();
                    this.kbToggle.checked = true;
                    this.useKnowledgeBase = true;
                    this.addMessageToChat(`${data.message} (${data.files.map(f => f.filename).join(', ')})`, 'system');
                } catch (error) {
                    console.error('Error uploading files:', error);
                    this.addMessageToChat(`Error uploading files: ${error.message}`, 'system');
                } finally {
                    progressDiv.style.display = 'none';
                    this.kbFileInput.value = '';
                }
            }
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === this.kbModal) {
                this.kbModal.style.display = 'none';
            }
        });
    }
    
    async loadKnowledgeFiles() {
        try {
            const response = await fetch(`${this.API_URL}/knowledge/files`);
            const data = await response.json();
            this.renderFileList(data.files);
        } catch (error) {
            console.error('Error loading files:', error);
            this.addMessageToChat('Error loading knowledge base files', 'system');
        }
    }
    
    renderFileList(files) {
        this.fileList.innerHTML = '';
        
        if (files.length === 0) {
            const emptyMessage = document.createElement('div');
            emptyMessage.className = 'empty-message';
            emptyMessage.textContent = 'No files in knowledge base';
            this.fileList.appendChild(emptyMessage);
            return;
        }
        
        files.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            
            const fileInfo = document.createElement('div');
            fileInfo.className = 'file-info';
            
            const fileName = document.createElement('div');
            fileName.className = 'file-name';
            fileName.textContent = file.name;
            
            const fileDetails = document.createElement('div');
            fileDetails.className = 'file-details';
            fileDetails.textContent = `${this.formatFileSize(file.size)} · ${this.formatDate(file.added)}`;
            
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.innerHTML = '<span class="material-icons">delete</span>';
            deleteBtn.onclick = () => this.deleteFile(file.id);
            
            fileInfo.appendChild(fileName);
            fileInfo.appendChild(fileDetails);
            fileItem.appendChild(fileInfo);
            fileItem.appendChild(deleteBtn);
            
            this.fileList.appendChild(fileItem);
        });
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
        return date.toLocaleDateString();
    }
    
    async deleteFile(fileId) {
        const progressDiv = document.getElementById('upload-progress');
        progressDiv.style.display = 'block';
        
        try {
            const response = await fetch(`${this.API_URL}/knowledge/delete/${fileId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete file');
            }
            
            await this.loadKnowledgeFiles();
            this.addMessageToChat('File deleted successfully', 'system');
            
            // If no files left, disable knowledge base
            const files = await (await fetch(`${this.API_URL}/knowledge/files`)).json();
            if (files.files.length === 0) {
                this.kbToggle.checked = false;
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
            
            // Always use knowledge query when toggle is enabled, otherwise use model-specific endpoint
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
                const data = await response.json();
                throw new Error(data.content || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.addMessageToChat(data.content || data.response, 'assistant');
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessageToChat(`Error: ${error.message}`, 'system');
        } finally {
            this.isProcessing = false;
        }
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

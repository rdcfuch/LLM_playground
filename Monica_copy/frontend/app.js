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
        
        // Set accepted file types
        this.kbFileInput.accept = '.txt';
        
        // Initialize state
        this.isProcessing = false;
        this.useKnowledgeBase = false;
        this.API_URL = 'http://127.0.0.1:8080';
        this.webEnabled = false;
        
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
        this.messageInput.addEventListener('keypress', (e) => {
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
        
        // Initialize web search toggle
        const webToggle = document.querySelector('#web-toggle input[type="checkbox"]');
        if (webToggle) {
            webToggle.addEventListener('change', (e) => {
                e.stopPropagation(); // Prevent event from bubbling to parent button
                this.webEnabled = e.target.checked;
            });
        }
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });
        
        // Initialize toggle switch
        const toggleSwitch = document.querySelector('.toggle-switch');
        if (toggleSwitch) {
            toggleSwitch.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent event from bubbling to parent button
                toggleSwitch.classList.toggle('active');
                this.webEnabled = !this.webEnabled;
            });
        }
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
                    
                    // Show success message with file names
                    const fileNames = data.files.map(f => f.name || f.filename).join(', ');
                    this.addMessageToChat(`Successfully uploaded: ${fileNames}`, 'system');
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
        
        if (!files || files.length === 0) {
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
            
            const fileTypeIcon = document.createElement('span');
            fileTypeIcon.className = 'material-icons file-type-icon';
            fileTypeIcon.textContent = 'description';  // Text file icon
            
            const fileName = document.createElement('div');
            fileName.className = 'file-name';
            fileName.textContent = file.name || 'Unnamed file';
            
            const fileDetails = document.createElement('div');
            fileDetails.className = 'file-details';
            const details = [];
            if (file.size) details.push(this.formatFileSize(file.size));
            if (file.added) details.push(this.formatDate(file.added));
            if (file.type) details.push(file.type.toUpperCase());
            if (file.chunks) details.push(`${file.chunks} chunks`);
            fileDetails.textContent = details.join(' · ');
            
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.innerHTML = '<span class="material-icons">delete</span>';
            deleteBtn.onclick = () => this.deleteFile(file.id);
            
            fileInfo.appendChild(fileTypeIcon);
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
            const response = await fetch(`${this.API_URL}/knowledge/files/${fileId}`, {
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
            this.addMessageToChat(data.content, 'assistant', data.sources);
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

    addMessageToChat(message, role, sources = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        // Create message content div
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Add message text with markdown rendering
        const textDiv = document.createElement('div');
        if (role === 'assistant') {
            // Clean and render markdown for assistant messages
            const cleanedMessage = this.cleanMarkdown(message);
            textDiv.innerHTML = marked.parse(cleanedMessage, {
                breaks: true,
                gfm: true,
                sanitize: false
            });
        } else {
            // For user and system messages, just use plain text
            textDiv.textContent = message;
        }
        contentDiv.appendChild(textDiv);
        
        // If there are sources, add them inside content div
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'message-sources';
            sourcesDiv.innerHTML = '<h4>Sources:</h4>';
            
            const sourcesList = document.createElement('ol');
            sources.forEach(source => {
                const sourceItem = document.createElement('li');
                sourceItem.innerHTML = `<strong>${source.source}</strong>: ${source.text}`;
                sourcesList.appendChild(sourceItem);
            });
            
            sourcesDiv.appendChild(sourcesList);
            contentDiv.appendChild(sourcesDiv);
        }
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;

        // Apply syntax highlighting to code blocks
        if (role === 'assistant') {
            messageDiv.querySelectorAll('pre code').forEach((block) => {
                Prism.highlightElement(block);
            });
        }
    }

    cleanMarkdown(text) {
        return text
            // Remove extra spaces around markdown syntax
            .replace(/\s*([*_~`])\s*/g, '$1')
            // Fix list formatting
            .replace(/^\s*[-*+]\s+/gm, '- ')
            .replace(/^\s*(\d+\.)\s+/gm, '$1 ')
            // Fix heading formatting
            .replace(/^\s*(#{1,6})\s+/gm, '$1 ')
            // Fix blockquote formatting
            .replace(/^\s*>\s+/gm, '> ')
            // Fix code block formatting
            .replace(/```(\w*)\s+/g, '```$1\n')
            .replace(/\s+```/g, '\n```')
            // Fix inline code formatting
            .replace(/`\s+/g, '`')
            .replace(/\s+`/g, '`')
            // Fix link and image formatting
            .replace(/\[\s+/g, '[')
            .replace(/\s+\]/g, ']')
            .replace(/\(\s+/g, '(')
            .replace(/\s+\)/g, ')');
    }
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});

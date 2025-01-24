import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [deleteStatus, setDeleteStatus] = useState('');
  const [chunks, setChunks] = useState([]);
  const [showChunks, setShowChunks] = useState(false);
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchFiles();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchFiles = async () => {
    try {
      const response = await axios.get('http://localhost:8000/files');
      if (response.data.success) {
        setFiles(response.data.files);
      }
    } catch (error) {
      console.error('Error fetching files:', error);
    }
  };

  const handleFileSelect = (event) => {
    setSelectedFile(event.target.files[0]);
    setUploadStatus('');
    setChunks([]);
    setShowChunks(false);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('Please select a file first');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);
    setIsUploading(true);
    setChunks([]);

    try {
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setUploadStatus('File uploaded successfully!');
        setSelectedFile(null);
        // Reset file input
        document.getElementById('fileInput').value = '';
        // Refresh file list
        fetchFiles();
        // Set chunks and show them
        setChunks(response.data.chunks || []);
        setShowChunks(true);
      } else {
        setUploadStatus(`Upload failed: ${response.data.message}`);
      }
    } catch (error) {
      setUploadStatus(`Error uploading file: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (filename) => {
    try {
      const response = await axios.delete(`http://localhost:8000/files/${filename}`);
      if (response.data.success) {
        setDeleteStatus(`File ${filename} deleted successfully`);
        // Refresh the file list
        fetchFiles();
        // Clear chunks if showing for this file
        setChunks([]);
        setShowChunks(false);
        // Clear the status message after 3 seconds
        setTimeout(() => setDeleteStatus(''), 3000);
      }
    } catch (error) {
      setDeleteStatus(`Error deleting file: ${error.message}`);
      setTimeout(() => setDeleteStatus(''), 3000);
    }
  };

  const handleQuery = async (query) => {
    try {
      setMessages([...messages, { role: 'user', content: query }]);
      setIsQuerying(true);
      
      const response = await axios.post('http://localhost:8000/query', { query });
      const data = response.data;
      
      if (data.findings) {
        // Format findings into a readable message
        const findingsText = Object.entries(data.findings)
          .map(([topic, items]) => `${topic}:\n${items.join('\n')}`)
          .join('\n\n');
        
        // Format evidence if available
        const evidenceText = data.evidence && data.evidence.length > 0 
          ? '\n\nEvidence:\n' + data.evidence.join('\n')
          : '';
          
        // Format recommendations if available
        const recommendationsText = data.recommendations && data.recommendations.length > 0
          ? '\n\nRecommendations:\n' + data.recommendations.join('\n')
          : '';
          
        // Format limitations if available
        const limitationsText = data.limitations && data.limitations.length > 0
          ? '\n\nLimitations:\n' + data.limitations.join('\n')
          : '';
        
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: findingsText + evidenceText + recommendationsText + limitationsText,
          confidence: data.confidence,
          reflection: data.reflection,
          findings: data.findings,
          evidence: data.evidence,
          recommendations: data.recommendations,
          limitations: data.limitations
        }]);
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: "I couldn't find any relevant information.",
          confidence: 0
        }]);
      }
    } catch (error) {
      console.error('Error querying:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, there was an error processing your query.',
        error: true
      }]);
    } finally {
      setIsQuerying(false);
    }
  };

  const handleMessageSubmit = async (e) => {
    e.preventDefault();
    if (!currentMessage.trim() || isQuerying) return;

    await handleQuery(currentMessage);
    setCurrentMessage('');
  };

  const Message = ({ message }) => {
    const [showJson, setShowJson] = useState(false);
    
    return (
      <div className={`message ${message.role} ${message.error ? 'error' : ''}`}>
        <div className="message-content">
          {message.content}
          {message.confidence !== undefined && (
            <div className="message-confidence">
              Confidence: {(message.confidence * 100).toFixed(1)}%
            </div>
          )}
          {message.reflection && (
            <div className="message-reflection">
              <h4>Analysis Process:</h4>
              <p><strong>Understanding:</strong> {message.reflection.understanding}</p>
              <p><strong>Search Strategy:</strong> {message.reflection.search_strategy}</p>
              {message.reflection.needs_clarification && (
                <div>
                  <p><strong>Clarification Needed:</strong></p>
                  <ul>
                    {message.reflection.follow_up_questions.map((q, i) => (
                      <li key={i}>{q}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
          {message.role === 'assistant' && (
            <div className="message-json">
              <button 
                className="json-toggle"
                onClick={() => setShowJson(!showJson)}
              >
                {showJson ? 'Hide JSON' : 'Show JSON'}
              </button>
              {showJson && (
                <pre className="json-view">
                  <code>
                    {JSON.stringify({
                      reflection: message.reflection,
                      findings: message.findings,
                      evidence: message.evidence,
                      confidence: message.confidence,
                      recommendations: message.recommendations,
                      limitations: message.limitations
                    }, null, 2)}
                  </code>
                </pre>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="App">
      <header className="App-header">
        <h3>Knowledge Base Manager</h3>
      </header>
      
      <div className="app-container">
        <div className="chat-sidebar">
          <section className="upload-section">
            <h2>Upload File</h2>
            <div className="upload-container">
              <input
                type="file"
                id="fileInput"
                onChange={handleFileSelect}
                accept=".txt,.pdf"
                disabled={isUploading}
              />
              <button 
                onClick={handleUpload}
                disabled={!selectedFile || isUploading}
                className={isUploading ? 'uploading' : ''}
              >
                {isUploading ? 'Uploading...' : 'Upload'}
              </button>
            </div>
            {uploadStatus && (
              <div className={`status ${uploadStatus.includes('successfully') ? 'success' : 'error'}`}>
                {uploadStatus}
              </div>
            )}
          </section>

          <section className="files-section">
            <h2>Files in Knowledge Base</h2>
            {deleteStatus && (
              <div className={`status ${deleteStatus.includes('successfully') ? 'success' : 'error'}`}>
                {deleteStatus}
              </div>
            )}
            {files.length > 0 ? (
              <ul className="file-list">
                {files.map((file, index) => (
                  <li key={index} className="file-item">
                    <span className="file-name">{file}</span>
                    <button 
                      onClick={() => handleDelete(file)}
                      className="delete-button"
                      title="Delete file"
                    >
                      Delete
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="no-files">No files in the knowledge base</p>
            )}
          </section>

          {showChunks && chunks.length > 0 && (
            <section className="chunks-section">
              <h2>File Chunks</h2>
              <div className="chunks-info">
                <p>Total Chunks: {chunks.length}</p>
              </div>
              <ul className="chunks-list">
                {chunks.map((chunk) => (
                  <li key={chunk.id} className="chunk-item">
                    <div className="chunk-header">
                      <span className="chunk-id">Chunk {chunk.id}</span>
                      {chunk.metadata && (
                        <span className="chunk-metadata">
                          {Object.entries(chunk.metadata).map(([key, value]) => (
                            <span key={key} className="metadata-item">
                              {key}: {value}
                            </span>
                          ))}
                        </span>
                      )}
                    </div>
                    <pre className="chunk-text">{chunk.text}</pre>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>

        <div className="main-content">
          <main>
            <div className="messages-container">
              {messages.map((message, index) => (
                <Message key={index} message={message} />
              ))}
              <div ref={messagesEndRef} />
            </div>
            
            <form onSubmit={handleMessageSubmit} className="message-form">
              <input
                type="text"
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                placeholder="Ask a question..."
                disabled={isQuerying}
              />
              <button type="submit" disabled={isQuerying || !currentMessage.trim()}>
                {isQuerying ? 'Thinking...' : 'Ask'}
              </button>
            </form>
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;

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
    // Scroll to top on initial load
    window.scrollTo(0, 0);
  }, []);

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
      const response = await axios.get('/files');
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
    setUploadStatus('Uploading...');

    try {
      const response = await axios.post('/upload', formData, {
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
        setUploadStatus('Upload failed: ' + response.data.message);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadStatus('Error uploading file: ' + error.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (filename) => {
    try {
      const response = await axios.delete(`/files/${filename}`);
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


  const handleQueryResponse = async (response) => {
    try {
      const data = await response.json();
      if (data.success) {
        // Parse and decode any Chinese characters in the response
        const decodedData = JSON.parse(JSON.stringify(data), (key, value) => {
          if (typeof value === 'string') {
            try {
              // Try to decode any encoded Unicode characters
              return decodeURIComponent(JSON.parse('"' + value.replace(/"/g, '\\"') + '"'));
            } catch (e) {
              return value;
            }
          }
          return value;
        });
        
        setMessages(prevMessages => [
          ...prevMessages,
          {
            type: 'assistant',
            content: decodedData.response,
            reflection: decodedData.reflection,
            confidence: decodedData.confidence,
            findings: decodedData.findings,
            evidence: decodedData.evidence,
            recommendations: decodedData.recommendations,
            limitations: decodedData.limitations
          }
        ]);
      } else {
        setMessages(prevMessages => [
          ...prevMessages,
          {
            type: 'assistant',
            content: data.message || 'An error occurred'
          }
        ]);
      }
    } catch (error) {
      console.error('Error processing response:', error);
      setMessages(prevMessages => [
        ...prevMessages,
        {
          type: 'assistant',
          content: 'Error processing response'
        }
      ]);
    }
    setIsQuerying(false);
  };

  const handleMessageSubmit = async (e) => {
    e.preventDefault();
    if (!currentMessage.trim()) return;

    // Add user message immediately
    setMessages(prevMessages => [
      ...prevMessages,
      { type: 'user', content: currentMessage }
    ]);
    
    setCurrentMessage('');
    setIsQuerying(true);

    try {
      const response = await axios.post('/query', {
        query: currentMessage
      });

      if (response.data.success) {
        // Add the response message
        setMessages(prevMessages => [
          ...prevMessages,
          {
            type: 'assistant',
            content: response.data.answer,
            reflection: response.data.reflection,
            confidence: response.data.confidence,
            documents: response.data.documents
          }
        ]);
      } else {
        throw new Error(response.data.message || 'Error processing query');
      }
    } catch (error) {
      console.error('Error querying:', error);
      setMessages(prevMessages => [
        ...prevMessages,
        {
          type: 'error',
          content: error.message || 'Error processing query'
        }
      ]);
    } finally {
      setIsQuerying(false);
    }
  };

  const renderMessage = (message, index) => {
    const renderAnswer = (answer) => {
      if (typeof answer === 'string') {
        return <p>{answer}</p>;
      }
      
      // Handle structured answer (dictionary)
      return Object.entries(answer).map(([key, value], i) => {
        const formattedKey = key.split('_').map(word => 
          word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
        
        const formattedValue = Array.isArray(value) ? value.join('\n') : value;
        
        return (
          <div key={i} className="answer-section">
            <strong>{formattedKey}:</strong> {formattedValue}
          </div>
        );
      });
    };

    switch (message.type) {
      case 'user':
        return (
          <div key={index} className="message user-message">
            <div className="message-content">{message.content}</div>
          </div>
        );
      case 'assistant':
        return (
          <div key={index} className="message assistant-message">
            <div className="message-content">
              <div className="answer-content">
                {renderAnswer(message.content)}
              </div>
              {message.reflection && (
                <div className="message-reflection">
                  <h4>Analysis:</h4>
                  <p><strong>Understanding:</strong> {message.reflection.understanding}</p>
                  <p><strong>Confidence:</strong> {(message.reflection.confidence * 100).toFixed(1)}%</p>
                  {message.reflection.needs_clarification && (
                    <div>
                      <p><strong>Follow-up Questions:</strong></p>
                      <ul>
                        {message.reflection.follow_up_questions.map((q, i) => (
                          <li key={i}>{q}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
            {message.documents && message.documents.length > 0 && (
              <div className="source-documents">
                <h4>Source Documents:</h4>
                {message.documents.map((doc, docIndex) => (
                  <div key={docIndex} className="document">
                    <div className="document-text">{doc.text}</div>
                    {doc.metadata && (
                      <div className="document-metadata">
                        <small>Source: {doc.metadata.file_name}</small>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      case 'error':
        return (
          <div key={index} className="message error-message">
            <div className="message-content">Error: {message.content}</div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="App">
      <style>
        {`
          .app-container {
            display: flex;
            height: calc(100vh - 60px);
            overflow: hidden;
          }

          .chat-sidebar {
            width: 300px;
            min-width: 300px;
            flex-shrink: 0;
            background: white;
            border-right: 1px solid #e2e8f0;
            overflow-y: auto;
            padding: 20px;
            height: 100%;
            box-sizing: border-box;
          }

          .main-content {
            flex: 1;
            overflow: hidden;
            display: flex;
            flex-direction: column;
          }

          main {
            flex: 1;
            overflow-y: auto;
            background: #f8fafc;
            position: relative;
          }

          .messages-container {
            padding: 20px;
            width: 100%;
            box-sizing: border-box;
          }

          .message {
            margin: 20px 0;
            display: flex;
            flex-direction: column;
            max-width: 100%;
          }

          .message-content {
            max-width: 80%;
            padding: 15px;
            border-radius: 15px;
            position: relative;
          }

          .user-message {
            align-items: flex-end;
          }

          .assistant-message {
            align-items: flex-start;
          }

          .user-message .message-content {
            background: #2b6cb0;
            color: white;
            border-bottom-right-radius: 5px;
          }

          .assistant-message .message-content {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-bottom-left-radius: 5px;
          }

          .answer-section {
            margin: 10px 0;
            padding: 5px 0;
            border-bottom: 1px solid #eee;
          }
          
          .answer-section:last-child {
            border-bottom: none;
          }
          
          .answer-section strong {
            color: #2c5282;
            margin-right: 8px;
          }
          
          .answer-content {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
          }
          
          .message-reflection {
            background: #ebf8ff;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
          }
          
          .message-reflection h4 {
            margin-top: 0;
            color: #2b6cb0;
          }
          
          .source-documents {
            margin-top: 20px;
            padding: 15px;
            background: #f0fff4;
            border-radius: 8px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
          }
          
          .source-documents h4 {
            margin-top: 0;
            color: #2f855a;
          }
          
          .document {
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 4px;
            border: 1px solid #e2e8f0;
          }
          
          .document-metadata {
            margin-top: 5px;
            color: #718096;
          }

          .user-message .message-content strong {
            color: #bee3f8;
          }

          .upload-section {
            margin-bottom: 20px;
          }

          .upload-section h2 {
            margin: 0 0 15px 0;
            font-size: 1.2em;
            color: #2d3748;
          }

          .upload-container {
            display: flex;
            flex-direction: column;
            gap: 10px;
            width: 100%;
          }

          .upload-container input[type="file"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            background: #f7fafc;
            box-sizing: border-box;
          }

          .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            margin-bottom: 8px;
            width: 100%;
            box-sizing: border-box;
          }

          .file-name {
            flex: 1;
            min-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            padding-right: 10px;
            font-size: 0.9em;
            color: #4a5568;
          }

          .delete-button {
            flex-shrink: 0;
            padding: 4px 8px;
            background: #e53e3e;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 0.8em;
            cursor: pointer;
            transition: background-color 0.2s;
            min-width: 60px;
            white-space: nowrap;
          }

          .status {
            margin-top: 10px;
            padding: 8px;
            border-radius: 4px;
            font-size: 0.9em;
          }

          .status.success {
            background: #c6f6d5;
            color: #2f855a;
          }

          .status.error {
            background: #fed7d7;
            color: #c53030;
          }

          .chunks-section {
            margin-top: 20px;
            border-top: 1px solid #e2e8f0;
            padding-top: 20px;
          }

          .chunks-info {
            margin-bottom: 10px;
            color: #4a5568;
            font-size: 0.9em;
          }

          .chunk-item {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            margin-bottom: 10px;
            padding: 10px;
          }

          .chunk-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 0.9em;
            color: #4a5568;
          }

          .chunk-text {
            font-size: 0.85em;
            white-space: pre-wrap;
            word-break: break-word;
            margin: 0;
            color: #2d3748;
            max-height: 100px;
            overflow-y: auto;
          }
        `}
      </style>
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
                className={`upload-button ${isUploading ? 'uploading' : ''}`}
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
              {messages.map((message, index) => renderMessage(message, index))}
              <div ref={messagesEndRef} />
            </div>
          </main>
        </div>
      </div>
      <div className="input-container">
        <form onSubmit={handleMessageSubmit} className="input-form">
          <input
            type="text"
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            placeholder="Type your question..."
            disabled={isQuerying}
            className="message-input"
          />
          <button type="submit" disabled={isQuerying} className="send-button">
            {isQuerying ? 'Processing...' : 'Send'}
          </button>
        </form>
      </div>
      <style>
        {`
          .input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            padding: 20px;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
          }

          .input-form {
            max-width: 800px;
            margin: 0 auto;
            display: flex;
            gap: 10px;
          }

          .message-input {
            flex: 1;
            padding: 12px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.2s;
          }

          .message-input:focus {
            border-color: #2b6cb0;
          }

          .send-button {
            padding: 12px 24px;
            background: #2b6cb0;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.2s;
          }

          .send-button:hover {
            background: #2c5282;
          }

          .send-button:disabled {
            background: #718096;
            cursor: not-allowed;
          }

          .App {
            padding-bottom: 100px;
          }
        `}
      </style>
    </div>
  );
}

export default App;

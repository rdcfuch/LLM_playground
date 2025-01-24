import React, { useState, useEffect } from 'react';
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

  useEffect(() => {
    fetchFiles();
  }, []);

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

  return (
    <div className="App">
      <header className="App-header">
        <h1>Knowledge Base Manager</h1>
      </header>
      
      <main>
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
      </main>
    </div>
  );
}

export default App;

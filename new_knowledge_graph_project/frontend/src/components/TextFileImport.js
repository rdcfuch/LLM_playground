import React, { useState, useEffect } from 'react';
import { Form, Button, Card, Alert, Spinner } from 'react-bootstrap';
import axios from 'axios';

const TextFileImport = ({ onDataImported }) => {
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [apiKeyStatus, setApiKeyStatus] = useState('');
  const [debugInfo, setDebugInfo] = useState(null);

  // Load API key from localStorage when component mounts
  useEffect(() => {
    const storedKey = localStorage.getItem('openai_api_key');
    if (storedKey) {
      setApiKey(storedKey);
      // Create a masked version of the API key for display
      const maskedKey = storedKey.substring(0, 3) + '...' + storedKey.substring(storedKey.length - 4);
      setApiKeyStatus(`API Key loaded: ${maskedKey}`);
    } else {
      setApiKeyStatus('No API Key found in localStorage');
    }
  }, []);

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    
    // Read file content
    if (selectedFile) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setText(event.target.result);
      };
      reader.readAsText(selectedFile);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!text) {
      setError('Please enter or upload text to parse');
      return;
    }
    
    // Check for API key again in case it was updated
    const currentApiKey = localStorage.getItem('openai_api_key') || apiKey;
    
    if (!currentApiKey) {
      setError('API key is required. Please set it in the home page.');
      return;
    }
    
    setLoading(true);
    setError(null);
    setResult(null);
    setDebugInfo(null);
    
    try {
      // Debug info - log the request details
      const requestInfo = {
        url: 'http://localhost:5001/api/parse-unstructured', // Use the full URL with correct port
        apiKeyLength: currentApiKey.length,
        textLength: text.length
      };
      console.log('Request details:', requestInfo);
      setDebugInfo(requestInfo);
      
      const response = await axios.post('http://localhost:5001/api/parse-unstructured', 
        { text },
        { 
          headers: { 'X-API-KEY': currentApiKey },
          timeout: 30000 // Increase timeout to 30 seconds
        }
      );
      
      console.log('Response received:', response.status);
      setResult(response.data);
      
      // Call the onDataImported prop with the parsed data
      if (response.data.status === 'success' && onDataImported) {
        onDataImported(response.data.parsed_data);
      }
      
    } catch (error) {
      console.error('Error details:', error);
      
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error('Response data:', error.response.data);
        console.error('Response status:', error.response.status);
        setError(`Server error: ${error.response.status} - ${error.response.data?.message || 'Unknown error'}`);
        setDebugInfo({
          errorType: 'Response error',
          status: error.response.status,
          data: error.response.data,
          headers: error.response.headers
        });
      } else if (error.request) {
        // The request was made but no response was received
        console.error('No response received:', error.request);
        setError('No response from server. Please check your network connection and ensure the backend is running.');
        setDebugInfo({
          errorType: 'Request error',
          request: {
            method: 'POST',
            url: 'http://localhost:5001/api/parse-unstructured'
          }
        });
      } else {
        // Something happened in setting up the request that triggered an Error
        console.error('Request setup error:', error.message);
        setError(`Error: ${error.message}`);
        setDebugInfo({
          errorType: 'Setup error',
          message: error.message
        });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <p>Import unstructured text and convert it to structured knowledge graph data.</p>
      
      {/* Display API Key Status */}
      <Alert variant="info" className="mb-3">
        <strong>API Key Status:</strong> {apiKeyStatus}
      </Alert>
      
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Label>Upload Text File</Form.Label>
          <Form.Control 
            type="file" 
            accept=".txt"
            onChange={handleFileChange}
          />
        </Form.Group>
        
        <Form.Group className="mb-3">
          <Form.Label>Or Enter Text Directly</Form.Label>
          <Form.Control 
            as="textarea" 
            rows={10} 
            placeholder="Enter text to parse..."
            value={text}
            onChange={handleTextChange}
          />
        </Form.Group>
        
        <Button 
          variant="primary" 
          type="submit"
          disabled={loading || !text || !apiKey}
        >
          {loading ? (
            <>
              <Spinner
                as="span"
                animation="border"
                size="sm"
                role="status"
                aria-hidden="true"
              />
              {' '}Processing...
            </>
          ) : 'Parse Text'}
        </Button>
        {!apiKey && (
          <Form.Text className="text-danger">
            API key is required. Please set it in the home page.
          </Form.Text>
        )}
      </Form>
      
      {error && (
        <Alert variant="danger" className="mt-3">
          {error}
          {debugInfo && (
            <div className="mt-2">
              <strong>Debug Info:</strong>
              <pre style={{ fontSize: '0.8rem' }}>
                {JSON.stringify(debugInfo, null, 2)}
              </pre>
            </div>
          )}
        </Alert>
      )}
      
      {result && result.status === 'success' && (
        <Card className="mt-4">
          <Card.Header>Parsed Data</Card.Header>
          <Card.Body>
            <pre style={{ maxHeight: '300px', overflow: 'auto' }}>
              {JSON.stringify(result.parsed_data, null, 2)}
            </pre>
          </Card.Body>
        </Card>
      )}
    </div>
  );
};

export default TextFileImport;
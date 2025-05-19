import React, { useState, useEffect } from 'react';
import { Form, Button, Modal, Alert } from 'react-bootstrap';
import { NEO4J_CONFIG } from '../config';

const ApiKeyConfig = ({ show, onHide, onSave }) => {
  const [apiKey, setApiKey] = useState('');
  const [savedKey, setSavedKey] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    // Load API key from localStorage when component mounts
    const storedKey = localStorage.getItem('openai_api_key');
    if (storedKey) {
      setSavedKey(storedKey);
      setApiKey(storedKey);
    }
  }, []);

  const handleSave = () => {
    try {
      // Save API key to localStorage
      localStorage.setItem('openai_api_key', apiKey);
      setSavedKey(apiKey);
      
      // Call the onSave callback with the API key
      if (onSave) {
        onSave(apiKey);
      }
      
      setSuccess('API key saved successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to save API key: ' + err.message);
    }
  };

  const handleClear = () => {
    localStorage.removeItem('openai_api_key');
    setApiKey('');
    setSavedKey('');
    setSuccess('API key cleared');
    setTimeout(() => setSuccess(null), 3000);
  };

  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>API Configuration</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {error && (
          <Alert variant="danger" dismissible onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert variant="success" dismissible onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}
        
        <p>
          Enter your OpenAI API key to enable LLM-powered features like unstructured data parsing.
          Your API key is stored locally in your browser and is never sent to our servers.
        </p>
        
        <div className="mb-3">
          <h6>Neo4j Connection Information</h6>
          <p className="text-muted">
            The application is configured to connect to Neo4j at:
            <code>{NEO4J_CONFIG.uri}</code> with user <code>{NEO4J_CONFIG.user}</code>
          </p>
        </div>
        
        <Form.Group className="mb-3">
          <Form.Label>OpenAI API Key</Form.Label>
          <Form.Control
            type="password"
            placeholder="sk-..."
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
          <Form.Text className="text-muted">
            {savedKey ? 'An API key is currently saved.' : 'No API key is currently saved.'}
          </Form.Text>
        </Form.Group>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClear}>
          Clear Key
        </Button>
        <Button variant="primary" onClick={handleSave} disabled={!apiKey}>
          Save Key
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ApiKeyConfig;
import React, { useState } from 'react';
import { Form, Button, Card, Alert, Spinner } from 'react-bootstrap';
import axios from 'axios';

const JsonLdImport = () => {
  const [jsonLd, setJsonLd] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleJsonLdChange = (e) => {
    setJsonLd(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!jsonLd) {
      setError('Please enter JSON-LD data');
      return;
    }
    
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      // Parse the JSON-LD to validate it
      let parsedJsonLd;
      try {
        parsedJsonLd = JSON.parse(jsonLd);
      } catch (parseError) {
        throw new Error('Invalid JSON-LD format: ' + parseError.message);
      }
      
      // Send the JSON-LD data to the backend
      const response = await axios.post('/api/import-jsonld', 
        { jsonLd: parsedJsonLd },
        { timeout: 30000 } // 30 second timeout
      );
      
      console.log('Response received:', response.status);
      setResult(response.data);
      
    } catch (error) {
      console.error('Error importing JSON-LD:', error);
      
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error('Response data:', error.response.data);
        console.error('Response status:', error.response.status);
        setError(`Server error: ${error.response.status} - ${error.response.data?.message || 'Unknown error'}`);
      } else if (error.request) {
        // The request was made but no response was received
        console.error('No response received:', error.request);
        setError('No response from server. Please check your network connection and ensure the backend is running.');
      } else {
        // Something happened in setting up the request that triggered an Error
        console.error('Request setup error:', error.message);
        setError(`Error: ${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <p>Import JSON-LD data directly into your knowledge graph.</p>
      
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Label>Enter JSON-LD Data</Form.Label>
          <Form.Control 
            as="textarea" 
            rows={15} 
            placeholder="Paste your JSON-LD data here..."
            value={jsonLd}
            onChange={handleJsonLdChange}
            style={{ fontFamily: 'monospace' }}
          />
          <Form.Text className="text-muted">
            Enter valid JSON-LD data to import directly into the Neo4j database.
          </Form.Text>
        </Form.Group>
        
        <Button 
          variant="primary" 
          type="submit"
          disabled={loading || !jsonLd}
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
              {' '}Importing...
            </>
          ) : 'Import JSON-LD'}
        </Button>
      </Form>
      
      {error && (
        <Alert variant="danger" className="mt-3">
          {error}
        </Alert>
      )}
      
      {result && (
        <Card className="mt-4">
          <Card.Header>Import Result</Card.Header>
          <Card.Body>
            <pre style={{ maxHeight: '300px', overflow: 'auto' }}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </Card.Body>
        </Card>
      )}
    </div>
  );
};

export default JsonLdImport;
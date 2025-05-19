import React, { useState, useEffect } from 'react';
import { Form, Button, Container, Row, Col, Card, Alert } from 'react-bootstrap';
import { NEO4J_CONFIG } from '../config';

const QueryInterface = () => {
  const [queryType, setQueryType] = useState('cypher');
  const [queryText, setQueryText] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [neo4jCredentials, setNeo4jCredentials] = useState({
    username: '',
    password: ''
  });
  const [showCredentials, setShowCredentials] = useState(false);

  // Load credentials from localStorage if available or from config
  useEffect(() => {
    const storedUsername = localStorage.getItem('neo4j_username');
    const storedPassword = localStorage.getItem('neo4j_password');
    
    if (storedUsername && storedPassword) {
      setNeo4jCredentials({
        username: storedUsername,
        password: storedPassword
      });
    } else if (NEO4J_CONFIG && NEO4J_CONFIG.user) {
      // Use credentials from config if available
      setNeo4jCredentials({
        username: NEO4J_CONFIG.user,
        password: NEO4J_CONFIG.password || '' // Handle case where password might not be in config
      });
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // Save credentials to localStorage
      localStorage.setItem('neo4j_username', neo4jCredentials.username);
      localStorage.setItem('neo4j_password', neo4jCredentials.password);
      
      const response = await fetch('http://localhost:5001/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: queryType,
          query: queryText,
          auth: {
            username: neo4jCredentials.username,
            password: neo4jCredentials.password
          }
        }),
      });
      
      const data = await response.json();
      
      if (data.status === 'error') {
        setError(data.message);
      } else {
        setResults(data.results);
      }
    } catch (err) {
      setError('Failed to execute query: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Check if credentials are available either from local state or config
  const hasCredentials = () => {
    return (
      (neo4jCredentials.username && neo4jCredentials.password) || 
      (NEO4J_CONFIG && NEO4J_CONFIG.user)
    );
  };

  return (
    <Container>
      <h2>Query Knowledge Graph</h2>
      <p className="lead">
        Query your knowledge graph using Cypher or SPARQL queries.
      </p>
      
      <Button 
        variant="outline-secondary" 
        className="mb-3"
        onClick={() => setShowCredentials(!showCredentials)}
      >
        {showCredentials ? 'Hide Neo4j Credentials' : 'Configure Neo4j Credentials'}
      </Button>
      
      {showCredentials && (
        <Card className="mb-4">
          <Card.Body>
            <Card.Title>Neo4j Database Credentials</Card.Title>
            <Form.Group className="mb-3">
              <Form.Label>Username</Form.Label>
              <Form.Control
                type="text"
                value={neo4jCredentials.username}
                onChange={(e) => setNeo4jCredentials({...neo4jCredentials, username: e.target.value})}
                placeholder="neo4j"
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Password</Form.Label>
              <Form.Control
                type="password"
                value={neo4jCredentials.password}
                onChange={(e) => setNeo4jCredentials({...neo4jCredentials, password: e.target.value})}
                placeholder="Enter your Neo4j password"
              />
            </Form.Group>
            <Form.Text className="text-muted">
              Credentials are stored in your browser's local storage.
              {NEO4J_CONFIG && NEO4J_CONFIG.user && 
                ` Default credentials from config are available (${NEO4J_CONFIG.user}).`}
            </Form.Text>
          </Card.Body>
        </Card>
      )}
      
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Label>Query Type</Form.Label>
          <Form.Select 
            value={queryType} 
            onChange={(e) => setQueryType(e.target.value)}
          >
            <option value="cypher">Cypher</option>
            <option value="sparql">SPARQL</option>
          </Form.Select>
        </Form.Group>
        
        <Form.Group className="mb-3">
          <Form.Label>Query</Form.Label>
          <Form.Control
            as="textarea"
            rows={5}
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
            placeholder={queryType === 'cypher' ? 
              'MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 10' : 
              'SELECT ?subject ?predicate ?object WHERE { ?subject ?predicate ?object } LIMIT 10'
            }
            required
          />
        </Form.Group>
        
        <Button 
          variant="primary" 
          type="submit" 
          disabled={loading || !hasCredentials()}
        >
          {loading ? 'Executing...' : 'Execute Query'}
        </Button>
        
        {!hasCredentials() && (
          <Alert variant="warning" className="mt-3">
            Please configure your Neo4j credentials before executing queries.
          </Alert>
        )}
      </Form>
      
      {error && (
        <Card className="mt-4 text-white bg-danger">
          <Card.Body>
            <Card.Title>Error</Card.Title>
            <Card.Text>{error}</Card.Text>
          </Card.Body>
        </Card>
      )}
      
      {results && (
        <div className="mt-4">
          <h3>Results</h3>
          <pre className="bg-light p-3 rounded">
            {JSON.stringify(results, null, 2)}
          </pre>
        </div>
      )}
    </Container>
  );
};

export default QueryInterface;
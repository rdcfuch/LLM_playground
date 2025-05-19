import React, { useState } from 'react';
import { Form, Button, Container, Row, Col, Card } from 'react-bootstrap';

const QueryInterface = () => {
  const [queryType, setQueryType] = useState('cypher');
  const [queryText, setQueryText] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:5001/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: queryType,
          query: queryText
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

  return (
    <Container>
      <h2>Query Knowledge Graph</h2>
      <p className="lead">
        Query your knowledge graph using Cypher or SPARQL queries.
      </p>
      
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
        
        <Button variant="primary" type="submit" disabled={loading}>
          {loading ? 'Executing...' : 'Execute Query'}
        </Button>
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
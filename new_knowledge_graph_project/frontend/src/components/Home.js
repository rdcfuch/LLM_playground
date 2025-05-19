import React, { useState } from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import ApiKeyConfig from './ApiKeyConfig';

const Home = () => {
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  
  return (
    <Container className="mt-4">
      <Row className="mb-4">
        <Col>
          <h1>Knowledge Graph Explorer</h1>
          <p className="lead">
            Visualize, query, and manage your knowledge graph data
          </p>
        </Col>
      </Row>
      
      <Row className="mb-3">
        <Col>
          <Button 
            variant="outline-primary" 
            onClick={() => setShowApiKeyModal(true)}
            className="mb-4"
          >
            OpenAI API Key Configuration
          </Button>
        </Col>
      </Row>
      
      <Row>
        <Col md={4} className="mb-4">
          <Card>
            <Card.Body>
              <Card.Title>Graph Visualization</Card.Title>
              <Card.Text>
                Explore your knowledge graph with an interactive visualization.
              </Card.Text>
              <Link to="/visualization" className="btn btn-primary">
                Explore Graph
              </Link>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={4} className="mb-4">
          <Card>
            <Card.Body>
              <Card.Title>Query Interface</Card.Title>
              <Card.Text>
                Query your knowledge graph using Cypher or SPARQL.
              </Card.Text>
              <Link to="/query" className="btn btn-primary">
                Query Data
              </Link>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={4} className="mb-4">
          <Card>
            <Card.Body>
              <Card.Title>Graph Editor</Card.Title>
              <Card.Text>
                Add, update, or delete nodes and relationships.
              </Card.Text>
              <Link to="/editor" className="btn btn-primary">
                Edit Graph
              </Link>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={4} className="mb-4">
          <Card>
            <Card.Body>
              <Card.Title>Data Import</Card.Title>
              <Card.Text>
                Import data from various sources into your knowledge graph.
              </Card.Text>
              <Link to="/import" className="btn btn-primary">
                Import Data
              </Link>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      {/* API Key Configuration Modal */}
      <ApiKeyConfig 
        show={showApiKeyModal}
        onHide={() => setShowApiKeyModal(false)}
        onSave={(key) => {
          localStorage.setItem('openai_api_key', key);
          setShowApiKeyModal(false);
        }}
      />
    </Container>
  );
};

export default Home;
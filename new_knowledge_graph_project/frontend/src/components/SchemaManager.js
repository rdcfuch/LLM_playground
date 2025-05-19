import React, { useState, useEffect } from 'react';
import { Card, Form, Button, Tab, Tabs, Alert, ListGroup } from 'react-bootstrap';
import axios from 'axios';
import { API_CONFIG } from '../config';

const SchemaManager = () => {
  const [schemas, setSchemas] = useState([]);
  const [newSchema, setNewSchema] = useState('');
  const [schemaName, setSchemaName] = useState('');
  const [message, setMessage] = useState(null);
  
  useEffect(() => {
    // TODO: Fetch schemas from API
    // For now, using mock data
    setSchemas([
      { id: 1, name: 'Employee-Project Schema', format: 'JSON-LD' },
      { id: 2, name: 'Product Catalog', format: 'OWL' }
    ]);
  }, []);
  
  const handleSchemaChange = (e) => {
    setNewSchema(e.target.value);
  };
  
  const handleNameChange = (e) => {
    setSchemaName(e.target.value);
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // Validate JSON
      const schemaObj = JSON.parse(newSchema);
      
      // Submit schema to API using config
      const response = await axios.post(
        `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.schema}`, 
        schemaObj
      );
      
      if (response.data.status === 'success') {
        setSchemas([...schemas, { 
          id: schemas.length + 1, 
          name: schemaName, 
          format: schemaObj['@context'] ? 'JSON-LD' : 'Custom' 
        }]);
        
        setMessage({ type: 'success', text: 'Schema created successfully!' });
        setNewSchema('');
        setSchemaName('');
      } else {
        setMessage({ type: 'danger', text: response.data.message });
      }
    } catch (error) {
      setMessage({ type: 'danger', text: 'Invalid JSON format or API error: ' + error.message });
    }
  };
  
  const exampleSchema = `{
  "@context": "http://schema.org",
  "@graph": [
    {
      "@id": "http://example.com/ontology#Employee",
      "@type": "rdfs:Class",
      "rdfs:label": "Employee"
    },
    {
      "@id": "http://example.com/ontology#Project",
      "@type": "rdfs:Class",
      "rdfs:label": "Project"
    },
    {
      "@id": "http://example.com/ontology#worksOn",
      "@type": "rdf:Property",
      "rdfs:domain": { "@id": "http://example.com/ontology#Employee" },
      "rdfs:range": { "@id": "http://example.com/ontology#Project" },
      "rdfs:label": "works on"
    }
  ]
}`;
  
  return (
    <div>
      <h1>Schema Manager</h1>
      
      {message && (
        <Alert variant={message.type} dismissible onClose={() => setMessage(null)}>
          {message.text}
        </Alert>
      )}
      
      <Tabs defaultActiveKey="create" className="mb-3">
        <Tab eventKey="create" title="Create Schema">
          <Card>
            <Card.Body>
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Schema Name</Form.Label>
                  <Form.Control 
                    type="text" 
                    value={schemaName}
                    onChange={handleNameChange}
                    placeholder="Enter schema name" 
                    required
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Schema Definition (JSON-LD)</Form.Label>
                  <Form.Control 
                    as="textarea" 
                    rows={15} 
                    value={newSchema}
                    onChange={handleSchemaChange}
                    placeholder="Enter JSON-LD schema" 
                    required
                  />
                  <Form.Text className="text-muted">
                    Define your schema using JSON-LD format.
                  </Form.Text>
                </Form.Group>
                
                <Button variant="primary" type="submit">
                  Create Schema
                </Button>
                <Button 
                  variant="outline-secondary" 
                  className="ms-2"
                  onClick={() => setNewSchema(exampleSchema)}
                >
                  Load Example
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Tab>
        
        <Tab eventKey="manage" title="Manage Schemas">
          <Card>
            <Card.Body>
              <ListGroup>
                {schemas.map(schema => (
                  <ListGroup.Item key={schema.id} className="d-flex justify-content-between align-items-center">
                    <div>
                      <h5>{schema.name}</h5>
                      <span className="badge bg-info">{schema.format}</span>
                    </div>
                    <div>
                      <Button variant="outline-primary" size="sm" className="me-2">View</Button>
                      <Button variant="outline-danger" size="sm">Delete</Button>
                    </div>
                  </ListGroup.Item>
                ))}
              </ListGroup>
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>
    </div>
  );
};

export default SchemaManager;
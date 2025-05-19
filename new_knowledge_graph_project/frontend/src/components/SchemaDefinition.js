import React, { useState } from 'react';
import { Card, Form, Button, Alert, Tabs, Tab } from 'react-bootstrap';
import axios from 'axios';

const SchemaDefinition = () => {
  const [schemaType, setSchemaType] = useState('json-ld');
  const [schemaText, setSchemaText] = useState('');
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Sample templates for different schema types
  const templates = {
    'json-ld': `{
  "@context": "http://schema.org",
  "@type": "Organization",
  "name": "Example Organization",
  "employees": {
    "@type": "Person",
    "name": "Employee Name",
    "jobTitle": "Job Title"
  },
  "projects": {
    "@type": "Project",
    "name": "Project Name",
    "startDate": "2023-01-01"
  }
}`,
    'owl': `<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#">
  <Class rdf:about="http://example.org/Person"/>
  <Class rdf:about="http://example.org/Organization"/>
  <ObjectProperty rdf:about="http://example.org/worksFor">
    <Domain rdf:resource="http://example.org/Person"/>
    <Range rdf:resource="http://example.org/Organization"/>
  </ObjectProperty>
</Ontology>`,
    'rdfs': `@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex: <http://example.org/> .

ex:Person rdfs:subClassOf rdfs:Resource .
ex:Organization rdfs:subClassOf rdfs:Resource .
ex:worksFor rdfs:domain ex:Person ;
           rdfs:range ex:Organization .`
  };
  
  const handleSchemaTypeChange = (type) => {
    setSchemaType(type);
    setSchemaText(templates[type]);
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    
    try {
      let schemaData;
      
      if (schemaType === 'json-ld') {
        schemaData = JSON.parse(schemaText);
      } else {
        // For OWL and RDFS, we'd need proper parsing
        // This is simplified for the example
        schemaData = { content: schemaText, format: schemaType };
      }
      
      const response = await axios.post('http://localhost:5000/api/schema', schemaData);
      
      if (response.data.status === 'success') {
        setMessage({ type: 'success', text: 'Schema created successfully!' });
      } else {
        setMessage({ type: 'danger', text: response.data.message });
      }
    } catch (error) {
      setMessage({ 
        type: 'danger', 
        text: error.response?.data?.message || 'Error creating schema. Please check your syntax.' 
      });
    } finally {
      setLoading(false);
    }
  };
  
  const loadTemplate = () => {
    setSchemaText(templates[schemaType]);
  };
  
  return (
    <div>
      <h2 className="mb-4">Schema Definition</h2>
      
      <Card>
        <Card.Body>
          <Tabs
            activeKey={schemaType}
            onSelect={(k) => handleSchemaTypeChange(k)}
            className="mb-3"
          >
            <Tab eventKey="json-ld" title="JSON-LD">
              <p>Define your schema using JSON-LD format, compatible with schema.org and web standards.</p>
            </Tab>
            <Tab eventKey="owl" title="OWL">
              <p>Use Web Ontology Language (OWL) for more complex ontologies with formal semantics.</p>
            </Tab>
            <Tab eventKey="rdfs" title="RDFS">
              <p>RDF Schema provides a simple way to define classes and properties for your knowledge graph.</p>
            </Tab>
          </Tabs>
          
          {message && (
            <Alert variant={message.type} dismissible onClose={() => setMessage(null)}>
              {message.text}
            </Alert>
          )}
          
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Schema Definition</Form.Label>
              <Form.Control
                as="textarea"
                rows={15}
                value={schemaText}
                onChange={(e) => setSchemaText(e.target.value)}
                placeholder={`Enter your ${schemaType.toUpperCase()} schema here...`}
              />
            </Form.Group>
            
            <div className="d-flex justify-content-between">
              <Button variant="secondary" onClick={loadTemplate}>
                Load Template
              </Button>
              <Button variant="primary" type="submit" disabled={loading}>
                {loading ? 'Creating Schema...' : 'Create Schema'}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default SchemaDefinition;
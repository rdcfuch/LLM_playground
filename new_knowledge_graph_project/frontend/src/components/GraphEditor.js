import React, { useState, useEffect } from 'react';
import { Form, Button, Container, Row, Col, Card, Modal, Alert, Tabs, Tab } from 'react-bootstrap';

const GraphEditor = () => {
  const [nodes, setNodes] = useState([]);
  const [relationships, setRelationships] = useState([]);
  const [showNodeModal, setShowNodeModal] = useState(false);
  const [showRelationshipModal, setShowRelationshipModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Node form state
  const [nodeLabel, setNodeLabel] = useState('');
  const [nodeProperties, setNodeProperties] = useState({});
  
  // Relationship form state
  const [sourceNode, setSourceNode] = useState('');
  const [targetNode, setTargetNode] = useState('');
  const [relationType, setRelationType] = useState('');
  const [relationProperties, setRelationProperties] = useState({});
  
  // Unstructured data state
  const [unstructuredText, setUnstructuredText] = useState('');
  const [parsedData, setParsedData] = useState(null);
  const [isParsingData, setIsParsingData] = useState(false);

  useEffect(() => {
    // Fetch graph data when component mounts
    fetchGraphData();
  }, []);

  const fetchGraphData = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5001/api/graph');
      const data = await response.json();
      
      if (data.nodes && data.links) {
        setNodes(data.nodes);
        setRelationships(data.links);
      }
    } catch (err) {
      setError('Failed to load graph data: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddNode = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/graph/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          operation: 'add_node',
          node: {
            label: nodeLabel,
            properties: nodeProperties
          }
        }),
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        // Refresh graph data
        fetchGraphData();
        // Reset form and close modal
        setNodeLabel('');
        setNodeProperties({});
        setShowNodeModal(false);
        setSuccess('Node added successfully');
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to add node: ' + err.message);
    }
  };

  const handleAddRelationship = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/graph/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          operation: 'add_relationship',
          relationship: {
            source: sourceNode,
            target: targetNode,
            type: relationType,
            properties: relationProperties
          }
        }),
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        // Refresh graph data
        fetchGraphData();
        // Reset form and close modal
        setSourceNode('');
        setTargetNode('');
        setRelationType('');
        setRelationProperties({});
        setShowRelationshipModal(false);
        setSuccess('Relationship added successfully');
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to add relationship: ' + err.message);
    }
  };

  // Handle property changes for node
  const handleNodePropertyChange = (key, value) => {
    setNodeProperties({
      ...nodeProperties,
      [key]: value
    });
  };

  // Handle property changes for relationship
  const handleRelationPropertyChange = (key, value) => {
    setRelationProperties({
      ...relationProperties,
      [key]: value
    });
  };
  
  // Handle unstructured data parsing
  const handleParseUnstructuredData = async () => {
    if (!unstructuredText.trim()) {
      setError('Please enter some text to parse');
      return;
    }
    
    setIsParsingData(true);
    setError(null);
    setParsedData(null);
    
    try {
      const response = await fetch('http://localhost:5001/api/parse-unstructured', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: unstructuredText
        }),
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setParsedData(data.parsed_data);
        setSuccess('Text successfully parsed to JSON-LD');
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(data.message || 'Failed to parse text');
      }
    } catch (err) {
      setError('Error: ' + err.message);
    } finally {
      setIsParsingData(false);
    }
  };
  
  // Handle importing parsed data to graph
  const handleImportParsedData = async () => {
    if (!parsedData) {
      setError('No parsed data to import');
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:5001/api/import-jsonld', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data: parsedData
        }),
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        fetchGraphData();
        setParsedData(null);
        setUnstructuredText('');
        setSuccess('Data successfully imported to graph');
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(data.message || 'Failed to import data');
      }
    } catch (err) {
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <h2>Graph Editor</h2>
      <p className="lead">
        Add, update, or delete nodes and relationships in your knowledge graph.
      </p>
      
      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}
      
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      <Tabs defaultActiveKey="structured" className="mb-4">
        <Tab eventKey="structured" title="Structured Editing">
          <Row className="mb-4">
            <Col>
              <Button variant="primary" onClick={() => setShowNodeModal(true)}>
                Add Node
              </Button>{' '}
              <Button variant="success" onClick={() => setShowRelationshipModal(true)}>
                Add Relationship
              </Button>
            </Col>
          </Row>
          
          {loading ? (
            <p>Loading graph data...</p>
          ) : (
            <Row>
              <Col md={6}>
                <h3>Nodes ({nodes.length})</h3>
                <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                  {nodes.map(node => (
                    <Card key={node.id} className="mb-2">
                      <Card.Body>
                        <Card.Title>{node.label}</Card.Title>
                        <Card.Subtitle className="mb-2 text-muted">ID: {node.id}</Card.Subtitle>
                        <pre>{JSON.stringify(node.properties, null, 2)}</pre>
                      </Card.Body>
                    </Card>
                  ))}
                </div>
              </Col>
              <Col md={6}>
                <h3>Relationships ({relationships.length})</h3>
                <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                  {relationships.map((rel, index) => (
                    <Card key={index} className="mb-2">
                      <Card.Body>
                        <Card.Title>{rel.type}</Card.Title>
                        <Card.Subtitle className="mb-2 text-muted">
                          {rel.source} → {rel.target}
                        </Card.Subtitle>
                        <pre>{JSON.stringify(rel.properties, null, 2)}</pre>
                      </Card.Body>
                    </Card>
                  ))}
                </div>
              </Col>
            </Row>
          )}
        </Tab>
        
        <Tab eventKey="unstructured" title="Unstructured Data Input">
          <Card>
            <Card.Body>
              <Card.Title>Parse Unstructured Text with LLM</Card.Title>
              <Card.Text>
                Enter unstructured text about entities and their relationships. 
                Our AI will parse it into structured JSON-LD format for your knowledge graph.
              </Card.Text>
              
              <Form.Group className="mb-3">
                <Form.Label>Unstructured Text</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={8}
                  value={unstructuredText}
                  onChange={(e) => setUnstructuredText(e.target.value)}
                  placeholder="Example: John Doe works at Acme Corp as a Software Engineer. He is 35 years old and has been working on the Knowledge Graph project since 2022."
                />
                <Form.Text className="text-muted">
                  Describe entities, their properties, and relationships in natural language.
                </Form.Text>
              </Form.Group>
              
              <Button 
                variant="primary" 
                onClick={handleParseUnstructuredData}
                disabled={isParsingData || !unstructuredText.trim()}
              >
                {isParsingData ? 'Parsing...' : 'Parse with LLM'}
              </Button>
              
              {parsedData && (
                <div className="mt-4">
                  <h4>Parsed JSON-LD</h4>
                  <pre className="bg-light p-3 rounded" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    {JSON.stringify(parsedData, null, 2)}
                  </pre>
                  <Button 
                    variant="success" 
                    onClick={handleImportParsedData}
                    className="mt-2"
                  >
                    Import to Graph
                  </Button>
                </div>
              )}
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>
      
      {/* Add Node Modal */}
      <Modal show={showNodeModal} onHide={() => setShowNodeModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Add Node</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Node Label</Form.Label>
              <Form.Control
                type="text"
                value={nodeLabel}
                onChange={(e) => setNodeLabel(e.target.value)}
                placeholder="e.g., Person, Organization, Project"
                required
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Properties (JSON format)</Form.Label>
              <Form.Control
                as="textarea"
                rows={5}
                placeholder='{"name": "John Doe", "age": 30}'
                onChange={(e) => {
                  try {
                    const props = JSON.parse(e.target.value);
                    setNodeProperties(props);
                    setError(null);
                  } catch (err) {
                    setError('Invalid JSON format');
                  }
                }}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowNodeModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleAddNode}>
            Add Node
          </Button>
        </Modal.Footer>
      </Modal>
      
      {/* Add Relationship Modal */}
      <Modal show={showRelationshipModal} onHide={() => setShowRelationshipModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Add Relationship</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Source Node ID</Form.Label>
              <Form.Control
                type="text"
                value={sourceNode}
                onChange={(e) => setSourceNode(e.target.value)}
                placeholder="ID of source node"
                required
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Target Node ID</Form.Label>
              <Form.Control
                type="text"
                value={targetNode}
                onChange={(e) => setTargetNode(e.target.value)}
                placeholder="ID of target node"
                required
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Relationship Type</Form.Label>
              <Form.Control
                type="text"
                value={relationType}
                onChange={(e) => setRelationType(e.target.value)}
                placeholder="e.g., WORKS_FOR, MANAGES, CONTAINS"
                required
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Properties (JSON format)</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                placeholder='{"since": "2022-01-01", "role": "Manager"}'
                onChange={(e) => {
                  try {
                    const props = JSON.parse(e.target.value);
                    setRelationProperties(props);
                    setError(null);
                  } catch (err) {
                    setError('Invalid JSON format');
                  }
                }}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowRelationshipModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleAddRelationship}>
            Add Relationship
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default GraphEditor;
import React, { useState, useEffect, useRef } from 'react';
import { Card, Form, Button, ButtonGroup, Row, Col, Alert, Spinner } from 'react-bootstrap';
import * as d3 from 'd3';
import axios from 'axios';
import { NEO4J_CONFIG } from '../config';

const GraphVisualization = () => {
  const svgRef = useRef(null);
  const [graph, setGraph] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('');
  const [nodeTypes, setNodeTypes] = useState([]);
  const [selectedNodeType, setSelectedNodeType] = useState('All');
  const [relationshipTypes, setRelationshipTypes] = useState([]);
  const [selectedRelationship, setSelectedRelationship] = useState('All');
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
  
  useEffect(() => {
    fetchGraphData();
  }, []);
  
  useEffect(() => {
    if (graph.nodes.length > 0) {
      renderGraph();
    }
  }, [graph, filter, selectedNodeType, selectedRelationship]);
  
  const fetchGraphData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('/api/graph');
      const data = response.data;
      
      // Extract unique node types and relationship types for filtering
      const types = [...new Set(data.nodes.map(node => node.label))];
      const relationships = [...new Set(data.links.map(link => link.type))];
      
      setGraph(data);
      setNodeTypes(types);
      setRelationshipTypes(relationships);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching graph data:', error);
      setError('Failed to load graph data. Please try again later.');
      setLoading(false);
      
      // For development: use mock data if API fails
      const mockGraph = {
        nodes: [
          { id: 1, label: "Person", properties: { name: "John Doe" } },
          { id: 2, label: "Person", properties: { name: "Jane Smith" } },
          { id: 3, label: "Organization", properties: { name: "Acme Corp" } },
          { id: 4, label: "Project", properties: { name: "Knowledge Graph" } },
          { id: 5, label: "Project", properties: { name: "Data Analytics" } }
        ],
        links: [
          { source: 1, target: 3, type: "WORKS_FOR", properties: {} },
          { source: 2, target: 3, type: "WORKS_FOR", properties: {} },
          { source: 1, target: 4, type: "CONTRIBUTES_TO", properties: {} },
          { source: 2, target: 4, type: "MANAGES", properties: {} },
          { source: 2, target: 5, type: "CONTRIBUTES_TO", properties: {} },
          { source: 3, target: 4, type: "SPONSORS", properties: {} }
        ]
      };
      
      // Extract unique node types and relationship types for filtering
      const types = [...new Set(mockGraph.nodes.map(node => node.label))];
      const relationships = [...new Set(mockGraph.links.map(link => link.type))];
      
      setGraph(mockGraph);
      setNodeTypes(types);
      setRelationshipTypes(relationships);
    }
  };
  
  const fetchFullNeo4jGraph = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Save credentials to localStorage
      localStorage.setItem('neo4j_username', neo4jCredentials.username);
      localStorage.setItem('neo4j_password', neo4jCredentials.password);
      
      // First, fetch all nodes
      const nodesResponse = await fetch('http://localhost:5001/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: 'cypher',
          query: 'MATCH (n) RETURN n LIMIT 1000',
          auth: {
            username: neo4jCredentials.username,
            password: neo4jCredentials.password
          }
        }),
      });
      
      const nodesData = await nodesResponse.json();
      
      if (nodesData.status === 'error') {
        setError(nodesData.message);
        setLoading(false);
        return;
      }
      
      // Then, fetch all relationships
      const relsResponse = await fetch('http://localhost:5001/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: 'cypher',
          query: 'MATCH ()-[r]->() RETURN r, startNode(r) as source, endNode(r) as target LIMIT 1000',
          auth: {
            username: neo4jCredentials.username,
            password: neo4jCredentials.password
          }
        }),
      });
      
      const relsData = await relsResponse.json();
      
      if (relsData.status === 'error') {
        setError(relsData.message);
        setLoading(false);
        return;
      }
      
      // Process nodes
      const nodes = [];
      const nodeMap = new Map();
      let idCounter = 1;
      
      if (Array.isArray(nodesData.results)) {
        nodesData.results.forEach(record => {
          if (!record || !record.n) {
            return; // Skip incomplete records
          }
          
          const node = record.n;
          const nodeKey = JSON.stringify(node);
          
          if (!nodeMap.has(nodeKey)) {
            // Handle different label formats (_labels vs labels)
            const labels = node._labels || node.labels || [];
            
            const nodeData = {
              id: idCounter++,
              label: Array.isArray(labels) && labels.length > 0 ? labels[0] : 'Unknown',
              properties: {}
            };
            
            // Extract properties
            Object.keys(node).forEach(key => {
              if (key !== '_labels' && key !== 'labels') {
                nodeData.properties[key] = node[key];
              }
            });
            
            // Make sure to include _labels in properties for display
            if (node._labels) {
              nodeData.properties._labels = node._labels;
            }
            
            nodes.push(nodeData);
            nodeMap.set(nodeKey, nodeData);
          }
        });
      }
      
      // Process relationships
      const links = [];
      const relationshipTypes = new Set();
      
      if (Array.isArray(relsData.results)) {
        relsData.results.forEach(record => {
          if (!record || !record.r || !record.source || !record.target) {
            return; // Skip incomplete records
          }
          
          const rel = record.r;
          const source = record.source;
          const target = record.target;
          
          // Find source and target nodes in our node map
          const sourceKey = JSON.stringify(source);
          const targetKey = JSON.stringify(target);
          
          const sourceNode = nodeMap.get(sourceKey);
          const targetNode = nodeMap.get(targetKey);
          
          if (sourceNode && targetNode) {
            const relType = rel.type || 'RELATED_TO';
            relationshipTypes.add(relType);
            
            links.push({
              source: sourceNode.id,
              target: targetNode.id,
              type: relType,
              properties: {}
            });
            
            // Extract relationship properties
            Object.keys(rel).forEach(key => {
              if (key !== 'type') {
                links[links.length - 1].properties[key] = rel[key];
              }
            });
          }
        });
      }
      
      // If no relationships were found, try a different approach
      if (links.length === 0) {
        console.log("No relationships found with first query, trying alternative...");
        
        const altRelsResponse = await fetch('http://localhost:5001/api/query', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            type: 'cypher',
            query: 'MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 1000',
            auth: {
              username: neo4jCredentials.username,
              password: neo4jCredentials.password
            }
          }),
        });
        
        const altRelsData = await altRelsResponse.json();
        
        if (altRelsData.status !== 'error' && Array.isArray(altRelsData.results)) {
          altRelsData.results.forEach(record => {
            if (!record || !record.a || !record.r || !record.b) {
              return; // Skip incomplete records
            }
            
            const source = record.a;
            const rel = record.r;
            const target = record.b;
            
            // Find source and target nodes in our node map
            const sourceKey = JSON.stringify(source);
            const targetKey = JSON.stringify(target);
            
            const sourceNode = nodeMap.get(sourceKey);
            const targetNode = nodeMap.get(targetKey);
            
            if (sourceNode && targetNode) {
              const relType = rel.type || 'RELATED_TO';
              relationshipTypes.add(relType);
              
              links.push({
                source: sourceNode.id,
                target: targetNode.id,
                type: relType,
                properties: {}
              });
              
              // Extract relationship properties
              Object.keys(rel).forEach(key => {
                if (key !== 'type') {
                  links[links.length - 1].properties[key] = rel[key];
                }
              });
            }
          });
        }
      }
      
      // Update the graph state with the new data
      const graphData = { nodes, links };
      setGraph(graphData);
      
      // Extract unique node types for filtering
      const types = [...new Set(nodes.map(node => node.label))];
      setNodeTypes(types);
      setRelationshipTypes([...relationshipTypes]);
      
      console.log('Processed nodes:', nodes.length);
      console.log('Processed relationships:', links.length);
      
    } catch (err) {
      console.error('Error details:', err);
      setError('Failed to fetch Neo4j graph: ' + err.message);
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
  
  const renderGraph = () => {
    // Clear previous visualization
    d3.select(svgRef.current).selectAll("*").remove();
    
    const svg = d3.select(svgRef.current);
    const width = svgRef.current.clientWidth;
    const height = 600;
    
    // Apply filters
    let filteredNodes = graph.nodes;
    let filteredLinks = graph.links;
    
    // Filter by node type
    if (selectedNodeType !== 'All') {
      filteredNodes = graph.nodes.filter(node => node.label === selectedNodeType);
      const nodeIds = new Set(filteredNodes.map(node => node.id));
      filteredLinks = graph.links.filter(link => 
        nodeIds.has(link.source.id || link.source) && nodeIds.has(link.target.id || link.target)
      );
    }
    
    // Filter by relationship type
    if (selectedRelationship !== 'All') {
      filteredLinks = filteredLinks.filter(link => link.type === selectedRelationship);
      const nodeIdsInLinks = new Set();
      filteredLinks.forEach(link => {
        nodeIdsInLinks.add(link.source.id || link.source);
        nodeIdsInLinks.add(link.target.id || link.target);
      });
      filteredNodes = filteredNodes.filter(node => nodeIdsInLinks.has(node.id));
    }
    
    // Filter by text search
    if (filter) {
      const lowerFilter = filter.toLowerCase();
      filteredNodes = filteredNodes.filter(node => 
        (node.properties.name && node.properties.name.toLowerCase().includes(lowerFilter)) ||
        node.label.toLowerCase().includes(lowerFilter)
      );
      const nodeIds = new Set(filteredNodes.map(node => node.id));
      filteredLinks = filteredLinks.filter(link => 
        nodeIds.has(link.source.id || link.source) && nodeIds.has(link.target.id || link.target)
      );
    }
    
    // Create a color scale for node types (using d3.schemeCategory10 like in test1.html)
    const color = d3.scaleOrdinal(d3.schemeCategory10)
      .domain(nodeTypes);
    
    // Create the simulation with similar parameters to test1.html
    const simulation = d3.forceSimulation(filteredNodes)
      .force("link", d3.forceLink(filteredLinks)
        .id(d => d.id)
        .distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));
    
    // Create links with styling similar to test1.html
    const link = svg.append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(filteredLinks)
      .enter().append("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", 1.5);
    
    // Create link labels (relationship types)
    const linkText = svg.append("g")
      .attr("class", "link-labels")
      .selectAll("text")
      .data(filteredLinks)
      .enter().append("text")
      .text(d => d.type)
      .attr("font-size", 10)
      .attr("fill", "#555")
      .attr("text-anchor", "middle");
    
    // Create nodes
    const node = svg.append("g")
      .attr("class", "nodes")
      .selectAll("g")
      .data(filteredNodes)
      .enter().append("g");
    
    // Add circles to nodes with styling similar to test1.html
    node.append("circle")
      .attr("r", 10)
      .attr("fill", d => color(d.label))
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));
    
    // Add labels to nodes
    node.append("text")
      .text(d => {
        // First try to get the name property
        if (d.properties.name) {
          return d.properties.name;
        }
        
        // If no name, show the first label from _labels if available
        if (d.properties._labels && Array.isArray(d.properties._labels) && d.properties._labels.length > 0) {
          return d.properties._labels[0];
        }
        
        // Fallback to the node label
        return d.label;
      })
      .attr("x", 15)
      .attr("y", 5)
      .attr("font-size", 12)
      .attr("pointer-events", "none"); // Make text non-interactive like in test1.html
    
    // Add tooltips
    node.append("title")
      .text(d => {
        let tooltip = `Type: ${d.label}\n`;
        
        // Add _labels information if available
        if (d.properties._labels && Array.isArray(d.properties._labels)) {
          tooltip += `Labels: ${d.properties._labels.join(', ')}\n`;
        }
        
        // Add all other properties
        for (const [key, value] of Object.entries(d.properties)) {
          if (key !== '_labels') {
            tooltip += `${key}: ${value}\n`;
          }
        }
        return tooltip;
      });
    
    // Update positions on simulation tick
    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);
      
      linkText
        .attr("x", d => (d.source.x + d.target.x) / 2)
        .attr("y", d => (d.source.y + d.target.y) / 2);
      
      node
        .attr("transform", d => `translate(${d.x},${d.y})`);
    });
    
    // Drag functions (same as in test1.html)
    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    
    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }
    
    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
    
    // Add zoom functionality
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        svg.selectAll("g").attr("transform", event.transform);
      });
    
    svg.call(zoom);
  };
  
  const handleExport = (format) => {
    const svgElement = svgRef.current;
    
    if (format === 'svg') {
      // Export as SVG
      const svgData = new XMLSerializer().serializeToString(svgElement);
      const blob = new Blob([svgData], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'knowledge_graph.svg';
      link.click();
    } else if (format === 'png') {
      // Export as PNG
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      const svgData = new XMLSerializer().serializeToString(svgElement);
      const img = new Image();
      
      img.onload = () => {
        canvas.width = svgElement.clientWidth;
        canvas.height = svgElement.clientHeight;
        context.drawImage(img, 0, 0);
        const pngUrl = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.href = pngUrl;
        link.download = 'knowledge_graph.png';
        link.click();
      };
      
      img.src = 'data:image/svg+xml;base64,' + btoa(svgData);
    }
  };
  
  return (
    <div>
      <h1>Knowledge Graph Visualization</h1>
      
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      <Card className="mb-4">
        <Card.Body>
          <Row>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>Search Nodes</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Search by name..."
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                />
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>Filter by Node Type</Form.Label>
                <Form.Select
                  value={selectedNodeType}
                  onChange={(e) => setSelectedNodeType(e.target.value)}
                >
                  <option value="All">All Types</option>
                  {nodeTypes.map((type, index) => (
                    <option key={index} value={type}>{type}</option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>Filter by Relationship</Form.Label>
                <Form.Select
                  value={selectedRelationship}
                  onChange={(e) => setSelectedRelationship(e.target.value)}
                >
                  <option value="All">All Relationships</option>
                  {relationshipTypes.map((type, index) => (
                    <option key={index} value={type}>{type}</option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
          </Row>
          
          <Row className="mb-3">
            <Col>
              <Button 
                variant="outline-secondary" 
                className="me-2"
                onClick={() => setShowCredentials(!showCredentials)}
              >
                {showCredentials ? 'Hide Neo4j Credentials' : 'Configure Neo4j Credentials'}
              </Button>
              
              <Button 
                variant="primary" 
                className="me-2"
                onClick={fetchFullNeo4jGraph}
                disabled={!hasCredentials()}
              >
                Show Full Neo4j Graph
              </Button>
              
              <ButtonGroup className="me-2">
                <Button variant="outline-primary" onClick={() => fetchGraphData()}>
                  Refresh
                </Button>
                <Button variant="outline-secondary" onClick={() => handleExport('svg')}>
                  Export SVG
                </Button>
                <Button variant="outline-secondary" onClick={() => handleExport('png')}>
                  Export PNG
                </Button>
              </ButtonGroup>
            </Col>
          </Row>
          
          {showCredentials && (
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Neo4j Username</Form.Label>
                  <Form.Control
                    type="text"
                    value={neo4jCredentials.username}
                    onChange={(e) => setNeo4jCredentials({...neo4jCredentials, username: e.target.value})}
                    placeholder="neo4j"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Neo4j Password</Form.Label>
                  <Form.Control
                    type="password"
                    value={neo4jCredentials.password}
                    onChange={(e) => setNeo4jCredentials({...neo4jCredentials, password: e.target.value})}
                    placeholder="Enter your Neo4j password"
                  />
                </Form.Group>
              </Col>
            </Row>
          )}
        </Card.Body>
      </Card>
      
      <Card>
        <Card.Body>
          {loading ? (
            <div className="text-center p-5">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
              </Spinner>
              <p className="mt-3">Loading graph data...</p>
            </div>
          ) : (
            <div className="graph-container" style={{ height: '600px', border: '1px solid #ddd' }}>
              <svg ref={svgRef} width="100%" height="100%"></svg>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

export default GraphVisualization;
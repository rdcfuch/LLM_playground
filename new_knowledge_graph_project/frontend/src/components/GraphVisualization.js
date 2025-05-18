import React, { useState, useEffect, useRef } from 'react';
import { Card, Form, Button, ButtonGroup, Row, Col, Alert, Spinner } from 'react-bootstrap';
import * as d3 from 'd3';
import axios from 'axios';

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
    
    // Create a color scale for node types
    const color = d3.scaleOrdinal(d3.schemeCategory10)
      .domain(nodeTypes);
    
    // Create the simulation
    const simulation = d3.forceSimulation(filteredNodes)
      .force("link", d3.forceLink(filteredLinks)
        .id(d => d.id)
        .distance(150))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide().radius(50));
    
    // Create links
    const link = svg.append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(filteredLinks)
      .enter().append("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", 1.5);
    
    // Create link labels
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
    
    // Add circles to nodes
    node.append("circle")
      .attr("r", 10)
      .attr("fill", d => color(d.label))
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));
    
    // Add labels to nodes
    node.append("text")
      .text(d => d.properties.name || d.label)
      .attr("x", 15)
      .attr("y", 5)
      .attr("font-size", 12);
    
    // Add tooltips
    node.append("title")
      .text(d => {
        let tooltip = `Type: ${d.label}\n`;
        for (const [key, value] of Object.entries(d.properties)) {
          tooltip += `${key}: ${value}\n`;
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
    
    // Drag functions
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
          
          <ButtonGroup className="mb-3">
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
            <svg 
              ref={svgRef} 
              width="100%" 
              height="600px" 
              style={{ border: '1px solid #ddd', borderRadius: '4px' }}
            />
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

export default GraphVisualization;
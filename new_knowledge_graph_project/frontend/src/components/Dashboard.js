import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { API_CONFIG } from '../config';

const Dashboard = () => {
  const [stats, setStats] = useState({
    schemas: 0,
    nodes: 0,
    relationships: 0,
    lastUpdated: null
  });

  useEffect(() => {
    // Fetch dashboard stats from API
    const fetchStats = async () => {
      try {
        // You would need to create this endpoint in the backend
        const response = await axios.get(`${API_CONFIG.baseUrl}/stats`);
        if (response.data) {
          setStats(response.data);
        }
      } catch (error) {
        console.error('Error fetching stats:', error);
        // Fallback to mock data
        setStats({
          schemas: 3,
          nodes: 1250,
          relationships: 3750,
          lastUpdated: new Date().toLocaleString()
        });
      }
    };
    
    fetchStats();
  }, []);

  return (
    <div>
      <h1>Knowledge Graph Dashboard</h1>
      <Row className="mt-4">
        <Col md={3}>
          <Card className="text-center mb-4">
            <Card.Body>
              <Card.Title>Schemas</Card.Title>
              <Card.Text className="display-4">{stats.schemas}</Card.Text>
              <Button as={Link} to="/schema" variant="primary">Manage Schemas</Button>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center mb-4">
            <Card.Body>
              <Card.Title>Nodes</Card.Title>
              <Card.Text className="display-4">{stats.nodes}</Card.Text>
              <Button as={Link} to="/visualization" variant="primary">View Graph</Button>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center mb-4">
            <Card.Body>
              <Card.Title>Relationships</Card.Title>
              <Card.Text className="display-4">{stats.relationships}</Card.Text>
              <Button as={Link} to="/visualization" variant="primary">View Graph</Button>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center mb-4">
            <Card.Body>
              <Card.Title>Last Updated</Card.Title>
              <Card.Text>{stats.lastUpdated}</Card.Text>
              <Button as={Link} to="/import" variant="primary">Import Data</Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      <Row className="mt-4">
        <Col md={6}>
          <Card>
            <Card.Header>Quick Actions</Card.Header>
            <Card.Body>
              <Button as={Link} to="/schema" variant="outline-primary" className="m-2">Create Schema</Button>
              <Button as={Link} to="/import" variant="outline-primary" className="m-2">Import Data</Button>
              <Button as={Link} to="/visualization" variant="outline-primary" className="m-2">Visualize Graph</Button>
              <Button as={Link} to="/query" variant="outline-primary" className="m-2">Query Data</Button>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card>
            <Card.Header>Recent Activities</Card.Header>
            <Card.Body>
              <ul className="list-unstyled">
                <li className="mb-2">Schema "Employee-Project" created (2 hours ago)</li>
                <li className="mb-2">Data imported from "employees.xlsx" (1 hour ago)</li>
                <li className="mb-2">Graph visualization exported (30 minutes ago)</li>
                <li className="mb-2">SPARQL query executed (10 minutes ago)</li>
              </ul>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
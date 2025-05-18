import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { Container, Nav, Navbar } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

// Import components
import Home from './components/Home';
import SchemaDefinition from './components/SchemaDefinition';
import DataImport from './components/DataImport';
import GraphVisualization from './components/GraphVisualization';
import QueryInterface from './components/QueryInterface';
import GraphEditor from './components/GraphEditor';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar bg="dark" variant="dark" expand="lg">
          <Container>
            <Navbar.Brand as={Link} to="/">Knowledge Graph System</Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
              <Nav className="me-auto">
                <Nav.Link as={Link} to="/">Home</Nav.Link>
                <Nav.Link as={Link} to="/schema">Schema Definition</Nav.Link>
                <Nav.Link as={Link} to="/import">Data Import</Nav.Link>
                <Nav.Link as={Link} to="/visualization">Visualization</Nav.Link>
                <Nav.Link as={Link} to="/query">Query</Nav.Link>
                <Nav.Link as={Link} to="/editor">Graph Editor</Nav.Link>
              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        <Container className="mt-4">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/schema" element={<SchemaDefinition />} />
            <Route path="/import" element={<DataImport />} />
            <Route path="/visualization" element={<GraphVisualization />} />
            <Route path="/query" element={<QueryInterface />} />
            <Route path="/editor" element={<GraphEditor />} />
          </Routes>
        </Container>
      </div>
    </Router>
  );
}

export default App;

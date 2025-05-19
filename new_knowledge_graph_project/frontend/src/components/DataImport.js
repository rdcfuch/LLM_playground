import React from 'react';
import { Container, Tabs, Tab } from 'react-bootstrap';
import TextFileImport from './TextFileImport';
import JsonLdImport from './JsonLdImport';

const DataImport = () => {
  return (
    <Container>
      <h2>Data Import</h2>
      <p className="lead">
        Import data from various sources into your knowledge graph.
      </p>
      
      <Tabs defaultActiveKey="structured" className="mb-4">
        <Tab eventKey="structured" title="Structured Data">
          {/* Your existing structured data import component */}
          <p>Import structured data from CSV, Excel, or JSON files.</p>
          {/* ... existing code ... */}
        </Tab>
        
        <Tab eventKey="unstructured" title="Unstructured Text">
          <TextFileImport />
        </Tab>
        
        <Tab eventKey="jsonld" title="JSON-LD">
          <JsonLdImport />
        </Tab>
        
        <Tab eventKey="pdf" title="PDF Documents">
          {/* Your existing PDF import component */}
          <p>Import data from PDF documents.</p>
          {/* ... existing code ... */}
        </Tab>
      </Tabs>
    </Container>
  );
};

export default DataImport;
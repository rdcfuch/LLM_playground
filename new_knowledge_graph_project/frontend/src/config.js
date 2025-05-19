/**
 * Application configuration
 */

// API configuration
const API_CONFIG = {
  baseUrl: 'http://localhost:5000/api',
  endpoints: {
    health: '/health',
    schema: '/schema',
    import: '/import',
    graph: '/graph',
    graphUpdate: '/graph/update',
    query: '/query'
  }
};

// Neo4j configuration (for frontend reference only)
const NEO4J_CONFIG = {
  uri: 'bolt://localhost:7687',
  user: 'neo4j',
  // Note: We don't include the password in frontend code for security reasons
  // This is just for reference to match the backend configuration
};

export { API_CONFIG, NEO4J_CONFIG };
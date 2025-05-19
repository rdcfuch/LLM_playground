from neo4j import GraphDatabase
from config import NEO4J_CONFIG  # Import the configuration

class Neo4jConnector:
    def __init__(self, uri=None, user=None, password=None):
        """Initialize Neo4j connection"""
        self.uri = uri or NEO4J_CONFIG["uri"]
        self.user = user or NEO4J_CONFIG["user"]
        self.password = password or NEO4J_CONFIG["password"]
        self.driver = None
        
    def connect(self):
        """Connect to Neo4j database"""
        if not self.driver:
            try:
                self.driver = GraphDatabase.driver(
                    self.uri, 
                    auth=(self.user, self.password)
                )
                return True
            except Exception as e:
                print(f"Failed to connect to Neo4j: {e}")
                return False
        return True
        
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            self.driver = None
            
    def query(self, query, params=None):
        """Execute a Cypher query"""
        if not self.connect():
            return []
            
        try:
            with self.driver.session() as session:
                result = session.run(query, params or {})
                return [record.data() for record in result]
        except Exception as e:
            print(f"Query failed: {e}")
            return []
            
    def test_connection(self):
        """Test the Neo4j connection"""
        if not self.connect():
            return False
            
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                return result.single()["test"] == 1
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
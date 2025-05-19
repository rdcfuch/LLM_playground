from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

# Import modules
from data_import import DataImporter
from schema_manager import SchemaManager
from llm_parser import LLMParser
from neo4j import GraphDatabase
from neo4j_connector import Neo4jConnector
from config import NEO4J_CONFIG  # Import the configuration
import pandas as pd
import PyPDF2
import rdflib
from jsonschema import validate

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Neo4j connection
class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

# Initialize Neo4j connection using config
neo4j_uri = NEO4J_CONFIG["uri"]
neo4j_user = NEO4J_CONFIG["user"]
neo4j_password = NEO4J_CONFIG["password"]

print(f"Connecting to Neo4j at {neo4j_uri} with user {neo4j_user}")
try:
    neo4j_conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
    # Test connection with a simple query
    test_result = neo4j_conn.query("RETURN 1 as test")
    print(f"Neo4j connection successful! Test result: {test_result}")
except Exception as e:
    print(f"Neo4j connection failed: {str(e)}")
    print("Make sure Neo4j is running and credentials are correct")

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/schema', methods=['POST'])
def create_schema():
    schema_data = request.json
    # Validate schema format (JSON-LD, OWL, or RDFS)
    # Store schema in Neo4j
    # Example: Create constraints and indexes based on schema
    
    try:
        # For JSON-LD schema
        if '@context' in schema_data:
            # Process JSON-LD schema
            # Create graph constraints based on schema
            query = """
            CREATE CONSTRAINT IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE
            """
            neo4j_conn.query(query)
            return jsonify({"status": "success", "message": "Schema created successfully"})
        else:
            return jsonify({"status": "error", "message": "Invalid schema format"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/import', methods=['POST'])
def import_data():
    print("\n=== /api/import endpoint called ===")
    print(f"Request files: {request.files}")
    print(f"Request headers: {request.headers}")
    
    if 'file' not in request.files:
        print("Error: No file provided in request")
        return jsonify({"status": "error", "message": "No file provided"})
    
    file = request.files['file']
    file_extension = os.path.splitext(file.filename)[1].lower()
    print(f"Processing file: {file.filename} (extension: {file_extension})")
    
    try:
        if file_extension in ['.xlsx', '.csv']:
            # Process Excel/CSV
            if file_extension == '.xlsx':
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file)
            
            # Map data to schema and import to Neo4j
            # This is a simplified example
            for _, row in df.iterrows():
                # Create nodes and relationships based on mapping
                pass
                
        elif file_extension == '.json':
            # Process JSON/JSON-LD
            data = json.load(file)
            # Import JSON data to Neo4j
            
        elif file_extension == '.pdf':
            # Process PDF
            reader = PyPDF2.PdfFileReader(file)
            text = ""
            for page_num in range(reader.numPages):
                text += reader.getPage(page_num).extractText()
            # Process extracted text
            
        elif file_extension == '.txt':
            # Process text file
            text = file.read().decode('utf-8')
            print(f"Text file content (first 100 chars): {text[:100]}...")
            
            # Get API key from request header
            api_key = request.headers.get('X-API-KEY')
            print(f"API Key provided: {'Yes' if api_key else 'No'}")
            
            # Create a new LLMParser instance with the provided API key
            parser = LLMParser(api_key=api_key)
            
            # Parse the text into JSON-LD
            print("Calling LLMParser to parse text to JSON-LD")
            parsed_data = parser.parse_text_to_jsonld(text)
            print(f"Parsed data received (type: {type(parsed_data)})")
            
            # Import the parsed data into Neo4j
            print("Importing parsed data into Neo4j")
            importer = DataImporter(neo4j_conn)
            importer.import_jsonld_data(parsed_data)
            
            return jsonify({
                "status": "success", 
                "message": "Text file processed and imported successfully",
                "parsed_data": parsed_data
            })
            
        else:
            return jsonify({"status": "error", "message": f"Unsupported file format: {file_extension}"})
        
        return jsonify({"status": "success", "message": "Data imported successfully"})
    
    except Exception as e:
        print(f"Error in import_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/graph', methods=['GET'])
def get_graph():
    # Query Neo4j for graph data
    query = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m LIMIT 1000
    """
    
    try:
        results = neo4j_conn.query(query)
        
        # Transform Neo4j results to graph format
        nodes = []
        links = []
        node_ids = set()
        
        for record in results:
            source = record['n']
            target = record['m']
            relationship = record['r']
            
            # Add source node if not already added
            if source.id not in node_ids:
                nodes.append({
                    "id": source.id,
                    "label": list(source.labels)[0],
                    "properties": dict(source)
                })
                node_ids.add(source.id)
            
            # Add target node if not already added
            if target.id not in node_ids:
                nodes.append({
                    "id": target.id,
                    "label": list(target.labels)[0],
                    "properties": dict(target)
                })
                node_ids.add(target.id)
            
            # Add relationship
            links.append({
                "source": source.id,
                "target": target.id,
                "type": relationship.type,
                "properties": dict(relationship)
            })
        
        return jsonify({"nodes": nodes, "links": links})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/query', methods=['POST'])
def execute_query():
    data = request.json
    query_type = data.get('type', 'cypher')
    query = data.get('query', '')
    auth = data.get('auth', {})
    
    # Use provided credentials if available, otherwise use config
    username = auth.get('username') or neo4j_user
    password = auth.get('password') or neo4j_password
    
    try:
        # Create a new connection with the provided credentials
        conn = Neo4jConnection(neo4j_uri, username, password)
        
        if query_type == 'cypher':
            # Execute Cypher query
            result = conn.query(query)
            
            # Convert Neo4j objects to serializable format
            serializable_result = []
            for record in result:
                record_dict = {}
                for key, value in record.items():
                    # Handle Neo4j Node objects
                    if hasattr(value, 'labels') and hasattr(value, 'items'):  # It's a Node
                        node_dict = dict(value.items())
                        node_dict['_labels'] = list(value.labels)
                        record_dict[key] = node_dict
                    # Handle Neo4j Relationship objects
                    elif hasattr(value, 'type') and hasattr(value, 'start_node'):  # It's a Relationship
                        rel_dict = dict(value.items())
                        rel_dict['_type'] = value.type
                        rel_dict['_start_node_id'] = value.start_node.id
                        rel_dict['_end_node_id'] = value.end_node.id
                        record_dict[key] = rel_dict
                    # Handle Neo4j Path objects
                    elif hasattr(value, 'start_node') and hasattr(value, 'relationships'):  # It's a Path
                        record_dict[key] = "Path object (serialized as string)"
                    # Handle primitive types and collections
                    elif isinstance(value, (str, int, float, bool, list, dict)) or value is None:
                        record_dict[key] = value
                    else:
                        # For any other type, convert to string
                        record_dict[key] = str(value)
                serializable_result.append(record_dict)
            
            return jsonify({
                "status": "success",
                "results": serializable_result
            })
        elif query_type == 'sparql':
            # Handle SPARQL queries (if implemented)
            return jsonify({
                "status": "error",
                "message": "SPARQL queries are not yet implemented"
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Unsupported query type: {query_type}"
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/graph/update', methods=['POST'])
def update_graph():
    update_data = request.json
    operation = update_data.get('operation')
    
    try:
        if operation == 'add_node':
            # Add node to graph
            node_data = update_data.get('node')
            # Fix this query:
            query = f"""
            CREATE (n:{node_data['label']}) 
            SET n = $properties
            RETURN n
            """
            neo4j_conn.query(query, {"properties": node_data['properties']})
            
        elif operation == 'add_relationship':
            # Add relationship to graph
            rel_data = update_data.get('relationship')
            query = f"""
            MATCH (a), (b)
            WHERE id(a) = $source_id AND id(b) = $target_id
            CREATE (a)-[r:{rel_data['type']} $properties]->(b)
            RETURN r
            """
            neo4j_conn.query(query, {
                "source_id": rel_data['source'],
                "target_id": rel_data['target'],
                "properties": rel_data['properties']
            })
            
        elif operation == 'update_node':
            # Update node properties
            node_data = update_data.get('node')
            query = """
            MATCH (n)
            WHERE id(n) = $node_id
            SET n += $properties
            RETURN n
            """
            neo4j_conn.query(query, {
                "node_id": node_data['id'],
                "properties": node_data['properties']
            })
            
        elif operation == 'delete_node':
            # Delete node
            node_id = update_data.get('node_id')
            query = """
            MATCH (n)
            WHERE id(n) = $node_id
            DETACH DELETE n
            """
            neo4j_conn.query(query, {"node_id": node_id})
            
        else:
            return jsonify({"status": "error", "message": f"Unsupported operation: {operation}"})
        
        return jsonify({"status": "success", "message": "Graph updated successfully"})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/parse-unstructured', methods=['POST'])
def parse_unstructured_text():
    """
    Parse unstructured text into JSON-LD format using LLM
    """
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({"status": "error", "message": "No text provided"})
        
        # Get API key from request header
        api_key = request.headers.get('X-API-KEY')
        
        # Create a new LLMParser instance with the provided API key
        parser = LLMParser(api_key=api_key)
        
        # Call the LLM parser service
        parsed_data = parser.parse_text_to_jsonld(text)

        print("Parsed data:", parsed_data)
        
        return jsonify({
            "status": "success", 
            "parsed_data": parsed_data
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/import-jsonld', methods=['POST'])
def import_jsonld_data():
    """
    Import JSON-LD data directly into the knowledge graph
    """
    try:
        data = request.json
        jsonld_data = data.get('data', {})
        
        if not jsonld_data:
            return jsonify({"status": "error", "message": "No JSON-LD data provided"})
        
        # Import the JSON-LD data into the graph database
        importer = data_import.DataImporter(neo4j_conn)
        result = importer.import_jsonld_data(jsonld_data)
        
        return jsonify({
            "status": "success",
            "message": "Data imported successfully",
            "details": result
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)



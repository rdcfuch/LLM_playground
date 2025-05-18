import pandas as pd
import json
import xml.etree.ElementTree as ET
from pdfminer.high_level import extract_text
import rdflib
from rdflib import Graph, URIRef, RDF  # Add these imports

class DataImporter:
    def __init__(self, neo4j_conn):
        self.neo4j_conn = neo4j_conn
        
    def import_excel(self, file_path, mapping):
        """Import data from Excel/CSV files"""
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Apply mapping to transform data according to schema
        # TODO: Implement mapping logic
        
        return df
    
    def import_json(self, file_path, mapping):
        """Import data from JSON files"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Apply mapping
        # TODO: Implement mapping logic
        
        return data
    
    def import_jsonld(self, file_path):
        """Import data from JSON-LD files"""
        g = rdflib.Graph()
        g.parse(file_path, format='json-ld')
        
        # Convert to Neo4j compatible format
        # TODO: Implement conversion logic
        
        return g
    
    def import_xml(self, file_path, mapping):
        """Import data from XML files"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Apply mapping
        # TODO: Implement mapping logic
        
        return root
    
    def import_pdf(self, file_path):
        """Extract text from PDF files"""
        text = extract_text(file_path)
        
        # Process extracted text
        # TODO: Implement text processing logic
        
        return text
    
    def validate_data(self, data, schema):
        """Validate imported data against schema"""
        # TODO: Implement validation logic
        return True, []  # Valid, no errors
    
    def import_jsonld_data(self, jsonld_data):
        """Import JSON-LD data directly"""
        print("\n=== Starting JSON-LD Import ===")
        print(f"Input data type: {type(jsonld_data)}")
        
        # Convert the JSON-LD data to a string if it's a dict
        if isinstance(jsonld_data, dict):
            print(f"Converting dict to JSON string. Keys: {list(jsonld_data.keys())}")
            jsonld_str = json.dumps(jsonld_data)
        else:
            jsonld_str = jsonld_data
            print(f"Using provided string data (length: {len(jsonld_str)})")
        
        # Parse the JSON-LD into an RDFLib graph
        g = Graph()
        try:
            g.parse(data=jsonld_str, format='json-ld')
            print(f"Successfully parsed JSON-LD. Graph contains {len(g)} triples")
        except Exception as e:
            print(f"Error parsing JSON-LD: {str(e)}")
            raise
        
        # Process the graph and import to Neo4j
        imported_nodes = []
        imported_relationships = []
        
        # Extract entities (nodes) from the graph
        entities = {}
        print("\n--- Extracting Entities ---")
        type_triples = list(g.triples((None, RDF.type, None)))
        print(f"Found {len(type_triples)} entities with RDF.type")
        
        # Inside the for loop where entities are processed
        for s, p, o in g.triples((None, RDF.type, None)):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                entity_id = str(s)
                entity_type = str(o).split('/')[-1]
                print(f"\nProcessing entity: {entity_id}")
                print(f"Entity type: '{entity_type}'")
                
                # Get all properties for this entity
                properties = {}
                for ps, pp, po in g.triples((s, None, None)):
                    if pp != RDF.type:
                        prop_name = str(pp).split('/')[-1]
                        if not isinstance(po, URIRef):
                            properties[prop_name] = str(po)
                
                print(f"Properties: {properties}")
                
                entities[entity_id] = {
                    'id': entity_id,
                    'type': entity_type,
                    'properties': properties
                }
                
                # Create node in Neo4j
                # Make sure entity_type is not empty
                if not entity_type:
                    entity_type = "Entity"  # Default label if none is provided
                    print(f"Using default entity type: {entity_type}")
                
                # Debug the Cypher query
                query = f"""
                CREATE (n:{entity_type})
                SET n = $properties
                RETURN id(n) as id
                """
                print(f"Executing Cypher query: {query}")
                print(f"With parameters: {properties}")
                
                try:
                    result = self.neo4j_conn.query(query, {"properties": properties})
                    neo4j_id = result[0]['id'] if result else None
                    print(f"Node created with Neo4j ID: {neo4j_id}")
                except Exception as e:
                    print(f"Error creating node: {str(e)}")
                    raise
                
                if neo4j_id:
                    entities[entity_id]['neo4j_id'] = neo4j_id
                    imported_nodes.append({
                        'id': neo4j_id,
                        'type': entity_type,
                        'properties': properties
                    })
        
        # Extract relationships
        print("\n--- Extracting Relationships ---")
        relationship_count = 0
        for s, p, o in g:
            if isinstance(s, URIRef) and isinstance(o, URIRef) and p != RDF.type:
                relationship_count += 1
                if str(s) in entities and str(o) in entities:
                    source_id = entities[str(s)].get('neo4j_id')
                    target_id = entities[str(o)].get('neo4j_id')
                    rel_type = str(p).split('/')[-1].upper()
                    
                    print(f"\nProcessing relationship: {str(s)} --[{rel_type}]--> {str(o)}")
                    print(f"Source Neo4j ID: {source_id}, Target Neo4j ID: {target_id}")
                    
                    if source_id and target_id:
                        # Create relationship in Neo4j
                        query = f"""
                        MATCH (a), (b)
                        WHERE id(a) = $source_id AND id(b) = $target_id
                        CREATE (a)-[r:{rel_type}]->(b)
                        RETURN id(r) as id
                        """
                        print(f"Executing Cypher query: {query}")
                        print(f"With parameters: source_id={source_id}, target_id={target_id}")
                        
                        try:
                            result = self.neo4j_conn.query(query, {
                                "source_id": source_id,
                                "target_id": target_id
                            })
                            
                            rel_id = result[0]['id'] if result else None
                            print(f"Relationship created with Neo4j ID: {rel_id}")
                            
                            if rel_id:
                                imported_relationships.append({
                                    'id': rel_id,
                                    'type': rel_type,
                                    'source': source_id,
                                    'target': target_id
                                })
                        except Exception as e:
                            print(f"Error creating relationship: {str(e)}")
                    else:
                        print("Skipping relationship creation - missing source or target Neo4j ID")
                else:
                    print(f"Skipping relationship - entities not found in graph: {str(s)} or {str(o)}")
        
        print(f"\nTotal relationships found: {relationship_count}")
        print(f"Successfully imported relationships: {len(imported_relationships)}")
        
        return {
            'nodes': imported_nodes,
            'relationships': imported_relationships
        }
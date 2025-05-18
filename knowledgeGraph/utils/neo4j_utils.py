import os
from fastapi import HTTPException

def export_to_neo4j_cypher(graph_docs, file_path="knowledge_graph_neo4j.cypher"):
    """
    Exports GraphDocument objects to a Cypher script file for Neo4j.

    Parameters:
    - graph_docs: A list of GraphDocument objects.
    - file_path: The path to the output Cypher file.
    """
    cypher_statements = []
    for graph_doc in graph_docs:
        for node in graph_doc.nodes:
            node_id_escaped = node.id.replace("'", "\\'")
            node_type_escaped = node.type.replace("'", "\\'")
            cypher_statements.append(f"CREATE (:`{node_type_escaped}` {{id: '{node_id_escaped}', type: '{node_type_escaped}'}})")

        for rel in graph_doc.relationships:
            source_id_escaped = rel.source.id.replace("'", "\\'")
            target_id_escaped = rel.target.id.replace("'", "\\'")
            rel_type_escaped = rel.type.replace("'", "\\'")
            cypher_statements.append(
                f"MATCH (a {{id: '{source_id_escaped}'}}), (b {{id: '{target_id_escaped}'}}) "
                f"CREATE (a)-[:`{rel_type_escaped}`]->(b)"
            )

    try:
        with open(file_path, 'w') as f:
            for stmt in cypher_statements:
                f.write(stmt + ';\n')
        print(f"Knowledge graph exported to {file_path}")
    except Exception as e:
        print(f"Error writing Cypher file: {e}")
        raise HTTPException(status_code=500, detail=f"Error writing Cypher file: {e}")
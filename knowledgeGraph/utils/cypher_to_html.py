import re
import json
from pathlib import Path

def visualize_from_cypher_to_html(cypher_file_path, output_html_path):
    """
    Reads a Neo4j Cypher file and generates an HTML file to visualize the knowledge graph using Vis.js.
    Ensures MATCH statements are parsed correctly for edges, with black edges and visible relationship labels.
    
    Args:
        cypher_file_path (str): Path to the input Cypher file
        output_html_path (str): Path for the output HTML file
    """
    # Initialize lists for nodes and edges
    nodes = []
    edges = []
    node_ids = set()
    
    # Read Cypher file
    try:
        with open(cypher_file_path, 'r') as file:
            cypher_content = file.read()
    except FileNotFoundError:
        print(f"Error: Cypher file {cypher_file_path} not found.")
        return
    
    # Parse CREATE statements for nodes
    create_pattern = r"CREATE\s*\(:`?(\w+)`?\s*\{id:\s*'([^']+)'\s*,\s*type:\s*'([^']+)'\}\s*\);"
    for match in re.finditer(create_pattern, cypher_content):
        node_type, node_id, _ = match.groups()
        node_id = node_id.strip()
        if node_id not in node_ids:
            nodes.append({
                'id': node_id,
                'label': f"{node_id}\n({node_type})",
                'group': node_type
            })
            node_ids.add(node_id)
    print(f"Parsed {len(nodes)} nodes: {[n['id'] for n in nodes]}")
    
    # Parse MATCH statements for relationships and infer missing nodes
    # More flexible regex to handle whitespace and line breaks
    rel_pattern = r"MATCH\s*\(\s*a\s*\{id:\s*'([^']+)'\}\s*\)\s*,\s*\(\s*b\s*\{id:\s*'([^']+)'\}\s*\)\s*CREATE\s*\(\s*a\s*\)-\[:`?(\w+)`?\]->\(\s*b\s*\)\s*;"
    unmatched_lines = []
    for match in re.finditer(rel_pattern, cypher_content, re.DOTALL):
        source_id, target_id, rel_type = match.groups()
        source_id = source_id.strip()
        target_id = target_id.strip()
        
        # Add source node if missing
        if source_id not in node_ids:
            nodes.append({
                'id': source_id,
                'label': f"{source_id}\n(Inferred)",
                'group': 'Inferred'
            })
            node_ids.add(source_id)
            print(f"Inferred node: {source_id}")
        
        # Add target node if missing
        if target_id not in node_ids:
            nodes.append({
                'id': target_id,
                'label': f"{target_id}\n(Inferred)",
                'group': 'Inferred'
            })
            node_ids.add(target_id)
            print(f"Inferred node: {target_id}")
        
        # Add edge
        edges.append({
            'from': source_id,
            'to': target_id,
            'label': rel_type,
            'arrows': 'to'
        })
    
    # Log unmatched MATCH statements for debugging
    match_lines = re.findall(r"MATCH.*?CREATE\s*\(a\)-\[:\w+]->\(b\);", cypher_content, re.DOTALL)
    for line in match_lines:
        if not re.search(rel_pattern, line, re.DOTALL):
            unmatched_lines.append(line.strip())
    if unmatched_lines:
        print(f"Unmatched MATCH statements ({len(unmatched_lines)}): {unmatched_lines}")
    
    print(f"Parsed {len(edges)} edges: {[(e['from'], e['to'], e['label']) for e in edges]}")
    
    # Convert nodes and edges to JSON strings
    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)
    
    # Generate HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Knowledge Graph Visualization</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js"></script>
    <style type="text/css">
        #network {{
            width: 100%;
            height: 600px;
            border: 1px solid lightgray;
        }}
    </style>
</head>
<body>
    <div id="network"></div>
    <script type="text/javascript">
        // Create nodes
        var nodes = new vis.DataSet({nodes_json});
        
        // Create edges
        var edges = new vis.DataSet({edges_json});
        
        // Create network
        var container = document.getElementById('network');
        var data = {{
            nodes: nodes,
            edges: edges
        }};
        var options = {{
            nodes: {{
                shape: 'dot',
                size: 16,
                font: {{
                    size: 12,
                    face: 'arial'
                }}
            }},
            edges: {{
                width: 2,
                color: {{ color: '#000000', highlight: '#000000' }},  // Black edges
                font: {{
                    size: 14,  // Larger labels for relationships
                    align: 'middle',
                    strokeWidth: 0,  // No background
                    color: '#000000'  // Black labels
                }},
                arrows: {{
                    to: {{ enabled: true, scaleFactor: 0.7 }}
                }},
                smooth: {{ enabled: true, type: 'dynamic' }}
            }},
            physics: {{
                enabled: false  // Disable physics to remove elastic effect
            }},
            layout: {{
                improvedLayout: true
            }},
            interaction: {{
                dragNodes: true,  // Allow dragging nodes
                dragView: true    // Allow dragging the view
            }}
        }};
        var network = new vis.Network(container, data, options);
        
        // Log for debugging
        console.log('Nodes:', nodes.get());
        console.log('Edges:', edges.get());
    </script>
</body>
</html>"""
    
    # Write to output HTML file
    try:
        with open(output_html_path, 'w') as file:
            file.write(html_content)
        print(f"HTML file generated successfully at {output_html_path}")
    except Exception as e:
        print(f"Error writing HTML file: {e}")

# Example usage
if __name__ == "__main__":
    visualize_from_cypher_to_html("knowledge_graph_neo4j.cypher", "knowledge_graph_viz.html")
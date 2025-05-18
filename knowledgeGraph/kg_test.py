# kg_test.py
# Script to extract and visualize a knowledge graph from a text using LangChain and OpenAI LLM

import asyncio
import os
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
import networkx as nx
import matplotlib.pyplot as plt
import logging
import re
import json

# -----------------------------
# Configuration & Initialization
# -----------------------------

# Set your OpenAI API key (ensure this is kept secure in production)
os.environ["OPENAI_API_KEY"] = "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"

# Initialize the LLM
llm = ChatOpenAI(model='gpt-4o')

# Example text to extract entities and relationships from
# text = """
# Marie Curie, 7 November 1867 – 4 July 1934, was a Polish and naturalised-French physicist and chemist who conducted pioneering research on radioactivity.
# She was the first woman to win a Nobel Prize, the first person to win a Nobel Prize twice, and the only person to win a Nobel Prize in two scientific fields.
# Her husband, Pierre Curie, was a co-winner of her first Nobel Prize, making them the first-ever married couple to win the Nobel Prize and launching the Curie family legacy of five Nobel Prizes.
# She was, in 1906, the first woman to become a professor at the University of Paris.
# Also, Robin Williams!
# """
text = """The CMBS Security MSBAM 2017-C34, rated by S&P, is a diversified commercial mortgage-backed security supported by a variety of loans across multiple metropolitan regions. One of the key components is a $25.3M loan on 444 West Ocean Blvd, Long Beach, originated by JPMorgan, and secured by a property leased to Premier Business Centers. The asset, located in Los Angeles, CA, has been affected by macroeconomic events such as tariffs and international trade risk. Another critical loan in the pool is a $30M loan on 888 East Ocean, Short Beach, originated by Wells Fargo, tied to a property occupied by Premier Industry Centers and located in San Francisco, CA.

Additional support for the security includes a $15.7M loan on 101 Market Street, originated by CitiBank, secured by a mixed-use property in downtown Oakland, CA. This asset, leased to Bluewave Financial Group and FlexStart Co-Working, has recently seen fluctuations due to local regulatory shifts and commercial zoning reform. Another $42M loan on 707 Mission Street, originated by Bank of America, is backed by a tech campus in San Jose, leased primarily to InnovateX Labs and BitCore Systems. The area has experienced strong demand but is also exposed to macro risks such as interest rate volatility and talent migration.

A $19.5M loan on 3200 Wilshire Blvd in Koreatown, Los Angeles, originated by Morgan Stanley, supports a retail-commercial complex leased to K-Fashion World and Urban Fresh Foods. This asset has seen exposure to consumer spending trends and shifting retail behaviors. Finally, the $23M loan on 500 2nd Avenue in Seattle, WA, originated by Goldman Sachs, is backed by a logistics facility occupied by Pacific Northwest Freight Co., located in an industrial corridor experiencing rising land costs due to zoning changes and port congestion."""

# Wrap the text in a LangChain Document
documents = [Document(page_content=text)]

# Optionally, you can use a schema-free transformer
no_schema = LLMGraphTransformer(llm=llm)

# -----------------------------
# Neo4j Export Function
# -----------------------------

def export_to_neo4j_cypher(graph_docs, file_path="knowledge_graph_neo4j.cypher"):
    """
    Exports GraphDocument objects to a Cypher script file for Neo4j.

    Parameters:
    - graph_docs: A list of GraphDocument objects.
    - file_path: The path to the output Cypher file.
    """
    cypher_statements = []

    # Create constraints for uniqueness if needed (optional, but good practice)
    # Example: cypher_statements.append("CREATE CONSTRAINT ON (n:Node) ASSERT n.id IS UNIQUE;")

    for graph_doc in graph_docs:
        # Create nodes
        for node in graph_doc.nodes:
            # Escape single quotes in node id and type for Cypher query
            node_id_escaped = node.id.replace("'", "\\'")
            node_type_escaped = node.type.replace("'", "\\'")
            # For simplicity, we'll store the type as a property as well, though Neo4j labels handle this.
            # You can add more properties if your nodes have them.
            cypher_statements.append(f"CREATE (:`{node_type_escaped}` {{id: '{node_id_escaped}', type: '{node_type_escaped}'}})")

        # Create relationships
        for rel in graph_doc.relationships:
            source_id_escaped = rel.source.id.replace("'", "\\'")
            target_id_escaped = rel.target.id.replace("'", "\\'")
            rel_type_escaped = rel.type.replace("'", "\\'")
            # You can add properties to relationships if they have them.
            cypher_statements.append(
                f"MATCH (a {{id: '{source_id_escaped}'}}), (b {{id: '{target_id_escaped}'}}) "
                f"CREATE (a)-[:`{rel_type_escaped}`]->(b)"
            )

    with open(file_path, 'w') as f:
        for stmt in cypher_statements:
            f.write(stmt + ';\n')
    print(f"Knowledge graph exported to {file_path}")

# -----------------------------
# HTML Visualization from Cypher Function
# -----------------------------

def visualize_from_cypher_to_html(cypher_file_path, html_output_path="graph.html"):
    """
    Reads a Cypher file, parses nodes and relationships, and generates an HTML file
    with a D3.js force-directed graph visualization.

    Parameters:
    - cypher_file_path: Path to the input Cypher file.
    - html_output_path: Path to the output HTML file.
    """
    nodes = []
    links = []
    node_ids = set()

    # Regex patterns to extract nodes and relationships
    # Node: CREATE (:`NODE_TYPE` {id: 'NODE_ID', type: 'NODE_TYPE'}) - simplified, assumes type is label
    node_pattern = re.compile(r"CREATE \(:`?([^`']+)`? \{id: '([^']*)'(?:, type: '([^']*)')?.*?\}\)")
    # Relationship: MATCH (a {id: 'SOURCE_ID'}), (b {id: 'TARGET_ID'}) CREATE (a)-[:`REL_TYPE`]->(b)
    rel_pattern = re.compile(r"MATCH \(a \{id: '([^']*)'\}\), \(b \{id: '([^']*)'\}\) CREATE \(a\)-\[:`?([^`']+)`?\]->\(b\)")

    try:
        with open(cypher_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('//') or line.startswith('#'):
                    continue

                node_match = node_pattern.match(line)
                if node_match:
                    node_type = node_match.group(1)
                    node_id = node_match.group(2)
                    # Use group(3) if available (type property), else group(1) (label)
                    actual_node_type = node_match.group(3) if node_match.group(3) else node_type
                    if node_id not in node_ids:
                        nodes.append({"id": node_id, "group": actual_node_type})
                        node_ids.add(node_id)
                    continue

                rel_match = rel_pattern.match(line)
                if rel_match:
                    source_id = rel_match.group(1)
                    target_id = rel_match.group(2)
                    rel_type = rel_match.group(3)
                    links.append({"source": source_id, "target": target_id, "type": rel_type})

    except FileNotFoundError:
        print(f"Error: Cypher file not found at {cypher_file_path}")
        return
    except Exception as e:
        print(f"Error processing Cypher file: {e}")
        return

    # HTML template based on test1.html structure
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Knowledge Graph Visualization from Cypher</title>
  <style>
    html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; font-family: sans-serif; }}
    svg {{ width: 100%; height: 100vh; }}
    .node circle {{ stroke: #fff; stroke-width: 1.5px; }}
    .node text {{ pointer-events: none; font-size: 10px; fill: #333; text-anchor: start; dominant-baseline: middle; }}
    .link {{ fill: none; stroke: #999; stroke-opacity: 0.6; }}
    .link-text {{ font-size: 8px; fill: #555; text-anchor: middle; dominant-baseline: central; }}
  </style>
</head>
<body>
  <svg></svg>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <script>
    const nodesData = {json.dumps(nodes, indent=2)};
    const linksData = {json.dumps(links, indent=2)};

    const svg = d3.select("svg"),
          viewWidth = window.innerWidth,
          viewHeight = window.innerHeight;

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    const simulation = d3.forceSimulation(nodesData)
      .force("link", d3.forceLink(linksData).id(d => d.id).distance(150))
      .force("charge", d3.forceManyBody().strength(-400))
      .force("center", d3.forceCenter(viewWidth / 2, viewHeight / 2))
      .force("collide", d3.forceCollide().radius(d => 20)); // Add collision force

    // Arrowhead marker definition
    svg.append('defs').append('marker')
        .attr('id', 'arrowhead')
        .attr('viewBox', '-0 -5 10 10')
        .attr('refX', 19) // Adjusts how far the arrow sits from the node
        .attr('refY', 0)
        .attr('orient', 'auto')
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('xoverflow', 'visible')
      .append('svg:path')
        .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
        .attr('fill', '#999')
        .style('stroke', 'none');

    const link = svg.append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(linksData)
      .join("line")
      .attr("class", "link")
      .attr("stroke-width", 1.5)
      .attr('marker-end', 'url(#arrowhead)');

    const linkText = svg.append("g")
      .attr("class", "link-texts")
      .selectAll("text")
      .data(linksData)
      .join("text")
      .attr("class", "link-text")
      .text(d => d.type);

    const node = svg.append("g")
      .attr("class", "nodes")
      .selectAll("g")
      .data(nodesData)
      .join("g")
      .attr("class", "node")
      .call(drag(simulation));

    node.append("circle")
      .attr("r", 10)
      .attr("fill", d => color(d.group));

    node.append("text")
      .text(d => d.id)
      .attr("x", 15)
      .attr("y", 0);

    simulation.on("tick", () => {{
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("transform", d => `translate(${{d.x}},${{d.y}})`);

      linkText
        .attr("x", d => (d.source.x + d.target.x) / 2)
        .attr("y", d => (d.source.y + d.target.y) / 2);
    }});

    function drag(simulation) {{
      function dragstarted(event, d) {{
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }}

      function dragged(event, d) {{
        d.fx = event.x;
        d.fy = event.y;
      }}

      function dragended(event, d) {{
        if (!event.active) simulation.alphaTarget(0);
        // Keep fx and fy to make nodes stay after drag
        // d.fx = null; 
        // d.fy = null;
      }}

      return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
    }}

    // Optional: Resize handler
    window.addEventListener('resize', () => {{
        svg.attr('width', window.innerWidth).attr('height', window.innerHeight);
        simulation.force("center", d3.forceCenter(window.innerWidth / 2, window.innerHeight / 2)).restart();
    }});
  </script>
</body>
</html>"""

    try:
        with open(html_output_path, 'w') as f:
            f.write(html_template)
        print(f"Knowledge graph visualization saved to {html_output_path}")
    except Exception as e:
        print(f"Error writing HTML file: {e}")

# -----------------------------
# Main Async Function
# -----------------------------

async def main():
    # Define allowed node types for the knowledge graph
    # allowed_nodes = ["Security", "loans", "assets", "Property Types"]
    # # Initialize the graph transformer with allowed node types
    # nodes_defined = LLMGraphTransformer(llm=llm, allowed_nodes=allowed_nodes)
    # # Extract graph documents asynchronously
    # data = await nodes_defined.aconvert_to_graph_documents(documents)
    # print("Transformed graph documents:")
    # print(data)

    # # Export to Neo4j Cypher format
    # if data:
    #     export_to_neo4j_cypher(data, file_path="knowledge_graph_neo4j.cypher")
        
    visualize_from_cypher_to_html("knowledge_graph_neo4j.cypher", html_output_path="graph.html")


# -----------------------------
# Entry Point
# -----------------------------

if __name__ == "__main__":
    asyncio.run(main())
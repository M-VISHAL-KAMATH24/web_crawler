import networkx as nx
import json

def build_link_graph(crawled_data):
    """
    Build a directed graph from crawled link data.
    Nodes: URLs (pages or external resources)
    Edges: Hyperlinks (internal or external)
    """
    G = nx.DiGraph()
    for page in crawled_data:
        src = page['url']
        G.add_node(src, type='page')

        # Add internal links
        for internal_link in page['internal_links']:
            G.add_node(internal_link, type='page')
            G.add_edge(src, internal_link, link_type='internal')

        # Add external links
        for external_link in page['external_links']:
            G.add_node(external_link, type='external')
            G.add_edge(src, external_link, link_type='external')
    return G

if __name__ == "__main__":
    # Load crawled link data
    with open('crawled_links.json', 'r') as f:
        crawled_data = json.load(f)

    # Build the graph
    G = build_link_graph(crawled_data)

    # Explore graph properties
    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

    # Example: Print each node and its out-degree (number of outgoing links)
    for node in G.nodes:
        print(f"Node: {node}, Out-degree: {G.out_degree(node)}")

    # Example: Print edge details
    for src, dst, attrs in G.edges(data=True):
        print(f"Link from {src} to {dst}: {attrs['link_type']}")

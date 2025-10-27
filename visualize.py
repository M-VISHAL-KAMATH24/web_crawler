import networkx as nx
import matplotlib.pyplot as plt
import json

def build_link_graph(crawled_data):
    G = nx.DiGraph()
    for page in crawled_data:
        src = page['url']
        G.add_node(src, type='page')
        for internal_link in page['internal_links']:
            G.add_node(internal_link, type='page')
            G.add_edge(src, internal_link, link_type='internal')
        for external_link in page['external_links']:
            G.add_node(external_link, type='external')
            G.add_edge(src, external_link, link_type='external')
    return G

# Load JSON crawl results
with open('crawled_links.json', 'r') as f:
    crawled_data = json.load(f)

# Build the graph
G = build_link_graph(crawled_data)

# Set node colors: skyblue for 'page', orange for 'external'
node_colors = ['skyblue' if data['type'] == 'page' else 'orange' for node, data in G.nodes(data=True)]
# Set edge colors: green for internal, red for external
edge_colors = ['green' if data['link_type'] == 'internal' else 'red' for u, v, data in G.edges(data=True)]

# Draw the graph
plt.figure(figsize=(8, 6))
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=600, alpha=0.9)
nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrowstyle='->', arrowsize=18, width=2)
nx.draw_networkx_labels(G, pos, font_size=10)

plt.title("Hyperlink Structure: Internal vs External Links")
plt.axis('off')
plt.tight_layout()
plt.show()

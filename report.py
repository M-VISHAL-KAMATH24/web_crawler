import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Load and build graph
with open('crawled_links.json', 'r') as f:
    crawled_data = json.load(f)

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

G = build_link_graph(crawled_data)

# Calculate influence scores
pagerank_scores = nx.pagerank(G)
hits_hubs, hits_authorities = nx.hits(G)

# Crawl statistics
num_nodes = G.number_of_nodes()
num_edges = G.number_of_edges()
num_internal = sum(1 for u,v,d in G.edges(data=True) if d['link_type'] == 'internal')
num_external = sum(1 for u,v,d in G.edges(data=True) if d['link_type'] == 'external')

print(f"Total pages (nodes): {num_nodes}")
print(f"Total links (edges): {num_edges}")
print(f"Internal links: {num_internal}")
print(f"External links: {num_external}")

# Prepare DataFrame
df_pages = pd.DataFrame({
    'page': list(pagerank_scores.keys()),
    'pagerank': list(pagerank_scores.values()),
    'authority': [hits_authorities.get(p, 0) for p in pagerank_scores.keys()],
    'hub': [hits_hubs.get(p, 0) for p in pagerank_scores.keys()],
    'type': [G.nodes[p]['type'] for p in pagerank_scores.keys()]
})

# Save summaries to CSV
df_pages.to_csv('page_influence_summary.csv', index=False)

# Save visualization snapshot
plt.figure(figsize=(8, 6))
pos = nx.spring_layout(G)
node_colors = ['skyblue' if data['type'] == 'page' else 'orange' for node, data in G.nodes(data=True)]
edge_colors = ['green' if data['link_type'] == 'internal' else 'red' for u, v, data in G.edges(data=True)]
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=600, alpha=0.9)
nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrowstyle='->', arrowsize=18, width=2)
nx.draw_networkx_labels(G, pos, font_size=10)
plt.title("Hyperlink Structure: Internal vs External Links")
plt.axis('off')
plt.tight_layout()
plt.savefig('hyperlink_structure.png')
plt.show()

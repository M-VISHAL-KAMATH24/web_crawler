import networkx as nx
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

# Load data and build graph (as in earlier phases)
with open('crawled_links.json', 'r') as f:
    crawled_data = json.load(f)
G = build_link_graph(crawled_data)

# Step 2: PageRank
pagerank_scores = nx.pagerank(G)
sorted_pagerank = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)
print("=== PageRank Results ===")
for url, score in sorted_pagerank:
    print(f"{url}: {score:.4f}")

# Step 3: HITS
hits_hubs, hits_authorities = nx.hits(G)
sorted_authorities = sorted(hits_authorities.items(), key=lambda x: x[1], reverse=True)
sorted_hubs = sorted(hits_hubs.items(), key=lambda x: x[1], reverse=True)

print("\n=== Top Authorities (HITS) ===")
for url, score in sorted_authorities:
    print(f"{url}: {score:.4f}")
print("\n=== Top Hubs (HITS) ===")
for url, score in sorted_hubs:
    print(f"{url}: {score:.4f}")

# PageRank: Assigns importance scores based on structure and quantity of incoming links. Higher scores mean “influential” pages.

# HITS: Calculates two scores for each page:

# Authority: Quality of information a page provides (many high-quality incoming links).

# Hub: How well a page points to other useful resources (many outgoing links to authoritative pages).


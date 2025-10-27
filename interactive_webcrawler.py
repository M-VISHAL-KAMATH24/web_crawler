import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

def get_html(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return None

def extract_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        if full_url.startswith('http'):
            links.add(full_url)
    return links

def is_internal_link(link, base_domain):
    return urlparse(link).netloc == base_domain

def crawl_website(start_url, max_pages=50):
    visited = set()
    to_visit = [start_url]
    base_domain = urlparse(start_url).netloc

    extracted_data = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        print(f"Crawling: {url}")
        html = get_html(url)
        if html is None:
            continue
        links = extract_links(html, url)
        internal_links = set()
        external_links = set()
        for link in links:
            if is_internal_link(link, base_domain):
                internal_links.add(link)
                if link not in visited and link not in to_visit:
                    to_visit.append(link)
            else:
                external_links.add(link)
        visited.add(url)
        extracted_data.append({
            'url': url,
            'internal_links': list(internal_links),
            'external_links': list(external_links)
        })
    return extracted_data

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

def visualize_graph(G):
    node_colors = ['skyblue' if data['type'] == 'page' else 'orange' for _, data in G.nodes(data=True)]
    edge_colors = ['green' if data['link_type'] == 'internal' else 'red' for _, _, data in G.edges(data=True)]

    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, k=0.15, iterations=20)

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=600, alpha=0.9)
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrowstyle='->', arrowsize=15, width=2)
    nx.draw_networkx_labels(G, pos, font_size=8)

    plt.title("Web Hyperlink Structure: Internal (blue) vs External (orange)")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def generate_reports(G):
    pagerank_scores = nx.pagerank(G)
    hits_hubs, hits_authorities = nx.hits(G)

    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    num_internal = sum(1 for _,_,d in G.edges(data=True) if d['link_type'] == 'internal')
    num_external = sum(1 for _,_,d in G.edges(data=True) if d['link_type'] == 'external')

    print(f"\nCrawl Summary:")
    print(f"Total pages (nodes): {num_nodes}")
    print(f"Total links (edges): {num_edges}")
    print(f"Internal links: {num_internal}")
    print(f"External links: {num_external}")

    df_pages = pd.DataFrame({
        'page': list(pagerank_scores.keys()),
        'pagerank': list(pagerank_scores.values()),
        'authority': [hits_authorities.get(p, 0) for p in pagerank_scores.keys()],
        'hub': [hits_hubs.get(p, 0) for p in pagerank_scores.keys()],
        'type': [G.nodes[p]['type'] for p in pagerank_scores.keys()]
    })

    print("\nTop Pages by PageRank:")
    print(df_pages.sort_values(by='pagerank', ascending=False).head(10).to_string(index=False))

    print("\nTop Authorities (HITS):")
    print(df_pages.sort_values(by='authority', ascending=False).head(10).to_string(index=False))

    print("\nTop Hubs (HITS):")
    print(df_pages.sort_values(by='hub', ascending=False).head(10).to_string(index=False))

    # Save summary file
    df_pages.to_csv('page_influence_summary.csv', index=False)
    print("\nDetailed page influence saved to 'page_influence_summary.csv'.")

def main():
    start_url = input("Enter the start URL to crawl (e.g. https://example.com): ").strip()
    if not start_url.startswith('http'):
        print("Please enter a valid URL starting with http or https.")
        return
    print("\nStarting crawl...")
    crawled_data = crawl_website(start_url, max_pages=50)

    print("\nBuilding graph...")
    G = build_link_graph(crawled_data)

    print("\nGenerating visualization...")
    visualize_graph(G)

    print("\nGenerating reports and insights...")
    generate_reports(G)

if __name__ == "__main__":
    main()

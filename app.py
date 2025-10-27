import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

def get_html(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
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

def crawl_website(start_url, max_pages=20):
    visited = set()
    to_visit = [start_url]
    base_domain = urlparse(start_url).netloc
    extracted_data = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
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

def draw_graph(G):
    fig, ax = plt.subplots(figsize=(8, 6))
    node_colors = ['skyblue' if data['type'] == 'page' else 'orange' for node, data in G.nodes(data=True)]
    edge_colors = ['green' if data['link_type'] == 'internal' else 'red' for u, v, data in G.edges(data=True)]
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=550, alpha=0.8, ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True, arrowstyle='->', arrowsize=15, width=2, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
    ax.set_title("Hyperlink Structure Graph")
    ax.axis('off')
    st.pyplot(fig)

def page_analysis(G):
    pagerank_scores = nx.pagerank(G)
    hits_hubs, hits_authorities = nx.hits(G)
    df_pages = pd.DataFrame({
        'page': list(pagerank_scores.keys()),
        'pagerank': list(pagerank_scores.values()),
        'authority': [hits_authorities.get(p, 0) for p in pagerank_scores.keys()],
        'hub': [hits_hubs.get(p, 0) for p in pagerank_scores.keys()],
        'type': [G.nodes[p]['type'] for p in pagerank_scores.keys()]
    })
    top_pagerank = df_pages.sort_values(by='pagerank', ascending=False)
    top_authorities = df_pages.sort_values(by='authority', ascending=False)
    top_hubs = df_pages.sort_values(by='hub', ascending=False)
    return df_pages, top_pagerank, top_authorities, top_hubs

st.title("Interactive Web Crawler Influence Analyzer")

url = st.text_input("Enter the start URL to crawl:", value="https://example.com")
max_pages = st.slider("Max pages to crawl", min_value=5, max_value=50, value=20, step=1)

if st.button('Run Crawler'):
    st.info(f"Starting crawl from {url} ...")
    crawled_data = crawl_website(url, max_pages)
    st.success(f"Crawl finished: {len(crawled_data)} pages processed.")
    G = build_link_graph(crawled_data)

    st.subheader("Hyperlink Network Graph")
    draw_graph(G)

    st.subheader("Analysis & Reports")
    df, top_pr, top_auth, top_hub = page_analysis(G)
    st.write("Crawl Statistics:")
    st.write(f"Total nodes: {G.number_of_nodes()}")
    st.write(f"Total edges: {G.number_of_edges()}")
    st.write(f"Internal links: {sum(1 for u,v,d in G.edges(data=True) if d['link_type']=='internal')}")
    st.write(f"External links: {sum(1 for u,v,d in G.edges(data=True) if d['link_type']=='external')}")

    st.write("Top Pages (PageRank):")
    st.dataframe(top_pr[['page', 'pagerank', 'type']].head(10))

    st.write("Top Authorities (HITS):")
    st.dataframe(top_auth[['page', 'authority', 'type']].head(10))

    st.write("Top Hubs (HITS):")
    st.dataframe(top_hub[['page', 'hub', 'type']].head(10))

    st.write("Full Data:")
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download full report CSV", csv, "page_influence_summary.csv", "text/csv")


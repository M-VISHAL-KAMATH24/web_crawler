import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json

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

def crawl_website(start_url, max_pages=100):
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

def save_to_json(data, filename='crawled_links.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    start_url = 'https://example.com'  # Replace this with the website you want to crawl
    data = crawl_website(start_url, max_pages=20)
    save_to_json(data)
    print(f"Crawled {len(data)} pages. Data saved to 'crawled_links.json'.")

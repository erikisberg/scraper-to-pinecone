import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import os
import json

def is_internal_link(base_url, link):
    """Check if the link is an internal link."""
    return urlparse(link).netloc == urlparse(base_url).netloc

def get_all_links(url, base_url):
    """Return all unique internal links found on a webpage."""
    internal_links = set()
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if not href.startswith(('http://', 'https://')):
                href = urljoin(base_url, href)
            if is_internal_link(base_url, href):
                internal_links.add(href)
    else:
        print(f"Failed to retrieve {url}")
    return internal_links

def filter_elements(soup, unwanted_classes):
    """Remove unwanted elements from the soup object."""
    for class_name in unwanted_classes:
        for tag in soup.find_all(class_=class_name):
            tag.decompose()

def sanitize_url(url):
    """Remove or replace characters in a URL that are not valid in filenames."""
    return url.replace('http://', '').replace('https://', '').replace('/', '_').replace(':', '_')

def extract_metadata(soup, current_page_url):
    """Extract metadata from a BeautifulSoup object."""
    title = soup.find('title').text if soup.find('title') else None
    author = soup.find(id="author").text if soup.find(id="author") else None
    publish_date = soup.find(id="publish-date").text if soup.find(id="publish-date") else None
    tags = [tag.text for tag in soup.find_all(id="tag")]
    url = current_page_url

    metadata = {
        'title': title,
        'author': author,
        'publish_date': publish_date,
        'tags': tags,
        'url': url
    }
    return metadata

def scrape_site_content(base_url, limit=5):
    """Scrape all text from a site starting with the base URL."""
    print(f"Starting to scrape {base_url} with limit {limit}")
    session = requests.Session()  # Using a session for efficiency
    to_visit = set([base_url])
    visited = set()
    page_count = 0

    # Create the directory to store the JSON files if it doesn't exist
    if not os.path.exists('websites'):
        os.makedirs('websites')

    while to_visit and page_count < limit:
        current_page = to_visit.pop()
        visited.add(current_page)
        filepath = os.path.join('websites', sanitize_url(current_page) + '.json')
        if os.path.exists(filepath):
            print(f"Skipping {current_page} because JSON file already exists")
        else:
            response = session.get(current_page)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                filter_elements(soup, ['navbar', 'footer', 'payment-wall', 'h1-alternative', 'h3-alternative', 'img', 'payment-wall'])
                # Extract metadata
                metadata = extract_metadata(soup, current_page)
                # Save the text content and metadata to a JSON file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump({'metadata': metadata, 'content': soup.text}, f, ensure_ascii=False, indent=4)
                page_count += 1  # Only increment the page count if a new page was scraped
            else:
                print(f"Failed to retrieve {current_page}")
        internal_links = get_all_links(current_page, base_url)
        to_visit.update(internal_links - visited)

base_url = "https://impactloop.se/"
scrape_site_content(base_url)

print("Finished scraping")

import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def is_internal_link(base_url, link):
    """Check if the link is an internal link."""
    return urlparse(link).netloc == urlparse(base_url).netloc

def get_all_links(url, base_url):
    """Return all unique internal links found on a webpage."""
    internal_links = set()
    response = requests.get(url)
    print(response.headers['Content-Type'])
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

def scrape_site_content(base_url, limit=10):
    """Scrape all text from a site starting with the base URL."""
    print(f"Starting to scrape {base_url} with limit {limit}")
    session = requests.Session()  # Using a session for efficiency
    to_visit = set([base_url])
    visited = set()
    site_content = {}
    page_count = 0

    while to_visit and page_count < limit:
        current_page = to_visit.pop()
        visited.add(current_page)
        response = session.get(current_page)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            charset_meta = soup.find('meta', charset=True)
            if charset_meta:
                response.encoding = charset_meta['charset']
            filter_elements(soup, ['navbar', 'footer', 'payment-wall', 'h1-alternative', 'h3-alternative'])
            page_text = [tag.get_text(strip=True) for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'])]
            site_content[current_page] = page_text
            # ...
            internal_links = get_all_links(current_page, base_url)
            to_visit.update(internal_links - visited)
            page_count += 1
        else:
            print(f"Failed to retrieve {current_page}")
    return site_content

def save_as_html(file, url, content):
    """Write the scraped content to an HTML file without HTML tags."""
    print(f"Saving content from {url}")
    file.write(f"{url}\n")
    for paragraph in content:
        file.write(paragraph + "\n")

base_url = "https://impactloop.se/"
site_content = scrape_site_content(base_url)

filename = "scraped_content.html"
with open(filename, "w", encoding="utf-8") as file:
    for url, content in site_content.items():
        save_as_html(file, url, content)

print("Finished scraping")
# Example to print the content from each page (you might want to save this instead)
for url, content in site_content.items():
    print(f"URL: {url}")
    print("Content:", content[:5], "\n...")  # Printing first 5 elements for brevity

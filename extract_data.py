import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
from collections import deque
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_same_domain(base_url, link_url):
    base_domain = urlparse(base_url).netloc
    link_domain = urlparse(link_url).netloc
    return base_domain == link_domain

def scrape_page(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title and main text (customize selectors for apurba.com.bd if needed)
        title = soup.title.string.strip() if soup.title else "No Title"
        text = ' '.join([p.get_text().strip() for p in soup.find_all('p')])
        
        return {
            'url': url,
            'title': title,
            'text': text
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Error scraping {url}: {e}")
        return None

def crawl_website(start_url, max_pages=50, delay=2):
    # Headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    visited = set()
    to_visit = deque([start_url])
    all_data = []
    
    while to_visit and len(all_data) < max_pages:
        url = to_visit.popleft()
        if url in visited:
            continue
        
        logging.info(f"Scraping: {url}")
        page_data = scrape_page(url, headers)
        if page_data:
            all_data.append(page_data)
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find and add new links
            for link in soup.find_all('a', href=True):
                new_url = urljoin(url, link['href'])
                if is_same_domain(start_url, new_url) and new_url not in visited:
                    to_visit.append(new_url)
            
            visited.add(url)
            time.sleep(delay)  # Delay to avoid rate limiting
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching links from {url}: {e}")
        
        # Save progress incrementally
        with open('doctors_website_data.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
    
    logging.info(f"Scraped {len(all_data)} pages. Data saved to website_data.json")
    return all_data

# Run the crawler
if __name__ == "__main__":
    crawl_data = crawl_website("https://www.doctorbangladesh.com/", max_pages=100, delay=3)
    print("crawl_data:", crawl_data)
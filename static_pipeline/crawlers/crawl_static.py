import requests
from bs4 import BeautifulSoup
import os
import json
import re
import sys
import time
from urllib.parse import urljoin, urlparse

# Add root directory to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(ROOT_DIR)

from static_pipeline.utils.file_utils import save_html, save_json, safe_filename

def extract_metadata_from_url(url):
    """
    Extract potential metadata from URL structure
    """
    metadata = {
        'satellite': None,
        'parameter': None,
        'region': None
    }
    
    url_lower = url.lower()
    
    # Extract satellite info
    satellites = ['insat-3dr', 'insat-3d', 'insat-3a', 'insat-3ds', 'kalpana-1', 
                  'megha-tropiques', 'saral', 'oceansat-2', 'oceansat-3', 'scatsat-1']
    
    for satellite in satellites:
        if satellite in url_lower:
            metadata['satellite'] = satellite.upper()
            break
    
    # Extract parameter info from URL
    if 'rainfall' in url_lower:
        metadata['parameter'] = 'rainfall'
    elif 'water' in url_lower:
        metadata['parameter'] = 'water'
    elif 'ocean' in url_lower:
        metadata['parameter'] = 'ocean'
    elif 'cloud' in url_lower:
        metadata['parameter'] = 'cloud'
    elif 'moisture' in url_lower:
        metadata['parameter'] = 'soil_moisture'
    
    return metadata

def crawl_page(url, max_retries=3, delay=1):
    """
    Crawl a single page with retry logic
    """
    for attempt in range(max_retries):
        try:
            print(f"[CRAWLING] {url} (attempt {attempt + 1})")
            
            # Add headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            # Extract title
            title = soup.title.string if soup.title else "Untitled"
            title = title.strip()
            
            # Extract paragraphs
            paragraphs = []
            for p in soup.find_all('p'):
                text = p.get_text().strip()
                if text:  # Only add non-empty paragraphs
                    paragraphs.append(text)
            
            # Extract headings
            headings = []
            for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                text = h.get_text().strip()
                if text:
                    headings.append(text)
            
            # Extract links to PDFs and DOCX files
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    href = urljoin(url, href)
                
                # Check if it's a PDF or DOCX file
                if any(ext in href.lower() for ext in ['.pdf', '.docx']):
                    links.append(href)
            
            # Extract metadata
            metadata = extract_metadata_from_url(url)
            
            # Prepare output data
            out = {
                'url': url,
                'title': title,
                'headings': headings,
                'paragraphs': paragraphs,
                'pdf_links': links,
                'metadata': metadata
            }

            # Generate safe filename
            filename_base = safe_filename(title)
            
            # Save HTML and JSON
            html_success = save_html(filename_base, html)
            json_success = save_json(filename_base + '.json', out)
            
            if html_success and json_success:
                print(f"[SUCCESS] Processed: {url}")
                return True
            else:
                print(f"[ERROR] Failed to save files for: {url}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed for {url} (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                print(f"[FAILED] Max retries reached for {url}")
                return False
        except Exception as e:
            print(f"[ERROR] Unexpected error processing {url}: {e}")
            return False

def main():
    """
    Main crawling function
    """
    # Ensure output directories exist
    os.makedirs('static_pipeline/output/raw_html', exist_ok=True)
    os.makedirs('static_pipeline/output/json_pages', exist_ok=True)
    
    # Load URL list
    url_file = 'static_pipeline/crawlers/url_list.txt'
    
    if not os.path.exists(url_file):
        print(f"[ERROR] URL list file not found: {url_file}")
        return
    
    with open(url_file, 'r') as f:
        urls = [url.strip() for url in f.readlines() if url.strip()]
    
    print(f"[INFO] Found {len(urls)} URLs to crawl")
    
    success_count = 0
    failed_count = 0
    
    for i, url in enumerate(urls, 1):
        print(f"\n[PROGRESS] {i}/{len(urls)} URLs processed")
        
        if crawl_page(url):
            success_count += 1
        else:
            failed_count += 1
        
        # Small delay between requests to be respectful
        time.sleep(0.5)
    
    print(f"\n[SUMMARY] Crawling completed!")
    print(f"[SUMMARY] Success: {success_count}")
    print(f"[SUMMARY] Failed: {failed_count}")
    print(f"[SUMMARY] Total: {len(urls)}")

if __name__ == "__main__":
    main()
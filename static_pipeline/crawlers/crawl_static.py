import requests
from bs4 import BeautifulSoup
import os, json
from utils.file_utils import save_html, save_json

with open('static_pipeline/crawlers/url_list.txt', 'r') as f:
    urls = [url.strip() for url in f.readlines() if url.strip()]

for url in urls:
    try:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.title.string if soup.title else "Untitled"
        paragraphs = [p.text.strip() for p in soup.find_all('p')]
        headings = [h.text.strip() for h in soup.find_all(['h1','h2','h3'])]
        links = [a['href'] for a in soup.find_all('a', href=True) if any(ext in a['href'] for ext in ['.pdf', '.docx'])]

        out = {
            'url': url,
            'title': title,
            'headings': headings,
            'paragraphs': paragraphs,
            'pdf_links': links
        }

        filename = title.lower().replace(' ', '_')[:50] + '.json'
        save_html(title, html)
        save_json(filename, out)

    except Exception as e:
        print(f"Error processing {url}: {e}")

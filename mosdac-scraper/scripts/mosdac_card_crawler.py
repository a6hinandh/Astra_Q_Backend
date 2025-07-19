import os
import re
import time
import json
from urllib.parse import urljoin, urlparse
from pathlib import Path
from playwright.sync_api import sync_playwright

START_URL = "https://mosdac.gov.in/"
DATA_DIR = Path(os.path.dirname(__file__)) / ".." / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

visited = set()
to_visit = [START_URL]

def url_to_filename(url):
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_")
    if not path:
        path = "home"
    fname = f"{parsed.netloc}_{path}"
    if parsed.query:
        fname += "_" + re.sub(r'[^a-zA-Z0-9]', '_', parsed.query)
    return fname + "_cards.json"

def is_internal(url, base):
    return urlparse(url).netloc == urlparse(base).netloc

def extract_cards(page):
    # Find all elements with a class containing 'card'
    card_elements = page.query_selector_all("[class*='card']")
    cards = []
    for el in card_elements:
        try:
            text = el.inner_text().strip()
            links = [a.get_attribute('href') for a in el.query_selector_all('a') if a.get_attribute('href')]
            cards.append({
                "text": text,
                "links": links
            })
        except Exception as e:
            print(f"[WARN] Card extraction error: {e}")
    return cards

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        while to_visit:
            url = to_visit.pop()
            if url in visited:
                continue
            print(f"[CRAWL] Visiting: {url}")
            try:
                page.goto(url, wait_until="networkidle")
                time.sleep(2)
                cards = extract_cards(page)
                fname = url_to_filename(url)
                out_path = DATA_DIR / fname
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump({"url": url, "cards": cards}, f, indent=2, ensure_ascii=False)
                print(f"[SAVE] {out_path} ({len(cards)} cards)")
                visited.add(url)
                links = page.eval_on_selector_all("a", "elements => elements.map(e => e.href)")
                for link in links:
                    if link and is_internal(link, START_URL) and link not in visited and link not in to_visit:
                        to_visit.append(link)
            except Exception as e:
                print(f"[ERROR] Failed to crawl {url}: {e}")
        browser.close()

if __name__ == "__main__":
    main() 
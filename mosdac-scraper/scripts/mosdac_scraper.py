import json
import logging
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
import time
import os

# Get the absolute path to the logs directory
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'mosdac_scraper.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MOSDACScraper:
    def __init__(self):
        self.base_url = "https://www.mosdac.gov.in"
        self.output_dir = Path("data")
        self.output_dir.mkdir(exist_ok=True)
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            filename='../logs/mosdac_scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def scrape_page(self, page):
        """Scrape data from current page"""
        datasets = []
        cards = page.query_selector_all(".card")
        print(f"[DEBUG] Found {len(cards)} cards on the page.")
        if len(cards) == 0:
            # Save a screenshot for debugging
            screenshot_path = os.path.join(os.path.dirname(__file__), '..', 'logs', f'no_cards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png')
            page.screenshot(path=screenshot_path)
            print(f"[DEBUG] No cards found. Screenshot saved to {screenshot_path}")
            # Optionally, print a snippet of the HTML
            html_snippet = page.content()[:1000]
            print(f"[DEBUG] Page HTML snippet:\n{html_snippet}")
        for card in cards:
            try:
                title = card.query_selector("h5").inner_text().strip()
                desc = card.query_selector(".card-text").inner_text().strip()
                link = card.query_selector("a").get_attribute("href")
                datasets.append({
                    "title": title,
                    "description": desc,
                    "link": f"{self.base_url}{link}" if link else None,
                    "scraped_at": datetime.now().isoformat()
                })
            except Exception as e:
                logging.warning(f"Card error: {e}")
        return datasets

    def handle_pagination(self, page):
        """Click through all pages"""
        all_data = []
        page_num = 1
        
        while True:
            logging.info(f"Scraping page {page_num}")
            all_data.extend(self.scrape_page(page))
            
            next_btn = page.query_selector("a:has-text('Next')")
            if not next_btn or "disabled" in next_btn.get_attribute("class", ""):
                break
                
            next_btn.click()
            page.wait_for_selector(".card", timeout=10000)
            page_num += 1
            time.sleep(2)  # Be polite
            
        return all_data

    def run(self):
        result = {
            "status": "success",
            "data": [],
            "metadata": {
                "url": self.base_url,
                "scraped_at": datetime.now().isoformat()
            }
        }

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(60000)
                
                # Navigate to target section
                page.goto(f"{self.base_url}/data-products", wait_until="domcontentloaded")
                
                # Handle pagination
                result["data"] = self.handle_pagination(page)
                result["metadata"]["pages_scraped"] = len(result["data"])
                
                # Save results
                filename = self.output_dir / f"mosdac_{datetime.now().strftime('%Y%m%d')}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                logging.info(f"Saved {len(result['data'])} items to {filename}")
                
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logging.error(f"Scraping failed: {e}")
            page.screenshot(path=f"../logs/error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
        finally:
            if 'browser' in locals():
                browser.close()
        return result

if __name__ == "__main__":
    scraper = MOSDACScraper()
    scraper.run()
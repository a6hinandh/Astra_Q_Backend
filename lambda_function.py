import os
import json
from playwright._impl._api_types import TimeoutError
from playwright.sync_api import sync_playwright

def lambda_handler(event, context):
    def run_scraper():
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("https://www.mosdac.gov.in")
            
            # Add your scraping logic here
            data = page.inner_text("body")
            browser.close()
            return data

    try:
        result = run_scraper()
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except TimeoutError:
        return {
            'statusCode': 408,
            'body': 'Request timeout'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
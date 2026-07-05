import os
import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        for path in ["/login", "/signup", "/signin", "/auth"]:
            url = f"https://www.dola.com{path}"
            print(f"Navigating to {url}...")
            try:
                page.goto(url, wait_until="load")
                page.wait_for_timeout(2000)
                print(f"Final URL: {page.url}")
                page.screenshot(path=f"dola_{path.replace('/', '')}.png")
            except Exception as e:
                print(f"Error on {url}:", e)
                
        browser.close()

if __name__ == "__main__":
    inspect()

import os
import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        
        try:
            print("Navigating to https://dola.com/ ...")
            page.goto("https://dola.com/", wait_until="load")
            page.wait_for_timeout(3000)
            
            # Click Decline All or Accept All to clear cookie banner
            print("Trying to click Accept All cookies...")
            try:
                # Try locating Accept All button
                btn = page.locator("button:has-text('Accept All'), button:has-text('Accept'), button:has-text('Accept all')").first
                if btn.count() > 0:
                    btn.click(timeout=3000)
                    print("Clicked Accept All cookies.")
                    page.wait_for_timeout(1000)
            except Exception as e:
                print("Failed to click cookie banner:", e)
                
            page.screenshot(path="dola_cookies_cleared.png")
            
            print("Attempting to trigger login popup...")
            try:
                # Find and click any element that triggers login
                # E.g. "Create Image" or "Writing" or click on the message textbox and type/press enter
                textbox = page.locator("[role='textbox'], textarea").first
                if textbox.count() > 0:
                    print("Filling textbox...")
                    textbox.fill("draw a cute dog")
                    page.wait_for_timeout(500)
                    
                    # Try clicking send
                    # Usually send button has an arrow svg or is next to textbox
                    send_btn = page.locator("button").last
                    print("Clicking last button (send)...")
                    send_btn.click(timeout=5000)
                    page.wait_for_timeout(3000)
            except Exception as e:
                print("Failed to trigger login popup:", e)
                
            page.screenshot(path="dola_triggered.png")
            print("Saved dola_triggered.png")
            
            # Print page text
            texts = page.evaluate("() => Array.from(document.querySelectorAll('button, input, a, p, span')).map(el => el.innerText.strip())")
            print("Page texts:", [t for t in texts if t][:100])
            
        finally:
            browser.close()

if __name__ == "__main__":
    inspect()

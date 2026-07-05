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
            print("Navigating to https://www.dola.com/chat/create-image ...")
            page.goto("https://www.dola.com/chat/create-image", wait_until="load")
            page.wait_for_timeout(3000)
            
            # Click Accept All cookies
            print("Clicking Accept All cookies...")
            try:
                cookie_btn = page.locator("button:has-text('Accept All'), button:has-text('Accept')").first
                if cookie_btn.count() > 0:
                    cookie_btn.click(timeout=3000)
                    page.wait_for_timeout(1000)
            except Exception as e:
                print("Cookie click failed:", e)
                
            # Click Log In button in header
            print("Clicking Log In button...")
            try:
                login_btn = page.locator("button:has-text('Log In'), a:has-text('Log In')").first
                login_btn.click(timeout=3000)
                page.wait_for_timeout(2000)
            except Exception as e:
                print("Login button click failed:", e)
                
            page.screenshot(path="dola_login_modal.png")
            print("Saved dola_login_modal.png")
            
            # Let's inspect the HTML of the login modal buttons
            print("--- HTML of all buttons/inputs in modal ---")
            elements = page.locator("div.semi-modal-content button, div.semi-modal-content a, button, a").all()
            for idx, el in enumerate(elements):
                try:
                    html = el.evaluate("el => el.outerHTML")
                    text = el.inner_text().strip()
                    print(f"Element {idx}: Text: {text} | HTML: {html[:250]}")
                except Exception as ex:
                    print("Error getting element html:", ex)
                    
        finally:
            browser.close()

if __name__ == "__main__":
    inspect()

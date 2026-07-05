import os
import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            page.goto("https://www.dola.com/chat/create-image", wait_until="load")
            page.wait_for_timeout(3000)
            
            # Print HTML of all buttons/elements at the bottom of the modal
            # Usually they are inside a flex container at the bottom of the login modal
            print("--- Inspecting bottom buttons ---")
            buttons = page.locator("div.semi-modal-content button, div.semi-modal-wrap button, button").all()
            for idx, btn in enumerate(buttons):
                try:
                    html = btn.evaluate("el => el.outerHTML")
                    # Check if it has svg
                    has_svg = btn.locator("svg").count() > 0
                    print(f"Btn {idx}: SVG={has_svg} | Text='{btn.inner_text()}' | HTML: {html[:200]}")
                except Exception as e:
                    print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    inspect()

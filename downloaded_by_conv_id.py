import os
import sys
import json
import time
import base64
import argparse
from playwright.sync_api import sync_playwright

def log(tag, msg):
    print(f"[{tag}] {msg}")

def is_valid_video(path):
    if not os.path.exists(path):
        return False
    size = os.path.getsize(path)
    if size < 50 * 1024: # Less than 50KB is likely invalid or a text error
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Download a generated video from Dola using a Conversation ID.")
    parser.add_argument("--conv_id", required=True, help="The Dola Conversation ID (e.g. 38415083498765841)")
    parser.add_argument("--account", required=True, help="The account name (e.g. account_008)")
    parser.add_argument("--output", default=None, help="Output path for the downloaded video")
    args = parser.parse_args()

    conv_id = args.conv_id.strip()
    account_name = args.account.replace(".json", "").strip()
    
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cookies_dir = os.path.join(base_dir, "cookies")
    account_path = os.path.join(cookies_dir, f"{account_name}.json")
    user_data_dir = os.path.join(base_dir, f"chrome_profile_acc_{account_name}")
    
    if args.output:
        target_path = args.output
    else:
        target_path = os.path.join(base_dir, f"video_{conv_id}.mp4")

    log("INFO", f"Conversation ID: {conv_id}")
    log("INFO", f"Account: {account_name}")
    log("INFO", f"Target Path: {target_path}")
    log("INFO", f"User Data Profile: {user_data_dir}")

    # Start Playwright
    with sync_playwright() as p:
        log("INFO", "Launching browser...")
        
        # Check for custom Chromium executable inside base directory
        custom_chromium_path = os.path.join(base_dir, "chromium", "chrome.exe")
        launch_kwargs = {
            "user_data_dir": user_data_dir,
            "headless": False,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-infobars",
                "--start-maximized"
            ]
        }
        if os.path.exists(custom_chromium_path):
            launch_kwargs["executable_path"] = custom_chromium_path
        else:
            launch_kwargs["channel"] = "chrome"

        context = p.chromium.launch_persistent_context(**launch_kwargs)
        page = context.new_page()

        # Inject cookies if file exists
        if os.path.exists(account_path):
            log("INFO", f"Injecting cookies from {account_path}...")
            try:
                with open(account_path, "r", encoding="utf-8") as f:
                    state_data = json.load(f)
                raw_cookies = state_data.get("cookies", state_data) if isinstance(state_data, dict) else state_data
                if raw_cookies:
                    cleaned_cookies = []
                    for c in raw_cookies:
                        c_clean = c.copy()
                        if "sameSite" in c_clean:
                            ss = str(c_clean["sameSite"]).capitalize()
                            if ss not in ["Strict", "Lax", "None"]:
                                del c_clean["sameSite"]
                            else:
                                c_clean["sameSite"] = ss
                        cleaned_cookies.append(c_clean)
                    context.add_cookies(cleaned_cookies)
                    log("SUCCESS", f"Injected {len(cleaned_cookies)} cookies.")
            except Exception as e:
                log("WARNING", f"Failed to inject cookies: {e}")

        # Setup network interception
        intercepted_url = None

        def on_response(response):
            nonlocal intercepted_url
            url = response.url
            # Detect video URL signatures
            if ".mp4" in url or "dola-output" in url or "r2.dola" in url or "-dola.dola.com" in url:
                if not intercepted_url:
                    intercepted_url = url
                    log("SUCCESS", f"Network intercepted video URL: {url[:100]}...")

        page.on("response", on_response)

        # Navigate to conversation page
        conv_url = f"https://www.dola.com/chat/{conv_id}"
        log("INFO", f"Navigating to conversation page: {conv_url}")
        page.goto(conv_url, wait_until="domcontentloaded")
        log("INFO", "Page loaded. Polling for video (up to 300 seconds)...")

        video_ready_detected = False
        video_src = None

        for i in range(1, 301):
            if intercepted_url:
                video_src = intercepted_url
                break

            # Check ready text or video element presence
            try:
                ready_check = page.evaluate("""() => {
                    const hasVideo = !!document.querySelector('video');
                    const t = document.body ? document.body.innerText.toLowerCase() : '';
                    const hasReadyText = (
                        t.includes('your video is ready') ||
                        t.includes('video is ready') ||
                        t.includes('image is ready') ||
                        t.includes('your image is ready') ||
                        t.includes('generation complete') ||
                        t.includes('video ready')
                    );
                    return hasVideo || hasReadyText;
                }""")
                if ready_check and not video_ready_detected:
                    video_ready_detected = True
                    log("SUCCESS", f"Ready state detected in DOM at {i}s.")
            except:
                pass

            # Play/autoplay fallback if ready
            if video_ready_detected and not intercepted_url:
                try:
                    # Hover and click to trigger fetch
                    page.evaluate("""() => {
                        const media = Array.from(document.querySelectorAll('video, img'));
                        if (media.length > 0) {
                            const target = media[media.length - 1];
                            target.scrollIntoView({ block: 'center' });
                            
                            // Click play button overlays
                            let parent = target;
                            for (let d=0; d<5; d++) {
                                if (!parent.parentElement) break;
                                parent = parent.parentElement;
                                const playBtn = parent.querySelector('[class*="play"], button, [role="button"], svg, [class*="icon"], [class*="btn"]');
                                if (playBtn) {
                                    playBtn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                                    break;
                                }
                            }
                        }
                    }""")
                except:
                    pass

            # Check DOM src scan as fallback
            if i % 5 == 0:
                try:
                    found_src = page.evaluate(r"""() => {
                        const videos = Array.from(document.querySelectorAll('video, video source'));
                        for (const el of videos) {
                            const s = el.getAttribute('src') || el.currentSrc || '';
                            if (s && !s.startsWith('blob:') && (s.includes('.mp4') || s.includes('-dola.dola.com') || s.includes('r2.dola') || s.includes('dola-output') || s.includes('cdn')))
                                return s;
                        }
                        const html = document.documentElement.innerHTML;
                        const m = html.match(/https?:\/\/[^"'\s<>]+(?:\.mp4|-dola\.dola\.com|r2\.dola\.ai|dola-output)[^"'\s<>]*/);
                        return m ? m[0] : null;
                    }""")
                    if found_src:
                        video_src = found_src
                        log("SUCCESS", f"DOM scan found video URL: {found_src[:100]}...")
                        break
                except:
                    pass

            # Reload page every 60s as a defensive measure
            if i > 0 and i % 60 == 0:
                log("INFO", "Reloading page to refresh state...")
                try:
                    page.reload(wait_until="domcontentloaded", timeout=20000)
                except:
                    pass

            time.sleep(1)

        # Download phase
        if not video_src and intercepted_url:
            video_src = intercepted_url

        if not video_src:
            log("ERROR", "Failed to retrieve video URL after 300 seconds.")
            context.close()
            sys.exit(1)

        log("INFO", f"Starting download from: {video_src[:100]}...")
        download_success = False

        # Method A: Python requests download
        if video_src.startswith("http") and not video_src.startswith("blob:"):
            try:
                log("INFO", "Trying requests download...")
                import requests
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://www.dola.com/",
                    "Origin": "https://www.dola.com"
                }
                resp = requests.get(video_src, headers=headers, timeout=60, stream=True)
                resp.raise_for_status()
                with open(target_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)
                if is_valid_video(target_path):
                    log("SUCCESS", f"Requests download succeeded. Size: {os.path.getsize(target_path)} bytes.")
                    download_success = True
            except Exception as e:
                log("WARNING", f"Requests download failed: {e}")

        # Method B: Browser fetch
        if not download_success:
            try:
                log("INFO", "Trying browser fetch download...")
                b64 = page.evaluate("""async (url) => {
                    const response = await fetch(url);
                    const blob = await response.blob();
                    return new Promise((resolve, reject) => {
                        const reader = new FileReader();
                        reader.onloadend = () => resolve(reader.result.split(',')[1]);
                        reader.onerror = () => reject(new Error('FileReader failed'));
                        reader.readAsDataURL(blob);
                    });
                }""", video_src)
                video_data = base64.b64decode(b64)
                with open(target_path, "wb") as f:
                    f.write(video_data)
                if is_valid_video(target_path):
                    log("SUCCESS", f"Browser fetch download succeeded. Size: {len(video_data)} bytes.")
                    download_success = True
            except Exception as e:
                log("WARNING", f"Browser fetch download failed: {e}")

        # Method C: Playwright download event via new tab
        if not download_success and video_src.startswith("http"):
            try:
                log("INFO", "Trying new tab download...")
                new_tab = context.new_page()
                with new_tab.expect_download(timeout=20000) as dl_info:
                    new_tab.goto(video_src, timeout=30000)
                dl = dl_info.value
                dl.save_as(target_path)
                if is_valid_video(target_path):
                    log("SUCCESS", f"New tab download succeeded. Size: {os.path.getsize(target_path)} bytes.")
                    download_success = True
                new_tab.close()
            except Exception as e:
                log("WARNING", f"New tab download failed: {e}")

        context.close()
        
        if download_success:
            log("SUCCESS", f"Video successfully downloaded and saved to: {target_path}")
            sys.exit(0)
        else:
            log("ERROR", "All download methods failed.")
            sys.exit(1)

if __name__ == "__main__":
    main()

# akira_admin.py — Standalone 100% Fully Automated Dola Account Creator & Sync Tool

import sys
import os
import json
import time
import random
import base64
import urllib.request
import urllib.parse
import hmac
import hashlib
import requests
import cv2
import numpy as np

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QFrame, QLabel, QLineEdit, QPushButton, QTextEdit, QCheckBox,
                             QComboBox, QMessageBox, QGridLayout)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QByteArray
from PyQt6.QtGui import QIcon, QPixmap, QFont

# Try to import logo data from main workspace
try:
    from logo_data import LOGO_PNG_B64
except ImportError:
    LOGO_PNG_B64 = ""

from admin_ui_config import UI_ADMIN_QSS

# --- Global Country Dialing Prefix Mapping (Fallback List) ---
SMS_COUNTRIES_MAP = {
    "0": ("Russia", "+7"), "1": ("Ukraine", "+380"), "2": ("Kazakhstan", "+7"), "3": ("China", "+86"),
    "4": ("Philippines", "+63"), "5": ("Myanmar", "+95"), "6": ("Indonesia", "+62"),
    "7": ("Malaysia", "+60"), "8": ("Kenya", "+254"), "9": ("Tanzania", "+255"),
    "10": ("Vietnam", "+84"), "11": ("Kyrgyzstan", "+996"), "12": ("USA", "+1"),
    "13": ("Israel", "+972"), "14": ("Hong Kong", "+852"), "15": ("Poland", "+48"),
    "16": ("United Kingdom", "+44"), "17": ("Madagascar", "+261"), "18": ("Congo", "+242"),
    "19": ("Nigeria", "+234"), "20": ("Macau", "+853"), "21": ("Egypt", "+20"),
    "22": ("India", "+91"), "23": ("Ireland", "+353"), "24": ("Cambodia", "+855"),
    "25": ("Laos", "+856"), "26": ("Haiti", "+509"), "27": ("Ivory Coast", "+225"),
    "28": ("Gambia", "+220"), "29": ("Yemen", "+967"), "30": ("South Africa", "+27"),
    "31": ("Romania", "+40"), "32": ("Colombia", "+57"), "33": ("Estonia", "+372"),
    "34": ("Azerbaijan", "+994"), "35": ("Angola", "+244"), "36": ("Sweden", "+46"),
    "37": ("France", "+33"), "38": ("Canada", "+1"), "39": ("Uzbekistan", "+998"),
    "40": ("Cameroon", "+237"), "41": ("Chad", "+235"), "42": ("Germany", "+49"),
    "43": ("Lithuania", "+370"), "44": ("Croatia", "+385"), "46": ("Iraq", "+964"),
    "47": ("Netherlands", "+31"), "48": ("Latvia", "+371"), "49": ("Austria", "+43"),
    "50": ("Belarus", "+375"), "51": ("Thailand", "+66"), "52": ("Saudi Arabia", "+966"),
    "53": ("Mexico", "+52"), "54": ("Taiwan", "+886"), "56": ("Spain", "+34"),
    "57": ("Iran", "+98"), "58": ("Algeria", "+213"), "59": ("Slovenia", "+386"),
    "60": ("Bangladesh", "+880"), "61": ("Senegal", "+221"), "62": ("Turkey", "+90"),
    "63": ("Sri Lanka", "+94"), "64": ("Peru", "+51"), "65": ("Pakistan", "+92"),
    "66": ("New Zealand", "+64"), "72": ("Brazil", "+55"), "73": ("Afghanistan", "+93"),
    "95": ("UAE", "+971")
}

# --- Comprehensive Name to Calling Code Map ---
NAME_TO_CODE = {
    "Russia": "+7", "Ukraine": "+380", "Kazakhstan": "+7", "China": "+86",
    "Philippines": "+63", "Myanmar": "+95", "Indonesia": "+62", "Malaysia": "+60",
    "Kenya": "+254", "Tanzania": "+255", "Vietnam": "+84", "Kyrgyzstan": "+996",
    "USA": "+1", "Israel": "+972", "Hong Kong": "+852", "Poland": "+48",
    "United Kingdom": "+44", "Madagascar": "+261", "Congo": "+242", "Nigeria": "+234",
    "Macau": "+853", "Egypt": "+20", "India": "+91", "Ireland": "+353",
    "Cambodia": "+855", "Laos": "+856", "Haiti": "+509", "Ivory Coast": "+225",
    "Gambia": "+220", "Yemen": "+967", "South Africa": "+27", "Romania": "+40",
    "Colombia": "+57", "Estonia": "+372", "Azerbaijan": "+994", "Angola": "+244",
    "Sweden": "+46", "France": "+33", "Canada": "+1", "Uzbekistan": "+998",
    "Cameroon": "+237", "Chad": "+235", "Germany": "+49", "Lithuania": "+370",
    "Croatia": "+385", "Iraq": "+964", "Netherlands": "+31", "Latvia": "+371",
    "Austria": "+43", "Belarus": "+375", "Thailand": "+66", "Saudi Arabia": "+966",
    "Mexico": "+52", "Taiwan": "+886", "Spain": "+34", "Iran": "+98",
    "Algeria": "+213", "Slovenia": "+386", "Bangladesh": "+880", "Senegal": "+221",
    "Turkey": "+90", "Sri Lanka": "+94", "Peru": "+51", "Pakistan": "+92",
    "New Zealand": "+64", "Brazil": "+55", "Afghanistan": "+93", "UAE": "+971",
    "Luxembourg": "+352", "Costa Rica": "+506", "Panama": "+507", "Argentina": "+54",
    "Uruguay": "+598", "Paraguay": "+595", "Chile": "+56", "Guyana": "+592",
    "Bolivia": "+591", "Benin": "+229", "Togo": "+228", "Gabon": "+241",
    "Rwanda": "+250", "Burundi": "+257", "Georgia": "+995", "Armenia": "+374",
    "Tajikistan": "+992", "Moldova": "+373", "Turkmenistan": "+993", "Japan": "+81",
    "South Korea": "+82", "Brunei": "+673", "Timor-Leste": "+670", "Singapore": "+65",
    "Fiji": "+679", "Solomon Islands": "+677", "Vanuatu": "+678", "Tonga": "+676",
    "Samoa": "+685", "Belgium": "+32", "Monaco": "+377", "Portugal": "+351",
    "Italy": "+39", "Malta": "+356", "Greece": "+30", "Cyprus": "+357",
    "Bahrain": "+973", "Kuwait": "+965", "Syria": "+963", "Jordan": "+962",
    "Qatar": "+974", "Oman": "+968", "Lebanon": "+961", "South Africa (virtual)": "+27",
    "Kazakhstan (virtual)": "+7", "Morocco (virtual)": "+212", "Morocco": "+212",
    "Tunisia": "+216", "Algeria (virtual)": "+213", "Honduras": "+504", "El Salvador": "+503",
    "Ecuador": "+593", "Guatemala": "+502", "Suriname": "+597", "Nicaragua": "+505",
    "Burkina Faso": "+226", "Papua New Guinea": "+675", "Papua": "+675", "Bhutan": "+975",
    "Puerto Rico": "+1", "Dominica": "+1", "Reunion": "+262", "Trinidad and Tobago": "+1",
    "Aruba": "+297", "Mauritania": "+222", "Somalia": "+252", "Uganda": "+256", "Mali": "+223",
    "Guinea": "+224", "Zimbabwe": "+263", "Mauritius": "+230", "Sudan": "+249", "Libya": "+218",
    "Swaziland": "+268", "Niger": "+227", "Zambia": "+260", "Zanzibar": "+255",
    "Sierra Leone": "+232", "Eritrea": "+291", "Lesotho": "+266", "Djibouti": "+253"
}

# --- Cryptographic Request Signer ---
def sign_payload(payload_str, secret_key="AkiraSecToken_2026_Key_Prod_v1"):
    payload_b64 = base64.urlsafe_b64encode(payload_str.encode('utf-8')).decode('utf-8')
    sig_bytes = hmac.new(secret_key.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).digest()
    sig_hex = sig_bytes.hex()
    return {
        "payload": payload_b64,
        "signature": sig_hex
    }

# --- Helper to load Logo Pixmap ---
def get_logo_pixmap(size=32):
    if LOGO_PNG_B64:
        try:
            pix = QPixmap()
            pix.loadFromData(QByteArray.fromBase64(LOGO_PNG_B64.encode()))
            return pix.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        except:
            pass
    return QPixmap()


# --- Local OpenCV Captcha Solver ---
def solve_slider_locally(bg_bytes, tp_bytes):
    try:
        # Decode images
        bg_img = cv2.imdecode(np.frombuffer(bg_bytes, np.uint8), cv2.IMREAD_COLOR)
        tp_img = cv2.imdecode(np.frombuffer(tp_bytes, np.uint8), cv2.IMREAD_COLOR)
        
        if bg_img is None or tp_img is None:
            return 0, 0
            
        raw_width = bg_img.shape[1]
        
        # Convert to grayscale
        bg_gray = cv2.cvtColor(bg_img, cv2.COLOR_BGR2GRAY)
        tp_gray = cv2.cvtColor(tp_img, cv2.COLOR_BGR2GRAY)
        
        # Run template matching
        res = cv2.matchTemplate(bg_gray, tp_gray, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(res)
        
        # Return best match X coordinate and raw image width
        return max_loc[0], raw_width
    except Exception:
        return 0, 0


# --- Paid APIs Captcha Solver (2Captcha Fallback) ---
def solve_slider_via_api(provider, api_key, bg_bytes, tp_bytes):
    try:
        bg_b64 = base64.b64encode(bg_bytes).decode("utf-8")
        tp_b64 = base64.b64encode(tp_bytes).decode("utf-8")

        if provider == "2Captcha":
            url = "https://2captcha.com/in.php"
            payload = {
                "key": api_key,
                "method": "base64",
                "action": "slide",
                "body": bg_b64,
                "img": tp_b64,
                "json": 1
            }
            res = requests.post(url, json=payload, timeout=20)
            res_data = res.json()
            if res_data.get("status") == 1:
                task_id = res_data.get("request")
                # Poll for solution (max 10 retries of 2 seconds)
                for _ in range(10):
                    time.sleep(2)
                    res_url = f"https://2captcha.com/res.php?key={api_key}&action=get&id={task_id}&json=1"
                    status_res = requests.get(res_url, timeout=10)
                    status_data = status_res.json()
                    if status_data.get("status") == 1:
                        return int(status_data.get("request"))
        
        elif provider == "CapMonster":
            url = "https://api.capmonster.cloud/createTask"
            payload = {
                "clientKey": api_key,
                "task": {
                    "type": "CustomTask",
                    "class": "TikTokSlider",
                    "image": bg_b64,
                    "extra": {
                        "tip": tp_b64
                    }
                }
            }
            res = requests.post(url, json=payload, timeout=20)
            res_data = res.json()
            if "taskId" in res_data:
                task_id = res_data["taskId"]
                for _ in range(10):
                    time.sleep(2)
                    status_url = "https://api.capmonster.cloud/getTaskResult"
                    status_res = requests.post(status_url, json={"clientKey": api_key, "taskId": task_id}, timeout=10)
                    status_data = status_res.json()
                    if status_data.get("status") == "ready":
                        return int(status_data.get("solution", {}).get("x", 0))
    except:
        pass
    return 0


# --- SMS Prices Loader Worker Thread ---
class SmsPriceLoaderThread(QThread):
    prices_loaded = pyqtSignal(list)
    log_signal = pyqtSignal(str, str)
    finished_signal = pyqtSignal()

    def __init__(self, provider, api_key, parent=None):
        super().__init__(parent)
        self.provider = provider
        self.api_key = api_key

    def run(self):
        if not self.api_key.strip():
            self.log_signal.emit("WARNING", "SMS API Key is missing. Cannot fetch country prices.")
            self.finished_signal.emit()
            return

        self.log_signal.emit("INFO", f"Fetching live 'Other' service numbers from {self.provider}...")
        
        if self.provider == "SMS Bower":
            sms_api_base = "https://smsbower.com/stubs/handler_api.php"
        else:
            sms_api_base = "https://hero-sms.com/stubs/handler_api.php"

        # 1. Fetch Dynamic Country Names dictionary to prevent showing generic IDs
        c_map = {}
        try:
            c_res = requests.get(f"{sms_api_base}?api_key={self.api_key}&action=getCountries", timeout=8)
            c_data = c_res.json()
            for k, v in c_data.items():
                if isinstance(v, dict) and "eng" in v:
                    c_map[str(k)] = v["eng"]
        except Exception as e:
            self.log_signal.emit("WARNING", f"Could not load dynamic country name dictionary: {e}. Falling back to default list.")

        # 2. Fetch Prices
        url = f"{sms_api_base}?api_key={self.api_key}&action=getPrices&service=ot"
        try:
            res = requests.get(url, timeout=15)
            data = res.json()
            
            countries_list = []
            for c_id, services in data.items():
                if "ot" in services:
                    ot = services["ot"]
                    cost = None
                    count = None
                    
                    if isinstance(ot, dict):
                        cost = ot.get("cost")
                        count = ot.get("count")
                    elif isinstance(ot, list) and len(ot) >= 2:
                        cost = ot[0]
                        count = ot[1]
                        
                    if cost is not None and count is not None and count > 0:
                        c_name = c_map.get(str(c_id))
                        
                        # Fallback to local map
                        if not c_name:
                            c_name, _ = SMS_COUNTRIES_MAP.get(str(c_id), ("", ""))
                        
                        # STRICT: Skip any country ID we cannot resolve to an exact name
                        if not c_name:
                            continue
                            
                        # Resolve calling prefix code
                        calling_code = NAME_TO_CODE.get(c_name, "")
                        if not calling_code:
                            _, calling_code = SMS_COUNTRIES_MAP.get(str(c_id), ("", ""))
                            
                        countries_list.append({
                            "id": str(c_id),
                            "name": c_name,
                            "code": calling_code,
                            "price": float(cost),
                            "count": int(count)
                        })
            
            # Sort by price ascending (cheapest first)
            countries_list.sort(key=lambda x: x["price"])
            self.prices_loaded.emit(countries_list)
            self.log_signal.emit("SUCCESS", f"Successfully loaded {len(countries_list)} resolved countries.")
        except Exception as e:
            self.log_signal.emit("ERROR", f"Failed to fetch country prices: {str(e)}")
            
        self.finished_signal.emit()


# --- Playwright Fully Automated Worker Thread ---
class PlaywrightAutomatedWorker(QThread):
    log_signal = pyqtSignal(str, str)
    finished_signal = pyqtSignal()
    session_completed = pyqtSignal(str, str) # (device_id, cookies_json)

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.should_stop = False
        self.playwright = None
        self.browser_context = None

    def log(self, log_type, msg):
        self.log_signal.emit(log_type, msg)

    def stop_automation(self):
        self.should_stop = True

    def run(self):
        from playwright.sync_api import sync_playwright
        import shutil
        
        target_count = self.settings.get("target_count", 1)
        device_id = self.settings.get("device_id")
        proxy_str = self.settings.get("proxy", "")
        sms_provider = self.settings.get("sms_provider", "HeroSMS")
        sms_key = self.settings.get("sms_key", "")
        sms_country = self.settings.get("sms_country", "0")
        loaded_countries = self.settings.get("countries_list", [])
        captcha_mode = self.settings.get("captcha_mode", "Auto (OpenCV/Paid API)")
        captcha_provider = self.settings.get("captcha_provider", "CapMonster")
        captcha_key = self.settings.get("captcha_key", "")

        # Determine SMS API URL
        if sms_provider == "SMS Bower":
            sms_api_base = "https://smsbower.com/stubs/handler_api.php"
        else:
            sms_api_base = "https://hero-sms.com/stubs/handler_api.php"

        self.log("INFO", f"Initiating Fully Automated creation of {target_count} accounts for Device: {device_id}")

        self.playwright = sync_playwright().start()

        # Parse Proxy
        proxy_config = None
        if proxy_str.strip():
            try:
                parts = proxy_str.strip().split(":")
                if len(parts) >= 2:
                    ip = parts[0]
                    port = parts[1]
                    username = parts[2] if len(parts) > 2 else None
                    password = parts[3] if len(parts) > 3 else None
                    server = f"http://{ip}:{port}"
                    proxy_config = {"server": server}
                    if username and password:
                        proxy_config["username"] = username
                        proxy_config["password"] = password
                    self.log("INFO", f"Routing via proxy exit node: {server}")
            except Exception as e:
                self.log("WARNING", f"Failed to parse proxy: {str(e)}. Running on direct connection.")

        # If countries_list is empty, build a default one to allow operation
        if not loaded_countries:
            c_name, calling_code = SMS_COUNTRIES_MAP.get(sms_country, ("Russia", "+7"))
            loaded_countries = [{
                "id": sms_country,
                "name": c_name,
                "code": calling_code,
                "price": 0.05,
                "count": 1
            }]

        # Find starting index for selected country in the list
        start_idx = 0
        for idx, c in enumerate(loaded_countries):
            if str(c["id"]) == str(sms_country):
                start_idx = idx
                break

        # Launch Profile Slots sequentially to avoid file locks
        for acc_idx in range(1, target_count + 1):
            if self.should_stop:
                break

            self.log("INFO", f"=== STARTING ACCOUNT CREATION {acc_idx}/{target_count} ===")
            
            slot_success = False
            current_country_idx = start_idx
            
            # Smart Fallback loop: try different countries/numbers within price thresholds for the SAME account slot
            while current_country_idx < len(loaded_countries):
                if self.should_stop:
                    break
                
                c = loaded_countries[current_country_idx]
                c_price = float(c["price"])
                
                # Check user price condition: Must be between $0.03 and $0.10
                if c_price < 0.03 or c_price > 0.10:
                    self.log("WARNING", f"Skipping {c['name']} because price ${c_price:.3f} is outside the $0.03 - $0.10 limit.")
                    current_country_idx += 1
                    continue
                
                self.log("INFO", f"Requesting virtual number from {c['name']} ({c['code']}) for ${c_price:.3f}...")
                
                activation_id = None
                phone_number = None
                
                # Step 1: Purchase SMS Number
                try:
                    for svc in ["dola", "ot"]:
                        req_url = f"{sms_api_base}?api_key={sms_key}&action=getNumber&service={svc}&country={c['id']}"
                        res = requests.get(req_url, timeout=12)
                        res_text = res.text.strip()
                        if res_text.startswith("ACCESS_NUMBER:"):
                            parts = res_text.split(":")
                            activation_id = parts[1]
                            phone_number = parts[2]
                            break
                except Exception as e:
                    self.log("ERROR", f"SMS purchase API connection failed: {str(e)}")
                
                if not (activation_id and phone_number):
                    self.log("WARNING", f"Purchase failed or out of stock for {c['name']}. Trying next cheapest option...")
                    current_country_idx += 1
                    continue
                
                self.log("SUCCESS", f"Obtained number: +{phone_number} from {c['name']} (ID: {activation_id})")

                # Step 2: Open Browser
                user_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"chrome_admin_slot_{acc_idx}")
                launch_args = ["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-setuid-sandbox"]
                
                try:
                    self.browser_context = self.playwright.chromium.launch_persistent_context(
                        user_data_dir=user_data_dir,
                        headless=False,
                        args=launch_args,
                        proxy=proxy_config,
                        viewport={"width": 1280, "height": 800}
                    )
                    
                    page = self.browser_context.new_page()
                    
                    # --- ROUTE BLOCKER: Abort media, fonts and trackers to save 70%+ proxy bandwidth ---
                    def block_heavy_resources(route):
                        req = route.request
                        res_type = req.resource_type
                        url = req.url.lower()
                        
                        # Block video/audio files, custom web fonts, and tracking/analytics pixels
                        if res_type in ["media", "font"] or any(x in url for x in ["telemetry", "analytics", "doubleclick", "facebook", "google-analytics", "tiktok", "clarity"]):
                            route.abort()
                        else:
                            route.continue_()
                            
                    page.route("**/*", block_heavy_resources)
                    
                    self.log("INFO", "Navigating to Dola AI Web App...")
                    page.goto("https://www.dola.com/chat/", timeout=60000)
                    page.wait_for_timeout(2000)

                    # Click Login Button
                    login_btn = page.locator('button:has-text("Log In"), a:has-text("Log In"), [role="button"]:has-text("Log In")').first
                    if login_btn.count() > 0:
                        login_btn.click(force=True)
                        page.wait_for_timeout(2000)

                    # Locate Phone Verification option in modal
                    phone_icon_btn = None
                    modal_buttons = page.locator(".semi-modal-content button, .semi-modal-wrap button, div[role='dialog'] button, div[class*='modal'] button").all()
                    for btn in modal_buttons:
                        html = btn.evaluate("el => el.outerHTML").lower()
                        if "svg" in html and "phone" in html or "tel" in html or "call" in html:
                            phone_icon_btn = btn
                            break
                            
                    if phone_icon_btn:
                        phone_icon_btn.click(force=True)
                        page.wait_for_timeout(1500)

                    # Input Phone Number
                    phone_input = page.locator('input[type="tel"], input[placeholder*="Phone"], input[placeholder*="number"]').first
                    if phone_input.count() > 0:
                        local_number = phone_number
                        matched_prefix = ""
                        for name, code in NAME_TO_CODE.items():
                            digits = code.replace("+", "").strip()
                            if phone_number.startswith(digits) and len(digits) > len(matched_prefix):
                                matched_prefix = digits
                                
                        if matched_prefix:
                            local_number = phone_number[len(matched_prefix):]
                            calling_code = f"+{matched_prefix}"
                            
                        try:
                            country_trigger = page.locator('button:has-text("+"), [role="button"]:has-text("+"), [class*="flag"], [class*="Country"]').first
                            if country_trigger.count() > 0 and country_trigger.is_visible():
                                country_trigger.click(force=True)
                                page.wait_for_timeout(1000)
                                option = page.locator(f'li:has-text("{calling_code}"), [role="option"]:has-text("{calling_code}"), div:has-text("{calling_code}")').first
                                if option.count() > 0:
                                    option.click(force=True)
                                    page.wait_for_timeout(500)
                        except:
                            pass
                        
                        phone_input.fill(local_number)
                        page.wait_for_timeout(1000)
                        
                        page.keyboard.press("Enter")
                        page.wait_for_timeout(3000)

                        # Step 3: Handle ByteDance Slider Captcha (Manual vs Auto)
                        self.log("INFO", "Checking for verification Slider Captcha...")
                        captcha_bg_sel = 'img#captcha-verify-image, img[class*="captcha_image"], img[class*="verify-img"]'
                        slider_handle_sel = 'div.secsdk-captcha-drag-icon, div.captcha_slider_button, [class*="handler"], [class*="slider"]'
                        
                        bg_element = page.locator(captcha_bg_sel).first
                        handle_element = page.locator(slider_handle_sel).first
                        
                        captcha_pass = True
                        if bg_element.count() > 0 and bg_element.is_visible():
                            if "Manual" in captcha_mode:
                                self.log("WARNING", "Slider Captcha detected! Please solve it manually in the browser window now...")
                                solved = False
                                for poll_sec in range(60):
                                    if self.should_stop:
                                        break
                                    page.wait_for_timeout(1000)
                                    if not bg_element.is_visible():
                                        solved = True
                                        break
                                if solved:
                                    self.log("SUCCESS", "Captcha solved manually!")
                                    page.wait_for_timeout(2000)
                                else:
                                    self.log("ERROR", "Manual captcha solving timed out or cancelled.")
                                    captcha_pass = False
                            else:
                                # Auto solver (OpenCV + API)
                                self.log("INFO", "Slider Captcha detected! Initiating Auto solver...")
                                bg_src = bg_element.get_attribute("src")
                                piece_element = page.locator('img.captcha_verify_img_slide, img[class*="slide"], img[class*="piece"]').first
                                piece_src = piece_element.get_attribute("src") if piece_element.count() > 0 else ""
                                
                                if bg_src and piece_src:
                                    bg_bytes = base64.b64decode(bg_src.split(",")[1])
                                    tp_bytes = base64.b64decode(piece_src.split(",")[1])
                                    
                                    self.log("INFO", "Solving locally using OpenCV template matching...")
                                    offset, raw_img_width = solve_slider_locally(bg_bytes, tp_bytes)
                                    
                                    if offset <= 0 and captcha_key.strip():
                                        self.log("INFO", f"Local solver failed. Retrying via {captcha_provider} API...")
                                        offset = solve_slider_via_api(captcha_provider, captcha_key, bg_bytes, tp_bytes)
                                        raw_img_width = 340
                                    
                                    if offset > 0:
                                        self.log("SUCCESS", f"Slide offset calculated: {offset} pixels.")
                                        bg_box = bg_element.bounding_box()
                                        handle_box = handle_element.bounding_box()
                                        
                                        if bg_box and handle_box:
                                            scale = bg_box["width"] / raw_img_width
                                            drag_distance = offset * scale
                                            
                                            start_x = handle_box["x"] + handle_box["width"] / 2
                                            start_y = handle_box["y"] + handle_box["height"] / 2
                                            
                                            page.mouse.move(start_x, start_y)
                                            page.mouse.down()
                                            
                                            steps = 15
                                            current_x = start_x
                                            for step in range(steps):
                                                step_dist = (drag_distance / steps)
                                                noise = random.uniform(-1, 1.5)
                                                current_x += step_dist + noise
                                                current_y = start_y + random.uniform(-0.5, 0.5)
                                                page.mouse.move(current_x, current_y)
                                                time.sleep(random.uniform(0.01, 0.03))
                                                
                                            page.mouse.move(start_x + drag_distance, start_y)
                                            page.mouse.up()
                                            
                                            self.log("INFO", "Slider drag-and-drop completed.")
                                            page.wait_for_timeout(3000)
                                    else:
                                        self.log("WARNING", "Could not calculate slider puzzle gap. Attempt manual slide now.")
                                        captcha_pass = False
                                else:
                                    self.log("WARNING", "Captcha image elements found but image source failed to load.")
                                    captcha_pass = False
                        
                        if not captcha_pass:
                            self.log("WARNING", "Slider verification failed. Retrying next country option...")
                            requests.get(f"{sms_api_base}?api_key={sms_key}&action=setStatus&id={activation_id}&status=8", timeout=5)
                            current_country_idx += 1
                            continue

                        # Step 4: Poll SMS verification OTP
                        self.log("INFO", "Awaiting verification OTP code arrival...")
                        otp_code = None
                        for poll_sec in range(20):
                            if self.should_stop:
                                break
                            time.sleep(3)
                            
                            status_url = f"{sms_api_base}?api_key={sms_key}&action=getStatus&id={activation_id}"
                            status_res = requests.get(status_url, timeout=10)
                            status_text = status_res.text.strip()
                            
                            if status_text.startswith("STATUS_OK:"):
                                otp_code = status_text.split(":")[1]
                                break
                            elif status_text == "STATUS_WAIT_CODE":
                                continue
                            else:
                                self.log("WARNING", f"Polling status alert: {status_text}")
                                
                        if otp_code:
                            self.log("SUCCESS", f"SMS verification code received: {otp_code}")
                            
                            otp_inputs = page.locator('input').all()
                            visible_inputs = [i for i in otp_inputs if i.is_visible()]
                            
                            if len(visible_inputs) >= 6:
                                for index_char, char in enumerate(otp_code[:len(visible_inputs)]):
                                    visible_inputs[index_char].fill(char)
                            elif len(visible_inputs) > 0:
                                visible_inputs[0].fill(otp_code)
                                page.keyboard.press("Enter")
                                
                            self.log("INFO", "Submitting verification code...")
                            page.wait_for_timeout(4000)
                            
                            cookies = self.browser_context.cookies()
                            has_login = False
                            for c_item in cookies:
                                if c_item["name"] == "flow_web_has_login" and c_item["value"] == "true":
                                    has_login = True
                                    break
                                    
                            if has_login:
                                self.log("SUCCESS", f"Account Onboarding succeeded for slot {acc_idx}!")
                                cookies_json = json.dumps(cookies)
                                self.session_completed.emit(device_id, cookies_json)
                                requests.get(f"{sms_api_base}?api_key={sms_key}&action=setStatus&id={activation_id}&status=6", timeout=5)
                                slot_success = True
                                break
                            else:
                                self.log("ERROR", "Dola did not transition to logged in state. Registration failed.")
                                requests.get(f"{sms_api_base}?api_key={sms_key}&action=setStatus&id={activation_id}&status=8", timeout=5)
                        else:
                            self.log("ERROR", "OTP code request timed out. Cancelling number reservation.")
                            requests.get(f"{sms_api_base}?api_key={sms_key}&action=setStatus&id={activation_id}&status=8", timeout=5)
                    else:
                        self.log("ERROR", "Failed to locate phone input box in browser page.")

                except Exception as ex:
                    self.log("ERROR", f"An execution error occurred in loop: {str(ex)}")
                finally:
                    if self.browser_context:
                        try: self.browser_context.close()
                        except: pass
                    # Clean up Chrome profile slots
                    try: shutil.rmtree(user_data_dir, ignore_errors=True)
                    except: pass
                
                # If we made it here without setting slot_success = True, it means this attempt failed
                self.log("WARNING", f"Onboarding failed using {c['name']}. Moving to next cheapest country in range...")
                current_country_idx += 1

            if slot_success:
                self.log("SUCCESS", f"Slot {acc_idx} completed successfully.")
            else:
                self.log("ERROR", f"Could not create account for Slot {acc_idx} after checking all matching countries.")

        self.log("SUCCESS", "All requested account registrations finished.")
        if self.playwright:
            try: self.playwright.stop()
            except: pass
        self.finished_signal.emit()


# --- Main Admin Dashboard ---
class AkiraAdminDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.price_loader = None
        self.saved_country_id = "0"
        self.loaded_countries = []
        self.init_ui()
        self.load_config()

    def init_ui(self):
        self.setWindowTitle("💎 AKIRA AUTOMATED DOLA ACCOUNT CREATOR")
        self.resize(1100, 710)
        self.setMinimumSize(1000, 620)
        self.setWindowIcon(QIcon(get_logo_pixmap(64)))
        self.setStyleSheet(UI_ADMIN_QSS)

        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QVBoxLayout(central)
        main_lay.setContentsMargins(20, 20, 20, 20)
        main_lay.setSpacing(15)

        # Header Area
        header_lay = QHBoxLayout()
        header_lay.setSpacing(12)
        
        logo_lbl = QLabel()
        logo_lbl.setPixmap(get_logo_pixmap(42))
        header_lay.addWidget(logo_lbl)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)
        title = QLabel("💎 AKIRA AUTOMATED DOLA ACCOUNT CREATOR")
        title.setObjectName("TitleLabel")
        subtitle = QLabel("Fully Automated Dola Account Onboarding & Session Sync Utility")
        subtitle.setObjectName("SubtitleLabel")
        title_vbox.addWidget(title)
        title_vbox.addWidget(subtitle)
        header_lay.addLayout(title_vbox)
        header_lay.addStretch()
        
        main_lay.addLayout(header_lay)

        # Horizontal Splitted Workspace
        workspace_lay = QHBoxLayout()
        workspace_lay.setSpacing(15)
        
        # Left Side Panel (Controls)
        ctrl_frame = QFrame()
        ctrl_frame.setObjectName("CardPanel")
        ctrl_lay = QVBoxLayout(ctrl_frame)
        ctrl_lay.setContentsMargins(15, 15, 15, 15)
        ctrl_lay.setSpacing(10)

        # Form Inputs Layout
        grid = QGridLayout()
        grid.setSpacing(8)

        grid.addWidget(QLabel("Target Client Device ID:"), 0, 0)
        self.txt_device = QLineEdit()
        self.txt_device.setPlaceholderText("Paste target hardware device ID...")
        grid.addWidget(self.txt_device, 0, 1)

        grid.addWidget(QLabel("Residential Proxy:"), 1, 0)
        self.txt_proxy = QLineEdit()
        self.txt_proxy.setPlaceholderText("ip:port:user:pass (Rotating)")
        grid.addWidget(self.txt_proxy, 1, 1)

        grid.addWidget(QLabel("Google Sheets API URL:"), 2, 0)
        self.txt_sheet = QLineEdit()
        self.txt_sheet.setPlaceholderText("Script deployment URL...")
        grid.addWidget(self.txt_sheet, 2, 1)

        grid.addWidget(QLabel("SMS Activation Service:"), 3, 0)
        self.cmb_sms_provider = QComboBox()
        self.cmb_sms_provider.addItems(["HeroSMS", "SMS Bower"])
        grid.addWidget(self.cmb_sms_provider, 3, 1)

        grid.addWidget(QLabel("SMS Service API Key:"), 4, 0)
        self.txt_sms_key = QLineEdit()
        self.txt_sms_key.setEchoMode(QLineEdit.EchoMode.Password)
        grid.addWidget(self.txt_sms_key, 4, 1)

        # Dynamic Country and Price Dropdown with Reload Button
        grid.addWidget(QLabel("SMS Country Selector:"), 5, 0)
        country_lay = QHBoxLayout()
        self.cmb_sms_country = QComboBox()
        self.cmb_sms_country.addItem("Click Load Prices to load...", "0")
        
        # Apply Monospace Font directly to widget so spacing alignments match perfectly
        self.cmb_sms_country.setFont(QFont("Consolas", 9))
        self.cmb_sms_country.view().setMinimumWidth(300)
        
        self.btn_load_countries = QPushButton("🔄 Load Prices")
        self.btn_load_countries.setObjectName("SecondaryButton")
        self.btn_load_countries.clicked.connect(self.load_sms_prices)
        
        country_lay.addWidget(self.cmb_sms_country, 4)
        country_lay.addWidget(self.btn_load_countries, 1)
        grid.addLayout(country_lay, 5, 1)

        # Captcha Solver Mode Selection Dropdown
        grid.addWidget(QLabel("Captcha Mode:"), 6, 0)
        self.cmb_captcha_mode = QComboBox()
        self.cmb_captcha_mode.addItems(["Auto (OpenCV/Paid API)", "Manual (Solve in Browser)"])
        grid.addWidget(self.cmb_captcha_mode, 6, 1)

        grid.addWidget(QLabel("Captcha Solver Service:"), 7, 0)
        self.cmb_captcha_provider = QComboBox()
        self.cmb_captcha_provider.addItems(["CapMonster", "2Captcha"])
        grid.addWidget(self.cmb_captcha_provider, 7, 1)

        grid.addWidget(QLabel("Captcha Solver API Key:"), 8, 0)
        self.txt_captcha_key = QLineEdit()
        self.txt_captcha_key.setEchoMode(QLineEdit.EchoMode.Password)
        grid.addWidget(self.txt_captcha_key, 8, 1)

        grid.addWidget(QLabel("Onboard Target Count:"), 9, 0)
        self.txt_count = QLineEdit("1")
        grid.addWidget(self.txt_count, 9, 1)

        ctrl_lay.addLayout(grid)

        # Action Buttons
        self.btn_start = QPushButton("🚀 Start Bulk Account Creation")
        self.btn_start.setObjectName("PrimaryButton")
        self.btn_start.clicked.connect(self.start_automation)

        self.btn_start.setEnabled(True)

        self.btn_stop = QPushButton("🛑 Stop Registration Loops")
        self.btn_stop.setObjectName("SecondaryButton")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_automation)

        ctrl_lay.addWidget(self.btn_start)
        ctrl_lay.addWidget(self.btn_stop)

        workspace_lay.addWidget(ctrl_frame, 4)

        # Right Side Panel (Console Viewer)
        console_frame = QFrame()
        console_frame.setObjectName("ConsoleBox")
        console_lay = QVBoxLayout(console_frame)
        console_lay.setContentsMargins(10, 10, 10, 10)
        console_lay.setSpacing(8)

        lbl_console = QLabel("Onboarding Activity Output Stream:")
        lbl_console.setObjectName("FormLabel")
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setPlaceholderText("Awaiting bulk script launch...")
        
        self.btn_clear = QPushButton("🗑️ Clear Logs")
        self.btn_clear.setObjectName("SecondaryButton")
        self.btn_clear.clicked.connect(self.clear_logs)

        console_lay.addWidget(lbl_console)
        console_lay.addWidget(self.console)
        console_lay.addWidget(self.btn_clear)

        workspace_lay.addWidget(console_frame, 5)
        main_lay.addLayout(workspace_lay)

        # Status Bar
        self.lbl_status = QLabel("System Status: Ready")
        self.lbl_status.setStyleSheet("color: #8C91A7; font-size: 8.5pt;")
        main_lay.addWidget(self.lbl_status)

    def log(self, log_type, msg):
        timestamp = time.strftime("%H:%M:%S")
        color = "#E5E7EB"
        prefix = f"[{log_type}]"
        
        if log_type == "SUCCESS":
            color = "#10B981"
        elif log_type == "ERROR":
            color = "#EF4444"
        elif log_type == "WARNING":
            color = "#F59E0B"
        elif log_type == "INFO":
            color = "#60A5FA"
            
        log_html = f'<span style="color:#6B7280;">[{timestamp}]</span> <span style="color:{color}; font-weight:bold;">{prefix}</span> <span style="color:#E5E7EB;">{msg}</span>'
        self.console.append(log_html)
        self.lbl_status.setText(f"Last Status: {msg[:60]}")

    def clear_logs(self):
        self.console.clear()

    # --- Live SMS Prices Fetch Action ---
    def load_sms_prices(self):
        provider = self.cmb_sms_provider.currentText()
        api_key = self.txt_sms_key.text().strip()

        if not api_key:
            QMessageBox.warning(self, "Missing Key", "Please enter the SMS API Key first to check prices.")
            return

        self.btn_load_countries.setEnabled(False)
        self.cmb_sms_country.clear()
        self.cmb_sms_country.addItem("Loading countries & prices...")

        self.price_loader = SmsPriceLoaderThread(provider, api_key, self)
        self.price_loader.log_signal.connect(self.log)
        self.price_loader.prices_loaded.connect(self.populate_countries_dropdown)
        self.price_loader.finished_signal.connect(lambda: self.btn_load_countries.setEnabled(True))
        self.price_loader.start()

    def populate_countries_dropdown(self, countries_list):
        self.loaded_countries = countries_list
        self.cmb_sms_country.clear()
        if not countries_list:
            self.cmb_sms_country.addItem("No countries available.", "0")
            return

        for c in countries_list:
            left_text = f"{c['name']} ({c['code']})" if c['code'] else c['name']
            display_text = f"{left_text:<28} ${c['price']:.2f}"
            self.cmb_sms_country.addItem(display_text, c['id'])

        # Auto-select previously saved country ID if found
        for idx in range(self.cmb_sms_country.count()):
            if self.cmb_sms_country.itemData(idx) == self.saved_country_id:
                self.cmb_sms_country.setCurrentIndex(idx)
                break

    def load_config(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        cfg_path = os.path.join(base_dir, "license_config.json")
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    url = cfg.get("web_app_url", "")
                    if url and "PASTE_YOUR" not in url:
                        self.txt_sheet.setText(url)
            except:
                pass

        proxy_path = os.path.join(base_dir, "proxies.txt")
        if os.path.exists(proxy_path):
            try:
                with open(proxy_path, "r", encoding="utf-8") as f:
                    lines = [l.strip() for l in f.read().splitlines() if l.strip()]
                    if lines:
                        self.txt_proxy.setText(lines[0])
            except:
                pass

        admin_cfg_path = os.path.join(base_dir, "admin_config.json")
        if os.path.exists(admin_cfg_path):
            try:
                with open(admin_cfg_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self.txt_device.setText(cfg.get("device_id", ""))
                    self.cmb_sms_provider.setCurrentText(cfg.get("sms_provider", "HeroSMS"))
                    self.txt_sms_key.setText(cfg.get("sms_key", ""))
                    self.saved_country_id = cfg.get("sms_country", "0")
                    self.cmb_captcha_mode.setCurrentText(cfg.get("captcha_mode", "Auto (OpenCV/Paid API)"))
                    self.cmb_captcha_provider.setCurrentText(cfg.get("captcha_provider", "CapMonster"))
                    self.txt_captcha_key.setText(cfg.get("captcha_key", ""))
                    self.txt_count.setText(cfg.get("target_count", "1"))
                    self.log("INFO", "Successfully loaded saved settings from admin_config.json")
                    
                    # Auto-trigger price loading if key exists
                    if self.txt_sms_key.text().strip():
                        from PyQt6.QtCore import QTimer
                        QTimer.singleShot(1000, self.load_sms_prices)
            except:
                pass

    def save_config(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cfg = {
            "device_id": self.txt_device.text().strip(),
            "sms_provider": self.cmb_sms_provider.currentText(),
            "sms_key": self.txt_sms_key.text().strip(),
            "sms_country": self.cmb_sms_country.currentData() or "0",
            "captcha_mode": self.cmb_captcha_mode.currentText(),
            "captcha_provider": self.cmb_captcha_provider.currentText(),
            "captcha_key": self.txt_captcha_key.text().strip(),
            "target_count": self.txt_count.text().strip()
        }
        try:
            with open(os.path.join(base_dir, "admin_config.json"), "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=4)
        except:
            pass

    def start_automation(self):
        device_id = self.txt_device.text().strip()
        sheet_url = self.txt_sheet.text().strip()
        sms_key = self.txt_sms_key.text().strip()
        captcha_mode = self.cmb_captcha_mode.currentText()
        captcha_key = self.txt_captcha_key.text().strip()

        if not device_id:
            QMessageBox.warning(self, "Missing Fields", "Please enter the target Client Device ID.")
            return
        if not sheet_url:
            QMessageBox.warning(self, "Missing Fields", "Please enter the Google Sheet API URL.")
            return
        if not sms_key:
            QMessageBox.warning(self, "Missing Fields", "Please enter the SMS Provider API key.")
            return
            
        # STRICT Check: If Auto mode is selected, Captcha solver API Key is mandatory
        if "Auto" in captcha_mode and not captcha_key:
            QMessageBox.warning(self, "Missing Fields", "Please enter the Captcha Solver API Key for Auto mode.")
            return

        self.save_config()

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)

        settings = {
            "device_id": device_id,
            "proxy": self.txt_proxy.text().strip(),
            "sms_provider": self.cmb_sms_provider.currentText(),
            "sms_key": sms_key,
            "sms_country": self.cmb_sms_country.currentData() or "0",
            "countries_list": getattr(self, "loaded_countries", []),
            "captcha_mode": captcha_mode,
            "captcha_provider": self.cmb_captcha_provider.currentText(),
            "captcha_key": captcha_key,
            "target_count": int(self.txt_count.text().strip() or "1")
        }

        self.worker = PlaywrightAutomatedWorker(settings, self)
        self.worker.log_signal.connect(self.log)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.session_completed.connect(self.upload_cookies_to_db)
        self.worker.start()

    def stop_automation(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop_automation()

    def on_worker_finished(self):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def upload_cookies_to_db(self, device_id, cookies_json):
        sheet_url = self.txt_sheet.text().strip()
        try:
            post_data = {
                "device_id": device_id,
                "event": "update_cookies",
                "cookies": cookies_json
            }
            
            payload_str = json.dumps(post_data)
            signed = sign_payload(payload_str)
            
            req_url = f"{sheet_url}?event=update_cookies&device_id={urllib.parse.quote(device_id)}"
            req = urllib.request.Request(
                req_url,
                data=urllib.parse.urlencode(signed).encode("utf-8"),
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                
                if "payload" in res_data:
                    decoded_bytes = base64.urlsafe_b64decode(res_data["payload"].encode('utf-8'))
                    res_data = json.loads(decoded_bytes.decode('utf-8'))
                
                if res_data.get("status") in ["success", "updated"]:
                    self.log("SUCCESS", f"Google Sheet updated! Account synced for Device: {device_id}")
                else:
                    self.log("ERROR", f"Database rejected sync: {res_data.get('message', 'Unknown Error')}")
        except Exception as e:
            self.log("ERROR", f"Database synchronization webhook failed: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Taskbar Icon ID
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('akira.admin.automatedcreator.v1')
    except:
        pass
        
    dashboard = AkiraAdminDashboard()
    dashboard.show()
    sys.exit(app.exec())

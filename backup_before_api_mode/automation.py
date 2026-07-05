import os
import sys
import time
import shutil
import random
import uuid
import base64
import subprocess
import re
from playwright.sync_api import sync_playwright
import json
import urllib.request

class DolaAutomationBot:
    def __init__(self, output_dir, callback_log, callback_status, client_mode=False):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.callback_log = callback_log
        self.callback_status = callback_status
        self.client_mode = client_mode
        self.headless = True
        self.optimize_prompts = True

        # Master profile to store login session cookies
        self.profile_dir_master = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "dola_profile_master"
        )
        os.makedirs(self.profile_dir_master, exist_ok=True)
        self.use_extension_vpn = False  # Default to Private Internet Access CLI system VPN
        self.use_vpn_mode = False
        self._current_context = None
        self.selected_account_name = None

    def _optimize_long_prompt(self, prompt_text):
        import re
        # Protect ratios (e.g., 9:16, 16:9, 1:1, etc.) from time/timestamp stripping
        ratios = []
        def repl_ratio(m):
            ratios.append(m.group(0))
            return f"__RATIO_{len(ratios)-1}__"
        prompt_text = re.sub(r'\b\d{1,2}:\d{1,2}\b', repl_ratio, prompt_text)

        # 1. Clean timestamps with any dashes (including Unicode en-dash and em-dash)
        cleaned = re.sub(r'(?i)\b(?:from|at|until|to)\s+\d{1,2}:\d{2}\s*(?:-|–|—|to)?\s*(?:\d{1,2}:\d{2})?\b', '', prompt_text)
        cleaned = re.sub(r'\b\d{1,2}:\d{2}\s*(?:-|–|—|to)?\s*(?:\d{1,2}:\d{2})?\b', '', cleaned)
        
        cleaned = re.sub(r'(?<!\d)[-–—]+(?!\d)', ' ', cleaned)  # Only replace dashes not inside storyboard ranges like 0-3s
        cleaned = re.sub(r'(?i)\b(?:from|at|until|to)\s*(?=\.|\?|!|,|;|\Z)', '', cleaned)

        # 3. Strip common audio cues / negative prompts (but keep harmless ones like cgi / music)
        cleaned = re.sub(r'(?i)\b(?:no\s+(?:captions|text\s+overlays|distorted\s+anatomy))\b', '', cleaned)
        cleaned = re.sub(r'(?i)\bnatural\s+audio\s+only\b', '', cleaned)
        cleaned = re.sub(r'(?i)\b(?:aquarium\s+ambience|water\s+sounds|distant\s+conversations|baby\s+squeals|babbling|laughter|chuckle)\b', '', cleaned)
        
        # Clean double spaces/punctuation
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\s*,\s*,+', ',', cleaned)
        cleaned = cleaned.strip(" ,.")

        # Restore ratios
        for idx, r in enumerate(ratios):
            cleaned = cleaned.replace(f"__RATIO_{idx}__", r)

        # 4. Truncate to safe character limit (max 1500 chars) ending at sentence or word boundary
        max_len = 1500
        if len(cleaned) <= max_len:
            return cleaned

        sub_text = cleaned[:max_len]
        last_dot = max(sub_text.rfind('.'), sub_text.rfind('!'), sub_text.rfind('?'))
        if last_dot > 120:
            return cleaned[:last_dot + 1].strip()

        last_space = sub_text.rfind(' ')
        if last_space > 0:
            return cleaned[:last_space].strip() + "..."
        return cleaned[:max_len].strip()


    def _notify_download(self, filename, row_id):
        """Show a Windows desktop toast notification when a video is downloaded."""
        try:
            import subprocess
            title = "AKIRA PRO"
            msg = f"Video #{row_id} downloaded successfully!\n{filename}"
            ps_cmd = (
                "Add-Type -AssemblyName System.Windows.Forms;"
                "$n = New-Object System.Windows.Forms.NotifyIcon;"
                "$n.Icon = [System.Drawing.SystemIcons]::Information;"
                "$n.Visible = $true;"
                f"$n.ShowBalloonTip(6000, '{title}', '{msg}', [System.Windows.Forms.ToolTipIcon]::Info);"
                "Start-Sleep -Seconds 7;"
                "$n.Dispose()"
            )
            subprocess.Popen(
                ["powershell", "-WindowStyle", "Hidden", "-Command", ps_cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass  # Notifications are non-critical — never crash the bot

    def _parse_proxy_string_local(self, proxy_str):
        proxy_str = proxy_str.strip()
        if not proxy_str:
            return None
        if "@" in proxy_str:
            try:
                creds, server = proxy_str.split("@", 1)
                server = server.strip()
                if not server.startswith("http://") and not server.startswith("https://") and not server.startswith("socks5://"):
                    server = f"http://{server}"
                res = {"server": server}
                if ":" in creds:
                    user, password = creds.split(":", 1)
                    res["username"] = user.strip()
                    res["password"] = password.strip()
                return res
            except:
                pass
        parts = proxy_str.split(":")
        if len(parts) == 4:
            ip, port, user, password = parts
            server = f"http://{ip.strip()}:{port.strip()}"
            return {"server": server, "username": user.strip(), "password": password.strip()}
        elif len(parts) == 2:
            ip, port = parts
            server = f"http://{ip.strip()}:{port.strip()}"
            return {"server": server}
        else:
            if not proxy_str.startswith("http://") and not proxy_str.startswith("https://") and not proxy_str.startswith("socks5://"):
                server = f"http://{proxy_str}"
            else:
                server = proxy_str
            return {"server": server}

    def _select_available_account(self, row_id):
        import json
        from datetime import date
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cookies_dir = os.path.join(base_dir, "cookies")
        os.makedirs(cookies_dir, exist_ok=True)
        
        usage_path = os.path.join(cookies_dir, "_usage.json")
        settings_path = os.path.join(base_dir, "vault_settings.json")
        
        limit = 6
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                limit = int(settings.get("daily_limit", 6))
            except:
                pass
                
        usage = {}
        if os.path.exists(usage_path):
            try:
                with open(usage_path, "r", encoding="utf-8") as f:
                    usage = json.load(f)
            except:
                pass
                
        today = str(date.today())
        
        # Reset locks: clear if date is old OR if locked_by row is NOT in active_row_ids
        # active_row_ids is a class-level set maintained by the bot to track running rows
        active_ids = getattr(DolaAutomationBot, "_active_row_ids", set())
        changed = False
        for k, v in usage.items():
            locked_by = v.get("locked_by")
            if locked_by is None:
                continue
            # Clear if: different day, OR the locking row is no longer running
            if v.get("date") != today or (locked_by not in active_ids and locked_by != row_id):
                v["locked_by"] = None
                if v.get("date") != today:
                    v["date"] = today
                    v["uses_today"] = 0
                changed = True
            elif locked_by == row_id:
                v["locked_by"] = None
                changed = True
        if changed:
            try:
                with open(usage_path, "w", encoding="utf-8") as f:
                    json.dump(usage, f, indent=2)
            except:
                pass

        files = sorted([f for f in os.listdir(cookies_dir) if f.endswith(".json") and not f.startswith("_")])
        if not files:
            return None
            
        # Offset starting search file based on row_id to achieve round-robin/row-specific accounts
        try:
            start_idx = (int(row_id) - 1) % len(files)
        except:
            start_idx = 0
            
        ordered_files = files[start_idx:] + files[:start_idx]
        
        selected_file = None
        for fname in ordered_files:
            fpath = os.path.join(cookies_dir, fname)
            
            u = usage.get(fname, {})
            if u.get("status") in ["EXPIRED", "FAILED"]:
                continue

            # Skip accounts that hit Dola's daily limit today or have 0 points left
            if u.get("status") == "DAILY_LIMIT" and u.get("date") == today:
                continue
            if u.get("points_left") == 0 and u.get("date") == today:
                continue
                
            uses_today = u.get("uses_today", 0) if u.get("date") == today else 0
            if uses_today >= limit:
                continue
                
            if u.get("locked_by") is not None:
                continue
                
            # Pre-Run Cookie Validation (expiration check)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cookies = data.get("cookies", data) if isinstance(data, dict) else data
                
                current_time = time.time()
                is_expired = True
                has_session_cookie = False
                
                for c in cookies:
                    if c.get("name") in ["sessionid", "sid_tt", "sid_guard"]:
                        has_session_cookie = True
                        exp = c.get("expiry")
                        if exp is None or exp > current_time:
                            is_expired = False
                            break
                            
                if has_session_cookie and is_expired:
                    self.log("WARNING", f"Pre-Run Validation: Account {fname} cookies expired based on expirationDate. Skipping.")
                    if "backup_status" in u or "backup_points_left" in u:
                        u["status"] = u.get("backup_status")
                        u["limit_timestamp"] = u.get("backup_limit_timestamp")
                        u["points_left"] = u.get("backup_points_left")
                        u["uses_today"] = u.get("backup_uses_today", 0)
                        u["date"] = u.get("backup_date", today)
                        for key in ["backup_status", "backup_limit_timestamp", "backup_points_left", "backup_uses_today", "backup_date"]:
                            u.pop(key, None)
                    else:
                        u["status"] = "EXPIRED"
                        u["date"] = today
                    usage[fname] = u
                    with open(usage_path, "w", encoding="utf-8") as f:
                        json.dump(usage, f, indent=2)
                    continue
            except Exception as parse_err:
                self.log("WARNING", f"Pre-Run Validation: Failed to parse cookies for {fname}: {str(parse_err)}")
                if "backup_status" in u or "backup_points_left" in u:
                    u["status"] = u.get("backup_status")
                    u["limit_timestamp"] = u.get("backup_limit_timestamp")
                    u["points_left"] = u.get("backup_points_left")
                    u["uses_today"] = u.get("backup_uses_today", 0)
                    u["date"] = u.get("backup_date", today)
                    for key in ["backup_status", "backup_limit_timestamp", "backup_points_left", "backup_uses_today", "backup_date"]:
                        u.pop(key, None)
                else:
                    u["status"] = "FAILED"
                usage[fname] = u
                with open(usage_path, "w", encoding="utf-8") as f:
                    json.dump(usage, f, indent=2)
                continue
                
            selected_file = fname
            break
            
        if selected_file:
            u = usage.get(selected_file, {})
            u["locked_by"] = row_id
            u["date"] = today
            usage[selected_file] = u
            with open(usage_path, "w", encoding="utf-8") as f:
                json.dump(usage, f, indent=2)
            return selected_file
            
        return None

    def _release_account_lock(self, fname, success=False, mark_expired=False, mark_daily_limit=False):
        import json
        from datetime import date
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cookies_dir = os.path.join(base_dir, "cookies")
        usage_path = os.path.join(cookies_dir, "_usage.json")
        
        if not os.path.exists(usage_path):
            return
            
        try:
            with open(usage_path, "r", encoding="utf-8") as f:
                usage = json.load(f)
        except:
            return
            
        if fname in usage:
            u = usage[fname]
            u["locked_by"] = None
            
            today = str(date.today())
            
            if success:
                # Execution succeeded: remove/discard the backup parameters
                for key in ["backup_status", "backup_limit_timestamp", "backup_points_left", "backup_uses_today", "backup_date"]:
                    u.pop(key, None)
                    
                if u.get("date") != today:
                    u["date"] = today
                    u["uses_today"] = 0
                u["uses_today"] = u.get("uses_today", 0) + 1
            else:
                # Execution failed/aborted/limit hit: restore backup if present
                if "backup_status" in u or "backup_points_left" in u:
                    u["status"] = u.get("backup_status")
                    u["limit_timestamp"] = u.get("backup_limit_timestamp")
                    u["points_left"] = u.get("backup_points_left")
                    u["uses_today"] = u.get("backup_uses_today", 0)
                    u["date"] = u.get("backup_date", today)
                    # Discard the backup parameters once restored
                    for key in ["backup_status", "backup_limit_timestamp", "backup_points_left", "backup_uses_today", "backup_date"]:
                        u.pop(key, None)
                else:
                    if u.get("date") != today:
                        u["date"] = today
                        u["uses_today"] = 0
                        
                    if mark_expired:
                        u["status"] = "EXPIRED"
        
                    if mark_daily_limit:
                        import time
                        u["status"] = "DAILY_LIMIT"
                        u["date"] = today  # limit resets next day automatically
                        u["limit_timestamp"] = time.time()
                
            usage[fname] = u
            
            with open(usage_path, "w", encoding="utf-8") as f:
                json.dump(usage, f, indent=2)

    def log(self, type_str, message):
        if self.callback_log:
            self.callback_log(type_str, message)
        else:
            print(f"[{type_str}] {message}")

    def update_status(self, row_id, status, action):
        if self.callback_status:
            self.callback_status(row_id, status, action)
        else:
            print(f"[Row {row_id} Status] {status}: {action}")

    def remove_watermark_from_video(self, row_id, target_path):
        import cv2
        import numpy as np
        from moviepy.editor import VideoFileClip

        temp_output_path = target_path + ".clean.mp4"
        self.update_status(row_id, "DOWNLOADING", "[5/5] Removing video watermark...")
        self.log("INFO", f"Row {row_id}: Removing watermark from video...")

        clip = None
        processed_clip = None
        try:
            cpu_cores = os.cpu_count() or 4
            clip = VideoFileClip(target_path)
            video_width, video_height = clip.size

            x_start = int(video_width * 0.78)
            x_end = int(video_width * 0.99)
            y_start = int(video_height * 0.92)
            y_end = int(video_height * 0.99)

            # Extract mask from first frame
            first_frame = clip.get_frame(0)
            roi = first_frame[y_start:y_end, x_start:x_end]
            r, g, b = roi[:,:,0], roi[:,:,1], roi[:,:,2]
            white_pixels = (r > 210) & (g > 210) & (b > 210)

            text_mask = np.zeros(roi.shape[:2], dtype=np.uint8)
            text_mask[white_pixels] = 255

            kernel = np.ones((7, 7), np.uint8)
            text_mask = cv2.dilate(text_mask, kernel, iterations=2)

            static_mask = np.zeros(first_frame.shape[:2], dtype=np.uint8)
            static_mask[y_start:y_end, x_start:x_end] = text_mask

            def process_frame(frame):
                return cv2.inpaint(frame, static_mask, inpaintRadius=8, flags=cv2.INPAINT_TELEA)

            processed_clip = clip.fl_image(process_frame)

            processed_clip.write_videofile(
                temp_output_path,
                codec="libx264",
                audio_codec="aac",
                bitrate="6000k",
                threads=cpu_cores,
                ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
                logger=None
            )

            clip.close()
            processed_clip.close()

            # Swap files
            if os.path.exists(temp_output_path):
                try:
                    os.remove(target_path)
                    os.rename(temp_output_path, target_path)
                    self.log("SUCCESS", f"Row {row_id}: Watermark removed successfully.")
                except Exception as e:
                    self.log("WARNING", f"Row {row_id}: Failed to replace video file: {str(e)}")
            else:
                self.log("WARNING", f"Row {row_id}: Watermark removal did not produce file. Keeping original.")

        except Exception as e:
            self.log("WARNING", f"Row {row_id}: Error removing watermark: {str(e)}. Keeping original video.")
            if clip:
                try: clip.close()
                except: pass
            if processed_clip:
                try: processed_clip.close()
                except: pass
            if os.path.exists(temp_output_path):
                try: os.remove(temp_output_path)
                except: pass

    def create_caption_txt_file(self, row_id, target_path, prompt):
        try:
            # 1. Parse prompt to extract the exact unique title/tags part outside quotes
            import re
            caption = ""

            # Match: "Visual Prompt",Video Title
            match = re.match(r'^"([^"]*)"\s*,\s*(.*)$', prompt.strip())
            if match:
                caption = match.group(2).strip()
            else:
                quoted_parts = re.findall(r'"([^"]*)"', prompt)
                if len(quoted_parts) >= 1:
                    last_quote_idx = prompt.rfind('"')
                    if last_quote_idx != -1 and last_quote_idx < len(prompt) - 1:
                        caption = prompt[last_quote_idx + 1:].strip(' ,')

            # Clean up leading/trailing quotes or spaces from the extracted title
            if caption:
                caption = caption.strip(' "\',')

            if not caption:
                # Fallback: Parse the first sentence or first 10 words
                quoted_parts = re.findall(r'"([^"]*)"', prompt)
                if quoted_parts:
                    caption = quoted_parts[0].strip()
                else:
                    caption = prompt

                # Truncate to first 10 words
                words = caption.split()
                if len(words) > 10:
                    caption = " ".join(words[:10]) + "..."

            # Write to txt file with exact same base path as the video
            txt_path = os.path.splitext(target_path)[0] + ".txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(caption)

            self.log("INFO", f"Row {row_id}: Saved unique caption to {os.path.basename(txt_path)}")
        except Exception as e:
            self.log("WARNING", f"Row {row_id}: Failed to generate caption txt file: {str(e)}")

    def _minimize_chrome(self):
        # Programmatic minimization disabled by user request
        pass

    def _clean_profile_session_only(self, user_data_dir):
        if not os.path.exists(user_data_dir):
            return

        if self.use_extension_vpn:
            targets = [
                "History",
                os.path.join("Default", "History")
            ]
        else:
            targets = [
                "Cookies", "History", "Local Storage", "IndexedDB", "Session Storage", "Web Data", "Preferences", "Network",
                os.path.join("Default", "Cookies"),
                os.path.join("Default", "History"),
                os.path.join("Default", "Local Storage"),
                os.path.join("Default", "IndexedDB"),
                os.path.join("Default", "Session Storage"),
                os.path.join("Default", "Web Data"),
                os.path.join("Default", "Preferences"),
                os.path.join("Default", "Network"),
            ]

        import shutil
        for t in targets:
            full_path = os.path.join(user_data_dir, t)
            if os.path.exists(full_path):
                try:
                    if os.path.isdir(full_path):
                        shutil.rmtree(full_path, ignore_errors=True)
                    else:
                        os.remove(full_path)
                except Exception:
                    pass

    def _rotate_vpn(self, row_id, user_data_dir, setup_mode):
        if self.use_extension_vpn:
            self.log("INFO", f"Row {row_id}: VPN extension in use. Skipping system VPN rotation.")
            return True

        # Common installation paths for PIA VPN CLI
        paths = [
            r"C:\Program Files\Private Internet Access\piactl.exe",
            r"C:\Program Files (x86)\Private Internet Access\piactl.exe",
            "piactl.exe",
            "piactl"
        ]

        piactl_path = None
        for p in paths:
            if "\\" in p or "/" in p:
                if os.path.exists(p):
                    piactl_path = p
                    break
            else:
                try:
                    res = subprocess.run([p, "--version"], capture_output=True, text=True, timeout=2)
                    if res.returncode == 0:
                        piactl_path = p
                        break
                except Exception:
                    continue

        if not piactl_path:
            self.log("WARNING", f"Row {row_id}: Private Internet Access CLI (piactl.exe) not found. Skipping IP rotation.")
            return False

        self.update_status(row_id, "SUBMITTING", "[1/5] Connecting to VPN...")

        try:
            pinned_region = None
            vpn_cfg_path = os.path.join(user_data_dir, "vpn_region_pin.json")
            if os.path.exists(vpn_cfg_path):
                try:
                    import json
                    with open(vpn_cfg_path, "r", encoding="utf-8") as f:
                        pinned_region = json.load(f).get("pinned_region")
                    if pinned_region:
                        self.log("INFO", f"Row {row_id}: Profile slot has pinned VPN region: '{pinned_region}'")
                except Exception:
                    pass

            # 1. Disconnect VPN
            subprocess.run([piactl_path, "disconnect"], capture_output=True, timeout=5)
            time.sleep(1)

            selected_region = pinned_region

            # 2. Get list of regions to pick a random location if not pinned
            if not pinned_region:
                res = subprocess.run([piactl_path, "get", "regions"], capture_output=True, text=True, timeout=5)
                if res.returncode == 0 and res.stdout.strip():
                    regions = [line.strip() for line in res.stdout.split('\n') if line.strip() and not line.startswith("-") and not line.startswith("Regions:")]
                    regions = [r for r in regions if r and not any(x in r.lower() for x in ["name", "region", "connection"])]
                    if regions:
                        allowed_keywords = ["singapore", "malaysia", "philippines", "indonesia"]
                        filtered_regions = [r for r in regions if any(k in r.lower() for k in allowed_keywords)]

                        if filtered_regions:
                            selected_region = random.choice(filtered_regions)
                        else:
                            selected_region = random.choice(regions)

            if selected_region:
                self.log("INFO", f"Row {row_id}: Setting VPN region to: '{selected_region}'...")
                subprocess.run([piactl_path, "set", "region", selected_region], capture_output=True, timeout=5)

            # 3. Connect VPN
            subprocess.run([piactl_path, "connect"], capture_output=True, timeout=5)

            # 4. Wait for connection state to become "Connected"
            self.log("INFO", f"Row {row_id}: Connecting to VPN and waiting for new IP address...")
            connected = False
            state = "Unknown"
            for attempt in range(15):
                state_res = subprocess.run([piactl_path, "get", "connectionstate"], capture_output=True, text=True, timeout=5)
                state = state_res.stdout.strip() if state_res.returncode == 0 else ""
                if "Connected" in state:
                    connected = True
                    self.log("SUCCESS", f"Row {row_id}: VPN successfully connected! Status: {state}")
                    break
                time.sleep(1)

            if not connected:
                self.log("WARNING", f"Row {row_id}: VPN connection check timed out (status: {state}). Proceeding anyway.")
            else:
                if not pinned_region and selected_region:
                    try:
                        import json
                        os.makedirs(user_data_dir, exist_ok=True)
                        with open(vpn_cfg_path, "w", encoding="utf-8") as f:
                            json.dump({"pinned_region": selected_region}, f)
                        self.log("SUCCESS", f"Row {row_id}: Pinned VPN region '{selected_region}' to this profile slot.")
                    except Exception as save_err:
                        self.log("WARNING", f"Row {row_id}: Failed to save pinned VPN region: {str(save_err)}")

            return connected
        except Exception as e:
            self.log("WARNING", f"Row {row_id}: Failed to rotate VPN: {str(e)}")
            return False

    def run_generation(self, row_id, prompt, model, duration, ratio, setup_mode=False, is_image=False, proxy_list=None, sms_key=None, sms_country="0", timeout_min=30):
        self.last_error_reason = None
        self.is_stopped = False

        # Track active row IDs at class level for stale lock detection
        if not hasattr(DolaAutomationBot, "_active_row_ids"):
            DolaAutomationBot._active_row_ids = set()
        DolaAutomationBot._active_row_ids.add(row_id)

        success = False
        selected_account = None

        # If duration is 15s, append "15 sec video" to the prompt
        is_15s = False
        try:
            if duration and ("15" in str(duration)):
                is_15s = True
        except:
            pass

        # Parse prompt to separate visual prompt from video title
        import re
        
        def clean_prompt_duration(text):
            # Strip any mentions of specific seconds or durations (e.g. 15-second, 15 sec, 15s, 10s, 10-second)
            # and any timestamp sequences (like 00:00, 00:03, 00:10) to bypass Dola's chatbot AI analyzer
            # which overrides/truncates output on detecting >10s or custom storyboard timestamps in prompt text.
            cleaned = text
            
            # Protect ratios (e.g., 9:16, 16:9, 1:1, etc.) from time/timestamp stripping
            ratios = []
            def repl_ratio(m):
                ratios.append(m.group(0))
                return f"__RATIO_{len(ratios)-1}__"
            cleaned = re.sub(r'\b\d{1,2}:\d{1,2}\b', repl_ratio, cleaned)
            
            # 1. Strip duration keywords (preserve storyboard ranges like 0-3s by using lookbehinds)
            cleaned = re.sub(r'(?i)(?<![-–—\d])\b\d+[\s-]?seconds?\b', '', cleaned)
            cleaned = re.sub(r'(?i)(?<![-–—\d])\b\d+s\b', '', cleaned)
            cleaned = re.sub(r'(?i)(?<![-–—\d])\b\d+[\s-]?sec\b', '', cleaned)
            
            # 2. Strip timestamp markers like "from 00:00 to 00:03", "at 00:05", "until 00:10"
            cleaned = re.sub(r'(?i)\b(?:at|until|from|to)\s+\d{1,2}:\d{2}\b', '', cleaned)
            # Strip any bare timestamps like "00:00", "00:03"
            cleaned = re.sub(r'\b\d{1,2}:\d{2}\b', '', cleaned)
            
            # 3. Clean up leftover prepositions before periods or punctuation
            cleaned = re.sub(r'(?i)\b(?:at|until|from|to)\s*(?=\.|\?|!|,|;|\Z)', '', cleaned)
            
            # 4. Clean up commas and spaces
            cleaned = re.sub(r'\s*,\s*,+', ',', cleaned)
            cleaned = re.sub(r'\s+', ' ', cleaned)
            
            # Restore ratios
            for idx, r in enumerate(ratios):
                cleaned = cleaned.replace(f"__RATIO_{idx}__", r)
                
            return cleaned.strip(" ,.")

        import csv
        import io
        
        visual_prompt = prompt
        title_part = ""
        
        visual_prompt = prompt.strip()
        title_part = ""
        
        # Only split prompt/title if the line is explicitly quoted (e.g. "prompt text", title_part)
        if visual_prompt.startswith('"') or visual_prompt.startswith("'"):
            try:
                reader = csv.reader(io.StringIO(visual_prompt))
                row = next(reader)
                if len(row) >= 2:
                    visual_prompt = row[0].strip()
                    title_part = row[1].strip()
                else:
                    visual_prompt = row[0].strip()
            except:
                if ',' in prompt:
                    parts = prompt.rsplit(',', 1)
                    visual_prompt = parts[0].strip()
                    title_part = parts[1].strip()
                
        visual_prompt = clean_prompt_duration(visual_prompt)
        if self.optimize_prompts:
            visual_prompt = self._optimize_long_prompt(visual_prompt)
        if title_part:
            prompt = f'"{visual_prompt}",{title_part}'
        else:
            prompt = visual_prompt

        max_page_retries = 5
        base_slot_id = 1 if int(row_id) % 2 == 1 else 2
        current_slot = base_slot_id
        
        selected_account = None
        user_data_dir = None
        p = None
        context = None

        # Route handler: Only block trackers/analytics, allow all other resources to load normally
        def build_selective_proxy_handler(proxy_cfg):
            def handle_route(route):
                url_lower = route.request.url.lower()

                # Only block known trackers and analytics — everything else loads normally
                trackers = ["sentry.io", "google-analytics", "doubleclick", "facebook.net",
                            "telemetry", "byteoversea", "bytegecko", "volces", "volcengine", "clarity"]
                if any(tk in url_lower for tk in trackers):
                    route.abort()
                    return

                # Intercept the completion or chat endpoint to enforce duration and ratio!
                if route.request.method == "POST" and ("completion" in url_lower or "chat" in url_lower or "send" in url_lower or "message" in url_lower):
                    try:
                        post_data = route.request.post_data
                        if post_data and post_data.strip().startswith(("{", "[")):
                            import json
                            body = json.loads(post_data)
                            if "chat_ability" in body and "ability_param" in body["chat_ability"]:
                                param_str = body["chat_ability"]["ability_param"]
                                if param_str:
                                    param = json.loads(param_str)
                                    self.log("INFO", f"Row {row_id}: [INTERCEPT] Original request params: {param}")
                                    
                                    # Override ratio/aspect_ratio
                                    param["ratio"] = ratio
                                    param["aspect_ratio"] = ratio
                                    
                                    # Override duration if 15s is selected
                                    if "duration" in param:
                                        if is_15s:
                                            param["duration"] = 15
                                            
                                    body["chat_ability"]["ability_param"] = json.dumps(param)
                                    self.log("INFO", f"Row {row_id}: [INTERCEPT] Patched request params: {param}")
                                    
                                    route.continue_(post_data=json.dumps(body))
                                    return
                    except Exception as e:
                        self.log("WARNING", f"Row {row_id}: Failed to patch request: {str(e)}")

                route.continue_()

            return handle_route

        for page_retry in range(max_page_retries):
            try:
                # Clean up previous loop context
                if context:
                    try: context.close()
                    except: pass
                if p:
                    try: p.stop()
                    except: pass
                if user_data_dir and os.path.exists(user_data_dir) and "_temp_" in user_data_dir:
                    try: shutil.rmtree(user_data_dir, ignore_errors=True)
                    except: pass
                    
                # If we already had an account locked, release it as failed
                if selected_account:
                    self._release_account_lock(selected_account, success=False)
                    selected_account = None

                if page_retry > 0:
                    self.log("INFO", f"Row {row_id}: === PAGE LOAD RETRY {page_retry + 1}/{max_page_retries} ===")
                    time.sleep(3)

                # 1. Select account if not in setup_mode
                if not setup_mode:
                    selected_account = self._select_available_account(row_id)
                    self.selected_account_name = selected_account
                    if not selected_account:
                        self.log("ERROR", f"Row {row_id}: No available accounts in Session Vault (all limit-hit, expired, or locked).")
                        self.last_error_reason = "NO_ACCOUNTS_AVAILABLE"
                        return False
                    account_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies", selected_account)
                else:
                    selected_account = None
                    self.selected_account_name = None
                    account_path = None
                    
                # 2. Get active proxies (Bypassed if Desktop VPN Mode is active)
                active_proxies = []
                if self.use_vpn_mode:
                    active_proxies = []
                elif proxy_list:
                    active_proxies = proxy_list
                else:
                    # Fallback to proxies.txt
                    proxies_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxies.txt")
                    if os.path.exists(proxies_path):
                        try:
                            with open(proxies_path, "r", encoding="utf-8") as f:
                                lines = [l.strip() for l in f.read().splitlines() if l.strip()]
                            for line in lines:
                                parsed = self._parse_proxy_string_local(line)
                                if parsed:
                                    active_proxies.append(parsed)
                        except:
                            pass

                # Find round-robin index for proxy pairing
                proxy_idx = 0
                if selected_account:
                    try:
                        cookies_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies")
                        all_accounts = sorted([f for f in os.listdir(cookies_dir) if f.endswith(".json") and not f.startswith("_")])
                        proxy_idx = all_accounts.index(selected_account)
                    except:
                        pass

                # 3. Launch browser with Smart Proxy Fallback
                browser_launched = False
                proxy_retries = 0
                max_proxy_retries = min(3, len(active_proxies)) if active_proxies else 1
                selected_proxy = None
                
                # Use account-specific profile folder to ensure absolute isolation and prevent concurrent conflicts
                acc_clean = os.path.splitext(selected_account)[0]
                user_data_dir = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    f"chrome_profile_acc_{acc_clean}"
                )
                self.log("INFO", f"Row {row_id}: Using persistent browser profile directory for account: {acc_clean}")

                # Proactively connect/rotate VPN if in Desktop VPN mode
                if self.use_vpn_mode and not self.use_extension_vpn:
                    self._rotate_vpn(row_id, user_data_dir, setup_mode)

                # Setup custom launching args
                launch_args = [
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-infobars",
                    "--start-maximized"
                ]

                while proxy_retries < max_proxy_retries:
                    if active_proxies:
                        current_proxy_idx = (proxy_idx + proxy_retries) % len(active_proxies)
                        selected_proxy = active_proxies[current_proxy_idx]
                        proxy_host = selected_proxy["server"].replace("http://", "").replace("https://", "")
                        
                        # Live Log Details (Log exact account filename and proxy IP used)
                        self.log("INFO", f"Row {row_id}: Selected Account {selected_account} on Proxy IP: {proxy_host}")
                    else:
                        selected_proxy = None
                        if not setup_mode:
                            self.log("INFO", f"Row {row_id}: Selected Account {selected_account} without proxy.")
                        else:
                            self.log("INFO", f"Row {row_id}: Launching in Setup Mode without proxy.")
                    
                    try:
                        # Select randomized User-Agent and Screen Viewport Resolution for anti-fingerprinting
                        USER_AGENTS = [
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                        ]
                        RESOLUTIONS = [
                            {"width": 1920, "height": 1080},
                            {"width": 1536, "height": 864},
                            {"width": 1440, "height": 900},
                            {"width": 1366, "height": 768}
                        ]
                        selected_ua = random.choice(USER_AGENTS)
                        selected_res = random.choice(RESOLUTIONS)
                        
                        p = sync_playwright().start()
                        
                        # Detect custom Chromium executable inside base directory
                        if getattr(sys, 'frozen', False):
                            base_dir = os.path.dirname(sys.executable)
                        else:
                            base_dir = os.path.dirname(os.path.abspath(__file__))
                            
                        # Look for custom chromium\chrome.exe
                        custom_chromium_path = os.path.join(base_dir, "chromium", "chrome.exe")

                        # Headless mode during actual generation when requested via GUI checkbox (or client mode default)
                        is_headless = False
                        if self.headless and not setup_mode and not self.use_extension_vpn:
                            is_headless = True
                            
                        launch_kwargs = {
                            "user_data_dir": user_data_dir,
                            "headless": is_headless,
                            "ignore_default_args": ["--disable-extensions"] if self.use_extension_vpn else None,
                            "args": launch_args,
                            "user_agent": selected_ua,
                            "viewport": selected_res,
                            "proxy": selected_proxy
                        }
                        
                        if os.path.exists(custom_chromium_path):
                            launch_kwargs["executable_path"] = custom_chromium_path
                        else:
                            # Fallback to local system Google Chrome channel
                            launch_kwargs["channel"] = "chrome"
                            
                        context = p.chromium.launch_persistent_context(**launch_kwargs)
                        self._current_context = context
                        
                        # Inject fetch interceptor at CONTEXT level so it fires on every page/navigation
                        # (Now handled via Playwright route interception on the backend)
                        
                        # 4. Inject cookies
                        cookies_injected = False
                        if not setup_mode and account_path:
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
                                    self.log("SUCCESS", f"Row {row_id}: Successfully injected {len(cleaned_cookies)} session cookies from {selected_account}.")
                                    cookies_injected = True
                                    
                                    # 4b. Inject Local Storage to prevent session clashing on shared profile slots
                                    origins = state_data.get("origins", [])
                                    if origins:
                                        ls_script = "try { window.localStorage.clear(); } catch(e) {}\n"
                                        for orig in origins:
                                            if "dola.com" in orig.get("origin", ""):
                                                for item in orig.get("localStorage", []):
                                                    k = item["name"].replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
                                                    v = item["value"].replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
                                                    ls_script += f"try {{ window.localStorage.setItem('{k}', '{v}'); }} catch(e) {{}}\n"
                                        context.add_init_script(f"try {{\n{ls_script}\n}} catch(e) {{}}")
                                        self.log("INFO", f"Row {row_id}: Registered localStorage injection script for {selected_account}.")
                            except Exception as cookie_err:
                                self.log("WARNING", f"Row {row_id}: Failed to inject saved cookies/localStorage: {str(cookie_err)}")
                        
                        # Reuse the default page opened by persistent context to prevent about:blank tab leaks
                        page = context.pages[0] if context.pages else context.new_page()
                        page.set_default_timeout(60000)
                        
                        # Console message listener to capture duration patching logs
                        def handle_console_msg(msg):
                            txt = msg.text
                            if any(k in txt for k in ["PATCHED_DURATION", "ORIGINAL_DURATION", "PATCH_ERROR", "FETCH_PATCHER"]):
                                self.log("INFO", f"Row {row_id}: [CONSOLE] {txt}")
                        page.on("console", handle_console_msg)
                        
                        # Clear cookies if setup mode
                        if setup_mode or not cookies_injected:
                            context.clear_cookies()
                            
                        # Enable selective proxy routing: page assets = direct (0 KB), dola API calls = proxied
                        context.route("**/*", build_selective_proxy_handler(selected_proxy))
                        self._minimize_chrome()
                        
                        browser_launched = True
                        break
                    except Exception as launch_err:
                        self.log("WARNING", f"Row {row_id}: Proxy connection failed on {proxy_host if selected_proxy else 'local'}: {str(launch_err)}. Attempting proxy fallback...")
                        proxy_retries += 1
                        if context:
                            try: context.close()
                            except: pass
                        if p:
                            try: p.stop()
                            except: pass
                
                if not browser_launched:
                    self.log("ERROR", f"Row {row_id}: Failed to launch browser after trying multiple proxies. Retrying slot run...")
                    continue



                # Wait and verify VPN connection to prevent loading Dola on real Pakistani IP
                if not self.use_extension_vpn:
                    self.log("INFO", f"Row {row_id}: Verifying VPN IP address...")
                    for check_attempt in range(15):
                        if self.is_stopped:
                            break
                        try:
                            # Verify VPN IP via Python urllib to avoid opening browser tabs
                            url = "https://ipinfo.io/json"
                            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                            
                            # If a proxy is configured, route urllib through the proxy
                            if selected_proxy:
                                proxy_server = selected_proxy.get("server", "")
                                proxy_handler = urllib.request.ProxyHandler({'http': proxy_server, 'https': proxy_server})
                                opener = urllib.request.build_opener(proxy_handler)
                            else:
                                opener = urllib.request.build_opener()
                                
                            with opener.open(req, timeout=8) as response:
                                ip_data = json.loads(response.read().decode('utf-8'))
                                
                            country = ip_data.get("country", "")
                            ip_addr = ip_data.get("ip", "")
                            city = ip_data.get("city", "")

                            if country == "PK":
                                self.log("WARNING", f"Row {row_id}: VPN IP still shows Pakistan (IP: {ip_addr}, {city}). Retrying...")
                                raise Exception("PAGE_NOT_LOADED")
                            else:
                                self.log("INFO", f"Row {row_id}: VPN IP confirmed: {ip_addr}, {country}, {city}")
                                break
                        except Exception as ip_err:
                            # Log as INFO for the first 5 attempts to avoid warning spam during transient DNS/DHCP setup
                            log_level = "INFO" if check_attempt < 5 else "WARNING"
                            self.log(log_level, f"Row {row_id}: VPN IP verification attempt {check_attempt + 1}/15: waiting for network to stabilize ({repr(ip_err)})")
                            time.sleep(3)

                nav_success = False
                max_nav_attempts = 5
                for nav_attempt in range(max_nav_attempts):
                    try:
                        page.goto("https://www.dola.com/chat/create-image", wait_until="domcontentloaded", timeout=120000)

                        is_restricted = (
                            "region-restricted" in page.url or
                            page.evaluate("""() => {
                                return document.body && document.body.innerText &&
                                       document.body.innerText.includes("not available in this country or region");
                            }""")
                        )

                        if is_restricted:
                            self.log("ERROR", f"Row {row_id}: Region restricted by AI Engine ('region-restricted' page loaded).")
                            raise Exception("PAGE_NOT_LOADED")

                        # Wipe browser storage to prevent stale auth states (only in setup_mode)
                        if setup_mode:
                            try:
                                page.evaluate("""() => {
                                    try { localStorage.clear(); } catch(e) {}
                                    try { sessionStorage.clear(); } catch(e) {}
                                    try {
                                        if (window.indexedDB && window.indexedDB.databases) {
                                            window.indexedDB.databases().then(dbs => {
                                                dbs.forEach(db => {
                                                    try { window.indexedDB.deleteDatabase(db.name); } catch(e) {}
                                                });
                                            });
                                        }
                                    } catch(e) {}
                                }""")
                                self.log("INFO", f"Row {row_id}: Successfully cleared session storage, localStorage, and IndexedDB.")
                            except Exception as clean_err:
                                self.log("WARNING", f"Row {row_id}: Non-critical error clearing browser storage: {str(clean_err)}")

                        nav_success = True
                        break
                    except Exception as nav_err:
                        err_str = str(nav_err)
                        # Check if the error is a proxy/network connection failure
                        is_proxy_error = any(code in err_str for code in [
                            "ERR_TUNNEL_CONNECTION_FAILED",
                            "ERR_PROXY_CONNECTION_FAILED",
                            "ERR_CONNECTION_REFUSED",
                            "ERR_CONNECTION_RESET",
                            "ERR_NAME_NOT_RESOLVED",
                            "ERR_CONNECTION_TIMED_OUT",
                            "ERR_PROXY_AUTH_UNSUPPORTED"
                        ])
                        
                        if is_proxy_error:
                            self.log("WARNING", f"Row {row_id}: Proxy connection failed: {err_str.split('Call log:')[0].strip()}. Aborting this proxy/account run...")
                            raise Exception("PROXY_CONNECTION_FAILED")
                            
                        if self.use_vpn_mode and not self.use_extension_vpn:
                            self.log("WARNING", f"Row {row_id}: Navigation failed: {str(nav_err)}. Rotating VPN IP and retrying...")
                            self._rotate_vpn(row_id, user_data_dir, setup_mode)
                        else:
                            self.log("WARNING", f"Row {row_id}: Navigation failed: {str(nav_err)}. Retrying navigation...")
                        page.wait_for_timeout(3000)

                if not nav_success:
                    self.last_error_reason = "REGION_RESTRICTED"
                    self.log("ERROR", f"Row {row_id}: All {max_nav_attempts} navigation attempts failed due to region restriction.")
                    raise Exception("PAGE_NOT_LOADED")

                self._minimize_chrome()

                # Check login status for automated generation
                if not setup_mode:
                    is_logged_in = True
                    try:
                        # Wait up to 7 seconds for any lazy-loaded login dialog or redirection
                        for check_sec in range(7):
                            page.wait_for_timeout(1000)
                            
                            # 1. Check URL redirecting to log in page or similar
                            current_url = page.url.lower()
                            if "login" in current_url or "register" in current_url:
                                is_logged_in = False
                                break
                                
                            # 2. Check for login-related text/elements on page
                            login_visible = page.evaluate("""() => {
                                const bodyText = document.body ? document.body.innerText.toLowerCase() : '';
                                if (
                                    bodyText.includes("log in / sign up") ||
                                    bodyText.includes("log in to unlock more features") ||
                                    bodyText.includes("sign in to dola") ||
                                    bodyText.includes("login to unlock")
                                ) {
                                    return true;
                                }
                                
                                // Check for phone number input or login buttons
                                const phoneInput = document.querySelector('input[placeholder*="Phone"], input[type="tel"]');
                                if (phoneInput && phoneInput.getBoundingClientRect().width > 0) {
                                    return true;
                                }
                                
                                return false;
                            }""")
                            
                            if login_visible:
                                is_logged_in = False
                                break
                    except Exception as check_err:
                        pass
                        
                    if not is_logged_in:
                        self.log("ERROR", f"Row {row_id}: Account {selected_account} cookie session is EXPIRED or invalid.")
                        self._release_account_lock(selected_account, success=False, mark_expired=True)
                        selected_account = None
                        raise Exception("SESSION_EXPIRED")

                    # Scrape profile nickname if logged in successfully
                    if is_logged_in:
                        try:
                            scraped_name = page.evaluate("""() => {
                                const sidebar = document.querySelector('aside, [class*="sidebar"]');
                                if (!sidebar) return null;
                                const elements = Array.from(sidebar.querySelectorAll('div, span, p, button, a'));
                                const candidates = [];
                                for (const el of elements) {
                                    const text = (el.innerText || '').trim();
                                    if (text && text.length > 2 && text.length < 20 && !text.includes('\\n') && 
                                        !['dola', 'new chat', 'ai creation', 'bots', 'chat history', 'settings', 'log in', 'feedback', 'help', 'logout', 'sign out'].includes(text.toLowerCase())) {
                                        const rect = el.getBoundingClientRect();
                                        if (rect.top > window.innerHeight * 0.7 && rect.left < 250) {
                                            candidates.push({ text, top: rect.top });
                                        }
                                    }
                                }
                                if (candidates.length > 0) {
                                    candidates.sort((a, b) => b.top - a.top);
                                    return candidates[0].text;
                                }
                                return null;
                            }""")
                            if scraped_name:
                                self.log("INFO", f"Row {row_id}: Scraped account nickname: {scraped_name}")
                                self._update_account_name(selected_account, scraped_name)
                        except Exception as scrape_err:
                            self.log("WARNING", f"Row {row_id}: Failed to scrape account name: {str(scrape_err)}")

                # First time / Login setup mode
                if setup_mode and not sms_key:
                    self.log("SYSTEM", f"Row {row_id}: Launcher running in headful setup mode. Please log in to AI Chat in the browser window.")
                    self.update_status(row_id, "SUBMITTING", "Waiting for manual Google login...")
                    
                    # Poll for up to 5 minutes (150 iterations of 2s) to allow manual Google Sign-In
                    for i in range(150):
                        if getattr(self, "is_stopped", False):
                            break
                        if page.is_closed():
                            self.log("WARNING", f"Row {row_id}: Browser window was closed by the user.")
                            break
                        try:
                            # User is logged in if the message textbox is visible, or the url is a chat session
                            textbox_visible = page.locator('[role="textbox"]').first.is_visible(timeout=500)
                            current_url = page.url
                            is_logged_in = bool(re.search(r"/chat/(local_\d+|\d+)", current_url))
                            
                            if is_logged_in:
                                self.log("SUCCESS", f"Row {row_id}: Google login detected! Session established.")
                                page.wait_for_timeout(2000)  # Wait for storage to settle
                                context.storage_state(path=os.path.join(self.profile_dir_master, "auth_state.json"))
                                self.log("SUCCESS", f"Row {row_id}: Master profile auth state saved.")
                                context.close()
                                p.stop()
                                return True
                        except Exception as check_err:
                            if "closed" in str(check_err).lower():
                                self.log("WARNING", f"Row {row_id}: Browser page or context was closed.")
                                break
                        page.wait_for_timeout(2000)
                    
                    # If we exit loop without success, clean up and exit setup mode
                    try:
                        context.close()
                        p.stop()
                    except:
                        pass
                    return False

                # HeroSMS Automated Registration / Verification
                if sms_key:
                    # 1. Trigger the login modal and wait for it
                    try:
                        self.log("INFO", f"Row {row_id}: Opening login modal...")
                        
                        def is_login_modal_open():
                            phone_input = page.locator('input[type="tel"], input[placeholder*="Phone"], input[placeholder*="number"]').first
                            if phone_input.count() > 0 and phone_input.is_visible():
                                return True
                            modal_selectors = [
                                '.semi-modal-content',
                                '.semi-modal-wrap',
                                'div[role="dialog"]',
                                'div[class*="modal"]',
                                'text="Log In / Sign Up"',
                                'text="Log in / Sign up"'
                            ]
                            for sel in modal_selectors:
                                if "text=" in sel:
                                    if page.get_by_text(sel.replace('text=', '').strip('"'), exact=False).first.is_visible():
                                        return True
                                else:
                                    if page.locator(sel).first.count() > 0 and page.locator(sel).first.is_visible():
                                        return True
                            return False

                        modal_open = False
                        for loop_attempt in range(4): # 4 attempts of 15 seconds = 60 seconds max
                            if getattr(self, "is_stopped", False):
                                break
                            
                            if is_login_modal_open():
                                modal_open = True
                                self.log("SUCCESS", f"Row {row_id}: Login modal/phone input is open and visible.")
                                break
                                
                            self.log("INFO", f"Row {row_id}: Click attempt {loop_attempt + 1}: Clicking Log In button...")
                            
                            # Click cookie consent if visible
                            cookie_btn = page.locator("button:has-text('Accept All'), button:has-text('Accept'), button:has-text('Accept all')").first
                            if cookie_btn.count() > 0 and cookie_btn.is_visible():
                                try:
                                    cookie_btn.click(timeout=2000)
                                    page.wait_for_timeout(500)
                                except:
                                    pass
                                    
                            login_btn = page.locator('button:has-text("Log In"), a:has-text("Log In"), [role="button"]:has-text("Log In")').first
                            if login_btn.count() > 0 and login_btn.is_visible():
                                login_btn.click(force=True)
                            else:
                                create_image_btn = page.locator("button:has-text('Create Image'), div:has-text('Create Image')").last
                                if create_image_btn.count() > 0 and create_image_btn.is_visible():
                                    self.log("INFO", f"Row {row_id}: Log In button not found, clicking 'Create Image' to trigger login...")
                                    create_image_btn.click(force=True)
                                    
                            # Wait up to 15 seconds, checking every second if it opened
                            for sec in range(15):
                                if getattr(self, "is_stopped", False):
                                    break
                                if is_login_modal_open():
                                    modal_open = True
                                    break
                                time.sleep(1)
                                
                            if modal_open:
                                break
                                
                        if not modal_open:
                            self.log("WARNING", f"Row {row_id}: Login modal did not open after multiple click attempts.")
                            
                    except Exception as e:
                        self.log("WARNING", f"Row {row_id}: Error preparing login form: {str(e)}")
                    
                    # 2. Wait up to 60 seconds specifically for the phone number input box to be visible
                    phone_input_ready = False
                    try:
                        for wait_sec in range(60):
                            if getattr(self, "is_stopped", False):
                                break
                            phone_input = page.locator('input[type="tel"], input[placeholder*="Phone"], input[placeholder*="number"]').first
                            if phone_input.count() > 0 and phone_input.is_visible():
                                phone_input_ready = True
                                break
                            
                            # Check if the modal wrapper is visible to prevent clicking main page elements
                            is_modal_visible = page.evaluate("""() => {
                                const selectors = ['.semi-modal-content', '.semi-modal-wrap', 'div[role="dialog"]'];
                                return selectors.some(sel => {
                                    const el = document.querySelector(sel);
                                    return el && el.getBoundingClientRect().width > 0;
                                });
                            }""")
                            
                            if is_modal_visible and wait_sec % 2 == 0:
                                try:
                                    modal_buttons = page.locator(".semi-modal-content button, .semi-modal-wrap button, div[role='dialog'] button, div[class*='modal'] button").all()
                                    target_btn = None
                                    for btn in modal_buttons:
                                        if not btn.is_visible():
                                            continue
                                        html = btn.evaluate("el => el.outerHTML").lower()
                                        if "svg" in html and "google" not in html and "facebook" not in html and "apple" not in html and "close" not in html:
                                            if "phone" in html or "tel" in html or "call" in html:
                                                target_btn = btn
                                                break
                                            if target_btn is None:
                                                target_btn = btn
                                                
                                    if target_btn:
                                        self.log("INFO", f"Row {row_id}: Detected phone icon button in login modal. Clicking it...")
                                        target_btn.click(force=True)
                                        page.wait_for_timeout(1500)
                                except Exception as click_err:
                                    pass
                            time.sleep(1)
                    except Exception:
                        pass
                        
                    if not phone_input_ready:
                        self.log("WARNING", f"Row {row_id}: Phone input form did not appear. Skipping number auto-purchase. Please log in manually.")
                    else:
                        # NOW, and ONLY now, buy the number!
                        self.log("INFO", f"Row {row_id}: Phone input box is visible. Requesting number from HeroSMS...")
                        import requests
                        try:
                            activation_id = None
                            phone_number = None
                            final_country = None
                            
                            # Fetch live prices from HeroSMS to perform backup/rotation
                            rotate_countries = []
                            prices_data = {}
                            try:
                                prices_url = f"https://hero-sms.com/stubs/handler_api.php?api_key={sms_key}&action=getPrices&service=ot"
                                p_res = requests.get(prices_url, timeout=10)
                                prices_data = p_res.json()
                                for c_id, services in prices_data.items():
                                    if "ot" in services:
                                        cost = services["ot"].get("cost")
                                        count = services["ot"].get("count")
                                        if cost is not None and count is not None and count > 0:
                                            cost_val = float(cost)
                                            if 0.03 <= cost_val <= 0.10:
                                                rotate_countries.append({
                                                    "id": c_id,
                                                    "cost": cost_val
                                                })
                                rotate_countries.sort(key=lambda x: x["cost"])
                            except Exception as pe:
                                self.log("WARNING", f"Row {row_id}: Failed to fetch active rotation prices: {str(pe)}")
                                
                            candidates = []
                            selected_cost = None
                            try:
                                if sms_country in prices_data and "ot" in prices_data[sms_country]:
                                    selected_cost = float(prices_data[sms_country]["ot"].get("cost", 999.0))
                            except:
                                pass
                                
                            if selected_cost is not None and 0.03 <= selected_cost <= 0.10:
                                candidates.append(sms_country)
                                
                            for rc in rotate_countries:
                                if rc["id"] not in candidates:
                                    candidates.append(rc["id"])
                                    
                            candidates = candidates[:3]
                            self.log("INFO", f"Row {row_id}: Candidate countries to attempt (Max 3, Range: $0.03 - $0.10): {candidates}")
                            
                            country_success = False
                            for attempt_idx, candidate_country in enumerate(candidates, 1):
                                if getattr(self, "is_stopped", False):
                                    break
                                
                                # Try up to 3 numbers for the same candidate country
                                for num_attempt in range(1, 4):
                                    if getattr(self, "is_stopped", False):
                                        break
                                        
                                    self.log("INFO", f"Row {row_id}: [Attempt {attempt_idx}/3, Number {num_attempt}/3] Requesting number for Country ID: {candidate_country}...")
                                    activation_id = None
                                    phone_number = None
                                    final_country = None
                                    
                                    for service_code in ["dola", "ot"]:
                                        req_url = f"https://hero-sms.com/stubs/handler_api.php?api_key={sms_key}&action=getNumber&service={service_code}&country={candidate_country}"
                                        res = requests.get(req_url, timeout=10)
                                        res_text = res.text.strip()
                                        
                                        if res_text.startswith("ACCESS_NUMBER:"):
                                            parts = res_text.split(":")
                                            activation_id = parts[1]
                                            phone_number = parts[2]
                                            final_country = candidate_country
                                            break
                                        else:
                                            self.log("WARNING", f"Row {row_id}: Service '{service_code}' for country {candidate_country} failed: {res_text}")
                                            
                                    if not (activation_id and phone_number):
                                        self.log("WARNING", f"Row {row_id}: Could not allocate number for country {candidate_country}.")
                                        break  # Try next candidate country
                                        
                                    self.log("SUCCESS", f"Row {row_id}: Obtained phone number: +{phone_number} (ID: {activation_id}, Country ID: {final_country})")
                                    
                                    try:
                                        # Ensure phone input is visible; if not (e.g. we went back to the 3-icon screen), click the phone icon button
                                        phone_input = page.locator('input[type="tel"], input[placeholder*="Phone"], input[placeholder*="number"]').first
                                        if not (phone_input.count() > 0 and phone_input.is_visible()):
                                            self.log("INFO", f"Row {row_id}: Phone input is not visible. Checking for circular phone icon button...")
                                            for wait_icon in range(10):
                                                if getattr(self, "is_stopped", False):
                                                    break
                                                # Restrict to modal buttons
                                                modal_buttons = page.locator(".semi-modal-content button, .semi-modal-wrap button, div[role='dialog'] button, div[class*='modal'] button").all()
                                                target_btn = None
                                                for btn in modal_buttons:
                                                    if not btn.is_visible():
                                                        continue
                                                    html = btn.evaluate("el => el.outerHTML").lower()
                                                    if "svg" in html and "google" not in html and "facebook" not in html and "apple" not in html and "close" not in html:
                                                        if "phone" in html or "tel" in html or "call" in html:
                                                            target_btn = btn
                                                            break
                                                        if target_btn is None:
                                                            target_btn = btn
                                                if target_btn:
                                                    self.log("INFO", f"Row {row_id}: Clicking circular phone icon button...")
                                                    target_btn.click(force=True)
                                                    page.wait_for_timeout(1500)
                                                    
                                                phone_input = page.locator('input[type="tel"], input[placeholder*="Phone"], input[placeholder*="number"]').first
                                                if phone_input.count() > 0 and phone_input.is_visible():
                                                    break
                                                page.wait_for_timeout(500)
                                        
                                        # Define country map to resolve name and dial prefix
                                        sms_countries_map = {
                                            0: ("Russia", "+7"), 1: ("Ukraine", "+380"), 2: ("Kazakhstan", "+7"), 3: ("China", "+86"),
                                            4: ("Philippines", "+63"), 5: ("Myanmar", "+95"), 6: ("Indonesia", "+62"),
                                            7: ("Malaysia", "+60"), 8: ("Kenya", "+254"), 9: ("Tanzania", "+255"),
                                            10: ("Vietnam", "+84"), 11: ("Kyrgyzstan", "+996"), 12: ("USA", "+1"),
                                            13: ("Israel", "+972"), 14: ("Hong Kong", "+852"), 15: ("Poland", "+48"),
                                            16: ("United Kingdom", "+44"), 17: ("Madagascar", "+261"), 18: ("Congo", "+242"),
                                            19: ("Nigeria", "+234"), 20: ("Macau", "+853"), 21: ("Egypt", "+20"),
                                            22: ("India", "+91"), 23: ("Ireland", "+353"), 24: ("Cambodia", "+855"),
                                            25: ("Laos", "+856"), 26: ("Haiti", "+509"), 27: ("Ivory Coast", "+225"),
                                            28: ("Gambia", "+220"), 29: ("Yemen", "+967"), 30: ("South Africa", "+27"),
                                            31: ("Romania", "+40"), 32: ("Colombia", "+57"), 33: ("Estonia", "+372"),
                                            34: ("Azerbaijan", "+994"), 35: ("Angola", "+244"), 36: ("Sweden", "+46"),
                                            37: ("France", "+33"), 38: ("Canada", "+1"), 39: ("Uzbekistan", "+998"),
                                            40: ("Cameroon", "+237"), 41: ("Chad", "+235"), 42: ("Germany", "+49"),
                                            43: ("Lithuania", "+370"), 44: ("Croatia", "+385"), 45: ("Sweden", "+46"),
                                            46: ("Iraq", "+964"), 47: ("Netherlands", "+31"), 48: ("Latvia", "+371"),
                                            49: ("Austria", "+43"), 50: ("Belarus", "+375"), 51: ("Thailand", "+66"),
                                            52: ("Saudi Arabia", "+966"), 53: ("Mexico", "+52"), 54: ("Taiwan", "+886"),
                                            55: ("Taiwan", "+886"), 56: ("Spain", "+34"), 57: ("Iran", "+98"),
                                            58: ("Algeria", "+213"), 59: ("Slovenia", "+386"), 60: ("Bangladesh", "+880"),
                                            61: ("Senegal", "+221"), 62: ("Turkey", "+90"), 63: ("Sri Lanka", "+94"),
                                            64: ("Peru", "+51"), 65: ("Pakistan", "+92"), 66: ("New Zealand", "+64"),
                                            67: ("Guinea", "+224"), 68: ("Mali", "+223"), 69: ("Venezuela", "+58"),
                                            70: ("Ethiopia", "+251"), 71: ("Mongolia", "+976"), 72: ("Brazil", "+55"),
                                            73: ("Afghanistan", "+93"), 74: ("Uganda", "+256"), 75: ("Angola", "+244"),
                                            76: ("Cyprus", "+357"), 77: ("France", "+33"), 78: ("Papua New Guinea", "+675"),
                                            79: ("Somalia", "+252"), 80: ("Maldives", "+960"), 81: ("Libya", "+218"),
                                            82: ("Morocco (Virtual)", "+212"), 83: ("Guinea-Bissau", "+245"),
                                            84: ("Mauritania", "+222"), 85: ("Oman", "+968"), 86: ("Nepal", "+977"),
                                            87: ("Qatar", "+974"), 88: ("Honduras", "+504"), 89: ("Tunisia", "+216"),
                                            90: ("Nicaragua", "+505"), 91: ("El Salvador", "+503"), 92: ("Bolivia", "+591"),
                                            93: ("Ecuador", "+593"), 94: ("Guatemala", "+502"), 95: ("UAE", "+971"),
                                            96: ("Zimbabwe", "+263"), 97: ("Suriname", "+597"), 98: ("Angola (Virtual)", "+244"),
                                            99: ("Mauritius", "+230"), 108: ("Bosnia", "+387"), 128: ("Georgia", "+995"),
                                            173: ("Switzerland", "+41"), 196: ("Singapore", "+65"), 199: ("Malta", "+356")
                                        }
                                        c_name = "Philippines"
                                        calling_code = "+63"
                                        try:
                                            c_id_int = int(final_country)
                                            if c_id_int in sms_countries_map:
                                                c_name, calling_code = sms_countries_map[c_id_int]
                                        except Exception:
                                            pass
                                            
                                        # Click country selector dropdown
                                        country_trigger = None
                                        triggers = [
                                            page.locator('button:has-text("+"), [role="button"]:has-text("+")'),
                                            page.locator('[class*="flag"], [class*="Country"], [class*="country"]'),
                                            page.locator('[class*="selected-flag"]')
                                        ]
                                        for tr in triggers:
                                            if tr.count() > 0 and tr.first.is_visible():
                                                country_trigger = tr.first
                                                break
                                                
                                        if country_trigger:
                                            self.log("INFO", f"Row {row_id}: Clicking country selector dropdown...")
                                            country_trigger.click(force=True)
                                            page.wait_for_timeout(1500)
                                            
                                            option_locators = [
                                                page.locator(f'li:has-text("{calling_code}"), [role="option"]:has-text("{calling_code}"), div:has-text("{calling_code}")'),
                                                page.locator(f'li:has-text("{c_name}"), [role="option"]:has-text("{c_name}"), div:has-text("{c_name}")'),
                                                page.locator(f'button:has-text("{calling_code}"), button:has-text("{c_name}")')
                                            ]
                                            option_clicked = False
                                            for opt in option_locators:
                                                cnt = opt.count()
                                                for idx in range(cnt):
                                                    item = opt.nth(idx)
                                                    if item.is_visible():
                                                        item.scroll_into_view_if_needed()
                                                        item.click(force=True)
                                                        self.log("INFO", f"Row {row_id}: Selected country option {calling_code} ({c_name}).")
                                                        option_clicked = True
                                                        break
                                                if option_clicked:
                                                    break
                                            if not option_clicked:
                                                self.log("WARNING", f"Row {row_id}: Could not find country option for {c_name} ({calling_code}) in dropdown. Please select it manually.")
                                            page.wait_for_timeout(1000)
                                            
                                        prefix_digits = calling_code.replace("+", "").strip()
                                        local_number = phone_number
                                        if phone_number.startswith(prefix_digits):
                                            local_number = phone_number[len(prefix_digits):]
                                            
                                        # Find input field and fill it
                                        phone_input = page.locator('input[type="tel"], input[placeholder*="Phone"], input[placeholder*="number"]').first
                                        if phone_input.count() > 0:
                                            phone_input.click(force=True)
                                            page.keyboard.press("Control+A")
                                            page.keyboard.press("Backspace")
                                            phone_input.fill(local_number)
                                            page.wait_for_timeout(1000)
                                            
                                            # Try to click the "Next" button automatically to trigger captcha
                                            clicked_next = False
                                            next_selectors = [
                                                'button:has-text("Next")', 'button:has-text("next")',
                                                'button:has-text("Continue")', 'button:has-text("continue")',
                                                'button:has-text("Log In")', 'button:has-text("log in")',
                                                'button:has-text("Sign In")', 'button:has-text("sign in")',
                                                'button:has-text("Send Code")', 'button:has-text("send code")',
                                                'button[type="submit"]',
                                                'form button'
                                            ]
                                            for sel in next_selectors:
                                                btn = page.locator(sel).first
                                                if btn.count() > 0 and btn.is_visible() and btn.is_enabled():
                                                    self.log("INFO", f"Row {row_id}: Clicking '{btn.text_content().strip()}' button to submit phone number.")
                                                    btn.click(force=True)
                                                    clicked_next = True
                                                    break
                                            
                                            if not clicked_next:
                                                self.log("INFO", f"Row {row_id}: Pressing Enter to submit phone number.")
                                                page.keyboard.press("Enter")
                                            
                                            page.wait_for_timeout(1000)
                                            self.log("INFO", f"Row {row_id}: Auto-filled phone number submitted. Please solve any captcha in browser window.")
                                            
                                            # Wait up to 180 seconds (3 minutes) for OTP code input box to appear
                                            otp_box_ready = False
                                            for wait_otp in range(180):
                                                if getattr(self, "is_stopped", False):
                                                    break
                                                
                                                # Robust check: check innerText of document.body for OTP keywords
                                                text_found = page.evaluate("""() => {
                                                    const text = document.body.innerText || "";
                                                    return text.toLowerCase().includes("enter 6-digit code") || 
                                                           text.toLowerCase().includes("verification code") || 
                                                           text.toLowerCase().includes("resend code");
                                                }""")
                                                
                                                inputs_count = 0
                                                inputs_loc = page.locator('input')
                                                for idx_inp in range(inputs_loc.count()):
                                                    if inputs_loc.nth(idx_inp).is_visible():
                                                        inputs_count += 1
                                                        
                                                if text_found or inputs_count >= 5:
                                                    self.log("SUCCESS", f"Row {row_id}: Captcha successfully resolved! OTP verification screen detected.")
                                                    otp_box_ready = True
                                                    break
                                                time.sleep(1)
                                                
                                            if not otp_box_ready:
                                                self.log("WARNING", f"Row {row_id}: OTP input box did not appear. Verification timeout.")
                                                raise Exception("OTP_BOX_TIMEOUT")
                                                
                                            # Poll for SMS code (1 minute = 20 iterations of 3 seconds)
                                            code_found = False
                                            for poll in range(20):
                                                if getattr(self, "is_stopped", False):
                                                    break
                                                    
                                                stat_url = f"https://hero-sms.com/stubs/handler_api.php?api_key={sms_key}&action=getStatus&id={activation_id}"
                                                stat_res = requests.get(stat_url, timeout=5)
                                                stat_text = stat_res.text.strip()
                                                
                                                if stat_text.startswith("STATUS_OK:"):
                                                    sms_code = stat_text.split(":")[1]
                                                    self.log("SUCCESS", f"Row {row_id}: HeroSMS received OTP: {sms_code}")
                                                    
                                                    # Fill OTP code
                                                    self.log("INFO", f"Row {row_id}: Fetching OTP code inputs...")
                                                    candidate_inputs = page.locator('input')
                                                    target_inputs = []
                                                    for idx in range(candidate_inputs.count()):
                                                        inp = candidate_inputs.nth(idx)
                                                        inp_type = inp.get_attribute("type")
                                                        if inp_type == "hidden":
                                                            continue
                                                        target_inputs.append(inp)
                                                        
                                                    if len(target_inputs) > 0:
                                                        self.log("INFO", f"Row {row_id}: Found {len(target_inputs)} input field(s). Typing OTP...")
                                                        first_input = target_inputs[0]
                                                        try:
                                                            first_input.focus()
                                                            page.wait_for_timeout(100)
                                                            first_input.click(force=True)
                                                            page.wait_for_timeout(100)
                                                            page.keyboard.press("Control+A")
                                                            page.keyboard.press("Backspace")
                                                        except Exception as focus_err:
                                                            self.log("WARNING", f"Row {row_id}: Input focus/click failed: {str(focus_err)}")
                                                        
                                                        page.keyboard.type(sms_code, delay=150)
                                                        page.wait_for_timeout(1000)
                                                    else:
                                                        self.log("WARNING", f"Row {row_id}: No input fields found. Typing code directly...")
                                                        page.keyboard.type(sms_code, delay=150)
                                                        page.wait_for_timeout(1000)
                                                        
                                                    # Post-OTP check: click any Submit / Verify / Next buttons if they appear
                                                    self.log("INFO", f"Row {row_id}: OTP filled. Checking for any post-OTP verification popups/buttons...")
                                                    page.wait_for_timeout(2000)
                                                    
                                                    for post_wait in range(15):
                                                        if getattr(self, "is_stopped", False):
                                                            break
                                                        curr_url = page.url
                                                        if re.search(r"/chat/(local_\d+|\d+)", curr_url):
                                                            self.log("SUCCESS", f"Row {row_id}: Successfully logged in post-OTP!")
                                                            break
                                                        confirm_selectors = [
                                                            'button:has-text("Submit")', 'button:has-text("submit")',
                                                            'button:has-text("Verify")', 'button:has-text("verify")',
                                                            'button:has-text("Confirm")', 'button:has-text("confirm")',
                                                            'button:has-text("Next")', 'button:has-text("next")',
                                                            'button:has-text("Continue")', 'button:has-text("continue")',
                                                            'button:has-text("OK")', 'button:has-text("ok")'
                                                        ]
                                                        clicked_confirm = False
                                                        for sel in confirm_selectors:
                                                            btn = page.locator(sel)
                                                            if btn.count() > 0 and btn.first.is_visible() and btn.first.is_enabled():
                                                                self.log("INFO", f"Row {row_id}: Clicking post-OTP button: {btn.first.text_content().strip()}")
                                                                btn.first.click(force=True)
                                                                clicked_confirm = True
                                                                break
                                                        if clicked_confirm:
                                                            page.wait_for_timeout(2000)
                                                        else:
                                                            time.sleep(1)
                                                            
                                                    requests.get(f"https://hero-sms.com/stubs/handler_api.php?api_key={sms_key}&action=setStatus&status=6&id={activation_id}")
                                                    code_found = True
                                                    break
                                                elif stat_text != "STATUS_WAIT_CODE":
                                                    self.log("WARNING", f"Row {row_id}: HeroSMS Status: {stat_text}")
                                                    
                                                time.sleep(3)
                                                
                                            if not code_found:
                                                self.log("WARNING", f"Row {row_id}: SMS code did not arrive within 1 minute. Refunding number...")
                                                raise Exception("SMS_TIMEOUT")
                                                
                                            self.log("SUCCESS", f"Row {row_id}: Verification code filled successfully!")
                                            page.wait_for_timeout(2000)
                                            country_success = True
                                            break  # Break num_attempt
                                    except Exception as sms_err:
                                        self.log("ERROR", f"Row {row_id}: Error on number attempt {num_attempt}: {str(sms_err)}")
                                        if activation_id:
                                            requests.get(f"https://hero-sms.com/stubs/handler_api.php?api_key={sms_key}&action=setStatus&status=8&id={activation_id}")
                                            self.log("INFO", f"Row {row_id}: Refund request sent for ID: {activation_id}")
                                        # Click back/edit icon in login modal to return to number entry if possible
                                        try:
                                            back_selectors = [
                                                '.semi-modal-back',
                                                '[class*="back"]',
                                                'span:has-text("<")',
                                                'button:has-text("<")',
                                                'button:has(svg)',
                                                '.semi-modal-header svg',
                                                'svg'
                                            ]
                                            back_btn = None
                                            for b_sel in back_selectors:
                                                el = page.locator(b_sel).first
                                                if el.count() > 0 and el.is_visible():
                                                    back_btn = el
                                                    break
                                            if back_btn:
                                                self.log("INFO", f"Row {row_id}: Clicking back button to return to number entry.")
                                                back_btn.click(force=True)
                                                page.wait_for_timeout(2000)
                                        except Exception as back_err:
                                            self.log("WARNING", f"Row {row_id}: Failed to click back button: {str(back_err)}")
                                            
                                if country_success:
                                    break  # Break candidates loop
                                    
                            if not country_success:
                                self.log("ERROR", f"Row {row_id}: HeroSMS number request failed.")
                                raise Exception("SMS_NO_NUMBER")
                        except Exception as sms_err:
                            self.log("ERROR", f"Row {row_id}: HeroSMS request error: {str(sms_err)}")
                            raise sms_err

                # Close the OK modal and Cookie popup robustly
                self.log("INFO", f"Row {row_id}: Checking for startup OK modal and cookie banner...")
                page.wait_for_timeout(1000)
                for attempt in range(10):
                    closed = page.evaluate("""() => {
                        const buttons = Array.from(document.querySelectorAll('button'));
                        
                        // 1. Close OK modal popup
                        const okBtn = buttons.find(b => b.textContent.trim() === 'OK');
                        if (okBtn) {
                            okBtn.click();
                            return true;
                        }
                        
                        // 2. Close Cookie consent banner popup
                        const acceptBtn = buttons.find(b => b.textContent.trim().toLowerCase() === 'accept all');
                        if (acceptBtn) {
                            acceptBtn.click();
                            return true;
                        }
                        
                        return false;
                    }""")
                    if closed:
                        self.log("INFO", f"Row {row_id}: Closed OK modal or cookie consent popup.")
                    page.wait_for_timeout(500)
                    wrap_exists = page.evaluate('() => document.querySelector(".semi-modal-wrap") !== null || document.body.innerText.includes("Accept Dola")')
                    if not wrap_exists:
                        break
                self._minimize_chrome()
                
                if setup_mode:
                    self.log("SUCCESS", f"Row {row_id}: SMS Registration complete! Saving session...")
                    page.wait_for_timeout(2000)
                    context.storage_state(path=os.path.join(self.profile_dir_master, "auth_state.json"))
                    self.log("SUCCESS", f"Row {row_id}: Master profile auth state saved.")
                    context.close()
                    p.stop()
                    return True

                # Force page load by clicking 'AI Creation' in the sidebar
                self.log("INFO", f"Row {row_id}: Forcing interface reload via AI Creation sidebar item...")
                try:
                    page.get_by_text("AI Creation", exact=True).first.click(timeout=5000)
                    self.log("SUCCESS", f"Row {row_id}: Clicked AI Creation sidebar item.")
                    page.wait_for_timeout(5000)
                except Exception as force_load_err:
                    self.log("WARNING", f"Row {row_id}: Failed to click AI Creation sidebar item: {str(force_load_err)}")

                # Dismiss cookie banner if it is visible
                try:
                    cookie_btn = page.locator("button:has-text('Accept All'), button:has-text('Accept'), button:has-text('Accept all')").first
                    if cookie_btn.count() > 0 and cookie_btn.is_visible():
                        cookie_btn.click(timeout=3000)
                        self.log("SUCCESS", f"Row {row_id}: Dismissed cookie banner popup.")
                        page.wait_for_timeout(1000)
                except Exception as cookie_err:
                    pass

                # Check and close "Log In to Unlock More Features" popup if it appears
                self.log("INFO", f"Row {row_id}: Checking for Log In popup...")
                page.wait_for_timeout(1000)
                try:
                    closed_login = page.evaluate("""() => {
                        const divs = Array.from(document.querySelectorAll('div, section, form'));
                        const loginModal = divs.find(el => {
                            const rect = el.getBoundingClientRect();
                            return rect.width > 0 && rect.height > 0 && el.textContent.includes("Log In to Unlock More Features");
                        });
                        if (loginModal) {
                            const buttons = Array.from(loginModal.querySelectorAll('button'));
                            const closeBtn = buttons.find(btn => {
                                const html = btn.outerHTML.toLowerCase();
                                const label = btn.getAttribute('aria-label') || '';
                                return html.includes('close') || label.toLowerCase().includes('close') || (btn.textContent.strip() === '' && btn.querySelector('svg'));
                            });
                            if (closeBtn) {
                                closeBtn.click();
                                return true;
                            }
                        }
                        return false;
                    }""")
                    if closed_login:
                        self.log("INFO", f"Row {row_id}: Closed Log In popup modal.")
                        page.wait_for_timeout(1000)
                        self._minimize_chrome()
                except Exception as e:
                    self.log("WARNING", f"Row {row_id}: Error checking/closing Log In popup: {str(e)}")

                self.update_status(row_id, "GENERATING", "[3/5] Submitting prompt request...")
                
                # 1. Switch to Video mode if is_image is False
                if not is_image:
                    self.log("INFO", f"Row {row_id}: Setting Video mode on Dola...")
                    
                    video_setup_success = False
                    # Loop click attempts for up to 60 seconds total
                    for attempt in range(12): # 12 attempts * 5s = 60s
                        try:
                            # Focus input first to trigger the Image/Video tabs carousel
                            textbox = page.locator('div:not(aside) [contenteditable], div:not([class*="sidebar"]) [contenteditable], [role="textbox"]:not(aside *), textarea').first
                            textbox.click(force=True)
                            page.wait_for_timeout(1000)
                            
                            # Verify if Video button is visible, click it if yes
                            has_video_tab = page.evaluate("""() => {
                                const buttons = Array.from(document.querySelectorAll('button, div, span, p'));
                                const vBtn = buttons.find(b => b.innerText && b.innerText.trim() === 'Video');
                                if (vBtn) {
                                    const rect = vBtn.getBoundingClientRect();
                                    return rect.width > 0 && rect.height > 0;
                                }
                                return false;
                            }""")
                            
                            if has_video_tab:
                                self.log("INFO", f"Row {row_id}: Video tab found. Clicking it (attempt {attempt + 1})...")
                                try:
                                    page.get_by_text("Video", exact=True).first.click(timeout=3000)
                                except:
                                    page.evaluate("""() => {
                                        const buttons = Array.from(document.querySelectorAll('button, div, span, p'));
                                        const videoBtn = buttons.find(b => b.innerText && b.innerText.trim() === 'Video');
                                        if (videoBtn) videoBtn.click();
                                    }""")
                                page.wait_for_timeout(2000)

                            # Verify if dropdowns (duration, ratio, model selector) are visible
                            dropdowns_loaded = page.evaluate("""() => {
                                const texts = Array.from(document.querySelectorAll('button, div, span, p')).map(el => el.innerText || '');
                                const has_duration = texts.some(t => t.includes('10s') || t.includes('5s') || t.includes('15s'));
                                const has_ratio = texts.some(t => t.includes('Ratio'));
                                const has_model = texts.some(t => t.includes('Model') || t.includes('Seedance'));
                                return has_duration && has_ratio && has_model;
                            }""")
                            
                            if dropdowns_loaded:
                                self.log("SUCCESS", f"Row {row_id}: Video mode confirmed. Dropdowns (duration/ratio/model) are visible.")
                                video_setup_success = True
                                break
                            else:
                                self.log("WARNING", f"Row {row_id}: Dropdown tabs not visible yet. Retrying Video tab selection...")
                        except Exception as click_err:
                            self.log("WARNING", f"Row {row_id}: Video click attempt {attempt + 1} failed: {str(click_err)}")
                        
                        page.wait_for_timeout(3000)

                    if not video_setup_success:
                        self.log("ERROR", f"Row {row_id}: Failed to switch to Video mode (dropdowns did not appear after 60s). Aborting to prevent image generation.")
                        raise Exception("VIDEO_MODE_FAILED")

                # 2. Select RATIO on Dola UI (e.g. 9:16, 16:9, 1:1)
                if not is_image and ratio:
                    self.log("INFO", f"Row {row_id}: Selecting ratio '{ratio}' on Dola...")
                    try:
                        ratio_btn = page.locator("button:has-text('Ratio')").first
                        if not ratio_btn.is_visible():
                            for possible_ratio in ["16:9", "9:16", "1:1"]:
                                btn_loc = page.locator("button").filter(has_text=possible_ratio).first
                                if btn_loc.is_visible():
                                    ratio_btn = btn_loc
                                    break
                                    
                        if ratio_btn and ratio_btn.is_visible():
                            ratio_btn.click()
                            page.wait_for_timeout(500)
                            
                            clicked_ratio = False
                            for sel_str in ["[role='menuitem']", "button", "div", "li", "span"]:
                                try:
                                    option_loc = page.locator(sel_str).filter(has_text=ratio).first
                                    if option_loc.is_visible():
                                        option_loc.click(force=True)
                                        clicked_ratio = True
                                        break
                                except:
                                    pass
                            
                            if clicked_ratio:
                                self.log("INFO", f"Row {row_id}: Ratio '{ratio}' selected successfully.")
                            else:
                                page.evaluate(f"""(ratioText) => {{
                                    const elements = Array.from(document.querySelectorAll('div, li, button, span, [role="menuitem"]'));
                                    const match = elements.find(el => el.innerText && el.innerText.trim() === ratioText);
                                    if (match) {{
                                        match.click();
                                        return true;
                                    }}
                                    return false;
                                }}""", ratio)
                                self.log("INFO", f"Row {row_id}: Ratio '{ratio}' selected via JS fallback.")
                            page.wait_for_timeout(500)
                        else:
                            self.log("WARNING", f"Row {row_id}: Ratio button not found on Dola UI.")
                    except Exception as ratio_err:
                        self.log("WARNING", f"Row {row_id}: Ratio selection failed: {str(ratio_err)[:80]}")

                # 3. Select DURATION on Dola UI (e.g. 5s, 10s, 15s) — only if NOT 15s (15s is handled by fetch patcher)
                if not is_image and duration and not is_15s:
                    dur_label = f"{duration}s" if not str(duration).endswith("s") else str(duration)
                    self.log("INFO", f"Row {row_id}: Selecting duration '{dur_label}' on Dola UI...")
                    try:
                        dur_btn = None
                        for possible_val in ["5s", "10s", "15s"]:
                            btn_loc = page.locator("button").filter(has_text=possible_val).first
                            if btn_loc.is_visible():
                                dur_btn = btn_loc
                                break
                                
                        if dur_btn:
                            dur_btn.click()
                            page.wait_for_timeout(500)
                            
                            clicked_dur = False
                            for sel_str in ["[role='menuitem']", "button", "div", "li", "span"]:
                                try:
                                    option_loc = page.locator(sel_str).filter(has_text=dur_label).first
                                    if option_loc.is_visible():
                                        option_loc.click(force=True)
                                        clicked_dur = True
                                        break
                                except:
                                    pass
                                    
                            if clicked_dur:
                                self.log("INFO", f"Row {row_id}: Duration '{dur_label}' selected successfully.")
                            else:
                                page.evaluate(f"""(durText) => {{
                                    const elements = Array.from(document.querySelectorAll('div, li, button, span, [role="menuitem"]'));
                                    const match = elements.find(el => el.innerText && el.innerText.trim() === durText);
                                    if (match) {{
                                        match.click();
                                        return true;
                                    }}
                                    return false;
                                }}""", dur_label)
                                self.log("INFO", f"Row {row_id}: Duration '{dur_label}' selected via JS fallback.")
                            page.wait_for_timeout(500)
                        else:
                            self.log("WARNING", f"Row {row_id}: Duration button not found on Dola UI.")
                    except Exception as dur_err:
                        self.log("WARNING", f"Row {row_id}: Duration selection failed: {str(dur_err)[:80]}")


                
                # Fill prompt in the Dola chat textbox
                self.log("INFO", f"Row {row_id}: Entering visual prompt: {visual_prompt}")
                try:
                    textbox = page.locator('div:not(aside) [contenteditable], div:not([class*="sidebar"]) [contenteditable], [role="textbox"]:not(aside *), textarea').first
                    textbox.click(force=True)
                    page.wait_for_timeout(500)
                    page.keyboard.press("Control+A")
                    page.keyboard.press("Backspace")
                    page.keyboard.insert_text(visual_prompt)
                    page.wait_for_timeout(1000)
                except Exception as type_err:
                    self.log("WARNING", f"Row {row_id}: Keyboard typing failed: {str(type_err)}. Trying direct fill...")
                    try:
                        textbox = page.locator('div:not(aside) [contenteditable], div:not([class*="sidebar"]) [contenteditable], [role="textbox"]:not(aside *), textarea').first
                        textbox.fill(visual_prompt)
                        page.wait_for_timeout(1000)
                    except Exception as fill_err:
                        self.log("ERROR", f"Row {row_id}: Failed to fill prompt in textbox: {str(fill_err)}")
                        raise fill_err

                self.log("INFO", f"Row {row_id}: Clicking submit button...")
                try:
                    send_btn = None
                    try:
                        container = page.locator('div:not(aside) [contenteditable], div:not([class*="sidebar"]) [contenteditable], [role="textbox"]:not(aside *), textarea').first.locator('xpath=../..')
                        for btn in container.locator('button').all():
                             if btn.is_visible() and "svg" in btn.evaluate("el => el.outerHTML").lower():
                                 send_btn = btn
                    except Exception as container_err:
                        self.log("WARNING", f"Row {row_id}: Relative send button search failed: {str(container_err)}")

                    if not send_btn:
                        for btn in page.locator("button").all():
                            try:
                                text = btn.inner_text().strip()
                                html = btn.evaluate("el => el.outerHTML")
                                is_visible = btn.is_visible()
                                if is_visible and text == "" and "svg" in html.lower() and "shrink-0" in html.lower():
                                    send_btn = btn
                            except:
                                pass

                    # Helper to perform the click / submission
                    def do_submit_attempt():
                        try:
                            # 1. Native click on detected send button
                            if send_btn and send_btn.is_visible():
                                send_btn.click(force=True)
                                page.wait_for_timeout(1000)
                            
                            # 2. Check if textbox still has text, try JS dispatch click
                            textbox_still_exists = page.evaluate('() => document.querySelector("div:not(aside) [contenteditable], div:not([class*=\'sidebar\']) [contenteditable], [role=\'textbox\']:not(aside *), textarea") !== null')
                            if textbox_still_exists:
                                textbox_val = page.locator('div:not(aside) [contenteditable], div:not([class*="sidebar"]) [contenteditable], [role="textbox"]:not(aside *), textarea').first.evaluate("el => el.textContent || el.value || ''")
                                if textbox_val and len(textbox_val.strip()) > 5:
                                    if send_btn:
                                        send_btn.evaluate("""(btn) => {
                                            btn.focus();
                                            const eventOpts = { bubbles: true, cancelable: true, view: window };
                                            btn.dispatchEvent(new MouseEvent('mousedown', eventOpts));
                                            btn.dispatchEvent(new MouseEvent('mouseup', eventOpts));
                                            btn.dispatchEvent(new MouseEvent('click', eventOpts));
                                        }""")
                                        page.wait_for_timeout(1500)
                            
                            # 3. Try Keyboard shortcuts if text still there
                            textbox_still_exists = page.evaluate('() => document.querySelector("div:not(aside) [contenteditable], div:not([class*=\'sidebar\']) [contenteditable], [role=\'textbox\']:not(aside *), textarea") !== null')
                            if textbox_still_exists:
                                textbox_val = page.locator('div:not(aside) [contenteditable], div:not([class*="sidebar"]) [contenteditable], [role="textbox"]:not(aside *), textarea').first.evaluate("el => el.textContent || el.value || ''")
                                if textbox_val and len(textbox_val.strip()) > 5:
                                    textbox = page.locator('div:not(aside) [contenteditable], div:not([class*="sidebar"]) [contenteditable], [role="textbox"]:not(aside *), textarea').first
                                    textbox.focus()
                                    page.keyboard.press("Control+Enter")
                                    page.wait_for_timeout(1000)
                                    page.keyboard.press("Enter")
                                    page.wait_for_timeout(500)
                        except Exception as click_err:
                            self.log("WARNING", f"Row {row_id}: Submit attempt error: {str(click_err)[:60]}")

                    self.log("INFO", f"Row {row_id}: Performing initial prompt submission...")
                    do_submit_attempt()
                    
                    # Monitor URL redirect loop (up to 180 seconds / 3 minutes)
                    self.log("INFO", f"Row {row_id}: Verifying submission redirect to chat page (waiting up to 3 mins)...")
                    submitted_successfully = False
                    
                    for nav_sec in range(180):
                        current_url = page.url.lower()
                        is_valid_chat_session = bool(re.search(r"/chat/(local_\d+|\d+)", current_url))
                        if is_valid_chat_session:
                            submitted_successfully = True
                            self.log("SUCCESS", f"Row {row_id}: Prompt submitted successfully! Redirected to: {current_url}")
                            break
                            
                        # Check high demand or logout redirect
                        high_demand_exists = page.evaluate("""() => {
                            return document.body && document.body.innerText && 
                                   document.body.innerText.includes("We are experiencing high demand right now");
                        }""")
                        if high_demand_exists or "from_logout" in current_url or "login" in current_url.lower():
                            self.log("WARNING", f"Row {row_id}: Detected High Demand error / logout redirect on website during submission.")
                            self.last_error_reason = "HIGH_DEMAND"
                            raise Exception("HIGH_DEMAND")
                            
                        # If stuck, click the submit/send button every 15 seconds
                        if nav_sec > 0 and nav_sec % 15 == 0:
                            self.log("INFO", f"Row {row_id}: Still not redirected after {nav_sec}s. Re-clicking submit/send button...")
                            do_submit_attempt()
                            
                        # If stuck on create-image or bare /chat for 30s or more, check and click sidebar 'New Chat'
                        if nav_sec >= 30 and nav_sec % 30 == 0:
                            history_clicked = page.evaluate("""() => {
                                const divs = Array.from(document.querySelectorAll('div, p, span, button'));
                                const historyHeader = divs.find(d => d.innerText && d.innerText.trim() === 'Chat History');
                                if (historyHeader) {
                                    const parent = historyHeader.parentElement;
                                    if (parent) {
                                        const items = Array.from(parent.querySelectorAll('div, p, span, button, a'));
                                        const chatItem = items.find(el => el.innerText && el.innerText.trim() === 'New Chat' && el !== historyHeader);
                                        if (chatItem) {
                                            chatItem.click();
                                            return 'clicked_history_item';
                                        }
                                    }
                                }
                                const allNewChats = Array.from(document.querySelectorAll('*'))
                                    .filter(el => el.innerText && el.innerText.trim() === 'New Chat');
                                for (const el of allNewChats) {
                                    if (el.closest('li') || el.closest('[class*="history"]') || el.closest('[class*="list"]')) {
                                        el.click();
                                        return 'clicked_fallback_history_item';
                                    }
                                }
                                return 'no_item_found';
                            }""")
                            
                            if history_clicked in ['clicked_history_item', 'clicked_fallback_history_item']:
                                self.log("INFO", f"Row {row_id}: Stuck on submission. Clicked sidebar history item ({history_clicked}).")
                                page.wait_for_timeout(3000)
                                do_submit_attempt()
                                page.wait_for_timeout(1000)
                                
                        page.wait_for_timeout(1000)
                        
                    if not submitted_successfully:
                        self.log("ERROR", f"Row {row_id}: Prompt submission failed to redirect after 180s timeout.")
                        raise Exception("PAGE_NOT_LOADED")
                        
                except Exception as e:
                    if "HIGH_DEMAND" in str(e) or "PAGE_NOT_LOADED" in str(e):
                        raise e
                    self.log("WARNING", f"Row {row_id}: Submission failed: {str(e)}")

                self.log("INFO", f"Row {row_id}: Waiting for generation confirmation message or 10-second warning (up to 240s)...")
                replied_yes = False
                confirmed_msg = None
                
                for conf_wait in range(240):
                    if getattr(self, "is_stopped", False):
                        raise Exception("USER_ABORTED")

                    # 1. Independent Warning Check
                    try:
                        if not replied_yes:
                            has_duration_warning = page.evaluate("""() => {
                                const elements = Array.from(document.querySelectorAll('div, p, span'));
                                return elements.some(el => {
                                    const txt = (el.innerText || '').toLowerCase();
                                    return txt.includes("longer than 10 seconds") && (txt.includes("generate") || txt.includes("generating"));
                                });
                            }""")
                            
                            if has_duration_warning:
                                self.log("WARNING", f"Row {row_id}: Detected 10-second warning prompt. Confirming with 'yes'...")
                                try:
                                    textbox = page.locator('textarea, [placeholder*="Message"], [role="textbox"]').first
                                    textbox.click(force=True)
                                    page.keyboard.press("Control+A")
                                    page.keyboard.press("Backspace")
                                    page.keyboard.type("yes")
                                    page.wait_for_timeout(500)
                                    
                                    js_clicked = page.evaluate("""() => {
                                        const allButtons = Array.from(document.querySelectorAll('button'));
                                        let sendBtn = null;
                                        for (const btn of allButtons) {
                                            const rect = btn.getBoundingClientRect();
                                            const html = btn.outerHTML.toLowerCase();
                                            const style = window.getComputedStyle(btn);
                                            const bgColor = style.backgroundColor;
                                            if (rect.width > 0 && rect.height > 0 && html.includes('svg') && html.includes('path')) {
                                                if (rect.top > window.innerHeight * 0.5) {
                                                    if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent') {
                                                        sendBtn = btn;
                                                    } else if (!sendBtn) {
                                                        sendBtn = btn;
                                                    }
                                                }
                                            }
                                        }
                                        if (sendBtn) {
                                            const eventOpts = { bubbles: true, cancelable: true, view: window };
                                            sendBtn.dispatchEvent(new MouseEvent('mousedown', eventOpts));
                                            sendBtn.dispatchEvent(new MouseEvent('mouseup', eventOpts));
                                            sendBtn.dispatchEvent(new MouseEvent('click', eventOpts));
                                            return 'clicked_send_btn_via_js';
                                        }
                                        return 'send_btn_not_found';
                                    }""")
                                    
                                    if js_clicked != 'clicked_send_btn_via_js':
                                        history_clicked = page.evaluate("""() => {
                                            const sidebarItems = Array.from(document.querySelectorAll('aside p, aside div, aside a, [class*="sidebar"] p'));
                                            for (const el of sidebarItems) {
                                                const txt = (el.innerText || '').toLowerCase();
                                                const rect = el.getBoundingClientRect();
                                                if (rect.width > 0 && rect.height > 0 && (txt.includes('create') || txt.includes('history') || txt.includes('generate'))) {
                                                    if (txt.includes('create') || txt.includes('generate')) {
                                                        const eventOpts = { bubbles: true, cancelable: true, view: window };
                                                        el.dispatchEvent(new MouseEvent('mousedown', eventOpts));
                                                        el.dispatchEvent(new MouseEvent('mouseup', eventOpts));
                                                        el.dispatchEvent(new MouseEvent('click', eventOpts));
                                                        return 'clicked_history_item';
                                                    }
                                                }
                                            }
                                            const allAsideDivs = Array.from(document.querySelectorAll('aside div'));
                                            for (const btn of allAsideDivs) {
                                                const rect = btn.getBoundingClientRect();
                                                if (rect.width > 0 && rect.height > 0) {
                                                    const html = btn.outerHTML.toLowerCase();
                                                    if (html.includes('svg') && html.includes('path')) {
                                                        const eventOpts = { bubbles: true, cancelable: true, view: window };
                                                        btn.dispatchEvent(new MouseEvent('mousedown', eventOpts));
                                                        btn.dispatchEvent(new MouseEvent('mouseup', eventOpts));
                                                        btn.dispatchEvent(new MouseEvent('click', eventOpts));
                                                        return 'clicked_fallback_history_item';
                                                    }
                                                }
                                            }
                                            return 'no_item_found';
                                        }""")
                                        if history_clicked in ['clicked_history_item', 'clicked_fallback_history_item']:
                                            self.log("INFO", f"Row {row_id}: Stuck on submission. Clicked sidebar history item ({history_clicked}).")
                                            page.wait_for_timeout(3000)
                                            continue
                                            
                                    replied_yes = True
                                    self.log("SUCCESS", f"Row {row_id}: Sent 'yes' response to 10-second limit warning.")
                                    page.wait_for_timeout(1500)
                                except Exception as reply_err:
                                    self.log("WARNING", f"Row {row_id}: Failed to reply 'yes' to warning: {str(reply_err)}")
                    except Exception as warning_err:
                        self.log("WARNING", f"Row {row_id}: Warning check error: {str(warning_err)}")

                    # 2a. Daily Limit Check (Dola: "You've reached the daily limit" or insufficient points warning)
                    try:
                        daily_limit_hit = False
                        page_text = page.evaluate("""() => {
                            const clone = document.body ? document.body.cloneNode(true) : null;
                            if (!clone) return '';
                            clone.querySelectorAll('aside, nav, header').forEach(el => el.remove());
                            return clone.innerText;
                        }""")
                        ltxt = page_text.lower()
                        
                        # 1. Check standard limit keywords
                        has_limit_keyword = any(k in ltxt for k in [
                            "reached the daily limit",
                            "daily limit for video generation",
                            "try again tomorrow",
                            "you've reached your limit",
                            "you have reached your limit",
                            "insufficient points"
                        ])
                            
                        # 2. Check dynamic points shortage warnings (e.g., "You only have 1 video point left today")
                        import re
                        points_match = re.search(r"you\s+(?:only\s+)?have\s+(\d+)\s+(?:video\s+)?points?\s+left\s+today", ltxt)
                        points_left = None
                        if points_match:
                            points_left = int(points_match.group(1))
                            try:
                                self._update_account_points(selected_account, points_left)
                            except Exception as pe:
                                self.log("WARNING", f"Failed to save parsed points limit: {str(pe)}")
                        
                        if has_limit_keyword or (points_left is not None and points_left == 0):
                            daily_limit_hit = True
                        
                        if daily_limit_hit:
                            self.log("ERROR", f"Row {row_id}: Account {selected_account} has hit limit or has insufficient points. Marking and switching account...")
                            self._release_account_lock(selected_account, success=False, mark_daily_limit=True)
                            selected_account = None
                            self.last_error_reason = "DAILY_LIMIT"
                            raise Exception("DAILY_LIMIT")
                    except Exception as e:
                        if "DAILY_LIMIT" in str(e):
                            raise e

                    # 2b. Independent Fail-Safe Content Policy Check
                    try:
                        policy_violated = False
                        for frame in page.frames:
                            try:
                                frame_text = frame.evaluate("() => document.body ? document.body.innerText : ''")
                                ltxt = frame_text.lower()
                                if any(k in ltxt for k in ["copyright violation", "policy violation", "policy-violating", "violate our", "violates our", "try something else"]):
                                    policy_violated = True
                                    break
                            except:
                                pass
                        if policy_violated:
                            self.log("ERROR", f"Row {row_id}: Content policy violation blocked this prompt!")
                            self.last_error_reason = "POLICY_VIOLATION"
                            raise Exception("POLICY_VIOLATION")
                    except Exception as e:
                        if "POLICY_VIOLATION" in str(e):
                            raise e

                    # 3. Check for successful generation message
                    try:
                        confirmed_msg = page.evaluate("""() => {
                            const bodyText = document.body ? document.body.innerText : '';
                            const t = bodyText.toLowerCase();
                            
                            // Check for standard video generation acceptance keywords
                            if (
                                t.includes("generating your video") ||
                                t.includes("will be generated using") ||
                                t.includes("i will generate") ||
                                t.includes("video is being generated") ||
                                t.includes("generating the video") ||
                                t.includes("generating it now") ||
                                t.includes("ok, i will generate") ||
                                t.includes("okay, i will generate") ||
                                t.includes("video will take") ||
                                t.includes("generation has started") ||
                                (t.includes("video") && t.includes("generating") && (t.includes("minutes") || t.includes("seconds") || t.includes("model")))
                            ) {
                                return "Got it, I'm generating your video right now.";
                            }
                            return null;
                        }""")
                    except:
                        pass

                    if confirmed_msg:
                        break

                    page.wait_for_timeout(1000)
                    self._minimize_chrome()

                if confirmed_msg:
                    self.log("SUCCESS", f"Row {row_id}: CONFIRMED: {confirmed_msg}")
                    self._check_and_update_points(page, selected_account)
                else:
                    self.log("ERROR", f"Row {row_id}: Generation confirmation message not found after 240s timeout.")
                    raise Exception("PAGE_NOT_LOADED")

                self.update_status(row_id, "GENERATING", f"[4/5] Rendering (up to {timeout_min} mins)...")
                self.log("INFO", f"Row {row_id}: Monitoring for 'Your video is ready' (up to {timeout_min} mins)...")

                video_src = None
                download_success = False
                video_ready_detected = False
                intercepted_mp4_url = None

                # ----------------------------------------------------------------
                # NETWORK INTERCEPT: Hook all page responses to passively capture
                # the real MP4 CDN URL the moment the browser fetches it.
                # This is the most reliable method — zero dependency on UI clicks.
                # ----------------------------------------------------------------
                def _on_response(response):
                    nonlocal intercepted_mp4_url
                    try:
                        url = response.url
                        ct = response.headers.get("content-type", "")
                        # Catch any video/mp4 CDN response or any .mp4 URL
                        if intercepted_mp4_url:
                            return
                        if (
                            response.request.resource_type == "media" or
                            "video" in ct or
                            ".mp4" in url or
                            "-dola.dola.com" in url or
                            "dola-output" in url or
                            "r2.dola.ai" in url or
                            ("cdn" in url and ("mp4" in url or "video" in url))
                        ):
                            intercepted_mp4_url = url
                            self.log("SUCCESS", f"Row {row_id}: [INTERCEPT] Caught MP4 CDN URL: {url[:100]}")
                    except:
                        pass

                page.on("response", _on_response)
                self.log("INFO", f"Row {row_id}: Network intercept active — scanning for MP4 CDN response...")

                # ----------------------------------------------------------------
                # POLLING PHASE: Every second check ready text + DOM src
                # Also trigger JS autoplay on video element once ready is detected
                # (autoplay forces the browser to fetch the MP4 from CDN → triggers intercept)
                # ----------------------------------------------------------------
                timeout_sec = int(timeout_min * 60)
                video_autoplay_triggered = False

                for i in range(timeout_sec):
                    if getattr(self, "is_stopped", False):
                        raise Exception("USER_ABORTED")

                    # If intercept already caught the URL → break immediately, no need to wait
                    if intercepted_mp4_url:
                        video_src = intercepted_mp4_url
                        self.log("SUCCESS", f"Row {row_id}: MP4 intercepted at {i}s. Proceeding to download ASAP!")
                        break

                    # Check for daily limit during generation loop
                    try:
                        chat_text = page.evaluate("""() => {
                            const clone = document.body ? document.body.cloneNode(true) : null;
                            if (!clone) return '';
                            clone.querySelectorAll('aside, nav, header').forEach(el => el.remove());
                            return clone.innerText.toLowerCase();
                        }""")
                        has_limit = any(k in chat_text for k in [
                            "reached the daily limit",
                            "daily limit for video generation",
                            "try again tomorrow",
                            "you've reached your limit",
                            "you have reached your limit",
                            "insufficient points",
                            "not enough points",
                            "need more points"
                        ])
                        if has_limit:
                            self.log("ERROR", f"Row {row_id}: Account {selected_account} hit daily limit or points shortage during generation.")
                            self._release_account_lock(selected_account, success=False, mark_daily_limit=True)
                            selected_account = None
                            self.last_error_reason = "DAILY_LIMIT"
                            raise Exception("DAILY_LIMIT")
                    except Exception as e:
                        if "DAILY_LIMIT" in str(e):
                            raise e

                    try:
                        # Scroll to bottom so new messages/content are visible
                        page.evaluate("""() => {
                            Array.from(document.querySelectorAll('*')).forEach(el => {
                                if (el.scrollHeight > el.clientHeight) el.scrollTop = el.scrollHeight;
                            });
                            window.scrollTo(0, document.body.scrollHeight);
                        }""")
                    except:
                        pass

                    # Check 1: "Your video is ready" text
                    try:
                        ready_check = page.evaluate("""() => {
                            const t = document.body ? document.body.innerText.toLowerCase() : '';
                            return (
                                t.includes('your video is ready') ||
                                t.includes('video is ready') ||
                                t.includes('image is ready') ||
                                t.includes('your image is ready') ||
                                t.includes('generation complete') ||
                                t.includes('video ready')
                            );
                        }""")
                        if ready_check and not video_ready_detected:
                            video_ready_detected = True
                            self.log("SUCCESS", f"Row {row_id}: 'Ready' state detected at {i}s!")
                    except:
                        pass

                    # Check 1.5: Playwright Native and JS Video Autoplay Interactions
                    # Simulates trusted hover and click sequences on the media card or play button overlay to trigger network CDN fetch.
                    if video_ready_detected and not intercepted_mp4_url and (i % 10 == 0 or not video_autoplay_triggered):
                        try:
                            # 1. Primary: Run fast JS hover and click simulation on the play button overlay
                            js_triggered = page.evaluate("""() => {
                                const mediaElements = Array.from(document.querySelectorAll('video, img'));
                                const validMedia = mediaElements.filter(el => {
                                    const rect = el.getBoundingClientRect();
                                    if (rect.width < 100 || rect.height < 100) return false;
                                    if (el.closest('aside') || el.closest('header') || el.closest('nav') || el.closest('input')) return false;
                                    return true;
                                });

                                if (validMedia.length === 0) return false;
                                const target = validMedia[validMedia.length - 1];
                                
                                // Scroll it into view smoothly
                                target.scrollIntoView({ block: 'center', behavior: 'smooth' });

                                let parentCard = target;
                                for (let depth = 0; depth < 5; depth++) {
                                    if (!parentCard.parentElement) break;
                                    parentCard = parentCard.parentElement;
                                    const playBtn = parentCard.querySelector('[class*="play"], button, [role="button"], svg, [class*="icon"], [class*="btn"]');
                                    if (playBtn) {
                                        // Simulate mouse hover sequence (mouseenter, mouseover, mousemove)
                                        const rect = playBtn.getBoundingClientRect();
                                        const clientX = rect.left + rect.width / 2;
                                        const clientY = rect.top + rect.height / 2;
                                        playBtn.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true, cancelable: true, clientX, clientY }));
                                        playBtn.dispatchEvent(new MouseEvent('mouseover', { bubbles: true, cancelable: true, clientX, clientY }));
                                        playBtn.dispatchEvent(new MouseEvent('mousemove', { bubbles: true, cancelable: true, clientX, clientY }));
                                        
                                        // Simulate click
                                        playBtn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
                                        return true;
                                    }
                                }
                                
                                // Fallback: dispatch hover/click on the media target itself
                                target.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
                                target.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
                                target.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                                return true;
                            }""")
                            
                            if js_triggered:
                                video_autoplay_triggered = True
                                self.log("INFO", f"Row {row_id}: JS Play Button Hover + Click triggered successfully.")
                        except Exception as js_err:
                            self.log("WARNING", f"Row {row_id}: JS Play Button Hover + Click simulation failed: {str(js_err)[:80]}")

                        # 2. Native Playwright Hover + Click Fallback (Only attempted if JS didn't trigger, with very low timeout)
                        if not video_autoplay_triggered:
                            try:
                                videos_locator = page.locator('video')
                                imgs_locator = page.locator('img')
                                
                                target_element = None
                                if videos_locator.count() > 0:
                                    target_element = videos_locator.last
                                elif imgs_locator.count() > 0:
                                    # Choose the last image only if it's likely a generated card (not a tiny avatar)
                                    last_img = imgs_locator.last
                                    box = last_img.bounding_box(timeout=500)
                                    if box and box['width'] >= 100 and box['height'] >= 100:
                                        target_element = last_img
                                        
                                if target_element and target_element.is_visible(timeout=500):
                                    # Scroll into view with very low timeout to prevent lockups
                                    target_element.scroll_into_view_if_needed(timeout=500)
                                    target_element.hover(timeout=500)
                                    target_element.click(timeout=500, force=True)
                                    video_autoplay_triggered = True
                                    self.log("INFO", f"Row {row_id}: Playwright Native interaction fallback succeeded.")
                            except Exception as native_err:
                                # Safe catch — no log spamming since standard interaction failures are handled
                                pass

                    # Check 2: JS fallback autoplay & parent click dispatch
                    if video_ready_detected and not intercepted_mp4_url and not video_autoplay_triggered:
                        try:
                            triggered = page.evaluate("""() => {
                                const videos = Array.from(document.querySelectorAll('video'));
                                const v = videos[videos.length - 1];
                                if (!v) return false;
                                v.scrollIntoView({ block: 'center' });
                                v.muted = true;
                                v.currentTime = 0;
                                const p = v.play();
                                if (p && p.catch) p.catch(() => {});
                                const clickEvt = new MouseEvent('click', { bubbles: true, cancelable: true });
                                v.dispatchEvent(clickEvt);
                                if (v.parentElement) {
                                    v.parentElement.dispatchEvent(clickEvt);
                                    if (v.parentElement.parentElement)
                                        v.parentElement.parentElement.dispatchEvent(clickEvt);
                                }
                                return true;
                            }""")
                            if triggered:
                                video_autoplay_triggered = True
                                self.log("INFO", f"Row {row_id}: Autoplay + click triggered on video element via JS fallback.")
                        except Exception as ap_err:
                            self.log("WARNING", f"Row {row_id}: JS Autoplay fallback failed: {str(ap_err)[:80]}")

                    # Check 3: DOM src scan (fallback — some players expose src directly)
                    if video_ready_detected and not intercepted_mp4_url:
                        try:
                            found_src = page.evaluate(r"""() => {
                                // Scan all video elements for a real src
                                const videos = Array.from(document.querySelectorAll('video, video source'));
                                for (const el of videos) {
                                    const s = el.getAttribute('src') || el.currentSrc || '';
                                    if (s && !s.startsWith('blob:') && (s.includes('.mp4') || s.includes('-dola.dola.com') || s.includes('r2.dola') || s.includes('dola-output') || s.includes('cdn')))
                                        return s;
                                }
                                // Scan innerHTML for any raw .mp4/dola CDN link
                                const html = document.documentElement.innerHTML;
                                const m = html.match(/https?:\/\/[^"'\s<>]+(?:\.mp4|-dola\.dola\.com|r2\.dola\.ai|dola-output)[^"'\s<>]*/);
                                return m ? m[0] : null;
                            }""")
                            if found_src:
                                video_src = found_src
                                self.log("SUCCESS", f"Row {row_id}: DOM scan found src at {i}s: {found_src[:80]}")
                                break
                        except:
                            pass

                    # Progress logs
                    if i > 0 and i % 30 == 0:
                        if video_ready_detected:
                            self.log("WARNING", f"Row {row_id}: Ready detected but no CDN URL captured yet ({i}s). Still scanning...")
                        else:
                            self.log("INFO", f"Row {row_id}: Still waiting for generation... ({i}/{timeout_sec}s)")

                    page.wait_for_timeout(1000)

                # Remove the response listener (cleanup)
                try:
                    page.remove_listener("response", _on_response)
                except:
                    pass

                # Final check: use intercepted URL if DOM scan didn't find one
                if intercepted_mp4_url and not video_src:
                    video_src = intercepted_mp4_url

                if not video_ready_detected and not video_src:
                    self.log("WARNING", f"Row {row_id}: 'Ready' state not detected after {timeout_sec}s. Still attempting download...")


                # ----------------------------------------------------------------
                # PHASE 3: Download using all available methods
                # ----------------------------------------------------------------
                target_filename = f"video_{row_id}_{uuid.uuid4().hex[:6]}.mp4"
                target_path = os.path.join(self.output_dir, target_filename)

                def try_all_download_methods(src_url):
                    """Try all download methods and return True on first success."""

                    # METHOD 1: New Tab Direct Download (Primary)
                    if src_url.startswith("http"):
                        new_tab = None
                        try:
                            self.log("INFO", f"Row {row_id}: Method 1 - New tab download...")
                            new_tab = context.new_page()
                            try:
                                with new_tab.expect_download(timeout=15000) as dl_info:
                                    new_tab.goto(src_url, timeout=30000)
                                dl = dl_info.value
                                dl.save_as(target_path)
                                if is_valid_video(target_path):
                                    self.log("SUCCESS", f"Row {row_id}: Method 1 (new tab) succeeded. Size: {os.path.getsize(target_path)} bytes.")
                                    return True
                            except:
                                pass
                        except Exception as e:
                            self.log("WARNING", f"Row {row_id}: Method 1 failed: {str(e)[:80]}")
                        finally:
                            if new_tab:
                                try: new_tab.close()
                                except: pass

                    # METHOD 2: Python requests HTTP download (Fallback, uses local IP - zero proxy data)
                    if src_url.startswith("http") and not src_url.startswith("blob:"):
                        try:
                            self.log("INFO", f"Row {row_id}: Method 2 - Python requests download...")
                            import requests as req_lib
                            cookies_dict = {}
                            try:
                                for c in context.cookies():
                                    cookies_dict[c["name"]] = c["value"]
                            except:
                                pass
                            headers = {
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                                "Referer": "https://www.dola.com/",
                                "Origin": "https://www.dola.com"
                            }
                            resp = req_lib.get(src_url, headers=headers, cookies=cookies_dict, timeout=120, stream=True)
                            resp.raise_for_status()
                            with open(target_path, "wb") as f:
                                for chunk in resp.iter_content(chunk_size=65536):
                                    if chunk:
                                        f.write(chunk)
                            if is_valid_video(target_path):
                                self.log("SUCCESS", f"Row {row_id}: Method 2 (requests) succeeded. Size: {os.path.getsize(target_path)} bytes.")
                                return True
                        except Exception as e:
                            self.log("WARNING", f"Row {row_id}: Method 2 failed: {str(e)[:80]}")

                    # METHOD 3: Browser Fetch (inherits auth cookies, fallback)
                    try:
                        self.log("INFO", f"Row {row_id}: Method 3 - Browser fetch...")
                        b64 = page.evaluate("""async (url) => {
                            const response = await fetch(url);
                            const blob = await response.blob();
                            return new Promise((resolve, reject) => {
                                const reader = new FileReader();
                                reader.onloadend = () => resolve(reader.result.split(',')[1]);
                                reader.onerror = () => reject(new Error('FileReader failed'));
                                reader.readAsDataURL(blob);
                            });
                        }""", src_url)
                        video_data = base64.b64decode(b64)
                        with open(target_path, "wb") as f:
                            f.write(video_data)
                        if is_valid_video(target_path):
                            self.log("SUCCESS", f"Row {row_id}: Method 3 succeeded. Size: {len(video_data)} bytes.")
                            return True
                    except Exception as e:
                        self.log("WARNING", f"Row {row_id}: Method 3 failed: {str(e)[:80]}")

                    # METHOD 4: Full DOM innerHTML .mp4 regex scan (catches any CDN link in page source)
                    try:
                        self.log("INFO", f"Row {row_id}: Method 4 - DOM innerHTML .mp4 regex scan...")
                        mp4_url = page.evaluate(r"""() => {
                            const html = document.documentElement.innerHTML;
                            const match = html.match(/https?:\/\/[^"'\s<>]+(?:\.mp4|-dola\.dola\.com|r2\.dola\.ai|dola-output)[^"'\s<>]*/);
                            return match ? match[0] : null;
                        }""")
                        if mp4_url and mp4_url != src_url:
                            import requests as req_lib
                            headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.dola.com/"}
                            resp = req_lib.get(mp4_url, headers=headers, timeout=120, stream=True)
                            resp.raise_for_status()
                            with open(target_path, "wb") as f:
                                for chunk in resp.iter_content(chunk_size=65536):
                                    if chunk:
                                        f.write(chunk)
                            if is_valid_video(target_path):
                                self.log("SUCCESS", f"Row {row_id}: Method 4 (DOM scanner) succeeded.")
                                return True
                    except Exception as e:
                        self.log("WARNING", f"Row {row_id}: Method 4 failed: {str(e)[:80]}")

                    # METHOD 5: Video element deep src scan + browser fetch
                    try:
                        self.log("INFO", f"Row {row_id}: Method 5 - Video element deep src scan...")
                        all_srcs = page.evaluate("""() => {
                            const srcs = [];
                            document.querySelectorAll('video, video source').forEach(el => {
                                const s = el.getAttribute('src') || el.currentSrc;
                                if (s && s.trim()) srcs.push(s.trim());
                            });
                            return srcs;
                        }""")
                        for alt_src in (all_srcs or []):
                            if alt_src == src_url:
                                continue
                            try:
                                b64 = page.evaluate("""async (url) => {
                                    const response = await fetch(url);
                                    const blob = await response.blob();
                                    return new Promise((resolve, reject) => {
                                        const reader = new FileReader();
                                        reader.onloadend = () => resolve(reader.result.split(',')[1]);
                                        reader.onerror = reject;
                                        reader.readAsDataURL(blob);
                                    });
                                }""", alt_src)
                                video_data = base64.b64decode(b64)
                                with open(target_path, "wb") as f:
                                    f.write(video_data)
                                if is_valid_video(target_path):
                                    self.log("SUCCESS", f"Row {row_id}: Method 5 (deep scan) succeeded. Size: {len(video_data)} bytes.")
                                    return True
                            except:
                                pass
                    except Exception as e:
                        self.log("WARNING", f"Row {row_id}: Method 5 failed: {str(e)[:80]}")

                    # METHOD 6: Click Dola's native Download button directly
                    try:
                        self.log("INFO", f"Row {row_id}: Method 6 - Clicking Dola download button...")
                        btn = page.locator(
                            'button:has-text("Download"), a:has-text("Download"), '
                            '[aria-label*="download" i], [title*="download" i], '
                            'button[class*="download" i], a[class*="download" i]'
                        ).last
                        if btn.count() > 0 and btn.is_visible():
                            with page.expect_download(timeout=60000) as dl_info:
                                btn.click(force=True)
                            dl = dl_info.value
                            dl.save_as(target_path)
                            if is_valid_video(target_path):
                                self.log("SUCCESS", f"Row {row_id}: Method 6 (download button) succeeded. Size: {os.path.getsize(target_path)} bytes.")
                                return True
                        else:
                            self.log("WARNING", f"Row {row_id}: Method 6 - No visible download button found.")
                    except Exception as e:
                        self.log("WARNING", f"Row {row_id}: Method 6 failed: {str(e)[:80]}")

                    return False

                # Try all download methods with found URL
                if video_src:
                    self.log("INFO", f"Row {row_id}: Starting download for: {video_src[:80]}...")
                    download_success = try_all_download_methods(video_src)

                # If still no success, do a final DOM + video element scan without pre-found URL
                if not download_success:
                    self.log("WARNING", f"Row {row_id}: No URL pre-found. Running final DOM fallback scan...")
                    try:
                        mp4_url = page.evaluate(r"""() => {
                            const html = document.documentElement.innerHTML;
                            const match = html.match(/https?:\/\/[^"'\s<>]+\.mp4[^"'\s<>]*/);
                            return match ? match[0] : null;
                        }""")
                        if mp4_url:
                            self.log("INFO", f"Row {row_id}: Final DOM scan found URL: {mp4_url[:80]}")
                            download_success = try_all_download_methods(mp4_url)
                    except:
                        pass

                if download_success:
                    # Remove watermark
                    self.remove_watermark_from_video(row_id, target_path)

                    # Generate companion txt file containing caption and hashtags
                    self.create_caption_txt_file(row_id, target_path, prompt)

                    self.update_status(row_id, "DONE", f"Success: {target_filename}")
                    self.log("SUCCESS", f"Row {row_id}: Video saved to {target_path}")
                    self._notify_download(target_filename, row_id)

                    # Save updated cookies back to account file
                    if not setup_mode and selected_account:
                        try:
                            context.storage_state(path=account_path)
                            self.log("SUCCESS", f"Row {row_id}: Updated auth cookies saved back to {selected_account}.")
                        except Exception as save_err:
                            self.log("WARNING", f"Row {row_id}: Failed to save updated cookies: {str(save_err)}")

                    try:
                        self._check_and_update_points(page, selected_account)
                    except:
                        pass
                    time.sleep(3)
                    context.close()
                    p.stop()
                    success = True
                    return True
                else:
                    self.log("ERROR", f"Row {row_id}: All download attempts failed. Video was generated but could not be downloaded.")
                    self.update_status(row_id, "FAILED", "Video generated but download failed.")
                    context.close()
                    p.stop()
                    return False


                
                video_src = None
                download_success = False

            except Exception as e:
                err_msg = str(e)
                if "PROXY_CONNECTION_FAILED" in err_msg:
                    self.log("ERROR", f"Row {row_id}: Proxy connection failed. Skipping retries to prevent browser restart loop.")
                    self.update_status(row_id, "FAILED", "Proxy connection failed.")
                    try:
                        if 'context' in locals() and context:
                            context.close()
                    except:
                        pass
                    return False
                elif "PAGE_NOT_LOADED" in err_msg:
                    self.log("WARNING", f"Row {row_id}: Page did not load properly (attempt {page_retry + 1}/{max_page_retries}). Closing context and retrying...")
                    try:
                        if 'context' in locals():
                            context.close()
                    except:
                        pass
                    if page_retry < max_page_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        self.log("ERROR", f"Row {row_id}: Page failed to load after {max_page_retries} attempts. Giving up.")
                        self.update_status(row_id, "FAILED", "Page failed to load.")
                        return False
                elif "SESSION_EXPIRED" in err_msg:
                    self.log("WARNING", f"Row {row_id}: Dola session expired. Closing context and trying next available account...")
                    try:
                        if 'context' in locals() and context:
                            context.close()
                    except:
                        pass
                    if page_retry < max_page_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        self.log("ERROR", f"Row {row_id}: Failed to find active session after {max_page_retries} attempts.")
                        self.update_status(row_id, "FAILED", "No active session available.")
                        return False
                elif "POLICY_VIOLATION" in err_msg:
                    try:
                        if 'context' in locals():
                            context.close()
                    except:
                        pass
                    self.update_status(row_id, "SKIPPED", "Error: Policy/Copyright Violation.")
                    return False
                elif "DAILY_LIMIT" in err_msg:
                    self.log("WARNING", f"Row {row_id}: Daily limit hit. Closing context and retrying with next account...")
                    try:
                        if 'context' in locals() and context:
                            context.close()
                    except:
                        pass
                    if page_retry < max_page_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        self.log("ERROR", f"Row {row_id}: All accounts hit daily limit. No more accounts available today.")
                        self.update_status(row_id, "FAILED", "All accounts hit daily limit.")
                        return False
                else:
                    self.log("ERROR", f"Row {row_id}: Script execution failed: {str(e)}")
                    self.update_status(row_id, "FAILED", f"Error: {str(e)[:40]}...")
                    try:
                        if 'context' in locals():
                            context.close()
                    except:
                        pass
                    return False
            finally:
                self._current_context = None
                if not setup_mode and selected_account:
                    self._release_account_lock(selected_account, success=success)
                if not setup_mode and 'user_data_dir' in locals() and user_data_dir and os.path.exists(user_data_dir):
                    if "_temp_" in user_data_dir or ("chrome_profile_slot_" not in user_data_dir and "chrome_profile_acc_" not in user_data_dir):
                        time.sleep(1)
                        shutil.rmtree(user_data_dir, ignore_errors=True)
                # Remove from active rows so stale lock detection works for future rows
                try:
                    DolaAutomationBot._active_row_ids.discard(row_id)
                except:
                    pass

    def _update_account_points(self, fname, points):
        import json
        from datetime import date
        
        if not fname:
            return
            
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cookies_dir = os.path.join(base_dir, "cookies")
        usage_path = os.path.join(cookies_dir, "_usage.json")
        
        if not os.path.exists(usage_path):
            return
            
        try:
            with open(usage_path, "r", encoding="utf-8") as f:
                usage = json.load(f)
        except:
            return
            
        if fname in usage:
            u = usage[fname]
            old_points = u.get("points_left")
            old_status = u.get("status")
            
            today = str(date.today())
            u["points_left"] = points
            u["date"] = today
            
            # If remaining points is 0, we can also set the status to DAILY_LIMIT for today
            if points == 0:
                import time
                u["status"] = "DAILY_LIMIT"
                if not u.get("limit_timestamp"):
                    u["limit_timestamp"] = time.time()
                
            usage[fname] = u
            
            # Only write to file and log if points or status actually changed
            if old_points != points or old_status != u.get("status"):
                try:
                    with open(usage_path, "w", encoding="utf-8") as f:
                        json.dump(usage, f, indent=2)
                    self.log("INFO", f"Account {fname} points updated in Session Vault: {points} points left.")
                except:
                    pass

    def _update_account_name(self, fname, name):
        import json
        if not fname or not name:
            return
            
        base_dir = os.path.dirname(os.path.abspath(__file__))
        usage_path = os.path.join(base_dir, "cookies", "_usage.json")
        if not os.path.exists(usage_path):
            return
            
        try:
            with open(usage_path, "r", encoding="utf-8") as f:
                usage = json.load(f)
        except:
            return
            
        if fname in usage:
            u = usage[fname]
            old_name = u.get("account_name")
            if old_name != name:
                u["account_name"] = name
                usage[fname] = u
                try:
                    with open(usage_path, "w", encoding="utf-8") as f:
                        json.dump(usage, f, indent=2)
                except:
                    pass

    def _check_and_update_points(self, page, selected_account):
        if not selected_account:
            return
        try:
            import re
            page_text = page.evaluate("() => document.body ? document.body.innerText : ''")
            t = page_text.lower()
            
            patterns = [
                r'(\d+)\s+(?:video\s+)?generations?\s+left',
                r'(\d+)\s+(?:video\s+)?generations?\s+remaining',
                r'(\d+)\s+remaining\s+generations?',
                r'(\d+)\s+points?\s+left',
                r'points?\s+left:\s*(\d+)',
                r'remaining\s+points?:\s*(\d+)',
                r'(\d+)\s+remaining\s+points?',
                r'(\d+)\s+video\s+generations?\s+remaining',
                r'(\d+)\s+video(?:s)?\s+left',
                r'(\d+)\s+video(?:s)?\s+remaining',
            ]
            
            found_points = None
            for pattern in patterns:
                matches = re.findall(pattern, t)
                if matches:
                    found_points = int(matches[-1])
                    break
                    
            if found_points is not None:
                self._update_account_points(selected_account, found_points)
        except Exception as err:
            self.log("WARNING", f"Failed to check/update points: {str(err)}")


def is_valid_video(path):
    if not os.path.exists(path):
        return False
    size = os.path.getsize(path)
    MIN_SIZE = 100 * 1024          # 100 KB minimum
    MAX_SIZE = 500 * 1024 * 1024   # 500 MB maximum (no artificial cap)
    if size < MIN_SIZE or size > MAX_SIZE:
        return False
    return True

# main.py — PyQt6 Application for Nexus Automator

import sys
import os
import random
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QLabel, QLineEdit,
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame, QFileDialog, QTextEdit, QCheckBox,
                             QProgressBar, QListWidget, QListWidgetItem, QSizePolicy,
                             QDialog, QMessageBox, QStackedWidget, QScrollArea,
                             QAbstractItemView, QListView)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer, QRectF, QRect, QByteArray, QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QPainter, QPen, QBrush, QLinearGradient, QPixmap

from logo_data import LOGO_PNG_B64, USER_AVATAR_B64

AKIRA_APP_VERSION = "1.0.3"

import base64
def _un(b64_str):
    try:
        decoded_bytes = base64.b64decode(b64_str.encode('utf-8'))
        return "".join([chr(b ^ 42) for b in decoded_bytes])
    except Exception:
        return ""

# Hardcoded configuration (XOR Obfuscated to prevent text extraction from binary)
CONFIG_DATA = {
    "web_app_url": _un("Ql5eWlkQBQVZSVhDWl4ETUVFTUZPBElFRwVHS0lYRVkFWQVrYUxTSUhdRHxmU15CGxlnWm9yaxppRkIdE3xYHXxTX2NgcGdrSBN4dUxHRB95chtoQ11SS0FYdR5NH2tHf3sfYFNSRFMTXAdeawVPUk9J"),
    "update_check_url": _un("Ql5eWlkQBQVYS10ETUNeQl9IX1lPWElFRF5PRF4ESUVHBVBLXENTS0RQQ0sHSEVeBUtBQ1hLdUlFRExDTVkFR0tDRAVfWk5LXk8EQFlFRA=="),
    "bitcoin_address": _un("MUJ2Qk1TRVlzdE52alQyNUFuVWlaMkY0dDZ5eTQyeVg="),
    "usdt_address": _un("MHg3MUM3NjU2RUM3YWI4OGIwOThkZWZCNzUxQjc0MDFCNWY2ZDg5NzZG"),
    "admin_contact_url": _un("Ql5eWlkQBQVdSwRHTwUTGBkeHR0ZExMaHRk=")
}

def get_logo_pixmap(size=32):
    pix = QPixmap()
    pix.loadFromData(QByteArray.fromBase64(LOGO_PNG_B64.encode()))
    return pix.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

def get_avatar_pixmap(size=32):
    pix = QPixmap()
    pix.loadFromData(QByteArray.fromBase64(USER_AVATAR_B64.encode()))
    return pix.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

def parse_proxy_string(proxy_str):
    """
    Parses proxy string format:
      IP:Port -> {"server": "http://IP:Port"}
      IP:Port:User:Pass -> {"server": "http://IP:Port", "username": "User", "password": "Pass"}
      User:Pass@IP:Port -> {"server": "http://IP:Port", "username": "User", "password": "Pass"}
    """
    proxy_str = proxy_str.strip()
    if not proxy_str:
        return None
        
    # Check if format is User:Pass@IP:Port
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
        except Exception:
            pass
            
    # Check if format is IP:Port:User:Pass
    parts = proxy_str.split(":")
    if len(parts) == 4:
        ip, port, user, password = parts
        server = f"http://{ip.strip()}:{port.strip()}"
        return {
            "server": server,
            "username": user.strip(),
            "password": password.strip()
        }
    elif len(parts) == 2:
        ip, port = parts
        server = f"http://{ip.strip()}:{port.strip()}"
        return {"server": server}
    else:
        # Fallback raw
        if not proxy_str.startswith("http://") and not proxy_str.startswith("https://") and not proxy_str.startswith("socks5://"):
            server = f"http://proxy_str"
        else:
            server = proxy_str
        return {"server": server}

# --- CUSTOM SIDEBAR TAB WIDGET FOR EXACT MATCH ---
class SidebarTabWidget(QWidget):
    def __init__(self, title, subtitle, icon_svg_base64, parent=None):
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self.icon_svg_base64 = icon_svg_base64
        self.active = False
        self.setFixedHeight(54)
        
        # Layout
        self.lay = QHBoxLayout(self)
        self.lay.setContentsMargins(12, 6, 12, 6)
        self.lay.setSpacing(12)
        
        # Left vector icon
        self.icon_lbl = QLabel(self)
        self.icon_lbl.setFixedSize(22, 22)
        self.icon_lbl.setStyleSheet("background: transparent; border: none;")
        self.lay.addWidget(self.icon_lbl)
        if not self.icon_svg_base64:
            self.icon_lbl.hide()
            self.lay.setContentsMargins(15, 6, 15, 6)
        
        # Right text block
        self.text_widget = QWidget(self)
        self.text_widget.setStyleSheet("background: transparent; border: none;")
        self.text_lay = QVBoxLayout(self.text_widget)
        self.text_lay.setContentsMargins(0, 0, 0, 0)
        self.text_lay.setSpacing(1)
        
        self.lbl_title = QLabel(self.title, self)
        self.lbl_title.setStyleSheet("font-weight: bold; border: none; background: transparent;")
        
        self.lbl_sub = QLabel(self.subtitle or "", self)
        self.lbl_sub.setStyleSheet("border: none; background: transparent;")
        
        self.text_lay.addWidget(self.lbl_title)
        if self.subtitle:
            self.text_lay.addWidget(self.lbl_sub)
        else:
            self.lbl_sub.hide()
            self.text_lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            
        self.lay.addWidget(self.text_widget, 1)
        
        self.update_state()

    def set_active(self, active):
        self.active = active
        self.update_state()
        self.update() # Force repaint

    def update_state(self):
        if self.active:
            self.lbl_title.setStyleSheet("font-weight: bold; color: #FFFFFF; font-size: 9.5pt; border: none; background: transparent;")
            self.lbl_sub.setStyleSheet("color: #D4AF37; font-size: 8.0pt; border: none; background: transparent;")
            
            if self.icon_svg_base64:
                # Draw vector icon colorized/tinted to gold
                pix = QPixmap()
                pix.loadFromData(QByteArray.fromBase64(self.icon_svg_base64.encode()))
                
                tinted_pix = QPixmap(pix.size())
                tinted_pix.fill(Qt.GlobalColor.transparent)
                painter = QPainter(tinted_pix)
                painter.drawPixmap(0, 0, pix)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                painter.fillRect(tinted_pix.rect(), QColor("#C5A059"))
                painter.end()
                
                self.icon_lbl.setPixmap(tinted_pix.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.lbl_title.setStyleSheet("font-weight: bold; color: #9CA3AF; font-size: 9.5pt; border: none; background: transparent;")
            self.lbl_sub.setStyleSheet("color: #6B7280; font-size: 8.0pt; border: none; background: transparent;")
            
            if self.icon_svg_base64:
                # Draw vector icon colorized/tinted to grey
                pix = QPixmap()
                pix.loadFromData(QByteArray.fromBase64(self.icon_svg_base64.encode()))
                
                # Simple tint to grey using source in composition
                tinted_pix = QPixmap(pix.size())
                tinted_pix.fill(Qt.GlobalColor.transparent)
                painter = QPainter(tinted_pix)
                painter.drawPixmap(0, 0, pix)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                painter.fillRect(tinted_pix.rect(), QColor("#6B7280"))
                painter.end()
                
                self.icon_lbl.setPixmap(tinted_pix.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def paintEvent(self, event):
        if self.active:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Flat dark slate background highlight for active tab
            painter.setBrush(QBrush(QColor(22, 23, 34, 255))) # #161722
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)
            
            # Subtle gold bottom selection strip (3px height)
            painter.setBrush(QBrush(QColor("#C5A059")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(8, self.height() - 4, self.width() - 16, 3), 1.5, 1.5)
            
            # Thin gold border outline
            pen = QPen(QColor("#C5A059"), 1.0)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)
            painter.end()

# --- CUSTOM GENERATING ICON WIDGET WITH SPINNING LOADING CIRCLE ---
class GeneratingIconWidget(QWidget):
    def __init__(self, icon_svg_base64, parent=None):
        super().__init__(parent)
        self.icon_svg_base64 = icon_svg_base64
        self.active = False
        self.angle = 0
        self.setFixedSize(36, 36)
        
        # Timer for rotation animation (ticks every 30ms for smooth spinning)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate_angle)
        self.timer.start(30)

    def set_active(self, active):
        self.active = active
        self.update()

    def rotate_angle(self):
        if self.active:
            self.angle = (self.angle + 6) % 360
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw semi-transparent green circle background
        painter.setBrush(QBrush(QColor(5, 150, 105, 40))) # rgba(5, 150, 105, 0.15)
        painter.setPen(QPen(QColor(5, 150, 105, 102), 1.5)) # rgba(5, 150, 105, 0.4)
        painter.drawEllipse(1, 1, 34, 34)
        
        # Draw spinning loading arc if active
        if self.active:
            pen_arc = QPen(QColor("#10B981"), 2.0)
            painter.setPen(pen_arc)
            # Draw a 90 degree arc that rotates around the circle
            painter.drawArc(1, 1, 34, 34, -self.angle * 16, 90 * 16)
        
        # Draw vector play icon in the center
        pix = QPixmap()
        pix.loadFromData(QByteArray.fromBase64(self.icon_svg_base64.encode()))
        
        # Center of widget is 36x36, icon is 18x18, so draw at (9, 9)
        painter.drawPixmap(9, 9, pix.scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        painter.end()

# --- CUSTOM RADIAL PROGRESS WIDGET ---
class RadialProgressWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.max_value = 100
        self.text_label = "0/100 done"
        self.setFixedSize(90, 90)

    def set_value(self, current, total):
        self.value = current
        self.max_value = total if total > 0 else 100
        self.text_label = f"{current}/{total} done"
        self.update() # Force repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate bounding box (margin of 6px to avoid clipping pen width)
        rect = QRectF(6, 6, 78, 78)
        
        # Draw background ring (dark slate border)
        pen_bg = QPen(QColor("#1F2231"), 6)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 0, 360 * 16)
        
        # Calculate percentage span angle
        percentage = (self.value / self.max_value) if self.max_value > 0 else 0
        span_angle = -int(percentage * 360 * 16)
        
        # Draw progress arc (solid gold accent)
        pen_fg = QPen(QColor("#C5A059"), 6)
        painter.setPen(pen_fg)
        painter.drawArc(rect, 90 * 16, span_angle) # Starts at top (90 deg)
        
        # Draw text percentage
        font_pct = QFont("Inter", 11, QFont.Weight.Bold)
        painter.setFont(font_pct)
        painter.setPen(QColor("#FFFFFF"))
        pct_text = f"{int(percentage * 100)}%"
        painter.drawText(QRectF(6, 24, 78, 22), Qt.AlignmentFlag.AlignCenter, pct_text)
        
        # Draw secondary text ("0/100 done")
        font_sub = QFont("Inter", 7)
        painter.setFont(font_sub)
        painter.setPen(QColor("#C5A059")) # Subtext in Gold
        painter.drawText(QRectF(6, 48, 78, 16), Qt.AlignmentFlag.AlignCenter, self.text_label)

from styles import UI_MASTER_QSS
from automation import DolaAutomationBot

# --- WORKER THREAD FOR PLAYWRIGHT RUNS ---
class PlaywrightWorker(QThread):
    log_signal = pyqtSignal(str, str)         # (type, message)
    status_signal = pyqtSignal(int, str, str) # (row_id, status, action)
    finished_signal = pyqtSignal(int, bool)   # (row_id, success)

    def __init__(self, bot, row_id, prompt, model, duration, ratio, setup_mode=False, is_image=False, proxy_list=None, sms_key=None, sms_country="0", timeout_min=30):
        super().__init__()
        self.bot = bot
        self.row_id = row_id
        self.prompt = prompt
        self.model = model
        self.duration = duration
        self.ratio = ratio
        self.setup_mode = setup_mode
        self.is_image = is_image
        self.proxy_list = proxy_list
        self.sms_key = sms_key
        self.sms_country = sms_country
        self.timeout_min = timeout_min

    def run(self):
        # Redirect bot log and status callbacks to PyQt signals
        self.bot.callback_log = lambda t, m: self.log_signal.emit(t, m)
        self.bot.callback_status = lambda rid, s, a: self.status_signal.emit(rid, s, a)

        success = self.bot.run_generation(
            row_id=self.row_id,
            prompt=self.prompt,
            model=self.model,
            duration=self.duration,
            ratio=self.ratio,
            setup_mode=self.setup_mode,
            is_image=self.is_image,
            proxy_list=self.proxy_list,
            sms_key=self.sms_key,
            sms_country=self.sms_country,
            timeout_min=self.timeout_min
        )
        self.error_reason = getattr(self.bot, "last_error_reason", None)
        self.finished_signal.emit(self.row_id, success)


def clean_val(text):
    if not text:
        return ""
    t = text.strip()
    # Strip common prefixes
    for prefix in ["default model:", "default length:", "default ratio:", "default batch:", "default speed:",
                    "model:", "length:", "ratio:", "batch:", "speed:"]:
        if t.lower().startswith(prefix):
            t = t[len(prefix):].strip()
            break
    # Remove seconds suffix only if it's a duration label like '15s' or '15 s'
    if t.lower().endswith("s") and t[:-1].strip().isdigit():
        t = t[:-1].strip()
    return t


# --- MAIN APPLICATION WINDOW ---
class NexusAutomatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AKIRA")
        
        # Dynamically calculate window size to fit the user's screen resolution
        screen_geom = QApplication.primaryScreen().geometry()
        screen_width = screen_geom.width()
        screen_height = screen_geom.height()
        
        # Target size: 90-95% of screen size, capped at 1280x800, but at least 1000x680
        width = min(1280, max(1000, int(screen_width * 0.95)))
        height = min(800, max(680, int(screen_height * 0.90)))
        
        # Adjust if screen is smaller than the target size
        if screen_width < 1280:
            width = max(950, screen_width - 40)
        if screen_height < 800:
            height = max(600, screen_height - 60)
            
        self.resize(width, height)
        self.setMinimumSize(min(950, width), min(600, height))
        
        # Load window icon
        self.setWindowIcon(QIcon(get_logo_pixmap(64)))
        self.setWindowTitle("AKIRA AI Video Generator")
        self.drag_position = None
        self.device_id = get_device_id()
        
        # State variables
        self.output_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Seedance Videos")
        self.img_output_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Dola Images")
        self.is_generating = False  # Starts in stopped state
        self.img_is_generating = False
        self.log_counter = 76      # Matches screenshot log index
        self.img_log_counter = 0
        self.workers = {}          # Active background threads
        self.img_workers = {}
        self.queue_data = []       # List of prompts dicts
        self.img_queue_data = []
        self.setup_mode_active = False
        self.is_queue_paused = False
        self.img_is_queue_paused = False
        self.img_action_text_cache = {}
        self.notifications = []    # Notification center list
        self.unread_notifications_count = 0

        # Dashboard Analytics Tracking
        self.dash_sessions = []          # List of completed session dicts
        self.dash_current_session = None # Active session tracking dict
        self.dash_total_generated = 0    # Lifetime success count
        self.dash_total_failed = 0       # Lifetime fail count
        self.dash_total_prompts = 0      # Lifetime prompts processed
        self.dash_total_time_sec = 0     # Lifetime total generation time
        self.dash_best_rate = 0.0        # Best session success rate
        self.dash_error_counts = {"Timeout": 0, "Policy": 0, "Rate Limit": 0, "Network": 0, "Other": 0}

        # Check license config for client mode — default to secure client mode for safety
        self.client_mode = True
        has_config = False
        try:
            if getattr(sys, 'frozen', False):
                config_dir = os.path.dirname(sys.executable)
            else:
                config_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(config_dir, "license_config.json")
            if os.path.exists(config_path):
                has_config = True
                with open(config_path, "r") as f:
                    cfg = json.load(f)
                    self.client_mode = cfg.get("client_mode", True)
        except Exception:
            pass

        self.is_client_build = not has_config

        # Build UI layout
        self.init_ui()
        
        # Apply CSS/QSS styles
        self.setStyleSheet(UI_MASTER_QSS)

        # Initialize to empty state (no mockup data)
        self.initialize_empty_state()

        # Connect slots
        self.connect_actions()

        # Instantiate mockup timer (kept but disabled/stopped on startup)
        self.mock_timer = QTimer(self)
        self.mock_timer.timeout.connect(self.run_mock_step)

        # Center the window on screen on startup
        self.center_on_screen()

        # Start background check for software updates
        self.check_for_updates()

    def check_for_updates(self):
        update_url = CONFIG_DATA.get("update_check_url", "")
        if update_url:
            self.update_checker = UpdateCheckerThread(AKIRA_APP_VERSION, update_url, self)
            self.update_checker.update_available.connect(self.on_update_available)
            self.update_checker.start()

    def on_update_available(self, version, download_url, changelog):
        dialog = AkiraUpdateDialog(version, download_url, changelog, self)
        try:
            pos = self.brand_logo.mapToGlobal(QPoint(0, self.brand_logo.height() + 8))
            screen = QApplication.primaryScreen().geometry()
            x = max(10, min(pos.x(), screen.width() - dialog.width() - 10))
            y = max(10, min(pos.y(), screen.height() - dialog.height() - 10))
            dialog.move(x, y)
        except Exception:
            pass
        dialog.exec()

    def check_updates_realtime(self):
        dialog = RealtimeUpdateDialog(AKIRA_APP_VERSION, CONFIG_DATA.get("update_check_url", ""), self)
        try:
            pos = self.brand_logo.mapToGlobal(QPoint(0, self.brand_logo.height() + 8))
            screen = QApplication.primaryScreen().geometry()
            x = max(10, min(pos.x(), screen.width() - dialog.width() - 10))
            y = max(10, min(pos.y(), screen.height() - dialog.height() - 10))
            dialog.move(x, y)
        except Exception:
            pass
        dialog.exec()

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)


    def init_ui(self):
        # Base central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout is vertical (Top Navbar + Stacked Workspace)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==========================================
        # TOP NAVBAR
        # ==========================================
        navbar = QFrame()
        navbar.setObjectName("SidebarPanel") # Styled as a flat slate panel in CSS
        navbar.setFixedHeight(65)
        navbar_layout = QHBoxLayout(navbar)
        navbar_layout.setContentsMargins(20, 5, 20, 5)
        navbar_layout.setSpacing(20)

        # Left side: Brand Logo & Title
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(10)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        
        self.brand_logo = QLabel()
        self.brand_logo.setObjectName("ProfileAvatar")
        self.brand_logo.setPixmap(get_logo_pixmap(28))
        self.brand_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        brand_name = QLabel("AKIRA")
        brand_name.setObjectName("SidebarBrandName")
        brand_name.setStyleSheet("font-size: 11pt; border: none; background: transparent; font-weight: bold;")
        
        self.brand_version = QPushButton(f"V{AKIRA_APP_VERSION}")
        self.brand_version.setObjectName("VersionBtn")
        self.brand_version.setCursor(Qt.CursorShape.PointingHandCursor)
        self.brand_version.setFlat(True)
        self.brand_version.clicked.connect(self.check_updates_realtime)
        
        brand_layout.addWidget(self.brand_logo)
        brand_layout.addWidget(brand_name)
        brand_layout.addWidget(self.brand_version)
        brand_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        navbar_layout.addLayout(brand_layout)
        
        navbar_layout.addSpacing(10)

        # Middle: Horizontal Navigation Tab List
        self.sidebar_menu = QListWidget(self)
        self.sidebar_menu.setObjectName("SidebarMenu")
        self.sidebar_menu.setFlow(QListView.Flow.LeftToRight)
        self.sidebar_menu.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sidebar_menu.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sidebar_menu.setFrameShape(QFrame.Shape.NoFrame)
        self.sidebar_menu.setFixedHeight(54)
        self.sidebar_menu.setStyleSheet("background: transparent; border: none; padding: 0px;")
        # Navigation icons
        sparkles_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI0ZGRkZGRiI+PHBhdGggZD0iTTEyIDJMMTQuNSA5LjVMMjIgMTJMMTQuNSAxNC41TDEyIDIyTDkuNSAxNC41TDIgMTJMOS41IDkuNUwxMiAyWiBNMTkgMTRMMjAuMTUgMTcuNUwyMyAxOEwyMC4xNSAxOC41TDE5IDIyTDE3Ljg1IDE4LjVMMTUgMThMMTcuODUgMTcuNUwxOSAxNFogTTcgNkw4LjE1IDkuNUwxMCAxTDguMTUgMTAuNUw3IDEyTDUuODUgMTAuNUwzIDEwTDUuODUgOS41TDcgNloiLz48L3N2Zz4="
        vault_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI0ZGRkZGRiI+PHBhdGggZD0iTTEyIDFMMy4zMiA3LjI3bC40MiA3LjI4TDEyIDIzbDguMjYtOC40NS50Mi03LjI4TDEyIDF6bTAgMy41NWw1Ljg5IDMuNzgtLjMxIDUuMjlMMTIgMTcuNjhsLTUuNTgtNS4wNi0uMzEtNS4yOUwxMiA0LjU1ek0xMiA4YTIgMiAwIDEgMCAwIDQgMiAyIDAgMCAwIDAtNHoiLz48L3N2Zz4="

        item_seed = QListWidgetItem()
        item_seed.setSizeHint(QSize(220, 54))
        self.sidebar_menu.addItem(item_seed)
        self.seed_widget = SidebarTabWidget("Seedance 2.0", "15 sec Video generation", None, self)
        self.sidebar_menu.setItemWidget(item_seed, self.seed_widget)

        item_vault = QListWidgetItem()
        item_vault.setSizeHint(QSize(175, 54))
        self.sidebar_menu.addItem(item_vault)
        self.vault_widget = SidebarTabWidget("Session Vault", "Accounts & History", vault_svg, self)
        self.sidebar_menu.setItemWidget(item_vault, self.vault_widget)

        self.sidebar_menu.setCurrentRow(0)
        self.seed_widget.set_active(True)
        
        navbar_layout.addWidget(self.sidebar_menu, 1)

        # Right side: Profile Box & Quick Actions
        right_navbar_layout = QHBoxLayout()
        right_navbar_layout.setSpacing(10)
        
        # Profile Box
        profile_box = QFrame()
        profile_box.setObjectName("ProfileBox")
        profile_box.setFixedHeight(46)
        profile_layout = QHBoxLayout(profile_box)
        profile_layout.setContentsMargins(8, 4, 8, 4)
        profile_layout.setSpacing(8)
        
        avatar = QLabel()
        avatar.setObjectName("ProfileAvatar")
        avatar.setPixmap(get_logo_pixmap(24))
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        details = QVBoxLayout()
        name = QLabel("AKIRA")
        name.setObjectName("ProfileName")
        name.setStyleSheet("font-size: 8.5pt; border: none; background: transparent; font-weight: bold;")
        self.lbl_sub = QLabel("AI Video Generator")
        self.lbl_sub.setObjectName("ProfilePlan")
        self.lbl_sub.setStyleSheet("font-size: 7.5pt; border: none; background: transparent;")
        details.addWidget(name)
        details.addWidget(self.lbl_sub)
        details.setSpacing(0)
        
        profile_layout.addWidget(avatar)
        profile_layout.addLayout(details)
        right_navbar_layout.addWidget(profile_box)

        # Header Action Buttons
        self.btn_refresh = QPushButton()
        self.btn_refresh.setObjectName("HeaderActionButton")
        self.btn_refresh.setText("🔄")
        self.btn_refresh.setToolTip("Check for software updates")
        
        self.btn_support = QPushButton()
        self.btn_support.setObjectName("HeaderActionButton")
        self.btn_support.setText("💬")
        self.btn_support.setToolTip("Announcements and news from admin")
        
        self.btn_theme = QPushButton()
        self.btn_theme.setObjectName("HeaderActionButton")
        self.btn_theme.setText("☀️")
        self.btn_theme.setToolTip("Toggle UI Theme")
        
        self.btn_bell = QPushButton()
        self.btn_bell.setObjectName("HeaderActionButton")
        self.btn_bell.setText("🔔")
        self.btn_bell.setToolTip("Live Notification Center")
        
        self.btn_client_mode = QPushButton()
        self.btn_client_mode.setObjectName("HeaderActionButton")
        self.btn_client_mode.setText("🛠️")
        self.btn_client_mode.setToolTip("Switch between Client & Developer mode")

        self.btn_restart = QPushButton("🔄 Restart")
        self.btn_restart.setObjectName("PromptActionButton")
        self.btn_restart.setFixedHeight(34)
        
        right_navbar_layout.addWidget(self.btn_refresh)
        right_navbar_layout.addWidget(self.btn_support)
        right_navbar_layout.addWidget(self.btn_theme)
        right_navbar_layout.addWidget(self.btn_bell)
        right_navbar_layout.addWidget(self.btn_client_mode)
        right_navbar_layout.addWidget(self.btn_restart)
        
        navbar_layout.addLayout(right_navbar_layout)
        
        main_layout.addWidget(navbar)

        # ==========================================
        # MAIN WORKSPACE
        # ==========================================
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("MainScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        workspace = QWidget()
        workspace.setObjectName("MainWorkspace")
        workspace_layout = QVBoxLayout(workspace)
        workspace_layout.setContentsMargins(24, 18, 24, 18)
        workspace_layout.setSpacing(15)

        # Top Header Nav
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        header_title = QLabel("Seedance Vid Gen")
        header_title.setObjectName("MainHeaderTitle")
        header_sub = QLabel("Bulk generate high quality Seedance AI videos via API integration.")
        header_sub.setObjectName("MainHeaderSubtitle")
        title_box.addWidget(header_title)
        title_box.addWidget(header_sub)
        title_box.setSpacing(2)
        
        header.addLayout(title_box)
        header.addStretch()
        
        # Action buttons
        self.btn_refresh = QPushButton()
        self.btn_refresh.setObjectName("HeaderActionButton")
        self.btn_refresh.setText("🔄")
        self.btn_refresh.setToolTip("Check for software updates")
        
        self.btn_support = QPushButton()
        self.btn_support.setObjectName("HeaderActionButton")
        self.btn_support.setText("💬")
        self.btn_support.setToolTip("Announcements and news from admin")
        
        self.btn_theme = QPushButton()
        self.btn_theme.setObjectName("HeaderActionButton")
        self.btn_theme.setText("☀️")
        self.btn_theme.setToolTip("Toggle UI Theme")
        
        self.btn_bell = QPushButton()
        self.btn_bell.setObjectName("HeaderActionButton")
        self.btn_bell.setText("🔔")
        self.btn_bell.setToolTip("Live Notification Center")
        
        self.btn_client_mode = QPushButton()
        self.btn_client_mode.setObjectName("HeaderActionButton")
        self.btn_client_mode.setText("🛠️" if not self.client_mode else "👤")
        self.btn_client_mode.setToolTip("Switch between Client & Developer mode")
        
        header.addWidget(self.btn_refresh)
        header.addWidget(self.btn_support)
        header.addWidget(self.btn_theme)
        header.addWidget(self.btn_bell)
        header.addWidget(self.btn_client_mode)
        workspace_layout.addLayout(header)

        # VIDEO OUTPUT LOCATION Card (re-designed top panel)
        output_card = QFrame()
        output_card.setObjectName("PanelCard")
        output_card.setMaximumHeight(70)
        output_layout = QVBoxLayout(output_card)
        output_layout.setContentsMargins(14, 8, 14, 8)
        output_layout.setSpacing(4)
        
        output_title = QLabel("Output Folder Location")
        output_title.setObjectName("FormInputLabel")
        output_layout.addWidget(output_title)
        
        output_bar = QHBoxLayout()
        self.output_path_input = QLineEdit(self.output_dir)
        self.output_path_input.setPlaceholderText("Select output folder location...")
        
        # Browse Button on the right
        self.btn_change_folder = QPushButton("📁 Browse")
        self.btn_change_folder.setObjectName("PromptActionButton")
        self.btn_change_folder.setFixedWidth(100)
        
        # Dummy hidden button for compatibility with connect_actions
        self.btn_open_folder = QPushButton()
        self.btn_open_folder.setVisible(False)
        
        output_bar.addWidget(self.output_path_input, 1)
        output_bar.addWidget(self.btn_change_folder)
        output_layout.addLayout(output_bar)
        workspace_layout.addWidget(output_card)

        # Stats Ribbon Card (horizontal row + circular progress widget)
        stats_card = QFrame()
        stats_card.setObjectName("PanelCard")
        stats_card.setMaximumHeight(90)
        stats_layout = QHBoxLayout(stats_card)
        stats_layout.setContentsMargins(14, 8, 14, 8)
        stats_layout.setSpacing(10)

        stats_items_layout = QHBoxLayout()
        self.stat_widgets = {}
        
        # Base64 Vector outline SVGs
        doc_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjRkZGRkZGIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTE0IDJINmEyIDIgMCAwIDAtMiAydjE2YTIgMiAwIDAgMCAyIDJoMTJhMiAyIDAgMCAwIDItMlY4eiIvPjxwb2x5bGluZSBwb2ludHM9IjE0IDIgMTQgOCAyMCA4Ii8+PC9zdmc+"
        clock_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjRkZGRkZGIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiLz48cG9seWxpbmUgcG9pbnRzPSIxMiA2IDEyIDEyIDE2IDE0Ii8+PC9zdmc+"
        play_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjRkZGRkZGIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlnb24gcG9pbnRzPSI1IDMgMTkgMTIgNSAyMSA1IDMiLz48L3N2Zz4="
        check_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjRkZGRkZGIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTIyIDExLjA4VjEyYTEwIDEwIDAgMSAxLTUuOTMtOS4xNCIvPjxwb2x5bGluZSBwb2ludHM9IjIyIDQgMTIgMTQuMDEgOSAxMS4wMSIvPjwvc3ZnPg=="
        cross_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjRkZGRkZGIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiLz48bGluZSB4MT0iMTUiIHkxPSI5IiB4Mj0iOSIgeTI9IjE1Ii8+PGxpbmUgeDE9IjkiIHkxPSI5IiB4Mj0iMTUiIHkyPSIxNSIvPjwvc3ZnPg=="
        skip_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjRkZGRkZGIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlnb24gcG9pbnRzPSI1IDQgMTUgMTIgNSAyMCA1IDQiLz48bGluZSB4MT0iMTkiIHkxPSI1IiB4Mj0iMTkiIHkyPSIxOSIvPjwvc3ZnPg=="

        stats_items = [
            ("TOTAL", "100", "Videos", None, doc_svg, "IconTotal"),
            ("QUEUED", "99", "Videos", "#8B5CF6", clock_svg, "IconQueued"),
            ("GENERATING", "1", "In Progress", "#10B981", play_svg, "IconGenerating"),
            ("DONE", "0", "Completed", "#10B981", check_svg, "IconDone"),
            ("FAILED", "0", "Failed", "#EF4444", cross_svg, "IconFailed"),
            ("SKIPPED", "0", "Skipped", "#9CA3AF", skip_svg, "IconSkipped")
        ]
        
        for idx, (name, val, subtitle, color, icon_svg, icon_obj_name) in enumerate(stats_items):
            sub = QWidget()
            sub.setStyleSheet("background: transparent; border: none;")
            sub_lay = QHBoxLayout(sub)
            sub_lay.setContentsMargins(4, 4, 4, 4)
            sub_lay.setSpacing(10)
            
            # Left text container (3 lines: Title, Value, Subtitle)
            text_container = QWidget()
            text_container.setStyleSheet("background: transparent; border: none;")
            text_container_lay = QVBoxLayout(text_container)
            text_container_lay.setContentsMargins(0, 0, 0, 0)
            text_container_lay.setSpacing(1)
            
            lbl = QLabel(name)
            lbl.setObjectName("StatLbl")
            
            val_lbl = QLabel(val)
            val_lbl.setObjectName("StatVal")
            if color:
                val_lbl.setStyleSheet(f"color: {color};")
                
            sub_lbl = QLabel(subtitle)
            sub_lbl.setObjectName("StatSub")
            
            text_container_lay.addWidget(lbl)
            text_container_lay.addWidget(val_lbl)
            text_container_lay.addWidget(sub_lbl)
            
            # Right circular vector icon badge
            if name == "GENERATING":
                icon_badge = GeneratingIconWidget(icon_svg)
                icon_badge.setObjectName(icon_obj_name)
                self.generating_icon_widget = icon_badge
            else:
                icon_badge = QLabel()
                icon_badge.setObjectName(icon_obj_name)
                icon_badge.setFixedSize(36, 36)
                icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Load vector outline SVG as QPixmap
                pix = QPixmap()
                pix.loadFromData(QByteArray.fromBase64(icon_svg.encode()))
                icon_badge.setPixmap(pix.scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            
            sub_lay.addWidget(text_container, 1)
            sub_lay.addWidget(icon_badge)
            
            stats_items_layout.addWidget(sub)
            self.stat_widgets[name] = val_lbl
            
            # Add small vertical line spacer divider between stat items
            if idx < len(stats_items) - 1:
                divider = QFrame()
                divider.setFrameShape(QFrame.Shape.VLine)
                divider.setStyleSheet("background-color: #1F2937; max-width: 1px; min-height: 40px; margin-left: 5px; margin-right: 5px; border: none;")
                stats_items_layout.addWidget(divider)
            
        stats_layout.addLayout(stats_items_layout, 1)
        
        # Add the sleek circular progress ring widget on the far right
        self.radial_progress = RadialProgressWidget()
        self.radial_progress.set_value(0, 100)
        stats_layout.addWidget(self.radial_progress)
        
        # Hidden progress components for backward compatibility with update threads
        self.progress_pct = QLabel("0/10 done (0%)", self)
        self.progress_pct.setVisible(False)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        stats_layout.addWidget(self.progress_pct)
        stats_layout.addWidget(self.progress_bar)

        workspace_layout.addWidget(stats_card)



        # 2-Column Grid Area
        cols_grid = QHBoxLayout()
        cols_grid.setSpacing(20)

        # LEFT COLUMN (Settings & Queue Table)
        left_col = QVBoxLayout()
        left_col.setSpacing(8)

        # Generation Settings Header (outside box)
        settings_hdr_widget = QWidget()
        settings_hdr_widget.setStyleSheet("background: transparent; border: none;")
        settings_hdr_outer = QVBoxLayout(settings_hdr_widget)
        settings_hdr_outer.setContentsMargins(6, 0, 6, 0)
        settings_hdr_outer.setSpacing(0)
        
        settings_hdr = QLabel("GENERATION SETTINGS")
        settings_hdr.setObjectName("PanelTitle")
        settings_hdr_outer.addWidget(settings_hdr)

        # Generation Settings Box
        settings_card = QFrame()
        settings_card.setObjectName("SettingsCard")
        settings_card.setMinimumHeight(280)
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(14, 16, 14, 16)
        settings_layout.setSpacing(8)

        form_grid = QGridLayout()
        form_grid.setSpacing(10)
        form_grid.setColumnStretch(0, 1)
        form_grid.setColumnStretch(1, 2)
        form_grid.setColumnStretch(2, 1)
        form_grid.setColumnStretch(3, 2)

        lbl_model = QLabel("Model:")
        lbl_model.setObjectName("FormInputLabel")
        self.cb_model = QComboBox()
        self.cb_model.setObjectName("cb_model")
        self.cb_model.addItems(["Seedance 2.0"])
        self.cb_model.setEnabled(True)
        self.cb_model.setCurrentIndex(0)

        lbl_dur = QLabel("Length:")
        lbl_dur.setObjectName("FormInputLabel")
        self.cb_dur = QComboBox()
        self.cb_dur.addItems(["15s", "10s", "5s"])
        self.cb_dur.setEnabled(True)
        self.cb_dur.setCurrentIndex(0)

        lbl_ratio = QLabel("Ratio:")
        lbl_ratio.setObjectName("FormInputLabel")
        self.cb_ratio = QComboBox()
        self.cb_ratio.addItems([
            "9:16", "16:9", "1:1", "4:3", 
            "3:4", "2:3", "3:2", "21:9"
        ])
        self.cb_ratio.setEnabled(True)
        self.cb_ratio.setCurrentIndex(0)

        # Batch Label with Info Icon
        lbl_batch_layout = QHBoxLayout()
        lbl_batch_layout.setSpacing(4)
        lbl_batch_layout.setContentsMargins(0, 0, 0, 0)
        lbl_batch = QLabel("Batch:")
        lbl_batch.setObjectName("FormInputLabel")
        lbl_batch_info = QLabel("ⓘ")
        lbl_batch_info.setStyleSheet("color: #C5A059; font-size: 10pt; font-weight: bold;")
        lbl_batch_info.setToolTip("<b>Batch Size:</b> Defines the maximum number of videos to generate in a single session. (Currently placeholder; runs all active prompts in the editor).")
        lbl_batch_layout.addWidget(lbl_batch)
        lbl_batch_layout.addWidget(lbl_batch_info)
        lbl_batch_layout.addStretch()
        lbl_batch_container = QWidget()
        lbl_batch_container.setLayout(lbl_batch_layout)

        self.inp_batch = QLineEdit("30")
        self.inp_batch.setEnabled(True)

        # Speed/Concurrent Threads Label with Info Icon
        lbl_speed_layout = QHBoxLayout()
        lbl_speed_layout.setSpacing(4)
        lbl_speed_layout.setContentsMargins(0, 0, 0, 0)
        lbl_speed = QLabel("Concurrent Threads:")
        lbl_speed.setObjectName("FormInputLabel")
        lbl_speed_info = QLabel("ⓘ")
        lbl_speed_info.setStyleSheet("color: #C5A059; font-size: 10pt; font-weight: bold;")
        lbl_speed_info.setToolTip("<b>Concurrent Threads:</b> The number of parallel browser windows running simultaneously. Higher threads speed up generation but require more CPU/RAM and stable proxies.")
        lbl_speed_layout.addWidget(lbl_speed)
        lbl_speed_layout.addWidget(lbl_speed_info)
        lbl_speed_layout.addStretch()
        lbl_speed_container = QWidget()
        lbl_speed_container.setLayout(lbl_speed_layout)

        self.inp_speed = QLineEdit("1")
        self.inp_speed.setEnabled(True)

        # Timeout Label with Info Icon
        lbl_timeout_layout = QHBoxLayout()
        lbl_timeout_layout.setSpacing(4)
        lbl_timeout_layout.setContentsMargins(0, 0, 0, 0)
        lbl_timeout = QLabel("Timeout (min):")
        lbl_timeout.setObjectName("FormInputLabel")
        lbl_timeout_info = QLabel("ⓘ")
        lbl_timeout_info.setStyleSheet("color: #C5A059; font-size: 10pt; font-weight: bold;")
        lbl_timeout_info.setToolTip("<b>Timeout (Minutes):</b> The maximum duration the tool will wait for the video rendering to finish on Dola before skipping. If the video is ready earlier, downloading triggers instantly.")
        lbl_timeout_layout.addWidget(lbl_timeout)
        lbl_timeout_layout.addWidget(lbl_timeout_info)
        lbl_timeout_layout.addStretch()
        lbl_timeout_container = QWidget()
        lbl_timeout_container.setLayout(lbl_timeout_layout)

        self.inp_timeout = QLineEdit("30")
        self.inp_timeout.setEnabled(True)

        self.cb_headless = QCheckBox("Run Headless / Hidden Browser")
        self.cb_headless.setChecked(True)

        # Row 0: Model & Length
        form_grid.addWidget(lbl_model, 0, 0)
        form_grid.addWidget(self.cb_model, 0, 1)
        form_grid.addWidget(lbl_dur, 0, 2)
        form_grid.addWidget(self.cb_dur, 0, 3)

        # Row 1: Ratio & Batch
        form_grid.addWidget(lbl_ratio, 1, 0)
        form_grid.addWidget(self.cb_ratio, 1, 1)
        form_grid.addWidget(lbl_batch_container, 1, 2)
        form_grid.addWidget(self.inp_batch, 1, 3)

        # Row 2: Concurrent Threads & Timeout (min)
        form_grid.addWidget(lbl_speed_container, 2, 0)
        form_grid.addWidget(self.inp_speed, 2, 1)
        form_grid.addWidget(lbl_timeout_container, 2, 2)
        form_grid.addWidget(self.inp_timeout, 2, 3)

        # Row 3: Headless Checkbox (spanning all columns)
        form_grid.addWidget(self.cb_headless, 3, 0, 1, 4)

        settings_layout.addLayout(form_grid)

        # Remove cb_vpn_mode — VPN mode is always Desktop App by default (no Chrome extension needed)
        self.cb_vpn_mode = QComboBox(self)  # kept as attribute for compatibility, hidden
        self.cb_vpn_mode.addItems(["Desktop App"])
        self.cb_vpn_mode.hide()

        # Proxy & SMS widgets — created here for backend compatibility, displayed on Dashboard
        self.lbl_proxy_count = QLabel("✓ 0 proxy(ies)", self)
        self.lbl_proxy_count.hide()
        self.txt_proxies = QTextEdit(self)
        self.txt_proxies.setPlaceholderText("Paste proxies here (1 per line)...")
        self.txt_proxies.textChanged.connect(self.update_proxy_count)
        self.txt_proxies.hide()
        self.btn_load_proxies = QPushButton("📁 Load Proxy File", self)
        self.btn_load_proxies.clicked.connect(self.load_proxy_file)
        self.btn_load_proxies.hide()
        
        self.btn_check_proxies = QPushButton("⚡ Check Proxies", self)
        self.btn_check_proxies.clicked.connect(self.check_proxies_clicked)
        self.btn_check_proxies.hide()
        self.lbl_sms_balance = QLabel("Balance: --", self)
        self.lbl_sms_balance.hide()
        self.inp_sms_key = QLineEdit(self)
        self.inp_sms_key.setPlaceholderText("Enter HeroSMS API Key...")
        self.inp_sms_key.hide()
        self.cb_sms_country = QComboBox(self)
        self.cb_sms_country.addItem("Load countries first...", "0")
        self.cb_sms_country.hide()
        self.btn_test_sms = QPushButton("💳 Test API / Balance", self)
        self.btn_test_sms.clicked.connect(self.test_herosms_balance)
        self.btn_test_sms.hide()

        self.btn_start = QPushButton("START GENERATION")
        self.btn_start.setObjectName("LaunchCTA")
        self.btn_start.setFixedWidth(200)
        self.btn_start.setFixedHeight(36)
        
        btn_start_lay = QHBoxLayout()
        btn_start_lay.addWidget(self.btn_start)
        btn_start_lay.addStretch()
        settings_layout.addLayout(btn_start_lay)
        
        # settings_card will be added to layout below at assembly time

        # Queue Table
        queue_card = QFrame()
        queue_card.setObjectName("PanelCard")
        queue_card.setMinimumHeight(220)
        queue_layout = QVBoxLayout(queue_card)
        queue_layout.setSpacing(8)
        
        # Title layout matching mockup
        queue_hdr_layout = QHBoxLayout()
        queue_hdr_layout.setContentsMargins(0, 0, 0, 0)
        queue_hdr_layout.setSpacing(8)
        
        queue_icon = QLabel("📊")
        queue_icon.setStyleSheet("font-size: 11pt; color: #FFFFFF;")
        
        queue_title = QLabel("Generation Queue")
        queue_title.setObjectName("PanelTitle")
        
        self.queue_count_badge = QLabel("0 Items")
        self.queue_count_badge.setObjectName("BadgeQueued")
        self.queue_count_badge.setStyleSheet("margin-left: 6px; font-size: 7.5pt;")
        
        queue_hdr_layout.addWidget(queue_icon)
        queue_hdr_layout.addWidget(queue_title)
        queue_hdr_layout.addWidget(self.queue_count_badge)
        queue_hdr_layout.addStretch()
        queue_layout.addLayout(queue_hdr_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["#", "Prompt (Preview)", "Status", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(1, 160)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 105) # Fixed 105px width for Status column to prevent badge text wrapping/clipping
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(40) # Compact row heights
        self.table.horizontalHeader().setFixedHeight(36)
        queue_layout.addWidget(self.table)

        # Queue Status Row (Estimated Time & API Status)
        queue_status_layout = QHBoxLayout()
        queue_status_layout.setContentsMargins(0, 5, 0, 0)
        queue_status_layout.setSpacing(10)
        
        self.lbl_control_est_time = QLabel("⏳ Estimated Time: --:--:--")
        self.lbl_control_est_time.setObjectName("FormInputLabel")
        self.lbl_control_est_time.setStyleSheet("color: #9CA3AF;")
        
        self.lbl_control_api_status = QLabel("🟢 API Status: Connected")
        self.lbl_control_api_status.setObjectName("FormInputLabel")
        self.lbl_control_api_status.setStyleSheet("color: #10B981; font-weight: bold;")
        
        queue_status_layout.addWidget(self.lbl_control_est_time)
        queue_status_layout.addStretch()
        queue_status_layout.addWidget(self.lbl_control_api_status)
        
        queue_layout.addLayout(queue_status_layout)

        # Queue Buttons Row (Start Queue, Pause, Clear Queue)
        queue_btn_layout = QHBoxLayout()
        queue_btn_layout.setContentsMargins(0, 5, 0, 0)
        queue_btn_layout.setSpacing(12)
        
        # Action Control Buttons
        self.btn_ctrl_start = QPushButton("▶ Start Queue")
        self.btn_ctrl_start.setObjectName("StartBtn")
        self.btn_ctrl_start.setFixedWidth(140)
        
        self.btn_ctrl_clear = QPushButton("🗑 Clear Queue")
        self.btn_ctrl_clear.setObjectName("ClearQueueBtn")
        self.btn_ctrl_clear.setFixedWidth(135)
        
        queue_btn_layout.addWidget(self.btn_ctrl_start)
        queue_btn_layout.addWidget(self.btn_ctrl_clear)
        queue_btn_layout.addStretch()
        
        queue_layout.addLayout(queue_btn_layout)
        
        # queue_card and left_col will be added to layout below at assembly time

        # RIGHT COLUMN (Prompts & Logs Terminal)
        right_col = QVBoxLayout()
        right_col.setSpacing(20)

        # Prompts Header (outside box)
        prompts_hdr_widget = QWidget()
        prompts_hdr_widget.setStyleSheet("background: transparent; border: none;")
        prompts_hdr_outer = QVBoxLayout(prompts_hdr_widget)
        prompts_hdr_outer.setContentsMargins(6, 0, 6, 0)
        prompts_hdr_outer.setSpacing(0)

        prompts_hdr_lay = QHBoxLayout()
        prompts_hdr = QLabel("PROMPTS")
        prompts_hdr.setObjectName("PanelTitle")
        self.prompts_count_badge = QLabel("0 PROMPTS")
        self.prompts_count_badge.setObjectName("BadgeQueued")
        
        prompts_hdr_lay.addWidget(prompts_hdr)
        prompts_hdr_lay.addWidget(self.prompts_count_badge)
        prompts_hdr_lay.addStretch()
        
        self.btn_txt = QPushButton("TXT")
        self.btn_txt.setObjectName("PromptActionButton")
        self.btn_csv = QPushButton("CSV")
        self.btn_csv.setObjectName("PromptActionButton")
        self.btn_clear = QPushButton("CLEAR")
        self.btn_clear.setObjectName("PromptActionButtonDanger")
        self.btn_txt.setEnabled(True)
        self.btn_csv.setEnabled(True)
        self.btn_clear.setEnabled(True)
        
        prompts_hdr_lay.addWidget(self.btn_txt)
        prompts_hdr_lay.addWidget(self.btn_csv)
        prompts_hdr_lay.addWidget(self.btn_clear)
        prompts_hdr_outer.addLayout(prompts_hdr_lay)

        # Prompts Box
        prompts_card = QFrame()
        prompts_card.setObjectName("PromptsCard")
        prompts_card.setMinimumHeight(200)
        prompts_layout = QVBoxLayout(prompts_card)
        prompts_layout.setContentsMargins(12, 12, 12, 12)
        prompts_layout.setSpacing(6)

        self.prompts_editor = QTextEdit()
        self.prompts_editor.setObjectName("PromptsEditor")
        self.prompts_editor.setEnabled(True)
        prompts_layout.addWidget(self.prompts_editor)
        
        prompts_note = QLabel("One prompt per line = one video. Import from .txt or .csv files using the buttons above.")
        prompts_note.setObjectName("ProfilePlan")
        prompts_layout.addWidget(prompts_note)

        
        # prompts_card will be added to layout below at assembly time

        # Live Console logs
        logs_card = QFrame()
        logs_card.setObjectName("PanelCard")
        logs_card.setMinimumHeight(200)
        logs_layout = QVBoxLayout(logs_card)
        logs_layout.setSpacing(6)

        logs_hdr_lay = QHBoxLayout()
        logs_hdr = QLabel("LIVE LOG CONSOLE")
        logs_hdr.setObjectName("PanelTitle")
        self.logs_sub = QLabel("STREAMING LIVE TELEMETRY")
        self.logs_sub.setObjectName("MenuLabel")
        
        logs_hdr_lay.addWidget(logs_hdr)
        logs_hdr_lay.addWidget(self.logs_sub)
        logs_hdr_lay.addStretch()

        self.console_search = QLineEdit()
        self.console_search.setObjectName("ConsoleSearchBox")
        self.console_search.setPlaceholderText("Search logs...")
        self.console_search.setFixedWidth(120)
        
        self.btn_copy_logs = QPushButton("📋")
        self.btn_copy_logs.setObjectName("ConsoleActionButton")
        self.btn_clear_logs = QPushButton("🗑️")
        self.btn_clear_logs.setObjectName("ConsoleActionButton")
        self.btn_download_logs = QPushButton("💾")
        self.btn_download_logs.setObjectName("ConsoleActionButton")

        logs_hdr_lay.addWidget(self.console_search)
        logs_hdr_lay.addWidget(self.btn_copy_logs)
        logs_hdr_lay.addWidget(self.btn_clear_logs)
        logs_hdr_lay.addWidget(self.btn_download_logs)
        logs_layout.addLayout(logs_hdr_lay)

        self.console = QTextEdit()
        self.console.setObjectName("ConsoleTerminal")
        self.console.setReadOnly(True)
        logs_layout.addWidget(self.console)

        # Assemble Left Column (Prompts & Settings)
        left_col.addWidget(prompts_hdr_widget)
        left_col.addWidget(prompts_card)
        left_col.addSpacing(18)
        left_col.addWidget(settings_hdr_widget)
        left_col.addWidget(settings_card)
        cols_grid.addLayout(left_col, 1)

        # Assemble Right Column (Queue Table only)
        right_col.addWidget(queue_card, 1)
        cols_grid.addLayout(right_col, 1)

        # Add columns grid to main workspace layout
        workspace_layout.addLayout(cols_grid)

        # Add logs console card to stretch full width at the bottom
        workspace_layout.addWidget(logs_card)

        self.scroll_area.setWidget(workspace)
        
        # Introduce stacked widget for main workspace area
        self.workspace_stack = QStackedWidget(self)
        
        # Instantiate pages so all actions/buttons are initialized safely
        self.dashboard_page = self.create_dashboard_page()
        self.image_scroll_area = self.create_image_generator_page()
        self.vault_page = self.create_session_vault_page()

        # ONLY add Video Generator and Session Vault to the visible stacked widget
        # Page 0: Video Generator
        self.workspace_stack.addWidget(self.scroll_area)
        # Page 1: Session Vault
        self.workspace_stack.addWidget(self.vault_page)
        
        # Default to page 0 (Video Generator)
        self.workspace_stack.setCurrentIndex(0)
        
        main_layout.addWidget(self.workspace_stack)

    def connect_actions(self):
        self.btn_start.clicked.connect(self.toggle_generation)
        self.btn_change_folder.clicked.connect(self.change_folder)
        self.btn_open_folder.clicked.connect(self.open_folder)
        
        self.btn_refresh.clicked.connect(self.check_updates_clicked)
        self.btn_support.clicked.connect(self.support_clicked)
        self.btn_bell.clicked.connect(self.bell_clicked)
        self.btn_client_mode.clicked.connect(self.toggle_client_mode)
        self.btn_client_mode.setVisible(not self.is_client_build)  # Hide toggle button in client builds
        self.btn_restart.clicked.connect(self.restart_tool)
        self.btn_restart.setVisible(not self.client_mode)  # Hidden in client mode
        self.btn_copy_logs.clicked.connect(self.copy_logs)
        self.btn_clear_logs.clicked.connect(self.clear_logs)
        self.btn_download_logs.clicked.connect(self.download_logs)
        self.console_search.textChanged.connect(self.filter_logs)
        
        self.btn_txt.clicked.connect(self.import_txt)
        self.btn_csv.clicked.connect(self.import_csv)
        self.btn_clear.clicked.connect(self.clear_prompts)
        self.prompts_editor.textChanged.connect(self.update_prompts_count)
        

        # Connect horizontal control bar buttons
        self.btn_ctrl_start.clicked.connect(self.toggle_queue_processing)
        self.btn_ctrl_clear.clicked.connect(self.clear_prompts)
        
        # Connect sidebar menu changes
        self.sidebar_menu.currentRowChanged.connect(self.on_sidebar_row_changed)
        
        # Connect Dola Image Generator page actions
        self.btn_img_start.clicked.connect(self.toggle_image_generation)
        self.btn_img_change_folder.clicked.connect(self.change_img_folder)
        self.btn_img_copy_logs.clicked.connect(self.copy_img_logs)
        self.btn_img_clear_logs.clicked.connect(self.clear_img_logs)
        self.btn_img_download_logs.clicked.connect(self.download_img_logs)
        self.img_console_search.textChanged.connect(self.filter_img_logs)
        
        self.btn_img_txt.clicked.connect(self.import_img_txt)
        self.btn_img_csv.clicked.connect(self.import_img_csv)
        self.btn_img_clear.clicked.connect(self.clear_img_prompts)
        self.img_prompts_editor.textChanged.connect(self.update_img_prompts_count)
        
        self.btn_img_ctrl_start.clicked.connect(self.control_img_start_clicked)
        self.btn_img_ctrl_pause.clicked.connect(self.control_img_pause_clicked)
        self.btn_img_ctrl_clear.clicked.connect(self.clear_img_prompts)

    def restart_tool(self):
        reply = QMessageBox.question(self, "Restart AKIRA",
            "Are you sure you want to restart AKIRA?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            import os
            import sys
            # Clean exit and restart python process
            python = sys.executable
            os.execl(python, python, *sys.argv)

    def toggle_client_mode(self):
        self.client_mode = not self.client_mode
        self.btn_client_mode.setText("👤" if self.client_mode else "🛠️")
        
        # Save choice back to config file
        try:
            import json
            if getattr(sys, 'frozen', False):
                config_dir = os.path.dirname(sys.executable)
            else:
                config_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(config_dir, "license_config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    cfg = json.load(f)
                cfg["client_mode"] = self.client_mode
                with open(config_path, "w") as f:
                    json.dump(cfg, f, indent=4)
        except Exception:
            pass
            
        # Hide restart button in client mode
        self.btn_restart.setVisible(not self.client_mode)
        
        mode_str = "Client Mode (Clean)" if self.client_mode else "Developer Mode (Verbose)"
        self.log("SYSTEM", f"Switched to {mode_str}. Log display layout updated.")

    def toggle_queue_processing(self):
        if not self.is_generating or self.is_queue_paused:
            self.control_start_clicked()
        else:
            self.control_pause_clicked()

    def control_start_clicked(self):
        if self.is_queue_paused:
            self.is_queue_paused = False
            self.log("SYSTEM", "Resuming queue processing...")
            self.btn_ctrl_start.setText("⏸ Pause Queue")
            
            # Determine maximum concurrency level
            try:
                text = clean_val(self.inp_speed.text()).strip().lower()
                if not text or not text.isdigit():
                    max_concurrency = 1
                else:
                    max_concurrency = max(1, int(text))
            except Exception:
                max_concurrency = 1

            # Start multiple workers to fill empty slots
            empty_slots = max_concurrency - len(self.workers)
            for _ in range(max(1, empty_slots)):
                self.run_next_automated_item()
        elif not self.is_generating:
            self.btn_ctrl_start.setText("⏸ Pause Queue")
            self.toggle_generation()

    def control_pause_clicked(self):
        if self.is_generating:
            self.is_queue_paused = True
            self.btn_ctrl_start.setText("▶ Start Queue")
            self.log("SYSTEM", "Queue processing paused. Active automation will finish. Remaining queue is suspended.")
        else:
            self.log("WARNING", "Generation is not active. Cannot pause.")

    def on_sidebar_row_changed(self, row):
        # Update selection state of custom SidebarTabWidgets
        for r in range(self.sidebar_menu.count()):
            widget = self.sidebar_menu.itemWidget(self.sidebar_menu.item(r))
            if isinstance(widget, SidebarTabWidget):
                widget.set_active(r == row)
                
        # Switch pages in QStackedWidget
        if row == 0:
            self.workspace_stack.setCurrentIndex(0) # Video Generator
        elif row == 1:
            self.workspace_stack.setCurrentIndex(1) # Session Vault

    def initialize_empty_state(self):
        self.action_text_cache = {}

        self.console.clear()
        self.log_counter = 0
        self.log("SYSTEM", f"AKIRA v{AKIRA_APP_VERSION} initialized successfully.")
        self.log("SYSTEM", "Ready for video generation pipeline.")
        
        self.prompts_editor.clear()
        self.prompts_count_badge.setText("0 PROMPTS")
        self.table.setRowCount(0)
        self.queue_count_badge.setText("0 Items")
        self.radial_progress.set_value(0, 100)
        
        # Reset stats labels to zero
        self.stat_widgets["TOTAL"].setText("0")
        self.stat_widgets["QUEUED"].setText("0")
        self.stat_widgets["GENERATING"].setText("0")
        self.stat_widgets["DONE"].setText("0")
        self.stat_widgets["FAILED"].setText("0")
        self.stat_widgets["SKIPPED"].setText("0")

    def create_action_buttons(self, row_num):
        widget = QWidget()
        lay = QHBoxLayout(widget)
        lay.setContentsMargins(4, 2, 4, 2)
        lay.setSpacing(6)
        
        btn_view = QPushButton("👁", widget)
        btn_view.setFixedSize(28, 28)
        btn_view.setObjectName("QueueActionViewBtn")
        btn_view.clicked.connect(lambda: self.log("INFO", f"Row {row_num}: Video preview active/requested."))
        
        btn_del = QPushButton("🗑", widget)
        btn_del.setFixedSize(28, 28)
        btn_del.setObjectName("QueueActionDelBtn")
        btn_del.clicked.connect(lambda: self.log("WARNING", f"Row {row_num}: Removed from queue."))
        
        lay.addWidget(btn_view)
        lay.addWidget(btn_del)
        return widget

    # ==========================================
    # LOG CONTROLS
    # ==========================================
    def log(self, type_str, message):
        # Apply filtering in Client Mode
        if self.client_mode:
            # Clean up any Dola references or redirect links to protect engine identity
            if " Redirected to: " in message and ("dola.com" in message or "dola" in message.lower()):
                message = message.split(" Redirected to: ")[0]
            message = message.replace("dola.com", "akira.ai").replace("Dola", "AKIRA").replace("dola", "akira")
            
            # 1. Discard watermark coordinates completely
            if "Watermark detected at:" in message:
                return
            
            # 2. Silently drop the 15-second rendering updates and loop diagnostics
            if "Still rendering video (elapsed:" in message or "Still waiting for video generation..." in message:
                return
                
            # Extract row prefix if any (e.g. "Row 1: ")
            row_prefix = ""
            if ":" in message:
                parts = message.split(":")
                if "Row" in parts[0]:
                    row_prefix = f"{parts[0]}: "
            
            # 3. Filter INFO logs
            if type_str == "INFO":
                is_important = False
                if "Removing watermark..." in message:
                    is_important = True
                    message = f"{row_prefix}Removing watermark..."
                elif "Downloading video..." in message or "Downloaded and cleaned" in message:
                    is_important = True
                    message = f"{row_prefix}Downloading video..."
                elif "Spawning automated Google Chrome" in message or "Starting browser engine..." in message:
                    is_important = True
                    message = f"{row_prefix}Starting browser engine..."
                elif "Selecting ratio" in message:
                    is_important = True
                    ratio_val = message.split("Selecting ratio")[-1].strip().replace("on Dola...", "").strip()
                    message = f"{row_prefix}Setting ratio to {ratio_val}..."
                elif "Entering visual prompt" in message:
                    is_important = True
                    prompt_val = message.split("Entering visual prompt:")[-1].strip()
                    if len(prompt_val) > 40:
                        prompt_val = prompt_val[:40] + "..."
                    message = f"{row_prefix}Submitting prompt: {prompt_val}"
                elif "Selected Account" in message:
                    is_important = True
                    acc_val = message.split("Selected Account")[-1].strip().split()[0]
                    message = f"{row_prefix}Using account: {acc_val}"
                
                if not is_important:
                    return

            # 4. Filter SUCCESS logs
            elif type_str == "SUCCESS":
                is_important = False
                if "CONFIRMED:" in message:
                    is_important = True
                    import re
                    start_idx = message.find("Got it, I'm generating")
                    if start_idx != -1:
                        clean_msg = message[start_idx:]
                        match = re.search(r"ready in (\d+-\d+ minutes|\d+-\d+ mins|\d+ minute|\d+ minutes)", clean_msg)
                        if match:
                            est_time = match.group(1)
                            message = f"{row_prefix}CONFIRMED: Generating video... Estimated time: {est_time}."
                        else:
                            message = f"{row_prefix}CONFIRMED: Generating video..."
                    else:
                        message = f"{row_prefix}CONFIRMED: Generating video..."
                elif "Video ready + src found" in message or "'Your video is ready' detected" in message:
                    is_important = True
                    message = f"{row_prefix}SUCCESS: Video generated successfully."
                elif "Video saved to" in message or "Video is ready for download. Output saved to" in message:
                    is_important = True
                    saved_path = message.split("saved to")[-1].strip() if "saved to" in message else message.split("Output saved to")[-1].strip()
                    message = f"{row_prefix}SUCCESS: Saved video to {os.path.basename(saved_path)}"
                elif "All prompts in generation queue processed" in message:
                    is_important = True
                
                if not is_important:
                    return

            # 5. Filter WARNING logs
            elif type_str == "WARNING":
                is_important = False
                if "Content policy violation" in message or "warning" in message.lower() or "aborted" in message.lower() or "Removed from queue" in message:
                    is_important = True
                
                if not is_important:
                    return

            # 6. Filter SYSTEM logs
            elif type_str == "SYSTEM":
                is_important = False
                if "initialized" in message.lower() or "starting" in message.lower() or "paused" in message.lower() or "resuming" in message.lower() or "aborted" in message.lower() or "update" in message.lower():
                    is_important = True
                
                if not is_important:
                    return

        self.log_counter += 1
        padded_cnt = str(self.log_counter).zfill(3)
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if self.client_mode:
            # Using Hex colors instead of RGBA because Qt's QTextEdit HTML engine does not support RGBA or inline span borders.
            # Table-based layout is used for perfect vertical alignment and border rendering.
            bg_color = "#0B1528"     # Dark blue
            text_color = "#60A5FA"   # Light blue
            border_color = "#1D2D44" # Muted blue border
            msg_color = "#D1D5DB"    # Light grey
            
            if type_str == "SUCCESS":
                bg_color = "#0D251C"
                text_color = "#10B981"
                border_color = "#1B4D3E"
                msg_color = "#10B981"
            elif type_str == "ERROR":
                bg_color = "#2E151B"
                text_color = "#F87171"
                border_color = "#5D2B34"
                msg_color = "#F87171"
            elif type_str == "WARNING":
                bg_color = "#2D200E"
                text_color = "#F59E0B"
                border_color = "#5B441D"
                msg_color = "#F59E0B"
            elif type_str == "SYSTEM":
                bg_color = "#1A1333"
                text_color = "#A78BFA"
                border_color = "#3C2E66"
                msg_color = "#A78BFA"
                
            log_line = f"""
            <table width='100%' cellpadding='4' cellspacing='0' style='margin-top: 3px; margin-bottom: 3px;'>
              <tr>
                <td width='35' style='color: #4E5A70; font-family: monospace; font-size: 9.5pt;'>{padded_cnt}</td>
                <td width='90' style='color: #4E5A70; font-size: 9.5pt;'>[{current_time}]</td>
                <td width='95'>
                  <table cellpadding='2' cellspacing='0' style='background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 4px;'>
                    <tr>
                      <td align='center' style='color: {text_color}; font-weight: bold; font-size: 8.5pt; font-family: sans-serif; padding-left: 6px; padding-right: 6px;'>{type_str}</td>
                    </tr>
                  </table>
                </td>
                <td style='color: {msg_color}; font-size: 10.5pt; padding-left: 6px;'>{message}</td>
              </tr>
            </table>
            """
        else:
            # Keep original simple text design for developer mode
            color = "#60A5FA" # blue
            if type_str == "SUCCESS": color = "#34D399" # green
            elif type_str == "ERROR": color = "#F87171" # red
            elif type_str == "WARNING": color = "#FACC15" # yellow
            elif type_str == "SYSTEM": color = "#A78BFA" # purple
            
            log_line = f"<font color='#4E5A70'>{padded_cnt}</font> [{current_time}] <font color='{color}'><b>{type_str}</b></font> {message}"
            
        self.console.append(log_line)
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())

    def add_notification(self, type_str, text):
        current_time = datetime.now().strftime("%H:%M")
        self.notifications.append({
            "type": type_str,
            "text": text,
            "time": current_time
        })
        self.unread_notifications_count += 1
        # Update badge on the bell icon button
        self.btn_bell.setText(f"🔔 ({self.unread_notifications_count})")
        
    def check_updates_clicked(self):
        self.log("SYSTEM", "Checking for software updates...")
        web_url = CONFIG_DATA.get("web_app_url", "")
        if not web_url or "PASTE_YOUR_DEPLOYED" in web_url:
            QMessageBox.warning(self, "Update Check", "Update URL not configured.")
            return
            
        self.update_worker = UpdateCheckWorker(web_url)
        self.update_worker.finished_signal.connect(self.on_update_check_finished)
        self.update_worker.start()
        
    def on_update_check_finished(self, res):
        if res.get("status") == "error":
            self.log("WARNING", f"Failed to check for updates: {res.get('message')}")
            QMessageBox.warning(self, "Update Check", "Unable to connect to update server. Please check your internet connection.")
            return
            
        latest = res.get("latest_version", "1.0.0")
        current = "1.0.0" # Current app version
        download_url = res.get("download_url", "https://wa.me/923477399073")
        
        if latest > current:
            self.log("SYSTEM", f"New update available! (Latest: v{latest}, Current: v{current})")
            reply = QMessageBox.question(
                self, 
                "Update Available", 
                f"A new version v{latest} is available! (Current: v{current})\n\n"
                "Would you like to open the download page now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl(download_url))
        else:
            self.log("SYSTEM", f"AKIRA is up to date (v{current}).")
            QMessageBox.information(self, "Up to Date", f"AKIRA is up to date! (v{current})")
            
    def support_clicked(self):
        self.log("SYSTEM", "Fetching announcements from admin...")
        web_url = CONFIG_DATA.get("web_app_url", "")
        if not web_url or "PASTE_YOUR_DEPLOYED" in web_url:
            # Fallback to direct support url
            self.log("INFO", "Opening Admin support chat...")
            QDesktopServices.openUrl(QUrl(CONFIG_DATA.get("admin_contact_url")))
            return
            
        self.announce_worker = AnnouncementWorker(web_url)
        self.announce_worker.finished_signal.connect(self.on_announcements_finished)
        self.announce_worker.start()
        
    def on_announcements_finished(self, res):
        if res.get("status") == "error" or not res.get("message"):
            self.log("INFO", "Opening Admin support chat...")
            QDesktopServices.openUrl(QUrl(CONFIG_DATA.get("admin_contact_url")))
            return
            
        title = res.get("title", "Admin Announcement")
        msg = res.get("message", "No new announcements.")
        date_str = res.get("date", "")
        
        dialog_text = f"<h3>📢 {title}</h3>"
        if date_str:
            dialog_text += f"<p style='color: #6B7280; font-size: 8.5pt;'>Date: {date_str}</p>"
        dialog_text += f"<p style='font-size: 10pt; line-height: 1.4;'>{msg}</p>"
        
        box = QMessageBox(self)
        box.setWindowTitle("Admin Notification")
        box.setTextFormat(Qt.TextFormat.RichText)
        box.setText(dialog_text)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        btn_chat = box.addButton("💬 Chat Support", QMessageBox.ButtonRole.ActionRole)
        
        box.exec()
        
        if box.clickedButton() == btn_chat:
            QDesktopServices.openUrl(QUrl(CONFIG_DATA.get("admin_contact_url")))
            
    def bell_clicked(self):
        # Reset badge
        self.btn_bell.setText("🔔")
        self.unread_notifications_count = 0
        
        if not self.notifications:
            QMessageBox.information(self, "Notifications", "No notifications yet.")
            return
            
        html = "<h3>🔔 Live Notification Center</h3><hr>"
        for n in reversed(self.notifications): # newest first
            color = "#D1D5DB"
            icon = "ℹ️"
            if n["type"] == "success":
                color = "#10B981"
                icon = "✨"
            elif n["type"] == "error":
                color = "#EF4444"
                icon = "❌"
            elif n["type"] == "warning":
                color = "#F59E0B"
                icon = "⚠️"
            html += f"<p style='font-size: 9.5pt;'><font color='{color}'>{icon} {n['time']}: {n['text']}</font></p>"
            
        box = QMessageBox(self)
        box.setWindowTitle("Notification Center")
        box.setTextFormat(Qt.TextFormat.RichText)
        box.setText(html)
        box.setStandardButtons(QMessageBox.StandardButton.Close)
        btn_clear = box.addButton("🗑️ Clear All", QMessageBox.ButtonRole.ActionRole)
        
        box.exec()
        
        if box.clickedButton() == btn_clear:
            self.notifications = []
            self.log("SYSTEM", "Notification Center cleared.")

    def prepopulate_mock_logs(self):
        self.console.clear()
        self.log_counter = 800
        # Matching exact logs from screenshot
        self.log("SYSTEM", "Initializing background video generation. Token Semaphore activated...")
        self.log("INFO", "Started 10 generation(s) using Premium Video Engine, parallel=50.")
        self.log("INFO", "Row 1: Verifying security execution token...")

    def copy_logs(self):
        self.console.selectAll()
        self.console.copy()
        cursor = self.console.textCursor()
        cursor.clearSelection()
        self.console.setTextCursor(cursor)
        self.log("SUCCESS", "Logs copied to clipboard.")

    def Skinner(self):
        pass

    def clear_logs(self):
        self.console.clear()
        self.log("SYSTEM", "Logs cleared.")

    def download_logs(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Logs", "", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.console.toPlainText())
            self.log("SUCCESS", f"Logs successfully saved to {path}")

    def filter_logs(self, query):
        # Basic filter logic for QTextEdit content
        query = query.lower()
        if not query:
            self.prepopulate_mock_logs()
            return
        lines = self.console.toPlainText().split('\n')
        self.console.clear()
        for l in lines:
            if query in l.lower():
                self.console.append(l)

    # ==========================================
    # PROMPT LOADER CONTROLS
    # ==========================================
    def import_txt(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Prompts (TXT)", "", "Text Files (*.txt)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.prompts_editor.setText(content)
                self.log("SUCCESS", f"Imported prompts from {os.path.basename(path)}")
            except Exception as e:
                self.log("ERROR", f"Failed to import TXT: {str(e)}")

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Prompts (CSV)", "", "CSV Files (*.csv)")
        if path:
            try:
                import csv
                import io
                cleaned = []
                with open(path, "r", encoding="utf-8", newline="") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if not row or not any(row):
                            continue
                        out = io.StringIO()
                        writer = csv.writer(out)
                        writer.writerow(row)
                        line_str = out.getvalue().strip()
                        if line_str:
                            cleaned.append(line_str)
                self.prompts_editor.setText("\n".join(cleaned))
                self.log("SUCCESS", f"Imported prompts from {os.path.basename(path)}")
            except Exception as e:
                self.log("ERROR", f"Failed to import CSV: {str(e)}")

    def update_proxy_count(self):
        text = self.txt_proxies.toPlainText().strip()
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        self.lbl_proxy_count.setText(f"✓ {len(lines)} proxy(ies)")
        
        # Autosave proxies to proxies.txt
        path = self._vault_proxies_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            self.vault_reload_proxies_silent()
        except:
            pass

    def update_img_proxy_count(self):
        text = self.txt_img_proxies.toPlainText().strip()
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        self.lbl_img_proxy_count.setText(f"✓ {len(lines)} proxy(ies)")

    def load_proxy_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Proxy File", "", "Text Files (*.txt)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.txt_proxies.setText(content)
                self.log("SUCCESS", f"Loaded proxies from {os.path.basename(path)}")
            except Exception as e:
                self.log("ERROR", f"Failed to load proxies: {str(e)}")

    def check_proxies_clicked(self):
        text = self.txt_proxies.toPlainText().strip()
        raw_list = [l.strip() for l in text.split("\n") if l.strip()]
        if not raw_list:
            QMessageBox.warning(self, "Proxy Checker", "Please add some proxies to test first.")
            return
            
        self.btn_check_proxies.setText("⚡ Testing...")
        self.btn_check_proxies.setEnabled(False)
        
        self.proxy_check_worker = ProxyCheckWorker(raw_list)
        self.proxy_check_worker.finished_signal.connect(self.on_proxy_check_finished)
        self.proxy_check_worker.progress_signal.connect(lambda msg: self.log("INFO", msg))
        self.proxy_check_worker.start()
        
    def on_proxy_check_finished(self, live, dead):
        self.btn_check_proxies.setText("⚡ Check Proxies")
        self.btn_check_proxies.setEnabled(True)
        
        self.log("SUCCESS", f"Proxy check finished! Live: {len(live)}, Dead/Expired: {len(dead)}")
        
        if not live:
            QMessageBox.critical(self, "Proxy Checker Result", "All tested proxies are DEAD/expired.")
            return
            
        reply = QMessageBox.question(
            self, 
            "Filter Proxies", 
            f"Proxy Check Results:\n\n"
            f"✓ Live: {len(live)}\n"
            f"✗ Dead: {len(dead)}\n\n"
            f"Would you like to remove dead proxies and keep only the live ones in the list?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.txt_proxies.blockSignals(True)
            self.txt_proxies.setPlainText("\n".join(live))
            self.txt_proxies.blockSignals(False)
            self.update_proxy_count()

    def check_vault_proxies_clicked(self):
        text = self.vault_proxy_input.toPlainText().strip()
        raw_list = [l.strip() for l in text.split("\n") if l.strip()]
        if not raw_list:
            QMessageBox.warning(self, "Proxy Checker", "Please add some proxies to test first.")
            return
            
        self.btn_vault_proxy_check.setText("⚡ Testing...")
        self.btn_vault_proxy_check.setEnabled(False)
        
        self.vault_proxy_check_worker = ProxyCheckWorker(raw_list)
        self.vault_proxy_check_worker.finished_signal.connect(self.on_vault_proxy_check_finished)
        self.vault_proxy_check_worker.progress_signal.connect(lambda msg: self.log("INFO", msg))
        self.vault_proxy_check_worker.start()
        
    def on_vault_proxy_check_finished(self, live, dead):
        self.btn_vault_proxy_check.setText("⚡ Check Proxies")
        self.btn_vault_proxy_check.setEnabled(True)
        
        self.log("SUCCESS", f"Vault proxy check finished! Live: {len(live)}, Dead/Expired: {len(dead)}")
        
        if not live:
            QMessageBox.critical(self, "Proxy Checker Result", "All tested proxies are DEAD/expired.")
            return
            
        reply = QMessageBox.question(
            self, 
            "Filter Proxies", 
            f"Proxy Check Results:\n\n"
            f"✓ Live: {len(live)}\n"
            f"✗ Dead: {len(dead)}\n\n"
            f"Would you like to remove dead proxies and keep only the live ones in the list?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.vault_proxy_input.blockSignals(True)
            self.vault_proxy_input.setPlainText("\n".join(live))
            self.vault_proxy_input.blockSignals(False)
            self.vault_save_proxies()

    def load_img_proxy_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Proxy File", "", "Text Files (*.txt)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.txt_img_proxies.setText(content)
                self.img_log("SUCCESS", f"Loaded proxies from {os.path.basename(path)}")
            except Exception as e:
                self.img_log("ERROR", f"Failed to load proxies: {str(e)}")

    def test_herosms_balance(self):
        key = self.inp_sms_key.text().strip()
        if not key:
            self.log("ERROR", "Please enter your HeroSMS API Key first.")
            return
        
        import requests
        try:
            url = f"https://hero-sms.com/stubs/handler_api.php?api_key={key}&action=getBalance"
            res = requests.get(url, timeout=8)
            text = res.text.strip()
            if text.startswith("ACCESS_BALANCE:"):
                bal = text.split(":")[1]
                try:
                    bal_val = float(bal)
                    self.lbl_sms_balance.setText(f"Balance: ${bal_val:.2f}")
                    self.log("SUCCESS", f"HeroSMS Connected. Balance: ${bal_val:.2f}")
                except:
                    self.lbl_sms_balance.setText(f"Balance: {bal}")
                    self.log("SUCCESS", f"HeroSMS Connected. Balance: {bal}")
                
                # Fetch prices for service 'ot' (Other)
                self.log("INFO", "Fetching country prices and availability...")
                prices_url = f"https://hero-sms.com/stubs/handler_api.php?api_key={key}&action=getPrices&service=ot"
                p_res = requests.get(prices_url, timeout=10)
                try:
                    prices_data = p_res.json()
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
                        34: ("Azerbaijan", "+994"), 35: ("UK (Virtual)", "+44"), 36: ("Canada", "+1"), 
                        37: ("Morocco", "+212"), 38: ("Ghana", "+233"), 39: ("Argentina", "+54"), 
                        40: ("Uzbekistan", "+998"), 41: ("Cameroon", "+237"), 42: ("Chad", "+235"), 
                        43: ("Germany", "+49"), 44: ("Lithuania", "+370"), 45: ("Croatia", "+385"), 
                        46: ("Sweden", "+46"), 47: ("Iraq", "+964"), 48: ("Netherlands", "+31"), 
                        49: ("Latvia", "+371"), 50: ("Austria", "+43"), 51: ("Belarus", "+375"), 
                        52: ("Thailand", "+66"), 53: ("Saudi Arabia", "+966"), 54: ("Mexico", "+52"), 
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
                        99: ("Mauritius", "+230"),
                        108: ("Bosnia", "+387"),
                        128: ("Georgia", "+995"),
                        173: ("Switzerland", "+41"),
                        196: ("Singapore", "+65"),
                        199: ("Malta", "+356")
                    }
                    
                    country_list = []
                    for c_id, services in prices_data.items():
                        if "ot" in services:
                            cost = services["ot"].get("cost")
                            count = services["ot"].get("count")
                            if cost is not None and count is not None and count > 0:
                                c_id_int = int(c_id)
                                
                                cost_usd = float(cost)
                                    
                                if c_id_int in sms_countries_map:
                                    c_name, c_code = sms_countries_map[c_id_int]
                                    display_str = f"{c_name} ({c_code}) - ${cost_usd:.2f}"
                                else:
                                    display_str = f"Country {c_id} - ${cost_usd:.2f}"
                                    
                                country_list.append({
                                    "id": c_id,
                                    "cost": cost_usd,
                                    "display": display_str
                                })
                    
                    # Sort by cost ascending so cheapest is first
                    country_list.sort(key=lambda x: x["cost"])
                    
                    self.cb_sms_country.clear()
                    for c in country_list:
                        self.cb_sms_country.addItem(c["display"], c["id"])
                    
                    if country_list:
                        self.cb_sms_country.setCurrentIndex(0)
                        self.log("SUCCESS", f"Loaded {len(country_list)} active countries from HeroSMS sorted by price. Cheapest option auto-selected.")
                    else:
                        self.cb_sms_country.addItem("No countries with stock", "0")
                        self.log("WARNING", "No active countries with available numbers found for service 'ot'.")
                except Exception as parse_err:
                    self.log("ERROR", f"Failed to parse prices JSON: {str(parse_err)}")
            else:
                self.log("ERROR", f"HeroSMS API returned: {text}")
        except Exception as e:
            self.log("ERROR", f"Failed to connect to HeroSMS: {str(e)}")

    def get_active_proxies(self, is_image=False):
        txt_box = self.txt_img_proxies if is_image else self.txt_proxies
        text = txt_box.toPlainText().strip()
        if not text:
            return []
        
        proxies = []
        for line in text.split("\n"):
            line = line.strip()
            if line:
                parsed = parse_proxy_string(line)
                if parsed:
                    proxies.append(parsed)
        return proxies

    def clear_prompts(self):
        self.prompts_editor.clear()
        self.table.setRowCount(0)
        self.prompts_count_badge.setText("0 PROMPTS")
        self.queue_count_badge.setText("0 Items")
        self.stat_widgets["TOTAL"].setText("0")
        self.stat_widgets["QUEUED"].setText("0")
        self.stat_widgets["GENERATING"].setText("0")
        self.stat_widgets["DONE"].setText("0")
        self.stat_widgets["FAILED"].setText("0")
        self.stat_widgets["SKIPPED"].setText("0")
        self.log("SYSTEM", "Prompts workspace and generation queue cleared.")

    def update_prompts_count(self):
        text = self.prompts_editor.toPlainText().strip()
        if not text:
            count = 0
        else:
            count = len([l for l in text.split('\n') if l.strip()])
        self.prompts_count_badge.setText(f"{count} PROMPTS")

    # ==========================================
    # FOLDER SELECTORS
    # ==========================================
    def change_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if folder:
            self.output_dir = folder
            self.output_path_input.setText(folder)
            self.log("SYSTEM", f"Video output location updated: {folder}")

    def open_folder(self):
        if os.path.exists(self.output_dir):
            os.startfile(self.output_dir)
        else:
            self.log("WARNING", f"Output folder {self.output_dir} does not exist.")

    # ==========================================
    # DATA GRID TABLE VIEW PRESETS
    # ==========================================
    def prepopulate_mock_table(self):
        # Load screenshot prompts
        prompts = [
            "Parent POV, raw iPhone 17 Pro Max back camera, pediatric clinic Dallas...",
            "Father POV, raw iPhone 17 Pro Max back camera, vertical 9:16...",
            "Mother POV, raw iPhone 17 Pro Max back camera, vertical 9:16...",
            "Parent POV, raw iPhone 17 Pro Max back camera, vertical 9:16...",
            "Father POV, raw iPhone 17 Pro Max back camera, vertical 9:16...",
            "Mother POV, raw iPhone 17 Pro Max back camera, vertical 9:16...",
            "Parent POV, raw iPhone 17 Pro Max back camera, vertical 9:16...",
            "Father POV, raw iPhone 17 Pro Max back camera, vertical 9:16...",
            "Mother POV, raw iPhone 17 Pro Max back camera, vertical 9:16...",
            "Parent POV, raw iPhone 17 Pro Max back camera, vertical 9:16..."
        ]
        
        self.prompts_editor.setText("\n".join(prompts))
        self.table.setRowCount(len(prompts))
        self.queue_count_badge.setText(f"{len(prompts)} Items")
        
        # Populate rows
        for idx, pr in enumerate(prompts):
            # Row index
            self.table.setItem(idx, 0, QTableWidgetItem(str(idx + 1)))
            # Prompt
            self.table.setItem(idx, 1, QTableWidgetItem(pr))
            # Status Badge (generating/submitting)
            badge = QLabel(self)
            if idx == 0:
                badge.setText("GENERATING")
                badge.setObjectName("BadgeGenerating")
            else:
                badge.setText("SUBMITTING")
                badge.setObjectName("BadgeSubmitting")
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(idx, 2, badge)
            
            # Action string
            action = "Requesting Video..." if idx == 0 else f"Staggering ({(idx*3.3):.1f}s)..."
            self.table.setItem(idx, 3, QTableWidgetItem(action))
            


        # Update Stats Cards
        self.stat_widgets["TOTAL"].setText("10")
        self.stat_widgets["QUEUED"].setText("10")
        self.stat_widgets["GENERATING"].setText("0")
        self.stat_widgets["DONE"].setText("0")
        self.stat_widgets["FAILED"].setText("0")
        self.stat_widgets["SKIPPED"].setText("0")

        self.progress_pct.setText("0/10 done (0%)")
        self.progress_bar.setValue(0)
        self.radial_progress.set_value(0, 10)

    # ==========================================
    # RUN TIMERS & AUTOMATION CONTROL
    # ==========================================
    def toggle_generation(self):
        if self.is_generating:
            # Stop Mock or Real generations
            self.is_generating = False
            self.is_queue_paused = False
            self.recalculate_stats()
            self.mock_timer.stop()
            
            # Gracefully abort active workers
            for rid, worker in list(self.workers.items()):
                if hasattr(worker, "bot") and worker.bot:
                    worker.bot.is_stopped = True
                self.log("WARNING", f"Gracefully aborting worker thread for Row {rid}...")

            self.btn_start.setText("START GENERATION")
            self.btn_start.setObjectName("LaunchCTA")
            self.btn_start.setStyleSheet("") # Clear custom color settings to apply CTA gradients
            self.btn_start.parentWidget().setStyleSheet(UI_MASTER_QSS) # Reapply
            self.btn_ctrl_start.setText("▶ Start Queue")
            
            # Unlock inputs
            self.cb_model.setEnabled(True)
            self.cb_dur.setEnabled(True)
            self.cb_ratio.setEnabled(True)
            self.inp_batch.setEnabled(True)
            self.inp_speed.setEnabled(True)
            self.inp_timeout.setEnabled(True)
            self.cb_headless.setEnabled(True)
            self.prompts_editor.setEnabled(True)
            self.btn_txt.setEnabled(True)
            self.btn_csv.setEnabled(True)
            self.btn_clear.setEnabled(True)
            
            self.log("SYSTEM", "All active video generation threads aborted.")
            self.dash_end_session()
        else:
            try:
                import sys, traceback as _tb

                # Capture ALL unhandled Qt/Python exceptions to crash_log.txt
                def _crash_hook(exc_type, exc_val, exc_tb):
                    msg = "".join(_tb.format_exception(exc_type, exc_val, exc_tb))
                    print("UNHANDLED EXCEPTION:\n" + msg)
                    try:
                        with open("crash_log.txt", "a", encoding="utf-8") as _f:
                            _f.write("\n=== UNHANDLED EXCEPTION ===\n" + msg)
                    except: pass
                sys.excepthook = _crash_hook

                # START active automation using Playwright!
                prompts_text = self.prompts_editor.toPlainText().strip()
                if not prompts_text:
                    self.log("ERROR", "No prompts available for video generation.")
                    return

                self.is_generating = True
                
                # Lock inputs
                self.cb_model.setEnabled(False)
                self.cb_dur.setEnabled(False)
                self.cb_ratio.setEnabled(False)
                self.inp_batch.setEnabled(False)
                self.inp_speed.setEnabled(False)
                self.inp_timeout.setEnabled(False)
                self.cb_headless.setEnabled(False)
                self.prompts_editor.setEnabled(False)
                self.btn_txt.setEnabled(False)
                self.btn_csv.setEnabled(False)
                self.btn_clear.setEnabled(False)

                self.btn_start.setText("STOP GENERATION")
                self.btn_start.setObjectName("StopCTA")
                self.btn_start.parentWidget().setStyleSheet(UI_MASTER_QSS)
                self.btn_ctrl_start.setText("⏸ Pause Queue")

                # Split prompts
                lines = [l.strip() for l in prompts_text.split('\n') if l.strip()]
                self.table.setRowCount(len(lines))
                self.queue_count_badge.setText(f"{len(lines)} Items")

                # Initialize stats
                self.stat_widgets["TOTAL"].setText(str(len(lines)))
                self.stat_widgets["QUEUED"].setText(str(len(lines)))
                self.stat_widgets["GENERATING"].setText("0")
                self.generating_icon_widget.set_active(False)
                self.stat_widgets["DONE"].setText("0")
                self.stat_widgets["FAILED"].setText("0")
                
                self.queue_data = []
                self.action_text_cache = {}
                
                for idx, prompt in enumerate(lines):
                    self.queue_data.append({"id": idx + 1, "prompt": prompt, "status": "QUEUED"})
                    self.action_text_cache[idx + 1] = "Waiting in queue..."
                
                # Populates and reorders table immediately using the unified renderer
                self.reorder_table_rows()

                self.log("SYSTEM", f"Starting Playwright controller. Processing {len(lines)} video(s)...")
                self.dash_start_session("Video")

                # Check if user holds Shift or toggles settings for setup mode
                # For automation start: check login setup mode
                setup_mode = False
                if "setup" in self.inp_speed.text().lower():
                    setup_mode = True
                    self.log("WARNING", "Running in manual Google Account Login Mode...")

                # Launch parallel Playwright threads up to the specified concurrency level
                try:
                    text = clean_val(self.inp_speed.text()).strip().lower()
                    if not text or not text.isdigit():
                        max_concurrency = 1
                    else:
                        max_concurrency = max(1, int(text))
                except Exception:
                    max_concurrency = 1

                self.log("INFO", f"Launching {max_concurrency} concurrent browser thread(s)...")
                for _ in range(max_concurrency):
                    self.run_next_automated_item(setup_mode)
            except Exception as e:
                import traceback
                print("CRASH IN START GENERATION:")
                traceback.print_exc()
                try:
                    with open("crash_log.txt", "a", encoding="utf-8") as f:
                        f.write("\n=== CRASH IN TOGGLE_GENERATION ===\n")
                        traceback.print_exc(file=f)
                except:
                    pass
                self.log("ERROR", f"Critical crash on start: {str(e)}")
                self.is_generating = False
                # Re-enable inputs on crash
                self.cb_model.setEnabled(True)
                self.cb_dur.setEnabled(True)
                self.cb_ratio.setEnabled(True)
                self.inp_batch.setEnabled(True)
                self.inp_speed.setEnabled(True)
                self.inp_timeout.setEnabled(True)
                self.cb_headless.setEnabled(True)
                self.prompts_editor.setEnabled(True)
                self.btn_txt.setEnabled(True)
                self.btn_csv.setEnabled(True)
                self.btn_clear.setEnabled(True)
                self.btn_start.setText("START GENERATION")
                self.btn_start.setObjectName("LaunchCTA")
                self.btn_start.parentWidget().setStyleSheet(UI_MASTER_QSS)

    def run_next_automated_item(self, setup_mode=False):
        try:
            if not self.is_generating or self.is_queue_paused:
                return
                
            # Look for next queued item
            queued = [item for item in self.queue_data if item["status"] == "QUEUED"]
            if not queued:
                if not self.workers:
                    self.log("SUCCESS", "All prompts in generation queue processed.")
                    self.toggle_generation() # Stop and reset inputs
                return

            next_item = queued[0]
            row_id = next_item["id"]
            next_item["status"] = "SUBMITTING"
            
            # Get parsed proxies list
            proxy_list = self.get_active_proxies(is_image=False)

            # Instantiate Playwright browser automation
            bot = DolaAutomationBot(
                output_dir=self.output_dir,
                callback_log=None,
                callback_status=None,
                client_mode=self.client_mode
            )
            bot.headless = self.cb_headless.isChecked()
            bot.optimize_prompts = True
            bot.use_extension_vpn = False  # VPN mode always desktop/no extension

            # Get HeroSMS details
            sms_key = self.inp_sms_key.text().strip()
            sms_country = self.cb_sms_country.currentData() or "0"

            # Get timeout
            try:
                timeout_val = int(self.inp_timeout.text().strip())
            except ValueError:
                timeout_val = 30

            worker = PlaywrightWorker(
                bot=bot,
                row_id=row_id,
                prompt=next_item["prompt"],
                model=clean_val(self.cb_model.currentText()),
                duration=clean_val(self.cb_dur.currentText()),
                ratio=clean_val(self.cb_ratio.currentText()),
                setup_mode=setup_mode,
                is_image=False,
                proxy_list=proxy_list,
                sms_key=sms_key,
                sms_country=sms_country,
                timeout_min=timeout_val
            )

            # Wire callbacks
            worker.log_signal.connect(self.log)
            worker.status_signal.connect(self.on_worker_status_update)
            worker.finished_signal.connect(self.on_worker_finished)

            self.workers[row_id] = worker
            worker.start()

            # Update stats
            self.recalculate_stats()
        except Exception as e:
            import traceback
            print("CRASH IN RUN_NEXT_AUTOMATED_ITEM:")
            traceback.print_exc()
            try:
                with open("crash_log.txt", "a", encoding="utf-8") as f:
                    f.write("\n=== CRASH IN RUN_NEXT_AUTOMATED_ITEM ===\n")
                    traceback.print_exc(file=f)
            except:
                pass
            self.log("ERROR", f"Failed to start automation worker: {str(e)}")
            if 'next_item' in locals():
                next_item["status"] = "FAILED"
            self.recalculate_stats()
            self.reorder_table_rows()

    def find_row_index_by_id(self, row_id):
        target_str = str(row_id)
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 0)
            if item and item.text() == target_str:
                return r
        return row_id - 1

    def reorder_table_rows(self):
        try:
            self.table.setSortingEnabled(False)
            
            # Sort self.queue_data:
            # 0: Active statuses (SUBMITTING, GENERATING, DOWNLOADING)
            # 1: QUEUED
            # 2: Completed statuses (DONE, FAILED, SKIPPED)
            def get_priority(status):
                if status in ["SUBMITTING", "GENERATING", "DOWNLOADING"]:
                    return 0
                elif status == "QUEUED":
                    return 1
                return 2

            sorted_queue = sorted(self.queue_data, key=lambda x: (get_priority(x["status"]), x["id"]))

            # Clear all cell widgets to ensure no leftover widgets interfere
            self.table.clearContents()
            self.table.setRowCount(len(sorted_queue))

            from PyQt6.QtGui import QBrush, QColor, QFont

            for r, item in enumerate(sorted_queue):
                row_id = item["id"]
                status = item["status"]
                prompt = item["prompt"]

                # Column 0: ID
                self.table.setItem(r, 0, QTableWidgetItem(str(row_id)))
                # Column 1: Prompt
                self.table.setItem(r, 1, QTableWidgetItem(prompt))

                # Column 2: Status (QTableWidgetItem)
                status_item = QTableWidgetItem(status)
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Apply Font and Colors based on Status
                font = QFont()
                font.setBold(True)
                status_item.setFont(font)
                
                if status == "SUBMITTING":
                    status_item.setForeground(QBrush(QColor("#F59E0B"))) # Orange
                elif status == "GENERATING":
                    status_item.setForeground(QBrush(QColor("#10B981"))) # Green
                elif status == "DOWNLOADING":
                    status_item.setForeground(QBrush(QColor("#3B82F6"))) # Blue
                elif status == "QUEUED":
                    status_item.setForeground(QBrush(QColor("#A78BFA"))) # Purple
                    font.setBold(False)
                    status_item.setFont(font)
                elif status == "DONE":
                    status_item.setForeground(QBrush(QColor("#10B981"))) # Green
                elif status == "FAILED":
                    status_item.setForeground(QBrush(QColor("#EF4444"))) # Red
                elif status == "SKIPPED":
                    status_item.setForeground(QBrush(QColor("#9CA3AF"))) # Gray
                    font.setBold(False)
                    status_item.setFont(font)
                
                self.table.setItem(r, 2, status_item)

                # Column 3: Action (QTableWidgetItem)
                action_text = self.action_text_cache.get(row_id, "Waiting in queue..." if status == "QUEUED" else "")
                action_item = QTableWidgetItem(action_text)
                
                if status in ["SUBMITTING", "GENERATING", "DOWNLOADING"]:
                    action_item.setForeground(QBrush(QColor("#FFFFFF")))
                elif "success" in action_text.lower() or status == "DONE":
                    action_item.setForeground(QBrush(QColor("#10B981")))
                elif "error" in action_text.lower() or "failed" in action_text.lower() or status == "FAILED":
                    action_item.setForeground(QBrush(QColor("#EF4444")))
                else:
                    action_item.setForeground(QBrush(QColor("#9CA3AF")))
                
                self.table.setItem(r, 3, action_item)

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print(f"CRASH IN REORDER_TABLE_ROWS:\n{tb}")
            self.log("ERROR", f"Reordering failed: {str(e)}")
            try:
                with open("crash_log.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n=== CRASH IN REORDER_TABLE_ROWS ===\n{tb}\n")
            except:
                pass

    def on_worker_status_update(self, row_id, status, action):
        # Find item and update status
        for item in self.queue_data:
            if item["id"] == row_id:
                item["status"] = status
                break
        
        self.action_text_cache[row_id] = action
        self.recalculate_stats()
        self.reorder_table_rows()

    def on_worker_finished(self, row_id, success):
        worker = self.workers.get(row_id)
        error_reason = getattr(worker, "error_reason", None) if worker else None

        if not success and error_reason in ["HIGH_DEMAND", "REGION_RESTRICTED"]:
            reason_lbl = "High Demand" if error_reason == "HIGH_DEMAND" else "Region Restricted"
            self.log("WARNING", f"Row {row_id}: AI Engine {reason_lbl.lower()} detected. Current session aborted. Retrying in a new browser window...")
            
            # Reset this item's status back to QUEUED
            for item in self.queue_data:
                if item["id"] == row_id:
                    item["status"] = "QUEUED"
                    break
            
            # Update cache action text
            self.action_text_cache[row_id] = f"Retrying in queue ({reason_lbl} fallback)..."
            
            # Remove worker reference
            if row_id in self.workers:
                del self.workers[row_id]
            
            self.recalculate_stats()
            self.reorder_table_rows()
            
            # Schedule retry launch after a 5-second cooldown
            QTimer.singleShot(5000, lambda: self.run_next_automated_item())
            return

        # Update state status
        for item in self.queue_data:
            if item["id"] == row_id:
                if error_reason == "POLICY_VIOLATION":
                    item["status"] = "SKIPPED"
                    self.action_text_cache[row_id] = "Policy violation (Skipped)"
                    self.add_notification("warning", f"Row {row_id}: Prompt skipped (Policy/Copyright Violation).")
                else:
                    item["status"] = "DONE" if success else "FAILED"
                    self.action_text_cache[row_id] = "Success" if success else "Failed"
                    if success:
                        self.add_notification("success", f"Row {row_id}: Video downloaded successfully!")
                    else:
                        self.add_notification("error", f"Row {row_id}: Generation failed.")
                break

        # Remove worker reference
        if row_id in self.workers:
            del self.workers[row_id]

        self.dash_record_result(success, error_reason)

        # Refresh Session Vault stats & tables
        try:
            self.vault_reload_accounts()
        except:
            pass

        self.recalculate_stats()
        self.reorder_table_rows()
        
        # Start next item in queue
        self.run_next_automated_item()

    def recalculate_stats(self):
        generating_count = 0
        is_actively_generating = False
        if self.queue_data:
            generating_count = len([i for i in self.queue_data if i["status"] in ["GENERATING", "DOWNLOADING"]])
            is_actively_generating = generating_count > 0
            
        generating_val = str(generating_count)
        self.stat_widgets["GENERATING"].setText(generating_val)
        self.generating_icon_widget.set_active(is_actively_generating)

        if not self.queue_data:
            self.stat_widgets["TOTAL"].setText("0")
            self.stat_widgets["QUEUED"].setText("0")
            self.stat_widgets["DONE"].setText("0")
            self.stat_widgets["FAILED"].setText("0")
            self.stat_widgets["SKIPPED"].setText("0")
            return
            
        total = len(self.queue_data)
        queued = len([i for i in self.queue_data if i["status"] == "QUEUED"])
        done = len([i for i in self.queue_data if i["status"] == "DONE"])
        failed = len([i for i in self.queue_data if i["status"] == "FAILED"])
        skipped = len([i for i in self.queue_data if i["status"] == "SKIPPED"])

        self.stat_widgets["TOTAL"].setText(str(total))
        self.stat_widgets["QUEUED"].setText(str(queued))
        self.stat_widgets["DONE"].setText(str(done))
        self.stat_widgets["FAILED"].setText(str(failed))
        self.stat_widgets["SKIPPED"].setText(str(skipped))

        pct = int(((done + failed + skipped) / total) * 100) if total > 0 else 0
        self.progress_pct.setText(f"{done + failed + skipped}/{total} done ({pct}%)")
        self.progress_bar.setValue(pct)
        self.radial_progress.set_value(done + failed + skipped, total)

    # ==========================================
    # SIMULATED MOCKUP RUNNING STEPS
    # ==========================================
    def run_mock_step(self):
        """Simulates step ticks for the screenshot mockup on startup."""
        if not self.is_generating or self.workers:
            return

        # Randomly complete row 2 or log details
        step = random.randint(1, 3)
        if step == 1:
            self.log("INFO", "Row 1: Frame compilation 78% finished...")
            self.table.setItem(0, 3, QTableWidgetItem("Rendering segments (78%)..."))
        elif step == 2:
            self.log("INFO", "Row 3: Directing generation parameters. Semaphore check active.")
            self.table.setItem(2, 3, QTableWidgetItem("Processing (attempt 14/250)..."))
        elif step == 3:
            # Change row 2 to Success
            self.log("SUCCESS", "Row 2: Video is ready for download. Output saved to E:\\Seedance Videos\\seedance_2.mp4")
            
            badge = QLabel("SUCCESS", self)
            badge.setObjectName("BadgeSuccess")
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(1, 2, badge)
            self.table.setItem(1, 3, QTableWidgetItem("Video successfully generated and downloaded."))
            
            # Shift a queued item to generating
            self.stat_widgets["QUEUED"].setText("3")
            self.stat_widgets["GENERATING"].setText("6")
            self.stat_widgets["DONE"].setText("2")
            self.progress_pct.setText("2/10 done (20%)")
            self.progress_bar.setValue(20)
            self.radial_progress.set_value(2, 10)
            
            # Change row 8 to generating
            badge8 = QLabel("GENERATING", self)
            badge8.setObjectName("BadgeGenerating")
            badge8.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(7, 2, badge8)
            self.table.setItem(7, 3, QTableWidgetItem("Processing..."))
            
            # Stop timer so it remains static at success state
            self.mock_timer.stop()

    # =========================================================================
    # SESSION VAULT PAGE — Accounts & Proxies Manager
    # =========================================================================
    def create_session_vault_page(self):
        import json, os

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        page = QWidget()
        page.setObjectName("MainWorkspace")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(18)

        # ── Header ──────────────────────────────────────────────────────────
        hdr_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        hdr_title = QLabel("Session Vault")
        hdr_title.setObjectName("MainHeaderTitle")
        hdr_sub = QLabel("Manage Dola account cookies and proxy IPs for multi-account rotation.")
        hdr_sub.setObjectName("MainHeaderSubtitle")
        title_box.addWidget(hdr_title)
        title_box.addWidget(hdr_sub)
        title_box.setSpacing(2)
        hdr_layout.addLayout(title_box)
        hdr_layout.addStretch()
        layout.addLayout(hdr_layout)

        # ── Stats Ribbon ─────────────────────────────────────────────────────
        stats_frame = QFrame()
        stats_frame.setObjectName("StatsRibbon")
        stats_frame.setStyleSheet("""
            QFrame#StatsRibbon {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0F2027, stop:0.5 #203A43, stop:1 #2C5364);
                border-radius: 12px;
                border: 1px solid #1E3A4A;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(20, 14, 20, 14)
        stats_layout.setSpacing(0)

        def make_stat_card(value_label_name, title, color):
            card = QVBoxLayout()
            lbl_val = QLabel("0")
            lbl_val.setObjectName(value_label_name)
            lbl_val.setStyleSheet(f"font-size: 22pt; font-weight: bold; color: {color}; background: transparent; border: none;")
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_title = QLabel(title)
            lbl_title.setStyleSheet("font-size: 8pt; color: #9CA3AF; background: transparent; border: none; letter-spacing: 1px;")
            lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card.addWidget(lbl_val)
            card.addWidget(lbl_title)
            card.setSpacing(2)
            return card, lbl_val

        divider_style = "background: #1E3A4A; max-width: 1px; min-width: 1px; margin: 10px 0;"

        c1, self.vault_lbl_total = make_stat_card("VaultStat", "TOTAL ACCOUNTS", "#10B981")
        c2, self.vault_lbl_active = make_stat_card("VaultStat", "ACTIVE", "#3B82F6")
        c3, self.vault_lbl_expired = make_stat_card("VaultStat", "EXPIRED / FAILED", "#EF4444")
        c4, self.vault_lbl_proxies = make_stat_card("VaultStat", "PROXIES", "#F59E0B")
        c5, self.vault_lbl_daily = make_stat_card("VaultStat", "VIDEOS TODAY", "#8B5CF6")

        for i, card in enumerate([c1, c2, c3, c4, c5]):
            stats_layout.addLayout(card)
            if i < 4:
                sep = QFrame()
                sep.setFrameShape(QFrame.Shape.VLine)
                sep.setStyleSheet(divider_style)
                stats_layout.addWidget(sep)

        layout.addWidget(stats_frame)

        # ── Two Column Layout ─────────────────────────────────────────────────
        two_col = QHBoxLayout()
        two_col.setSpacing(16)

        # ══ LEFT: ACCOUNTS PANEL ═════════════════════════════════════════════
        acc_card = QFrame()
        acc_card.setObjectName("PromptsCard")
        acc_layout = QVBoxLayout(acc_card)
        acc_layout.setContentsMargins(16, 14, 16, 14)
        acc_layout.setSpacing(10)

        # Title row
        acc_hdr = QHBoxLayout()
        acc_title = QLabel("🔐  ACCOUNT SESSIONS")
        acc_title.setObjectName("PanelTitle")
        self.vault_acc_count_badge = QLabel("0 Accounts")
        self.vault_acc_count_badge.setObjectName("BadgeQueued")
        acc_hdr.addWidget(acc_title)
        acc_hdr.addStretch()
        acc_hdr.addWidget(self.vault_acc_count_badge)
        acc_layout.addLayout(acc_hdr)

        # Account Table
        self.vault_acc_table = QTableWidget()
        self.vault_acc_table.setColumnCount(5)
        self.vault_acc_table.setHorizontalHeaderLabels(["#", "Account File", "Session ID", "Uses Today", "Status"])
        self.vault_acc_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.vault_acc_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.vault_acc_table.setColumnWidth(0, 40)
        self.vault_acc_table.setColumnWidth(3, 90)
        self.vault_acc_table.setColumnWidth(4, 90)
        self.vault_acc_table.verticalHeader().setVisible(False)
        self.vault_acc_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.vault_acc_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.vault_acc_table.setStyleSheet("""
            QTableWidget { background: #111827; border: 1px solid #1D263B; border-radius: 8px; gridline-color: #1F2937; color: #E5E7EB; font-size: 9pt; }
            QTableWidget::item { padding: 5px; border: none; }
            QTableWidget::item:selected { background: #1E3A4A; color: #10B981; }
        """)
        self.vault_acc_table.setMinimumHeight(240)
        acc_layout.addWidget(self.vault_acc_table)

        # Paste Area
        paste_label = QLabel("Paste JSON Cookie String below and click  ＋ Add Account:")
        paste_label.setStyleSheet("font-size: 8.5pt; color: #9CA3AF; background: transparent; border: none;")
        acc_layout.addWidget(paste_label)

        self.vault_cookie_paste = QTextEdit()
        self.vault_cookie_paste.setObjectName("PromptsEditor")
        self.vault_cookie_paste.setPlaceholderText('Paste exported JSON cookies here (e.g. from EditThisCookie extension) ...\n\n[{"name":"sessionid","value":"...","domain":".dola.com",...}]')
        self.vault_cookie_paste.setMaximumHeight(110)
        acc_layout.addWidget(self.vault_cookie_paste)

        # Buttons row
        acc_btn_row = QHBoxLayout()
        acc_btn_row.setSpacing(8)

        self.btn_vault_add = QPushButton("  ＋  Add Account")
        self.btn_vault_add.setObjectName("LaunchCTA")
        self.btn_vault_add.setFixedHeight(36)

        self.btn_vault_import_folder = QPushButton("  📂  Import Folder")
        self.btn_vault_import_folder.setObjectName("PromptActionButton")
        self.btn_vault_import_folder.setFixedHeight(36)

        self.btn_vault_check_accounts = QPushButton("  ⚡  Check Sessions")
        self.btn_vault_check_accounts.setObjectName("PromptActionButton")
        self.btn_vault_check_accounts.setFixedHeight(36)

        self.btn_vault_remove = QPushButton("  🗑  Remove Selected")
        self.btn_vault_remove.setObjectName("PromptActionButtonDanger")
        self.btn_vault_remove.setFixedHeight(36)

        self.btn_vault_clear_all = QPushButton("  ✕  Clear All")
        self.btn_vault_clear_all.setObjectName("PromptActionButtonDanger")
        self.btn_vault_clear_all.setFixedHeight(36)

        self.btn_vault_reload = QPushButton("  ↻  Reload")
        self.btn_vault_reload.setObjectName("PromptActionButton")
        self.btn_vault_reload.setFixedHeight(36)

        acc_btn_row.addWidget(self.btn_vault_add)
        acc_btn_row.addWidget(self.btn_vault_import_folder)
        acc_btn_row.addWidget(self.btn_vault_check_accounts)
        acc_btn_row.addWidget(self.btn_vault_remove)
        acc_btn_row.addWidget(self.btn_vault_clear_all)
        acc_btn_row.addWidget(self.btn_vault_reload)
        acc_layout.addLayout(acc_btn_row)

        hint = QLabel("💡  Export cookies from browser using EditThisCookie → Export as JSON → paste above → Add Account.")
        hint.setStyleSheet("font-size: 8pt; color: #6B7280; background: transparent; border: none;")
        hint.setWordWrap(True)
        acc_layout.addWidget(hint)

        two_col.addWidget(acc_card, 3)

        # ══ RIGHT: PROXY PANEL ════════════════════════════════════════════════
        proxy_card = QFrame()
        proxy_card.setObjectName("PromptsCard")
        proxy_layout = QVBoxLayout(proxy_card)
        proxy_layout.setContentsMargins(16, 14, 16, 14)
        proxy_layout.setSpacing(10)

        # Title row
        proxy_hdr = QHBoxLayout()
        proxy_title = QLabel("🌐  PROXY LIST  (IP Rotation)")
        proxy_title.setObjectName("PanelTitle")
        self.vault_proxy_count_badge = QLabel("0 Proxies")
        self.vault_proxy_count_badge.setObjectName("BadgeQueued")
        proxy_hdr.addWidget(proxy_title)
        proxy_hdr.addStretch()
        proxy_hdr.addWidget(self.vault_proxy_count_badge)
        proxy_layout.addLayout(proxy_hdr)

        # Proxy Table
        self.vault_proxy_table = QTableWidget()
        self.vault_proxy_table.setColumnCount(3)
        self.vault_proxy_table.setHorizontalHeaderLabels(["#", "Proxy Address", "Status"])
        self.vault_proxy_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.vault_proxy_table.setColumnWidth(0, 40)
        self.vault_proxy_table.setColumnWidth(2, 80)
        self.vault_proxy_table.verticalHeader().setVisible(False)
        self.vault_proxy_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.vault_proxy_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.vault_proxy_table.setStyleSheet("""
            QTableWidget { background: #111827; border: 1px solid #1D263B; border-radius: 8px; gridline-color: #1F2937; color: #E5E7EB; font-size: 9pt; }
            QTableWidget::item { padding: 5px; border: none; }
            QTableWidget::item:selected { background: #1E3A4A; color: #F59E0B; }
        """)
        self.vault_proxy_table.setMinimumHeight(180)
        proxy_layout.addWidget(self.vault_proxy_table)

        proxy_input_label = QLabel("Paste proxies below (1 per line)  —  format:  IP:Port  or  IP:Port:User:Pass")
        proxy_input_label.setStyleSheet("font-size: 8.5pt; color: #9CA3AF; background: transparent; border: none;")
        proxy_layout.addWidget(proxy_input_label)

        self.vault_proxy_input = QTextEdit()
        self.vault_proxy_input.setObjectName("PromptsEditor")
        self.vault_proxy_input.setPlaceholderText("192.168.1.1:8080\n192.168.1.2:8080:user:pass\nuser:pass@192.168.1.3:8080\n...")
        self.vault_proxy_input.setMaximumHeight(120)
        proxy_layout.addWidget(self.vault_proxy_input)

        # Proxy Buttons
        proxy_btn_row = QHBoxLayout()
        proxy_btn_row.setSpacing(8)

        self.btn_vault_proxy_save = QPushButton("  💾  Save Proxies")
        self.btn_vault_proxy_save.setObjectName("LaunchCTA")
        self.btn_vault_proxy_save.setFixedHeight(36)

        self.btn_vault_proxy_load = QPushButton("  📂  Load from File")
        self.btn_vault_proxy_load.setObjectName("PromptActionButton")
        self.btn_vault_proxy_load.setFixedHeight(36)

        self.btn_vault_proxy_check = QPushButton("  ⚡  Check Proxies")
        self.btn_vault_proxy_check.setObjectName("PromptActionButton")
        self.btn_vault_proxy_check.setFixedHeight(36)

        self.btn_vault_proxy_clear = QPushButton("  ✕  Clear")
        self.btn_vault_proxy_clear.setObjectName("PromptActionButtonDanger")
        self.btn_vault_proxy_clear.setFixedHeight(36)

        proxy_btn_row.addWidget(self.btn_vault_proxy_save)
        proxy_btn_row.addWidget(self.btn_vault_proxy_load)
        proxy_btn_row.addWidget(self.btn_vault_proxy_check)
        proxy_btn_row.addWidget(self.btn_vault_proxy_clear)
        proxy_layout.addLayout(proxy_btn_row)

        # Usage limit setting
        limit_row = QHBoxLayout()
        limit_lbl = QLabel("Max videos per account per 24h:")
        limit_lbl.setStyleSheet("font-size: 9pt; color: #9CA3AF; background: transparent; border: none;")
        self.vault_daily_limit = QLineEdit("3")
        self.vault_daily_limit.setObjectName("SettingsInput")
        self.vault_daily_limit.setFixedWidth(60)
        self.vault_daily_limit.setFixedHeight(32)
        self.vault_daily_limit.setStyleSheet("background: #0F1923; color: #10B981; border: 1px solid #1E3A4A; border-radius: 6px; padding: 4px 8px; font-size: 10pt; font-weight: bold;")
        limit_row.addWidget(limit_lbl)
        limit_row.addWidget(self.vault_daily_limit)
        limit_row.addStretch()

        self.btn_vault_save_settings = QPushButton("  ✓  Apply Settings")
        self.btn_vault_save_settings.setObjectName("PromptActionButton")
        self.btn_vault_save_settings.setFixedHeight(32)
        limit_row.addWidget(self.btn_vault_save_settings)
        proxy_layout.addLayout(limit_row)

        proxy_layout.addStretch()
        two_col.addWidget(proxy_card, 2)

        layout.addLayout(two_col)

        # ── SESSION HISTORY SECTION (Moved from Dashboard) ──
        sess_hdr_lay = QHBoxLayout()
        sess_hdr = QLabel("📋  SESSION HISTORY")
        sess_hdr.setStyleSheet("font-family: 'Outfit', 'Inter', sans-serif; font-size: 10pt; font-weight: bold; color: #FFFFFF; letter-spacing: 1.5px; padding-top: 15px;")
        self.dash_session_count_badge = QLabel("0 sessions")
        self.dash_session_count_badge.setStyleSheet("font-size: 8pt; color: #6B7280; font-weight: bold; padding-top: 17px;")
        sess_hdr_lay.addWidget(sess_hdr)
        sess_hdr_lay.addStretch()
        sess_hdr_lay.addWidget(self.dash_session_count_badge)
        layout.addLayout(sess_hdr_lay)

        self.dash_session_table = QTableWidget(0, 7)
        self.dash_session_table.setHorizontalHeaderLabels(["Date / Time", "Type", "Prompts", "✅ Success", "❌ Failed", "Duration", "Rate"])
        self.dash_session_table.horizontalHeader().setStretchLastSection(True)
        self.dash_session_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.dash_session_table.verticalHeader().setVisible(False)
        self.dash_session_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.dash_session_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.dash_session_table.setMinimumHeight(220)
        self.dash_session_table.setMaximumHeight(350)
        self.dash_session_table.setStyleSheet("""
            QTableWidget {
                background-color: #0C0D14;
                border: 1px solid #161722;
                border-radius: 8px;
                gridline-color: #161722;
                font-size: 9pt;
                color: #D1D5DB;
            }
            QTableWidget::item {
                padding: 6px 10px;
            }
        """)
        layout.addWidget(self.dash_session_table)

        layout.addStretch()

        scroll.setWidget(page)

        # Connect vault actions
        self.btn_vault_add.clicked.connect(self.vault_add_account)
        self.btn_vault_import_folder.clicked.connect(self.vault_import_folder)
        self.btn_vault_check_accounts.clicked.connect(self.vault_check_accounts_clicked)
        self.btn_vault_remove.clicked.connect(self.vault_remove_selected)
        self.btn_vault_clear_all.clicked.connect(self.vault_clear_all)
        self.btn_vault_reload.clicked.connect(self.vault_reload_accounts)
        self.btn_vault_proxy_save.clicked.connect(self.vault_save_proxies)
        self.btn_vault_proxy_load.clicked.connect(self.vault_load_proxies_file)
        self.btn_vault_proxy_check.clicked.connect(self.check_vault_proxies_clicked)
        self.btn_vault_proxy_clear.clicked.connect(lambda: self.vault_proxy_input.clear())
        self.btn_vault_save_settings.clicked.connect(self.vault_save_settings)

        # Load existing data on startup
        QTimer.singleShot(500, self.vault_reload_accounts)
        QTimer.singleShot(500, self.vault_reload_proxies)

        return scroll

    # ── Session Vault Backend Methods ─────────────────────────────────────────

    def _vault_cookies_dir(self):
        base = os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, 'frozen', False) else os.path.dirname(sys.executable)
        d = os.path.join(base, "cookies")
        os.makedirs(d, exist_ok=True)
        return d

    def _vault_usage_path(self):
        return os.path.join(self._vault_cookies_dir(), "_usage.json")

    def _vault_proxies_path(self):
        base = os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, 'frozen', False) else os.path.dirname(sys.executable)
        return os.path.join(base, "proxies.txt")

    def _vault_settings_path(self):
        base = os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, 'frozen', False) else os.path.dirname(sys.executable)
        return os.path.join(base, "vault_settings.json")

    def _load_usage(self):
        import json
        path = self._vault_usage_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_usage(self, data):
        import json
        with open(self._vault_usage_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def vault_check_accounts_clicked(self):
        import json, os, time
        from datetime import date
        cookies_dir = self._vault_cookies_dir()
        usage = self._load_usage()
        today = str(date.today())
        
        if not os.path.exists(cookies_dir):
            QMessageBox.warning(self, "Session Vault", "Cookies directory does not exist.")
            return
            
        files = [f for f in os.listdir(cookies_dir) if f.endswith(".json") and not f.startswith("_")]
        if not files:
            QMessageBox.warning(self, "Session Vault", "No accounts to check.")
            return
            
        current_time = time.time()
        checked_count = 0
        expired_count = 0
        
        for fname in files:
            fpath = os.path.join(cookies_dir, fname)
            u = usage.get(fname, {})
            
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cookies = data.get("cookies", data) if isinstance(data, dict) else data
                
                is_expired = True
                has_session_cookie = False
                for c in cookies:
                    if c.get("name") in ["sessionid", "sid_tt", "sid_guard"]:
                        has_session_cookie = True
                        exp = c.get("expiry")
                        if exp is None or exp > current_time:
                            is_expired = False
                            break
                            
                if not has_session_cookie:
                    u["status"] = "NO SESSION"
                    expired_count += 1
                elif is_expired:
                    u["status"] = "EXPIRED"
                    expired_count += 1
                else:
                    u["status"] = "READY"
            except:
                u["status"] = "FAILED"
                expired_count += 1
                
            u["date"] = today
            usage[fname] = u
            checked_count += 1
            
        self._save_usage(usage)
        self.vault_reload_accounts()
        
        QMessageBox.information(
            self, 
            "Session Vault Check", 
            f"Account Sessions Check Complete!\n\n"
            f"Total Checked: {checked_count}\n"
            f"✓ Ready: {checked_count - expired_count}\n"
            f"✗ Expired/Failed: {expired_count}"
        )

    def vault_reload_accounts(self):
        import json
        from datetime import date
        import time
        cookies_dir = self._vault_cookies_dir()
        usage = self._load_usage()
        today = str(date.today())
        current_time = time.time()

        files = sorted([f for f in os.listdir(cookies_dir) if f.endswith(".json") and not f.startswith("_")])
        self.vault_acc_table.setRowCount(0)

        active_count = 0
        expired_count = 0

        try:
            limit = int(self.vault_daily_limit.text().strip())
        except:
            limit = 3

        for idx, fname in enumerate(files):
            fpath = os.path.join(cookies_dir, fname)
            session_preview = "—"
            cookies_expired = False
            has_session_cookie = False
            
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cookies = data.get("cookies", data) if isinstance(data, dict) else data
                for c in cookies:
                    if c.get("name") in ("sessionid", "sid_tt", "sid_guard"):
                        has_session_cookie = True
                        session_preview = c.get("value", "")[:22] + "..."
                        exp = c.get("expiry")
                        if exp is not None and exp < current_time:
                            cookies_expired = True
                        break
            except:
                session_preview = "⚠ Parse Error"

            u = usage.get(fname, {})
            status_val = u.get("status")
            uses_today = u.get("uses_today", 0) if u.get("date") == today else 0
            is_full = uses_today >= limit

            if status_val == "EXPIRED" or cookies_expired:
                expired_count += 1
                status_text = "EXPIRED"
                status_color = "#EF4444"
            elif not has_session_cookie and status_val != "FAILED":
                expired_count += 1
                status_text = "NO SESSION"
                status_color = "#EF4444"
            elif status_val == "FAILED":
                expired_count += 1
                status_text = "FAILED"
                status_color = "#EF4444"
            elif is_full:
                expired_count += 1
                status_text = "LIMIT HIT"
                status_color = "#EF4444"
            else:
                active_count += 1
                status_text = "✓ READY"
                status_color = "#10B981"

            row = self.vault_acc_table.rowCount()
            self.vault_acc_table.insertRow(row)
            self.vault_acc_table.setItem(row, 0, QTableWidgetItem(str(idx + 1)))
            self.vault_acc_table.setItem(row, 1, QTableWidgetItem(fname))
            self.vault_acc_table.setItem(row, 2, QTableWidgetItem(session_preview))

            progress_lbl = QLabel(f"{uses_today} / {limit}")
            progress_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            progress_lbl.setStyleSheet(f"color: {'#EF4444' if is_full else '#F59E0B'}; font-weight: bold; background: transparent;")
            self.vault_acc_table.setCellWidget(row, 3, progress_lbl)

            status_lbl = QLabel(status_text)
            status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_lbl.setStyleSheet(f"color: {status_color}; font-weight: bold; background: transparent; font-size: 8pt;")
            self.vault_acc_table.setCellWidget(row, 4, status_lbl)

        total = len(files)
        self.vault_lbl_total.setText(str(total))
        self.vault_lbl_active.setText(str(active_count))
        self.vault_lbl_expired.setText(str(expired_count))
        self.vault_acc_count_badge.setText(f"{total} Accounts")

    def vault_reload_proxies(self):
        path = self._vault_proxies_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            self.vault_proxy_input.setPlainText(content)
            
            # Sync dashboard proxy input
            self.txt_proxies.blockSignals(True)
            self.txt_proxies.setPlainText(content)
            self.txt_proxies.blockSignals(False)
            
            lines = [l.strip() for l in content.splitlines() if l.strip()]
            self.vault_proxy_table.setRowCount(0)
            for idx, line in enumerate(lines):
                row = self.vault_proxy_table.rowCount()
                self.vault_proxy_table.insertRow(row)
                self.vault_proxy_table.setItem(row, 0, QTableWidgetItem(str(idx + 1)))
                # Mask credentials in display
                display = line
                if ":" in line:
                    parts = line.split(":")
                    if len(parts) >= 4:
                        display = f"{parts[0]}:{parts[1]}:****:****"
                self.vault_proxy_table.setItem(row, 1, QTableWidgetItem(display))
                status_lbl = QLabel("LOADED")
                status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                status_lbl.setStyleSheet("color: #10B981; font-weight: bold; background: transparent; font-size: 8pt;")
                self.vault_proxy_table.setCellWidget(row, 2, status_lbl)
            self.vault_proxy_count_badge.setText(f"{len(lines)} Proxies")
            self.vault_lbl_proxies.setText(str(len(lines)))
            
            # Update dashboard badge label
            self.lbl_proxy_count.setText(f"✓ {len(lines)} proxy(ies)")
        except Exception as e:
            self.log("WARNING", f"Could not load proxies: {str(e)}")

    def vault_reload_proxies_silent(self):
        path = self._vault_proxies_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            self.vault_proxy_input.blockSignals(True)
            self.vault_proxy_input.setPlainText(content)
            self.vault_proxy_input.blockSignals(False)
            
            lines = [l.strip() for l in content.splitlines() if l.strip()]
            self.vault_proxy_table.setRowCount(0)
            for idx, line in enumerate(lines):
                row = self.vault_proxy_table.rowCount()
                self.vault_proxy_table.insertRow(row)
                self.vault_proxy_table.setItem(row, 0, QTableWidgetItem(str(idx + 1)))
                display = line
                if ":" in line:
                    parts = line.split(":")
                    if len(parts) >= 4:
                        display = f"{parts[0]}:{parts[1]}:****:****"
                self.vault_proxy_table.setItem(row, 1, QTableWidgetItem(display))
                status_lbl = QLabel("LOADED")
                status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                status_lbl.setStyleSheet("color: #10B981; font-weight: bold; background: transparent; font-size: 8pt;")
                self.vault_proxy_table.setCellWidget(row, 2, status_lbl)
            self.vault_proxy_count_badge.setText(f"{len(lines)} Proxies")
            self.vault_lbl_proxies.setText(str(len(lines)))
        except:
            pass

    def vault_add_account(self):
        import json, re, time
        raw = self.vault_cookie_paste.toPlainText().strip()
        if not raw:
            QMessageBox.warning(self, "Empty Input", "Please paste a JSON cookie string first.")
            return
        
        data = None
        if raw.startswith("[") or raw.startswith("{"):
            try:
                data = json.loads(raw)
            except Exception as e:
                QMessageBox.critical(self, "Invalid JSON", f"Could not parse cookies JSON:\n{str(e)}")
                return
        else:
            # Parse Netscape / Tab-separated Format
            try:
                parsed_cookies = []
                lines = raw.splitlines()
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith("//"):
                        continue
                    parts = line.split("\t")
                    if len(parts) < 7:
                        parts = re.split(r'\s{2,}', line)
                        if len(parts) < 7:
                            parts = line.split(" ")
                            if len(parts) < 7:
                                continue
                                
                    domain = parts[0].strip()
                    include_sub = parts[1].strip().upper() == "TRUE"
                    path = parts[2].strip()
                    secure = parts[3].strip().upper() == "TRUE"
                    
                    try:
                        expiry = int(float(parts[4].strip()))
                        if expiry <= 0:
                            expiry = int(time.time() + 3600 * 24 * 30)
                    except:
                        expiry = int(time.time() + 3600 * 24 * 30)
                        
                    name = parts[5].strip()
                    value = parts[6].strip()
                    
                    cookie = {
                        "name": name,
                        "value": value,
                        "domain": domain,
                        "path": path,
                        "secure": secure,
                        "httpOnly": False,
                        "sameSite": "Lax"
                    }
                    if expiry > 0:
                        cookie["expiry"] = expiry
                    parsed_cookies.append(cookie)
                    
                if not parsed_cookies:
                    raise Exception("No valid rows parsed from Netscape format.")
                data = parsed_cookies
            except Exception as e:
                QMessageBox.critical(self, "Invalid Format", f"Could not parse Netscape/Tab cookies:\n{str(e)}")
                return

        cookies_dir = self._vault_cookies_dir()
        existing = [f for f in os.listdir(cookies_dir) if f.endswith(".json") and not f.startswith("_")]
        next_num = len(existing) + 1
        fname = f"account_{next_num:03d}.json"
        fpath = os.path.join(cookies_dir, fname)

        if isinstance(data, list):
            save_data = {"cookies": data, "origins": []}
        else:
            save_data = data

        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2)

        self.vault_cookie_paste.clear()
        self.vault_reload_accounts()
        self.log("SUCCESS", f"Session Vault: Added account → {fname}")

    def vault_import_folder(self):
        import json, shutil
        folder = QFileDialog.getExistingDirectory(self, "Select Cookies Folder")
        if not folder:
            return
        cookies_dir = self._vault_cookies_dir()
        existing = [f for f in os.listdir(cookies_dir) if f.endswith(".json") and not f.startswith("_")]
        count = len(existing)
        imported = 0
        for fname in sorted(os.listdir(folder)):
            if fname.endswith(".json"):
                src = os.path.join(folder, fname)
                count += 1
                dst = os.path.join(cookies_dir, f"account_{count:03d}.json")
                try:
                    shutil.copy2(src, dst)
                    imported += 1
                except:
                    pass
        self.vault_reload_accounts()
        self.log("SUCCESS", f"Session Vault: Imported {imported} account files from folder.")

    def vault_remove_selected(self):
        selected = self.vault_acc_table.selectedItems()
        if not selected:
            return
        rows = set(item.row() for item in selected)
        cookies_dir = self._vault_cookies_dir()
        removed = 0
        for row in sorted(rows, reverse=True):
            fname_item = self.vault_acc_table.item(row, 1)
            if fname_item:
                fpath = os.path.join(cookies_dir, fname_item.text())
                try:
                    if os.path.exists(fpath):
                        os.remove(fpath)
                        removed += 1
                except:
                    pass
        self.vault_reload_accounts()
        self.log("SYSTEM", f"Session Vault: Removed {removed} account(s).")

    def vault_clear_all(self):
        reply = QMessageBox.question(self, "Clear All Accounts",
            "Are you sure you want to delete ALL account cookie files? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        cookies_dir = self._vault_cookies_dir()
        for fname in os.listdir(cookies_dir):
            if fname.endswith(".json") and not fname.startswith("_"):
                try:
                    os.remove(os.path.join(cookies_dir, fname))
                except:
                    pass
        self.vault_reload_accounts()
        self.log("SYSTEM", "Session Vault: All account cookies cleared.")

    def vault_save_proxies(self):
        content = self.vault_proxy_input.toPlainText().strip()
        lines = [l.strip() for l in content.splitlines() if l.strip()]
        with open(self._vault_proxies_path(), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        self.vault_reload_proxies()
        self.log("SUCCESS", f"Session Vault: Saved {len(lines)} proxy entries.")

    def vault_load_proxies_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Proxies File", "", "Text Files (*.txt);;All Files (*)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            self.vault_proxy_input.setPlainText(content)
            self.log("SUCCESS", f"Session Vault: Loaded proxies from {os.path.basename(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load file:\n{str(e)}")

    def vault_save_settings(self):
        import json
        try:
            limit = int(self.vault_daily_limit.text().strip())
        except:
            limit = 3
        settings = {"daily_limit": limit}
        with open(self._vault_settings_path(), "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        self.vault_reload_accounts()
        self.log("SUCCESS", f"Session Vault: Daily limit set to {limit} videos/account.")

    # =========================================================================
    # DOLA IMAGE GENERATOR INTEGRATION CODE (DEDICATED PAGES, QUEUES, LOGS)
    # =========================================================================
    def create_dashboard_page(self):

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        dash = QFrame()
        dash.setStyleSheet("background-color: transparent; border: none;")
        lay = QVBoxLayout(dash)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(20)

        # ── HEADER ──
        hdr = QHBoxLayout()
        lbl_welcome = QLabel("📊 Analytics Dashboard")
        lbl_welcome.setStyleSheet("font-family: 'Outfit', 'Inter', sans-serif; font-size: 16pt; font-weight: bold; color: #FFFFFF;")
        self.dash_last_updated = QLabel("Last updated: --")
        self.dash_last_updated.setStyleSheet("font-size: 8.5pt; color: #6B7280;")
        hdr.addWidget(lbl_welcome)
        hdr.addStretch()
        hdr.addWidget(self.dash_last_updated)
        lay.addLayout(hdr)

        # ── QUICK LAUNCH CARDS ──
        launch_grid = QHBoxLayout()
        launch_grid.setSpacing(16)

        vid_card = QFrame()
        vid_card.setStyleSheet("background-color: #0F1626; border: 1px solid #1D2B44; border-radius: 12px; padding: 18px;")
        vid_lay = QVBoxLayout(vid_card)
        vid_title = QLabel("🎥 AI VIDEO ENGINE")
        vid_title.setStyleSheet("font-size: 13pt; font-weight: bold; color: #8B5CF6;")
        vid_desc = QLabel("Automate video generation using Seedance 2.0 with multi-threaded queue.")
        vid_desc.setWordWrap(True)
        vid_desc.setStyleSheet("color: #9CA3AF; margin-top: 8px; margin-bottom: 14px; font-size: 9pt;")
        btn_open_vid = QPushButton("Open Video Generator")
        btn_open_vid.setObjectName("LaunchCTA")
        btn_open_vid.clicked.connect(lambda: self.sidebar_menu.setCurrentRow(1))
        vid_lay.addWidget(vid_title)
        vid_lay.addWidget(vid_desc)
        vid_lay.addWidget(btn_open_vid)

        img_card = QFrame()
        img_card.setStyleSheet("background-color: #0F1626; border: 1px solid #1D2B44; border-radius: 12px; padding: 18px;")
        img_lay = QVBoxLayout(img_card)
        img_title = QLabel("🖼️ AI IMAGE ENGINE")
        img_title.setStyleSheet("font-size: 13pt; font-weight: bold; color: #10B981;")
        img_desc = QLabel("Batch image generation using Dola AI with style and ratio presets.")
        img_desc.setWordWrap(True)
        img_desc.setStyleSheet("color: #9CA3AF; margin-top: 8px; margin-bottom: 14px; font-size: 9pt;")
        btn_open_img = QPushButton("Open Image Generator")
        btn_open_img.setObjectName("LaunchCTA")
        btn_open_img.setStyleSheet("background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #059669);")
        btn_open_img.clicked.connect(lambda: self.sidebar_menu.setCurrentRow(2))
        img_lay.addWidget(img_title)
        img_lay.addWidget(img_desc)
        img_lay.addWidget(btn_open_img)

        launch_grid.addWidget(vid_card)
        launch_grid.addWidget(img_card)
        lay.addLayout(launch_grid)

        # ── PERFORMANCE METRICS SECTION ──
        perf_hdr = QLabel("⚡  PERFORMANCE METRICS")
        perf_hdr.setStyleSheet("font-family: 'Outfit', 'Inter', sans-serif; font-size: 10pt; font-weight: bold; color: #FFFFFF; letter-spacing: 1.5px; padding-top: 4px;")
        lay.addWidget(perf_hdr)

        # Metric card builder helper
        def make_metric_card(icon, label, initial_val, accent_color):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: #0F1626;
                    border: 1px solid #1D2B44;
                    border-left: 3px solid {accent_color};
                    border-radius: 10px;
                    padding: 14px 16px;
                }}
            """)
            card_lay = QHBoxLayout(card)
            card_lay.setContentsMargins(12, 10, 12, 10)
            card_lay.setSpacing(12)

            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet(f"font-size: 18pt; background: transparent; border: none;")
            icon_lbl.setFixedWidth(36)

            text_box = QVBoxLayout()
            text_box.setSpacing(2)
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 7.5pt; font-weight: bold; color: #6B7280; letter-spacing: 1px; background: transparent; border: none;")
            val = QLabel(initial_val)
            val.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {accent_color}; font-family: 'Outfit', 'Inter', monospace; background: transparent; border: none;")
            text_box.addWidget(lbl)
            text_box.addWidget(val)

            card_lay.addWidget(icon_lbl)
            card_lay.addLayout(text_box)
            card_lay.addStretch()
            return card, val

        perf_grid = QGridLayout()
        perf_grid.setSpacing(14)

        card1, self.dash_metric_gen_hr = make_metric_card("📈", "GENERATIONS / HOUR", "0.0", "#06B6D4")
        card2, self.dash_metric_time = make_metric_card("⏱️", "TOTAL TIME SPENT", "0m", "#F59E0B")
        card3, self.dash_metric_prompts = make_metric_card("📝", "TOTAL PROMPTS", "0", "#8B5CF6")
        card4, self.dash_metric_sessions = make_metric_card("🖥️", "TOTAL SESSIONS", "0", "#3B82F6")
        card5, self.dash_metric_best = make_metric_card("🏆", "BEST SESSION RATE", "0%", "#10B981")
        card6, self.dash_metric_errors = make_metric_card("🔴", "TOTAL ERRORS", "0", "#EF4444")

        perf_grid.addWidget(card1, 0, 0)
        perf_grid.addWidget(card2, 0, 1)
        perf_grid.addWidget(card3, 0, 2)
        perf_grid.addWidget(card4, 1, 0)
        perf_grid.addWidget(card5, 1, 1)
        perf_grid.addWidget(card6, 1, 2)
        lay.addLayout(perf_grid)

        # ── SESSION HISTORY SECTION ──
        sess_hdr_lay = QHBoxLayout()
        sess_hdr = QLabel("📋  SESSION HISTORY")
        sess_hdr.setStyleSheet("font-family: 'Outfit', 'Inter', sans-serif; font-size: 10pt; font-weight: bold; color: #FFFFFF; letter-spacing: 1.5px; padding-top: 4px;")
        self.dash_session_count_badge = QLabel("0 sessions")
        self.dash_session_count_badge.setStyleSheet("font-size: 8pt; color: #6B7280; font-weight: bold; padding-top: 6px;")
        sess_hdr_lay.addWidget(sess_hdr)
        sess_hdr_lay.addStretch()
        sess_hdr_lay.addWidget(self.dash_session_count_badge)
        lay.addLayout(sess_hdr_lay)

        self.dash_session_table = QTableWidget(0, 7)
        self.dash_session_table.setHorizontalHeaderLabels(["Date / Time", "Type", "Prompts", "✅ Success", "❌ Failed", "Duration", "Rate"])
        self.dash_session_table.horizontalHeader().setStretchLastSection(True)
        self.dash_session_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.dash_session_table.verticalHeader().setVisible(False)
        self.dash_session_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.dash_session_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.dash_session_table.setMinimumHeight(220)
        self.dash_session_table.setMaximumHeight(350)
        self.dash_session_table.setStyleSheet("""
            QTableWidget {
                background-color: #0B1120;
                border: 1px solid #1D2B44;
                border-radius: 10px;
                gridline-color: #141E33;
                font-size: 9pt;
                color: #D1D5DB;
            }
            QTableWidget::item {
                padding: 6px 10px;
                border-bottom: 1px solid #141E33;
            }
            QHeaderView::section {
                background-color: #0F1626;
                color: #6B7280;
                font-size: 8pt;
                font-weight: bold;
                letter-spacing: 0.5px;
                padding: 8px 10px;
                border: none;
                border-bottom: 2px solid #8B5CF6;
            }
        """)
        lay.addWidget(self.dash_session_table)

        # ── SYSTEM INFO CARD ──
        sys_card = QFrame()
        sys_card.setStyleSheet("background-color: #0F1626; border: 1px solid #1D2B44; border-radius: 10px; padding: 12px 16px;")
        sys_lay = QHBoxLayout(sys_card)
        sys_lay.setContentsMargins(12, 8, 12, 8)
        lbl_hwid = QLabel(f"Device ID: {self.device_id}")
        lbl_hwid.setStyleSheet("color: #4B5563; font-family: monospace; font-size: 8pt;")
        lbl_guard = QLabel("Pakistan IP Leak Guard: 🟢 Active")
        lbl_guard.setStyleSheet("color: #10B981; font-weight: bold; font-size: 8.5pt;")
        sys_lay.addWidget(lbl_hwid)
        sys_lay.addStretch()
        sys_lay.addWidget(lbl_guard)
        lay.addWidget(sys_card)

        # ── PROXY & SMS ACTIVATION SECTION ──
        proxy_sms_hdr = QLabel("⚙️  CONFIGURATION")
        proxy_sms_hdr.setStyleSheet("font-family: 'Outfit', 'Inter', sans-serif; font-size: 10pt; font-weight: bold; color: #FFFFFF; letter-spacing: 1.5px; padding-top: 8px;")
        lay.addWidget(proxy_sms_hdr)

        config_row = QHBoxLayout()
        config_row.setSpacing(16)

        # ── Proxy Card ──
        proxy_dash_card = QFrame()
        proxy_dash_card.setStyleSheet("background-color: #0F1626; border: 1px solid #1D2B44; border-radius: 10px;")
        proxy_dash_layout = QVBoxLayout(proxy_dash_card)
        proxy_dash_layout.setContentsMargins(14, 12, 14, 12)
        proxy_dash_layout.setSpacing(8)

        proxy_title_row = QHBoxLayout()
        proxy_title_lbl = QLabel("🌐  PROXY LIST  (IP Rotation)")
        proxy_title_lbl.setStyleSheet("font-size: 9pt; font-weight: bold; color: #F59E0B; letter-spacing: 1px; background: transparent; border: none;")
        self.lbl_proxy_count.setParent(proxy_dash_card)
        self.lbl_proxy_count.setStyleSheet("font-size: 8pt; color: #10B981; font-weight: bold; background: transparent; border: none;")
        self.lbl_proxy_count.show()
        proxy_title_row.addWidget(proxy_title_lbl)
        proxy_title_row.addStretch()
        proxy_title_row.addWidget(self.lbl_proxy_count)
        proxy_dash_layout.addLayout(proxy_title_row)

        self.txt_proxies.setParent(proxy_dash_card)
        self.txt_proxies.setPlaceholderText("Paste proxies here (1 per line)...\nFormat: IP:Port or IP:Port:User:Pass")
        self.txt_proxies.setStyleSheet("background-color: #070A13; border: 1px solid #1D263B; color: #FFFFFF; padding: 6px; border-radius: 6px; font-family: monospace; font-size: 8.5pt; max-height: 90px; min-height: 70px;")
        self.txt_proxies.show()
        proxy_dash_layout.addWidget(self.txt_proxies)

        proxy_buttons_row = QHBoxLayout()
        proxy_buttons_row.setSpacing(8)

        self.btn_load_proxies.setParent(proxy_dash_card)
        self.btn_load_proxies.setStyleSheet("""
            QPushButton {
                background-color: #1F2937; border: 1px solid #1D263B; color: #FFFFFF;
                font-weight: bold; font-size: 8.5pt; border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #374151; }
        """)
        self.btn_load_proxies.show()

        self.btn_check_proxies.setParent(proxy_dash_card)
        self.btn_check_proxies.setStyleSheet("""
            QPushButton {
                background-color: #1F2937; border: 1px solid #1D263B; color: #FFFFFF;
                font-weight: bold; font-size: 8.5pt; border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #374151; }
        """)
        self.btn_check_proxies.show()

        proxy_buttons_row.addWidget(self.btn_load_proxies)
        proxy_buttons_row.addWidget(self.btn_check_proxies)
        proxy_dash_layout.addLayout(proxy_buttons_row)
        config_row.addWidget(proxy_dash_card, 1)

        # ── SMS Activation Card ──
        sms_dash_card = QFrame()
        sms_dash_card.setStyleSheet("background-color: #0F1626; border: 1px solid #1D2B44; border-radius: 10px;")
        sms_dash_layout = QVBoxLayout(sms_dash_card)
        sms_dash_layout.setContentsMargins(14, 12, 14, 12)
        sms_dash_layout.setSpacing(8)

        sms_title_row = QHBoxLayout()
        sms_title_lbl = QLabel("📱  SMS ACTIVATION  (HeroSMS)")
        sms_title_lbl.setStyleSheet("font-size: 9pt; font-weight: bold; color: #8B5CF6; letter-spacing: 1px; background: transparent; border: none;")
        self.lbl_sms_balance.setParent(sms_dash_card)
        self.lbl_sms_balance.setStyleSheet("font-size: 8pt; color: #F59E0B; font-weight: bold; background: transparent; border: none;")
        self.lbl_sms_balance.show()
        sms_title_row.addWidget(sms_title_lbl)
        sms_title_row.addStretch()
        sms_title_row.addWidget(self.lbl_sms_balance)
        sms_dash_layout.addLayout(sms_title_row)

        self.inp_sms_key.setParent(sms_dash_card)
        self.inp_sms_key.setStyleSheet("background-color: #070A13; border: 1px solid #1D263B; color: #FFFFFF; padding: 6px; border-radius: 6px; font-size: 8.5pt;")
        self.inp_sms_key.show()
        sms_dash_layout.addWidget(self.inp_sms_key)

        sms_bottom_row = QHBoxLayout()
        sms_bottom_row.setSpacing(8)
        self.cb_sms_country.setParent(sms_dash_card)
        self.cb_sms_country.setStyleSheet("""
            QComboBox { background-color: #070A13; border: 1px solid #1D263B; color: #FFFFFF;
                padding: 6px; border-radius: 6px; font-size: 8.5pt; }
            QComboBox QAbstractItemView { background-color: #0F1626; color: #FFFFFF;
                selection-background-color: #1D2B44; }
        """)
        self.cb_sms_country.show()
        self.btn_test_sms.setParent(sms_dash_card)
        self.btn_test_sms.setStyleSheet("""
            QPushButton { background-color: #1F2937; border: 1px solid #1D263B; color: #FFFFFF;
                font-weight: bold; font-size: 8.5pt; border-radius: 6px; padding: 6px 12px; }
            QPushButton:hover { background-color: #374151; }
        """)
        self.btn_test_sms.show()
        sms_bottom_row.addWidget(self.cb_sms_country)
        sms_bottom_row.addWidget(self.btn_test_sms)
        sms_dash_layout.addLayout(sms_bottom_row)
        sms_dash_layout.addStretch()
        config_row.addWidget(sms_dash_card, 1)

        lay.addLayout(config_row)

        lay.addStretch()
        scroll.setWidget(dash)
        return scroll


    # ── DASHBOARD ANALYTICS TRACKING METHODS ──
    def dash_start_session(self, session_type="Video"):
        import time as _time
        self.dash_current_session = {
            "start_time": _time.time(),
            "type": session_type,
            "prompts": 0,
            "success": 0,
            "failed": 0,
        }

    def dash_record_result(self, success, error_reason=None):
        if self.dash_current_session:
            self.dash_current_session["prompts"] += 1
            if success:
                self.dash_current_session["success"] += 1
                self.dash_total_generated += 1
            else:
                self.dash_current_session["failed"] += 1
                self.dash_total_failed += 1
                # Categorize error
                if error_reason == "POLICY_VIOLATION":
                    self.dash_error_counts["Policy"] += 1
                elif error_reason == "HIGH_DEMAND":
                    self.dash_error_counts["Rate Limit"] += 1
                elif error_reason == "REGION_RESTRICTED":
                    self.dash_error_counts["Network"] += 1
                elif error_reason in ["TIMEOUT", None]:
                    self.dash_error_counts["Timeout"] += 1
                else:
                    self.dash_error_counts["Other"] += 1
            self.dash_total_prompts += 1

    def dash_end_session(self):
        import time as _time
        if not self.dash_current_session:
            return
        s = self.dash_current_session
        duration = _time.time() - s["start_time"]
        self.dash_total_time_sec += duration
        rate = (s["success"] / s["prompts"] * 100) if s["prompts"] > 0 else 0.0
        if rate > self.dash_best_rate:
            self.dash_best_rate = rate

        from datetime import datetime
        self.dash_sessions.insert(0, {
            "datetime": datetime.now().strftime("%b %d, %H:%M"),
            "type": s["type"],
            "prompts": s["prompts"],
            "success": s["success"],
            "failed": s["failed"],
            "duration_sec": duration,
            "rate": rate,
        })
        self.dash_current_session = None
        self.refresh_dashboard()

    def refresh_dashboard(self):
        # Session count badge
        if hasattr(self, "dash_session_count_badge") and self.dash_session_count_badge:
            self.dash_session_count_badge.setText(f"{len(self.dash_sessions)} session(s)")

        # Session History Table
        if hasattr(self, "dash_session_table") and self.dash_session_table:
            self.dash_session_table.setRowCount(len(self.dash_sessions))
            for row, s in enumerate(self.dash_sessions):
                self.dash_session_table.setItem(row, 0, QTableWidgetItem(s["datetime"]))

                type_item = QTableWidgetItem(s["type"])
                if s["type"] == "Video":
                    type_item.setForeground(QColor("#8B5CF6"))
                else:
                    type_item.setForeground(QColor("#10B981"))
                self.dash_session_table.setItem(row, 1, type_item)

                self.dash_session_table.setItem(row, 2, QTableWidgetItem(str(s["prompts"])))

                suc_item = QTableWidgetItem(str(s["success"]))
                suc_item.setForeground(QColor("#10B981"))
                self.dash_session_table.setItem(row, 3, suc_item)

                fail_item = QTableWidgetItem(str(s["failed"]))
                fail_item.setForeground(QColor("#EF4444"))
                self.dash_session_table.setItem(row, 4, fail_item)

                dur_sec = s["duration_sec"]
                if dur_sec < 60:
                    dur_str = f"{int(dur_sec)}s"
                elif dur_sec < 3600:
                    dur_str = f"{int(dur_sec // 60)}m {int(dur_sec % 60)}s"
                else:
                    dur_str = f"{int(dur_sec // 3600)}h {int((dur_sec % 3600) // 60)}m"
                self.dash_session_table.setItem(row, 5, QTableWidgetItem(dur_str))

                rate_item = QTableWidgetItem(f"{s['rate']:.0f}%")
                if s["rate"] >= 80:
                    rate_item.setForeground(QColor("#10B981"))
                elif s["rate"] >= 50:
                    rate_item.setForeground(QColor("#F59E0B"))
                else:
                    rate_item.setForeground(QColor("#EF4444"))
                self.dash_session_table.setItem(row, 6, rate_item)

    def create_image_generator_page(self):
        scroll = QScrollArea()
        scroll.setObjectName("MainScrollArea")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        workspace = QWidget()
        workspace.setObjectName("MainWorkspace")
        workspace_layout = QVBoxLayout(workspace)
        workspace_layout.setContentsMargins(24, 18, 24, 18)
        workspace_layout.setSpacing(15)
        
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        header_title = QLabel("Dola Image Gen")
        header_title.setObjectName("MainHeaderTitle")
        header_sub = QLabel("Bulk generate high quality Dola AI images via automated browser control.")
        header_sub.setObjectName("MainHeaderSubtitle")
        title_box.addWidget(header_title)
        title_box.addWidget(header_sub)
        title_box.setSpacing(2)
        
        header.addLayout(title_box)
        header.addStretch()
        
        # Share action buttons from Main window
        header.addWidget(self.btn_refresh)
        header.addWidget(self.btn_support)
        header.addWidget(self.btn_theme)
        header.addWidget(self.btn_bell)
        header.addWidget(self.btn_client_mode)
        workspace_layout.addLayout(header)
        
        output_card = QFrame()
        output_card.setObjectName("PanelCard")
        output_card.setMaximumHeight(70)
        output_layout = QVBoxLayout(output_card)
        output_layout.setContentsMargins(14, 8, 14, 8)
        output_layout.setSpacing(4)
        
        output_title = QLabel("Output Folder Location")
        output_title.setObjectName("FormInputLabel")
        output_layout.addWidget(output_title)
        
        output_bar = QHBoxLayout()
        self.img_output_path_input = QLineEdit(self.img_output_dir)
        self.img_output_path_input.setPlaceholderText("Select output folder location...")
        
        self.btn_img_change_folder = QPushButton("📁 Browse")
        self.btn_img_change_folder.setObjectName("PromptActionButton")
        self.btn_img_change_folder.setFixedWidth(100)
        
        output_bar.addWidget(self.img_output_path_input, 1)
        output_bar.addWidget(self.btn_img_change_folder)
        output_layout.addLayout(output_bar)
        workspace_layout.addWidget(output_card)
        
        stats_card = QFrame()
        stats_card.setObjectName("PanelCard")
        stats_card.setMaximumHeight(90)
        stats_layout = QHBoxLayout(stats_card)
        stats_layout.setContentsMargins(14, 8, 14, 8)
        stats_layout.setSpacing(10)
        
        stats_items_layout = QHBoxLayout()
        self.img_stat_widgets = {}
        
        doc_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjRkZGRkZGIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTE0IDJINmEyIDIgMCAwIDAtMiAydjE2YTIgMiAwIDAgMCAyIDJoMTJhMiAyIDAgMCAwIDItMlY4eiIvPjxwb2x5bGluZSBwb2ludHM9IjE0IDIgMTQgOCAyMCA4Ii8+PC9zdmc+"
        clock_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjRkZGRkZGIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiLz48cG9seWxpbmUgcG9pbnRzPSIxMiA2IDEyIDEyIDE2IDE0Ii8+PC9zdmc+"
        play_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjRkZGRkZGIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlnb24gcG9pbnRzPSI1IDMgMTkgMTIgNSAyMSA1IDMiLz48L3N2Zz4="
        check_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjRkZGRkZGIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTIyIDExLjA4VjEyYTEwIDEwIDAgMSAxLTUuOTMtOS4xNCIvPjxwb2x5bGluZSBwb2ludHM9IjIyIDQgMTIgMTQuMDEgOSAxMS4wMSIvPjwvc3ZnPg=="
        cross_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjRkZGRkZGIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiLz48bGluZSB4MT0iMTUiIHkxPSI5IiB4Mj0iOSIgeTI9IjE1Ii8+PGxpbmUgeDE9IjkiIHkxPSI5IiB4Mj0iMTUiIHkyPSIxNSIvPjwvc3ZnPg=="
        skip_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjRkZGRkZGIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlnb24gcG9pbnRzPSI1IDQgMTUgMTIgNSAyMCA1IDQiLzY+PGxpbmUgeDE9IjE5IiB5MT0iNSIgeDI9IjE5IiB5Mj0iMTkiLz48L3N2Zz4="
        
        stats_items = [
            ("TOTAL", "0", "Images", None, doc_svg, "IconTotal"),
            ("QUEUED", "0", "Images", "#8B5CF6", clock_svg, "IconQueued"),
            ("GENERATING", "0", "In Progress", "#10B981", play_svg, "IconGenerating"),
            ("DONE", "0", "Completed", "#10B981", check_svg, "IconDone"),
            ("FAILED", "0", "Failed", "#EF4444", cross_svg, "IconFailed"),
            ("SKIPPED", "0", "Skipped", "#9CA3AF", skip_svg, "IconSkipped")
        ]
        
        for idx, (name, val, subtitle, color, icon_svg, icon_obj_name) in enumerate(stats_items):
            sub = QWidget()
            sub.setStyleSheet("background: transparent; border: none;")
            sub_lay = QHBoxLayout(sub)
            sub_lay.setContentsMargins(4, 4, 4, 4)
            sub_lay.setSpacing(10)
            
            text_container = QWidget()
            text_container.setStyleSheet("background: transparent; border: none;")
            text_container_lay = QVBoxLayout(text_container)
            text_container_lay.setContentsMargins(0, 0, 0, 0)
            text_container_lay.setSpacing(1)
            
            lbl = QLabel(name)
            lbl.setObjectName("StatLbl")
            
            val_lbl = QLabel(val)
            val_lbl.setObjectName("StatVal")
            if color:
                val_lbl.setStyleSheet(f"color: {color};")
                
            sub_lbl = QLabel(subtitle)
            sub_lbl.setObjectName("StatSub")
            
            text_container_lay.addWidget(lbl)
            text_container_lay.addWidget(val_lbl)
            text_container_lay.addWidget(sub_lbl)
            
            if name == "GENERATING":
                icon_badge = GeneratingIconWidget(icon_svg)
                icon_badge.setObjectName(icon_obj_name)
                self.img_generating_icon_widget = icon_badge
            else:
                icon_badge = QLabel()
                icon_badge.setObjectName(icon_obj_name)
                icon_badge.setFixedSize(36, 36)
                icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                pix = QPixmap()
                pix.loadFromData(QByteArray.fromBase64(icon_svg.encode()))
                icon_badge.setPixmap(pix.scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                
            sub_lay.addWidget(text_container, 1)
            sub_lay.addWidget(icon_badge)
            
            stats_items_layout.addWidget(sub)
            self.img_stat_widgets[name] = val_lbl
            
            if idx < len(stats_items) - 1:
                divider = QFrame()
                divider.setFrameShape(QFrame.Shape.VLine)
                divider.setStyleSheet("background-color: #1F2937; max-width: 1px; min-height: 40px; margin-left: 5px; margin-right: 5px; border: none;")
                stats_items_layout.addWidget(divider)
                
        stats_layout.addLayout(stats_items_layout, 1)
        
        self.img_radial_progress = RadialProgressWidget()
        self.img_radial_progress.set_value(0, 100)
        stats_layout.addWidget(self.img_radial_progress)
        workspace_layout.addWidget(stats_card)
        
        cols_grid = QHBoxLayout()
        cols_grid.setSpacing(20)
        
        left_col = QVBoxLayout()
        left_col.setSpacing(20)
        
        settings_card = QFrame()
        settings_card.setObjectName("SettingsCard")
        settings_card.setMinimumHeight(280)
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setSpacing(8)
        
        settings_hdr = QLabel("GENERATION SETTINGS")
        settings_hdr.setObjectName("PanelTitle")
        settings_layout.addWidget(settings_hdr)
        
        form_grid = QGridLayout()
        form_grid.setSpacing(10)
        form_grid.setColumnStretch(0, 1)
        form_grid.setColumnStretch(1, 2)
        form_grid.setColumnStretch(2, 1)
        form_grid.setColumnStretch(3, 2)

        lbl_img_model = QLabel("Model:")
        lbl_img_model.setObjectName("FormInputLabel")
        self.cb_img_model = QComboBox()
        self.cb_img_model.setObjectName("cb_model")
        self.cb_img_model.addItems(["Dola Image"])
        self.cb_img_model.setEnabled(True)
        self.cb_img_model.setCurrentIndex(0)

        lbl_img_style = QLabel("Style:")
        lbl_img_style.setObjectName("FormInputLabel")
        self.cb_img_style = QComboBox()
        self.cb_img_style.addItems([
            "Portraits", "Landscape", "Anime", "3D", "Cyberpunk", 
            "Oil Painting", "Watercolor", "Flat Illustration", 
            "Children's Drawing", "Pixel", "Colored Pencil", 
            "Ink Wash", "Ink Print"
        ])
        self.cb_img_style.setEnabled(True)
        self.cb_img_style.setCurrentIndex(0)

        lbl_img_ratio = QLabel("Ratio:")
        lbl_img_ratio.setObjectName("FormInputLabel")
        self.cb_img_ratio = QComboBox()
        self.cb_img_ratio.addItems([
            "1:1", "9:16", "16:9", "3:4", 
            "4:3", "2:3"
        ])
        self.cb_img_ratio.setEnabled(True)
        self.cb_img_ratio.setCurrentIndex(0)

        lbl_img_batch = QLabel("Batch:")
        lbl_img_batch.setObjectName("FormInputLabel")
        self.inp_img_batch = QLineEdit("30")
        self.inp_img_batch.setEnabled(True)

        lbl_img_speed = QLabel("Concurrent Threads:")
        lbl_img_speed.setObjectName("FormInputLabel")
        self.inp_img_speed = QLineEdit("1")
        self.inp_img_speed.setEnabled(True)

        lbl_img_timeout = QLabel("Timeout (min):")
        lbl_img_timeout.setObjectName("FormInputLabel")
        self.inp_img_timeout = QLineEdit("30")
        self.inp_img_timeout.setEnabled(True)

        # Row 0: Model & Style
        form_grid.addWidget(lbl_img_model, 0, 0)
        form_grid.addWidget(self.cb_img_model, 0, 1)
        form_grid.addWidget(lbl_img_style, 0, 2)
        form_grid.addWidget(self.cb_img_style, 0, 3)

        # Row 1: Ratio & Batch
        form_grid.addWidget(lbl_img_ratio, 1, 0)
        form_grid.addWidget(self.cb_img_ratio, 1, 1)
        form_grid.addWidget(lbl_img_batch, 1, 2)
        form_grid.addWidget(self.inp_img_batch, 1, 3)

        # Row 2: Concurrent Threads & Timeout (min)
        form_grid.addWidget(lbl_img_speed, 2, 0)
        form_grid.addWidget(self.inp_img_speed, 2, 1)
        form_grid.addWidget(lbl_img_timeout, 2, 2)
        form_grid.addWidget(self.inp_img_timeout, 2, 3)

        settings_layout.addLayout(form_grid)

        # Remove cb_img_vpn_mode (compatibility)
        self.cb_img_vpn_mode = QComboBox(self)
        self.cb_img_vpn_mode.addItems(["Chrome Extension (PIA)", "Desktop App (Surfshark/PIA)"])
        self.cb_img_vpn_mode.setCurrentIndex(1)
        self.cb_img_vpn_mode.hide()

        # Proxy Section
        lbl_proxy_title_container = QWidget()
        lbl_proxy_title_container.setStyleSheet("background: transparent; border: none;")
        proxy_title_layout = QHBoxLayout(lbl_proxy_title_container)
        proxy_title_layout.setContentsMargins(0, 5, 0, 0)
        
        lbl_proxy = QLabel("PROXY LIST (IP Rotation)", self)
        lbl_proxy.setObjectName("FormInputLabel")
        
        self.lbl_img_proxy_count = QLabel("✓ 0 proxy(ies)", self)
        self.lbl_img_proxy_count.setStyleSheet("font-size: 8pt; color: #10B981; font-weight: bold; background: transparent; border: none;")
        
        proxy_title_layout.addWidget(lbl_proxy)
        proxy_title_layout.addStretch()
        proxy_title_layout.addWidget(self.lbl_img_proxy_count)
        settings_layout.addWidget(lbl_proxy_title_container)
        
        self.txt_img_proxies = QTextEdit(self)
        self.txt_img_proxies.setPlaceholderText("Paste proxies here (1 per line)...\nFormat: IP:Port or IP:Port:User:Pass")
        self.txt_img_proxies.setStyleSheet("background-color: #070A13; border: 1px solid #1D263B; color: #FFFFFF; padding: 6px; border-radius: 6px; font-family: monospace; font-size: 8.5pt; max-height: 80px;")
        self.txt_img_proxies.textChanged.connect(self.update_img_proxy_count)
        settings_layout.addWidget(self.txt_img_proxies)
        
        self.btn_load_img_proxies = QPushButton("📁 Load Proxy File", self)
        self.btn_load_img_proxies.setStyleSheet("""
            QPushButton {
                background-color: #1F2937;
                border: 1px solid #1D263B;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 8.5pt;
                border-radius: 6px;
                padding: 6px 12px;
                max-width: 140px;
            }
            QPushButton:hover {
                background-color: #374151;
            }
        """)
        self.btn_load_img_proxies.clicked.connect(self.load_img_proxy_file)
        settings_layout.addWidget(self.btn_load_img_proxies)
        
        self.btn_img_start = QPushButton("START GENERATION")
        self.btn_img_start.setObjectName("LaunchCTA")
        self.btn_img_start.setStyleSheet("background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #059669);")
        self.btn_img_start.setFixedWidth(200)
        self.btn_img_start.setFixedHeight(36)
        
        btn_img_start_lay = QHBoxLayout()
        btn_img_start_lay.addWidget(self.btn_img_start)
        btn_img_start_lay.addStretch()
        settings_layout.addLayout(btn_img_start_lay)
        
        
        # settings_card will be added to layout below at assembly time
        
        queue_card = QFrame()
        queue_card.setObjectName("PanelCard")
        queue_card.setMinimumHeight(220)
        queue_layout = QVBoxLayout(queue_card)
        queue_layout.setSpacing(8)
        
        queue_hdr_layout = QHBoxLayout()
        queue_hdr_layout.setContentsMargins(0, 0, 0, 0)
        queue_hdr_layout.setSpacing(8)
        
        queue_icon = QLabel("📊")
        queue_icon.setStyleSheet("font-size: 11pt; color: #FFFFFF;")
        
        queue_title = QLabel("Generation Queue")
        queue_title.setObjectName("PanelTitle")
        
        self.img_queue_count_badge = QLabel("0 Items")
        self.img_queue_count_badge.setObjectName("BadgeQueued")
        self.img_queue_count_badge.setStyleSheet("margin-left: 6px; font-size: 7.5pt;")
        
        queue_hdr_layout.addWidget(queue_icon)
        queue_hdr_layout.addWidget(queue_title)
        queue_hdr_layout.addWidget(self.img_queue_count_badge)
        queue_hdr_layout.addStretch()
        queue_layout.addLayout(queue_hdr_layout)
        
        self.img_table = QTableWidget()
        self.img_table.setColumnCount(4)
        self.img_table.setHorizontalHeaderLabels(["#", "Prompt (Preview)", "Status", "Action"])
        self.img_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.img_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.img_table.setColumnWidth(1, 160)
        self.img_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.img_table.setColumnWidth(2, 105)
        self.img_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.img_table.verticalHeader().setVisible(False)
        self.img_table.verticalHeader().setDefaultSectionSize(40)
        self.img_table.horizontalHeader().setFixedHeight(36)
        queue_layout.addWidget(self.img_table)
        
        queue_status_layout = QHBoxLayout()
        queue_status_layout.setContentsMargins(0, 5, 0, 0)
        queue_status_layout.setSpacing(10)
        
        self.lbl_img_control_est_time = QLabel("⏳ Estimated Time: --:--:--")
        self.lbl_img_control_est_time.setObjectName("FormInputLabel")
        self.lbl_img_control_est_time.setStyleSheet("color: #9CA3AF;")
        
        self.lbl_img_control_api_status = QLabel("🟢 API Status: Connected")
        self.lbl_img_control_api_status.setObjectName("FormInputLabel")
        self.lbl_img_control_api_status.setStyleSheet("color: #10B981; font-weight: bold;")
        
        queue_status_layout.addWidget(self.lbl_img_control_est_time)
        queue_status_layout.addStretch()
        queue_status_layout.addWidget(self.lbl_img_control_api_status)
        queue_layout.addLayout(queue_status_layout)
        
        queue_btn_layout = QHBoxLayout()
        queue_btn_layout.setContentsMargins(0, 5, 0, 0)
        queue_btn_layout.setSpacing(12)
        
        self.btn_img_ctrl_start = QPushButton("▶ Start Queue")
        self.btn_img_ctrl_start.setObjectName("StartBtn")
        self.btn_img_ctrl_start.setFixedWidth(120)
        
        self.btn_img_ctrl_pause = QPushButton("⏸ Pause")
        self.btn_img_ctrl_pause.setObjectName("PauseBtn")
        self.btn_img_ctrl_pause.setFixedWidth(90)
        
        self.btn_img_ctrl_clear = QPushButton("🗑 Clear Queue")
        self.btn_img_ctrl_clear.setObjectName("ClearQueueBtn")
        self.btn_img_ctrl_clear.setFixedWidth(135)
        
        queue_btn_layout.addWidget(self.btn_img_ctrl_start)
        queue_btn_layout.addWidget(self.btn_img_ctrl_pause)
        queue_btn_layout.addWidget(self.btn_img_ctrl_clear)
        queue_btn_layout.addStretch()
        queue_layout.addLayout(queue_btn_layout)
        
        
        # queue_card and left_col will be added to layout below at assembly time
        
        right_col = QVBoxLayout()
        right_col.setSpacing(20)
        
        prompts_card = QFrame()
        prompts_card.setObjectName("PromptsCard")
        prompts_card.setMinimumHeight(200)
        prompts_layout = QVBoxLayout(prompts_card)
        prompts_layout.setSpacing(6)
        
        prompts_hdr_lay = QHBoxLayout()
        prompts_hdr = QLabel("PROMPTS")
        prompts_hdr.setObjectName("PanelTitle")
        self.img_prompts_count_badge = QLabel("0 PROMPTS")
        self.img_prompts_count_badge.setObjectName("BadgeQueued")
        
        prompts_hdr_lay.addWidget(prompts_hdr)
        prompts_hdr_lay.addWidget(self.img_prompts_count_badge)
        prompts_hdr_lay.addStretch()
        
        self.btn_img_txt = QPushButton("TXT")
        self.btn_img_txt.setObjectName("PromptActionButton")
        self.btn_img_csv = QPushButton("CSV")
        self.btn_img_csv.setObjectName("PromptActionButton")
        self.btn_img_clear = QPushButton("CLEAR")
        self.btn_img_clear.setObjectName("PromptActionButtonDanger")
        self.btn_img_txt.setEnabled(True)
        self.btn_img_csv.setEnabled(True)
        self.btn_img_clear.setEnabled(True)
        
        prompts_hdr_lay.addWidget(self.btn_img_txt)
        prompts_hdr_lay.addWidget(self.btn_img_csv)
        prompts_hdr_lay.addWidget(self.btn_img_clear)
        prompts_layout.addLayout(prompts_hdr_lay)
        
        self.img_prompts_editor = QTextEdit()
        self.img_prompts_editor.setObjectName("PromptsEditor")
        self.img_prompts_editor.setEnabled(True)
        prompts_layout.addWidget(self.img_prompts_editor)
        
        prompts_note = QLabel("One prompt per line = one image. Import from .txt or .csv files using the buttons above.")
        prompts_note.setObjectName("ProfilePlan")
        prompts_layout.addWidget(prompts_note)
        
        
        # prompts_card will be added to layout below at assembly time
        
        logs_card = QFrame()
        logs_card.setObjectName("PanelCard")
        logs_card.setMinimumHeight(200)
        logs_layout = QVBoxLayout(logs_card)
        logs_layout.setSpacing(6)
        
        logs_hdr_lay = QHBoxLayout()
        logs_hdr = QLabel("LIVE LOG CONSOLE")
        logs_hdr.setObjectName("PanelTitle")
        logs_sub = QLabel("STREAMING LIVE TELEMETRY")
        logs_sub.setObjectName("MenuLabel")
        
        logs_hdr_lay.addWidget(logs_hdr)
        logs_hdr_lay.addWidget(logs_sub)
        logs_hdr_lay.addStretch()
        
        self.img_console_search = QLineEdit()
        self.img_console_search.setObjectName("ConsoleSearchBox")
        self.img_console_search.setPlaceholderText("Search logs...")
        self.img_console_search.setFixedWidth(120)
        
        self.btn_img_copy_logs = QPushButton("📋")
        self.btn_img_copy_logs.setObjectName("ConsoleActionButton")
        self.btn_img_clear_logs = QPushButton("🗑️")
        self.btn_img_clear_logs.setObjectName("ConsoleActionButton")
        self.btn_img_download_logs = QPushButton("💾")
        self.btn_img_download_logs.setObjectName("ConsoleActionButton")
        
        logs_hdr_lay.addWidget(self.img_console_search)
        logs_hdr_lay.addWidget(self.btn_img_copy_logs)
        logs_hdr_lay.addWidget(self.btn_img_clear_logs)
        logs_hdr_lay.addWidget(self.btn_img_download_logs)
        logs_layout.addLayout(logs_hdr_lay)
        
        self.img_console = QTextEdit()
        self.img_console.setObjectName("ConsoleTerminal")
        self.img_console.setReadOnly(True)
        logs_layout.addWidget(self.img_console)
        
        # Assemble Left Column (Prompts & Settings)
        left_col.addWidget(prompts_card)
        left_col.addWidget(settings_card)
        cols_grid.addLayout(left_col, 1)

        # Assemble Right Column (Queue Table only)
        right_col.addWidget(queue_card, 1)
        cols_grid.addLayout(right_col, 1)

        # Add columns grid to main workspace layout
        workspace_layout.addLayout(cols_grid)

        # Add logs console card to stretch full width at the bottom
        workspace_layout.addWidget(logs_card)

        scroll.setWidget(workspace)
        
        return scroll

    def img_log(self, type_str, message):
        if self.client_mode:
            if " Redirected to: " in message and ("dola.com" in message or "dola" in message.lower()):
                message = message.split(" Redirected to: ")[0]
            message = message.replace("dola.com", "akira.ai").replace("Dola", "AKIRA").replace("dola", "akira")
            
        self.img_log_counter += 1
        padded_cnt = str(self.img_log_counter).zfill(3)
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if self.client_mode:
            bg_color = "#0B1528"
            text_color = "#60A5FA"
            border_color = "#1D2D44"
            msg_color = "#D1D5DB"
            
            if type_str == "SUCCESS":
                bg_color = "#0D251C"
                text_color = "#10B981"
                border_color = "#1B4D3E"
                msg_color = "#10B981"
            elif type_str == "ERROR":
                bg_color = "#2E151B"
                text_color = "#F87171"
                border_color = "#5D2B34"
                msg_color = "#F87171"
            elif type_str == "WARNING":
                bg_color = "#2D200E"
                text_color = "#F59E0B"
                border_color = "#5B441D"
                msg_color = "#F59E0B"
            elif type_str == "SYSTEM":
                bg_color = "#1A1333"
                text_color = "#A78BFA"
                border_color = "#3C2E66"
                msg_color = "#A78BFA"
                
            log_line = f"""
            <table width='100%' cellpadding='4' cellspacing='0' style='margin-top: 3px; margin-bottom: 3px;'>
              <tr>
                <td width='35' style='color: #4E5A70; font-family: monospace; font-size: 9.5pt;'>{padded_cnt}</td>
                <td width='90' style='color: #4E5A70; font-size: 9.5pt;'>[{current_time}]</td>
                <td width='95'>
                  <table cellpadding='2' cellspacing='0' style='background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 4px;'>
                    <tr>
                      <td align='center' style='color: {text_color}; font-weight: bold; font-size: 8.5pt; font-family: sans-serif; padding-left: 6px; padding-right: 6px;'>{type_str}</td>
                    </tr>
                  </table>
                </td>
                <td style='color: {msg_color}; font-size: 10.5pt; padding-left: 6px;'>{message}</td>
              </tr>
            </table>
            """
        else:
            color = "#60A5FA"
            if type_str == "SUCCESS": color = "#34D399"
            elif type_str == "ERROR": color = "#F87171"
            elif type_str == "WARNING": color = "#FACC15"
            elif type_str == "SYSTEM": color = "#A78BFA"
            log_line = f"<font color='#4E5A70'>{padded_cnt}</font> [{current_time}] <font color='{color}'><b>{type_str}</b></font> {message}"
            
        self.img_console.append(log_line)
        self.img_console.verticalScrollBar().setValue(self.img_console.verticalScrollBar().maximum())

    def change_img_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Output Directory")
        if folder:
            self.img_output_dir = folder
            self.img_output_path_input.setText(folder)
            self.img_log("SUCCESS", f"Image output directory changed to {folder}")

    def import_img_txt(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Image Prompts (TXT)", "", "Text Files (*.txt)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.img_prompts_editor.setText(content)
                self.img_log("SUCCESS", f"Imported prompts from {os.path.basename(path)}")
            except Exception as e:
                self.img_log("ERROR", f"Failed to import TXT: {str(e)}")

    def import_img_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Image Prompts (CSV)", "", "CSV Files (*.csv)")
        if path:
            try:
                import csv
                import io
                cleaned = []
                with open(path, "r", encoding="utf-8", newline="") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if not row or not any(row):
                            continue
                        out = io.StringIO()
                        writer = csv.writer(out)
                        writer.writerow(row)
                        line_str = out.getvalue().strip()
                        if line_str:
                            cleaned.append(line_str)
                self.img_prompts_editor.setText("\n".join(cleaned))
                self.img_log("SUCCESS", f"Imported prompts from {os.path.basename(path)}")
            except Exception as e:
                self.img_log("ERROR", f"Failed to import CSV: {str(e)}")

    def clear_img_prompts(self):
        self.img_prompts_editor.clear()
        self.img_log("SYSTEM", "Prompts workspace cleared.")

    def update_img_prompts_count(self):
        text = self.img_prompts_editor.toPlainText().strip()
        if not text:
            count = 0
        else:
            count = len([l for l in text.split('\n') if l.strip()])
        self.img_prompts_count_badge.setText(f"{count} PROMPTS")

    def control_img_start_clicked(self):
        if self.img_is_queue_paused:
            self.img_is_queue_paused = False
            self.img_log("SYSTEM", "Resuming queue processing...")
            
            try:
                text = clean_val(self.inp_img_speed.text()).strip().lower()
                if not text or not text.isdigit():
                    max_concurrency = 1
                else:
                    max_concurrency = max(1, int(text))
            except Exception:
                max_concurrency = 1

            empty_slots = max_concurrency - len(self.img_workers)
            for _ in range(max(1, empty_slots)):
                self.run_next_image_item()
        elif not self.img_is_generating:
            self.toggle_image_generation()

    def control_img_pause_clicked(self):
        if self.img_is_generating:
            self.img_is_queue_paused = True
            self.img_log("SYSTEM", "Queue processing paused. Active automation will finish. Remaining queue is suspended.")
        else:
            self.img_log("WARNING", "Generation is not active. Cannot pause.")

    def toggle_image_generation(self):
        if self.img_is_generating:
            self.img_is_generating = False
            self.btn_img_start.setText("START GENERATION")
            self.btn_img_start.setStyleSheet("background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #059669);")
            self.cb_img_model.setEnabled(True)
            self.cb_img_style.setEnabled(True)
            self.cb_img_ratio.setEnabled(True)
            self.inp_img_batch.setEnabled(True)
            self.inp_img_speed.setEnabled(True)
            self.inp_img_timeout.setEnabled(True)
            
            aborted_rows = list(self.img_workers.keys())
            for rid in aborted_rows:
                self.img_log("WARNING", f"Gracefully aborting worker thread for Row {rid}...")
                worker = self.img_workers.get(rid)
                if worker:
                    if hasattr(worker, "bot"):
                        worker.bot.is_stopped = True
                    worker.terminate()
                    worker.wait()
                if rid in self.img_workers:
                    del self.img_workers[rid]
                    
            for item in self.img_queue_data:
                if item["status"] in ["SUBMITTING", "GENERATING", "DOWNLOADING"]:
                    item["status"] = "FAILED"
                    self.img_action_text_cache[item["id"]] = "Aborted by user"
                    
            self.img_log("SYSTEM", "All active image generation threads aborted.")
            self.dash_end_session()
            self.recalculate_img_stats()
            self.reorder_img_table_rows()
            return
            
        text = self.img_prompts_editor.toPlainText().strip()
        if not text:
            self.img_log("ERROR", "No prompts available for image generation.")
            QMessageBox.critical(self, "Queue Empty", "Please write or import prompts before starting.")
            return
            
        self.img_is_generating = True
        self.img_is_queue_paused = False
        self.btn_img_start.setText("STOP GENERATION")
        self.btn_img_start.setStyleSheet("background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #EF4444, stop:1 #DC2626);")
        
        self.cb_img_model.setEnabled(False)
        self.cb_img_style.setEnabled(False)
        self.cb_img_ratio.setEnabled(False)
        self.inp_img_batch.setEnabled(False)
        self.inp_img_speed.setEnabled(False)
        self.inp_img_timeout.setEnabled(False)
        
        self.img_queue_data = []
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for idx, line in enumerate(lines, 1):
            self.img_queue_data.append({
                "id": idx,
                "prompt": line,
                "status": "QUEUED"
            })
            
        self.img_action_text_cache.clear()
        self.img_log_counter = 0
        self.img_console.clear()
        
        self.img_log("SYSTEM", "Initializing background image generation queue...")
        self.img_log("INFO", f"Started {len(lines)} generation(s) using Dola Image Engine.")
        self.dash_start_session("Image")
        
        self.recalculate_img_stats()
        self.reorder_img_table_rows()
        
        try:
            speed_text = clean_val(self.inp_img_speed.text()).strip().lower()
            if not speed_text or not speed_text.isdigit():
                max_concurrency = 1
            else:
                max_concurrency = max(1, int(speed_text))
        except Exception:
            max_concurrency = 1
            
        for _ in range(max_concurrency):
            self.run_next_image_item()

    def run_next_image_item(self, setup_mode=False):
        try:
            if not self.img_is_generating or self.img_is_queue_paused:
                return
                
            queued = [item for item in self.img_queue_data if item["status"] == "QUEUED"]
            if not queued:
                if not self.img_workers:
                    self.img_log("SUCCESS", "All prompts in image queue processed.")
                    self.toggle_image_generation()
                return
                
            next_item = queued[0]
            row_id = next_item["id"]
            next_item["status"] = "SUBMITTING"
            
            # Get parsed image proxies list
            proxy_list = self.get_active_proxies(is_image=True)

            bot = DolaAutomationBot(
                output_dir=self.img_output_dir,
                callback_log=None,
                callback_status=None,
                client_mode=self.client_mode
            )
            bot.use_extension_vpn = (self.cb_img_vpn_mode.currentText() == "Chrome Extension (PIA)")
            
            # Get timeout for image
            try:
                timeout_val = int(self.inp_img_timeout.text().strip())
            except ValueError:
                timeout_val = 30

            # Image tab doesn't have SMS inputs, fallback to empty/none
            worker = PlaywrightWorker(
                bot=bot,
                row_id=row_id,
                prompt=next_item["prompt"],
                model=clean_val(self.cb_img_style.currentText()),
                duration="0",
                ratio=clean_val(self.cb_img_ratio.currentText()),
                setup_mode=setup_mode,
                is_image=True,
                proxy_list=proxy_list,
                sms_key=None,
                sms_country="0",
                timeout_min=timeout_val
            )
            
            worker.log_signal.connect(self.img_log)
            worker.status_signal.connect(self.on_img_worker_status_update)
            worker.finished_signal.connect(self.on_img_worker_finished)
            
            self.img_workers[row_id] = worker
            worker.start()
            
            self.recalculate_img_stats()
        except Exception as e:
            self.img_log("ERROR", f"Failed to start image worker: {str(e)}")
            if 'next_item' in locals():
                next_item["status"] = "FAILED"
            self.recalculate_img_stats()
            self.reorder_img_table_rows()

    def on_img_worker_status_update(self, row_id, status, action):
        for item in self.img_queue_data:
            if item["id"] == row_id:
                item["status"] = status
                break
        self.img_action_text_cache[row_id] = action
        self.recalculate_img_stats()
        self.reorder_img_table_rows()

    def on_img_worker_finished(self, row_id, success):
        worker = self.img_workers.get(row_id)
        error_reason = getattr(worker, "error_reason", None) if worker else None
        
        if not success and error_reason in ["HIGH_DEMAND", "REGION_RESTRICTED"]:
            reason_lbl = "High Demand" if error_reason == "HIGH_DEMAND" else "Region Restricted"
            self.img_log("WARNING", f"Row {row_id}: AI Engine {reason_lbl.lower()} detected. Session aborted. Retrying...")
            
            for item in self.img_queue_data:
                if item["id"] == row_id:
                    item["status"] = "QUEUED"
                    break
            self.img_action_text_cache[row_id] = f"Retrying in queue ({reason_lbl})..."
            
            if row_id in self.img_workers:
                del self.img_workers[row_id]
                
            self.recalculate_img_stats()
            self.reorder_img_table_rows()
            
            QTimer.singleShot(5000, lambda: self.run_next_image_item())
            return
            
        for item in self.img_queue_data:
            if item["id"] == row_id:
                if error_reason == "POLICY_VIOLATION":
                    item["status"] = "SKIPPED"
                    self.img_action_text_cache[row_id] = "Policy violation (Skipped)"
                    self.add_notification("warning", f"Row {row_id}: Image prompt skipped (Policy Violation).")
                else:
                    item["status"] = "DONE" if success else "FAILED"
                    self.img_action_text_cache[row_id] = "Success" if success else "Failed"
                    if success:
                        self.add_notification("success", f"Row {row_id}: Image downloaded successfully!")
                    else:
                        self.add_notification("error", f"Row {row_id}: Image generation failed.")
                break
                
        if row_id in self.img_workers:
            del self.img_workers[row_id]

        self.dash_record_result(success, error_reason)
            
        self.recalculate_img_stats()
        self.reorder_img_table_rows()
        self.run_next_image_item()

    def recalculate_img_stats(self):
        generating_count = 0
        is_actively_generating = False
        if self.img_queue_data:
            generating_count = len([i for i in self.img_queue_data if i["status"] in ["SUBMITTING", "GENERATING", "DOWNLOADING"]])
            is_actively_generating = generating_count > 0
            
        self.img_stat_widgets["GENERATING"].setText(str(generating_count))
        self.img_generating_icon_widget.set_active(is_actively_generating)
        
        if not self.img_queue_data:
            for k in ["TOTAL", "QUEUED", "DONE", "FAILED", "SKIPPED"]:
                self.img_stat_widgets[k].setText("0")
            self.img_radial_progress.set_value(0, 100)
            return
            
        total = len(self.img_queue_data)
        queued = len([i for i in self.img_queue_data if i["status"] == "QUEUED"])
        done = len([i for i in self.img_queue_data if i["status"] == "DONE"])
        failed = len([i for i in self.img_queue_data if i["status"] == "FAILED"])
        skipped = len([i for i in self.img_queue_data if i["status"] == "SKIPPED"])
        
        self.img_stat_widgets["TOTAL"].setText(str(total))
        self.img_stat_widgets["QUEUED"].setText(str(queued))
        self.img_stat_widgets["DONE"].setText(str(done))
        self.img_stat_widgets["FAILED"].setText(str(failed))
        self.img_stat_widgets["SKIPPED"].setText(str(skipped))
        
        self.img_radial_progress.set_value(done + failed + skipped, total)
        self.img_queue_count_badge.setText(f"{queued} Items")

    def reorder_img_table_rows(self):
        try:
            self.img_table.setSortingEnabled(False)
            def get_priority(status):
                if status in ["SUBMITTING", "GENERATING", "DOWNLOADING"]:
                    return 0
                elif status == "QUEUED":
                    return 1
                return 2
                
            sorted_queue = sorted(self.img_queue_data, key=lambda x: (get_priority(x["status"]), x["id"]))
            self.img_table.clearContents()
            self.img_table.setRowCount(len(sorted_queue))
            
            for r, item in enumerate(sorted_queue):
                row_id = item["id"]
                status = item["status"]
                prompt = item["prompt"]
                
                self.img_table.setItem(r, 0, QTableWidgetItem(str(row_id)))
                self.img_table.setItem(r, 1, QTableWidgetItem(prompt))
                
                status_item = QTableWidgetItem(status)
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                font = QFont()
                font.setBold(True)
                status_item.setFont(font)
                
                if status == "SUBMITTING":
                    status_item.setForeground(QBrush(QColor("#F59E0B")))
                elif status == "GENERATING":
                    status_item.setForeground(QBrush(QColor("#10B981")))
                elif status == "DOWNLOADING":
                    status_item.setForeground(QBrush(QColor("#3B82F6")))
                elif status == "QUEUED":
                    status_item.setForeground(QBrush(QColor("#A78BFA")))
                    font.setBold(False)
                    status_item.setFont(font)
                elif status == "DONE":
                    status_item.setForeground(QBrush(QColor("#10B981")))
                elif status == "FAILED":
                    status_item.setForeground(QBrush(QColor("#EF4444")))
                elif status == "SKIPPED":
                    status_item.setForeground(QBrush(QColor("#9CA3AF")))
                    font.setBold(False)
                    status_item.setFont(font)
                    
                self.img_table.setItem(r, 2, status_item)
                
                action_text = self.img_action_text_cache.get(row_id, "Waiting in queue..." if status == "QUEUED" else "")
                action_item = QTableWidgetItem(action_text)
                
                if status in ["SUBMITTING", "GENERATING", "DOWNLOADING"]:
                    action_item.setForeground(QBrush(QColor("#FFFFFF")))
                elif "success" in action_text.lower() or status == "DONE":
                    action_item.setForeground(QBrush(QColor("#10B981")))
                elif "error" in action_text.lower() or "failed" in action_text.lower() or status == "FAILED":
                    action_item.setForeground(QBrush(QColor("#EF4444")))
                else:
                    action_item.setForeground(QBrush(QColor("#9CA3AF")))
                    
                self.img_table.setItem(r, 3, action_item)
                
                # Add action buttons to last column
                btn_widget = self.create_img_action_buttons(row_id)
                self.img_table.setCellWidget(r, 3, btn_widget)
        except Exception as e:
            print(f"Error reordering image table: {e}")

    def create_img_action_buttons(self, row_num):
        widget = QWidget()
        lay = QHBoxLayout(widget)
        lay.setContentsMargins(4, 2, 4, 2)
        lay.setSpacing(6)
        
        btn_view = QPushButton("👁", widget)
        btn_view.setFixedSize(28, 28)
        btn_view.setObjectName("QueueActionViewBtn")
        btn_view.clicked.connect(lambda: self.img_log("INFO", f"Row {row_num}: Image preview active/requested."))
        
        btn_del = QPushButton("🗑", widget)
        btn_del.setFixedSize(28, 28)
        btn_del.setObjectName("QueueActionDelBtn")
        btn_del.clicked.connect(lambda: self.img_log("WARNING", f"Row {row_num}: Removed from queue."))
        
        lay.addWidget(btn_view)
        lay.addWidget(btn_del)
        return widget

    def copy_img_logs(self):
        self.img_console.selectAll()
        self.img_console.copy()
        cursor = self.img_console.textCursor()
        cursor.clearSelection()
        self.img_console.setTextCursor(cursor)
        self.img_log("SUCCESS", "Image logs copied to clipboard.")

    def clear_img_logs(self):
        self.img_console.clear()
        self.img_log("SYSTEM", "Image logs cleared.")

    def download_img_logs(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Image Logs", "", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.img_console.toPlainText())
            self.img_log("SUCCESS", f"Image logs saved to {path}")

    def filter_img_logs(self, query):
        query = query.lower()
        if not query:
            return
        lines = self.img_console.toPlainText().split('\n')
        self.img_console.clear()
        for l in lines:
            if query in l.lower():
                self.img_console.append(l)

            self.mock_timer.stop()


# --- UNIQUE DEVICE ID & LICENSING HELPERS ---
import subprocess
import urllib.request
import urllib.parse
import json

class UpdateCheckWorker(QThread):
    finished_signal = pyqtSignal(dict)
    
    def __init__(self, web_url):
        super().__init__()
        self.web_url = web_url
        
    def run(self):
        try:
            url = f"{self.web_url}?action=check_version"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                self.finished_signal.emit(res_data)
        except Exception as e:
            self.finished_signal.emit({"status": "error", "message": str(e)})

class AnnouncementWorker(QThread):
    finished_signal = pyqtSignal(dict)
    
    def __init__(self, web_url):
        super().__init__()
        self.web_url = web_url
        
    def run(self):
        try:
            url = f"{self.web_url}?action=get_announcements"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                self.finished_signal.emit(res_data)
        except Exception as e:
            self.finished_signal.emit({"status": "error", "message": str(e)})

class ProxyCheckWorker(QThread):
    finished_signal = pyqtSignal(list, list) # (live_list, dead_list)
    progress_signal = pyqtSignal(str)
    
    def __init__(self, raw_proxies):
        super().__init__()
        self.raw_proxies = raw_proxies
        
    def run(self):
        import urllib.request
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        live = []
        dead = []
        
        self.progress_signal.emit(f"Checking {len(self.raw_proxies)} proxies concurrently...")
        
        def check_one(proxy_raw):
            try:
                parsed = parse_proxy_string(proxy_raw)
                if not parsed:
                    return proxy_raw, False
                server = parsed["server"].replace("http://", "").replace("https://", "")
                if "username" in parsed and "password" in parsed:
                    formatted_url = f"http://{parsed['username']}:{parsed['password']}@{server}"
                else:
                    formatted_url = f"http://{server}"
                
                proxy_handler = urllib.request.ProxyHandler({'http': formatted_url, 'https': formatted_url})
                opener = urllib.request.build_opener(proxy_handler)
                req = urllib.request.Request("http://api.ipify.org", headers={'User-Agent': 'Mozilla/5.0'})
                with opener.open(req, timeout=4) as response:
                    return proxy_raw, True
            except Exception:
                return proxy_raw, False
                
        if not self.raw_proxies:
            self.finished_signal.emit([], [])
            return
            
        max_workers = min(20, len(self.raw_proxies))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(check_one, p): p for p in self.raw_proxies}
            for future in as_completed(futures):
                proxy_raw, is_live = future.result()
                if is_live:
                    live.append(proxy_raw)
                else:
                    dead.append(proxy_raw)
                    
        self.finished_signal.emit(live, dead)

def get_device_id():
    try:
        # Fetch unique CPU ID
        cpu = subprocess.check_output("wmic cpu get processorid", shell=True).decode().strip().split('\n')[-1].strip()
        # Fetch unique Motherboard UUID
        mb = subprocess.check_output("wmic csproduct get uuid", shell=True).decode().strip().split('\n')[-1].strip()
        raw_id = f"AKIRA_CPU_{cpu}_MB_{mb}".replace(" ", "").replace("\r", "").strip()
        return raw_id
    except Exception:
        import uuid
        node_id = str(uuid.getnode())
        return f"AKIRA_NODE_{node_id}"

def check_license_status(web_app_url, device_id):
    try:
        # Get location information in the background/quickly (timeout of 2.5s to not block)
        ip_addr = ""
        city_name = ""
        country_name = ""
        try:
            req_loc = urllib.request.Request(
                "http://ip-api.com/json", 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req_loc, timeout=2.5) as response_loc:
                loc_data = json.loads(response_loc.read().decode('utf-8'))
                if loc_data.get("status") == "success":
                    ip_addr = loc_data.get("query", "")
                    city_name = loc_data.get("city", "")
                    country_name = loc_data.get("country", "")
        except Exception:
            pass

        url = f"{web_app_url}?device_id={urllib.parse.quote(device_id)}&action=startup"
        if ip_addr:
            url += f"&ip={urllib.parse.quote(ip_addr)}&city={urllib.parse.quote(city_name)}&country={urllib.parse.quote(country_name)}"
            
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_bytes = response.read()
            raw_text = raw_bytes.decode('utf-8', errors='ignore').strip()
            try:
                res_data = json.loads(raw_text)
                
                # Check for secure response format (HMAC Signature Check)
                if "payload" in res_data and "signature" in res_data:
                    import hmac
                    import hashlib
                    import base64
                    
                    payload = res_data["payload"]
                    signature = res_data["signature"]
                    
                    # Decrypt secret key
                    secret_key = _un("a0FDWEt5T0l+RUFPRHUYGhgcdWFPU3V6WEVOdVwb")
                    
                    # Compute signature
                    computed_sig = hmac.new(secret_key.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()
                    if not hmac.compare_digest(computed_sig, signature):
                        return {
                            "status": "error", 
                            "message": "License validation integrity check failed!\n\n"
                                       "Server response signature mismatch (MITM spoofing detected)."
                        }
                    
                    # Decode payload
                    decoded_payload = base64.b64decode(payload.encode('utf-8')).decode('utf-8')
                    return json.loads(decoded_payload)
                else:
                    return {
                        "status": "error", 
                        "message": "License validation integrity check failed!\n\n"
                                   "Missing secure cryptographic signature in server response. "
                                   "Please ensure you have updated your Google Sheet macro code."
                    }
            except json.JSONDecodeError:
                if "<html" in raw_text.lower() or "<!doctype" in raw_text.lower():
                    return {
                        "status": "error", 
                        "message": "Google Web App returned HTML instead of JSON.\n\n"
                                   "Please ensure:\n"
                                   "1. You selected 'Execute as: Me' and 'Who has access: Anyone' in settings.\n"
                                   "2. You copied the Deployed '/exec' URL (not the '/edit' URL).\n"
                                   "3. You created a 'New Deployment' or 'New Version' if you changed the code."
                    }
                return {"status": "error", "message": f"Server Response: {raw_text[:200]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def format_license_plan_text(plan, time_left_sec):
    try:
        time_left_sec = int(time_left_sec)
    except Exception:
        time_left_sec = 0

    if plan.lower() == "lifetime" or time_left_sec > 10 * 365 * 24 * 3600:
        return f"AKIRA {plan} License - Lifetime Active"
        
    sec_in_day = 24 * 3600
    sec_in_month = 30 * sec_in_day
    sec_in_year = 365 * sec_in_day
    
    if time_left_sec >= sec_in_year:
        years = time_left_sec // sec_in_year
        rem = time_left_sec % sec_in_year
        months = rem // sec_in_month
        rem = rem % sec_in_month
        days = rem // sec_in_day
        return f"AKIRA {plan} License - {years}y {months}m {days}d Left"
    elif time_left_sec >= sec_in_month:
        months = time_left_sec // sec_in_month
        rem = time_left_sec % sec_in_month
        days = rem // sec_in_day
        return f"AKIRA {plan} License - {months}m {days}d Left"
    elif time_left_sec >= sec_in_day:
        days = time_left_sec // sec_in_day
        rem = time_left_sec % sec_in_day
        hours = rem // 3600
        return f"AKIRA {plan} License - {days}d {hours}h Left"
    else:
        hours = time_left_sec // 3600
        rem = time_left_sec % 3600
        mins = rem // 60
        secs = rem % 60
        return f"AKIRA {plan} License - {hours}h {mins}m {secs}s Left"

# --- UPDATE CHECKER THREAD AND CUSTOM GOLD/BLACK DIALOG ---
class UpdateCheckerThread(QThread):
    update_available = pyqtSignal(str, str, str)  # version, url, changelog
    
    def __init__(self, current_version, update_url, parent=None):
        super().__init__(parent)
        self.current_version = current_version
        self.update_url = update_url
        
    def run(self):
        import urllib.request
        import json
        import urllib.parse
        try:
            req = urllib.request.Request(self.update_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as response:
                raw_data = response.read().decode('utf-8', errors='ignore').strip()
                data = json.loads(raw_data)
                
            latest_version = data.get("latest_version", "1.0.0")
            download_url = data.get("download_url", "")
            changelog = data.get("changelog", "")
            
            # Simple semantic version check
            if self.is_newer(self.current_version, latest_version):
                self.update_available.emit(latest_version, download_url, changelog)
        except Exception:
            pass
            
    def is_newer(self, current, latest):
        try:
            c_parts = [int(x) for x in current.split(".")]
            l_parts = [int(x) for x in latest.split(".")]
            return l_parts > c_parts
        except Exception:
            return latest != current

class UpdateDownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, download_url, dest_path, parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.dest_path = dest_path
        
    def run(self):
        import urllib.request
        import os
        try:
            req = urllib.request.Request(self.download_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                total_size = int(response.info().get('Content-Length', 0))
                bytes_downloaded = 0
                block_size = 8192
                
                with open(self.dest_path, 'wb') as f:
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        f.write(buffer)
                        bytes_downloaded += len(buffer)
                        if total_size > 0:
                            percent = int((bytes_downloaded / total_size) * 100)
                            self.progress.emit(percent)
                
                self.finished.emit(self.dest_path)
        except Exception as e:
            if os.path.exists(self.dest_path):
                try:
                    os.remove(self.dest_path)
                except Exception:
                    pass
            self.error.emit(str(e))

class AkiraUpdateDialog(QDialog):
    def __init__(self, new_version, download_url, changelog, parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.setWindowTitle("Software Update Available")
        self.setFixedSize(480, 360)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #0C0D14;
                border: 2px solid #C5A059;
                border-radius: 8px;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Inter', sans-serif;
            }
            QTextEdit {
                background-color: #161722;
                color: #E2E8F0;
                border: 1px solid #161722;
                border-radius: 4px;
                font-family: 'Inter', sans-serif;
                font-size: 9.5pt;
                padding: 10px;
            }
            QProgressBar {
                background-color: #161722;
                border: 1px solid #161722;
                border-radius: 4px;
                text-align: center;
                color: #FFFFFF;
                font-weight: bold;
                height: 22px;
            }
            QProgressBar::chunk {
                background-color: #C5A059;
                border-radius: 4px;
            }
            QPushButton#btn_update {
                background-color: #C5A059;
                color: #0C0D14;
                font-weight: bold;
                border-radius: 4px;
                padding: 10px;
                border: none;
                font-size: 10pt;
            }
            QPushButton#btn_update:hover {
                background-color: #D4B26F;
            }
            QPushButton#btn_later {
                background-color: #161722;
                color: #C5A059;
                border: 1px solid #C5A059;
                font-weight: bold;
                border-radius: 4px;
                padding: 10px;
                font-size: 10pt;
            }
            QPushButton#btn_later:hover {
                background-color: #1E2030;
            }
        """)
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(25, 25, 25, 25)
        lay.setSpacing(15)
        
        # Header / Title
        title_box = QHBoxLayout()
        logo_lbl = QLabel(self)
        logo_lbl.setPixmap(get_logo_pixmap(40))
        
        title_info = QVBoxLayout()
        title = QLabel("SYSTEM UPDATE AVAILABLE", self)
        title.setStyleSheet("font-family: 'Outfit', 'Inter', sans-serif; font-size: 13pt; font-weight: 900; color: #C5A059; letter-spacing: 1.5px;")
        sub_title = QLabel("New optimization package ready", self)
        sub_title.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 7.5pt; color: #9CA3AF; letter-spacing: 0.5px; text-transform: uppercase;")
        title_info.addWidget(title)
        title_info.addWidget(sub_title)
        title_info.setSpacing(1)
        
        title_box.addWidget(logo_lbl)
        title_box.addLayout(title_info)
        title_box.addStretch()
        lay.addLayout(title_box)
        
        # Gold divider line
        divider = QFrame(self)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #C5A059; max-height: 1px; border: none; margin-top: -5px; margin-bottom: 5px;")
        lay.addWidget(divider)
        
        # Sub-header
        self.sub = QLabel(f"AKIRA Engine Version {new_version} is ready. Please review the release notes:", self)
        self.sub.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 9.5pt; color: #E2E8F0; font-weight: bold;")
        self.sub.setWordWrap(True)
        lay.addWidget(self.sub)
        
        # Keypoints changelog with Golden Ticks in HTML
        self.txt_changelog = QTextEdit(self)
        self.txt_changelog.setReadOnly(True)
        
        # Parse changelog to create premium HTML list with golden ticks
        lines = changelog.split('\n')
        html_content = '<div style="font-family: \'Inter\', sans-serif; color: #E2E8F0;">'
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            if line_str.startswith("-") or line_str.startswith("*"):
                line_str = line_str[1:].strip()
            
            html_content += (
                f'<div style="margin-bottom: 10px; display: table; width: 100%;">'
                f'<span style="color: #C5A059; font-weight: bold; font-size: 11pt; '
                f'display: table-cell; width: 20px; vertical-align: top; padding-top: 1px;">✔</span>'
                f'<span style="display: table-cell; vertical-align: top; font-size: 9.5pt; '
                f'line-height: 1.4; color: #D1D5DB;">{line_str}</span>'
                f'</div>'
            )
        html_content += '</div>'
        self.txt_changelog.setHtml(html_content)
        lay.addWidget(self.txt_changelog)
        
        # Progress Bar & Status (Hidden initially)
        self.lbl_progress = QLabel("Downloading Update: 0%", self)
        self.lbl_progress.setStyleSheet("font-size: 10.5pt; font-weight: bold; color: #C5A059;")
        self.lbl_progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_progress.hide()
        lay.addWidget(self.lbl_progress)
        
        self.pbar = QProgressBar(self)
        self.pbar.setRange(0, 100)
        self.pbar.setValue(0)
        self.pbar.setTextVisible(False)
        self.pbar.hide()
        lay.addWidget(self.pbar)
        
        # Buttons layout
        self.btn_box = QHBoxLayout()
        
        self.btn_later = QPushButton("Maybe Later", self)
        self.btn_later.setObjectName("btn_later")
        self.btn_later.clicked.connect(self.reject)
        
        self.btn_update = QPushButton("Update Now", self)
        self.btn_update.setObjectName("btn_update")
        self.btn_update.clicked.connect(self.do_update)
        
        self.btn_box.addWidget(self.btn_later)
        self.btn_box.addWidget(self.btn_update)
        lay.addLayout(self.btn_box)
        
    def do_update(self):
        # Hide standard dialog views
        self.txt_changelog.hide()
        self.btn_later.hide()
        self.btn_update.hide()
        self.sub.hide()
        
        # Show and center progress views
        self.lbl_progress.show()
        self.pbar.show()
        
        # Start background download thread to temporary directory
        import tempfile
        import os
        dest_path = os.path.join(tempfile.gettempdir(), "akira_setup_update.exe")
        
        self.downloader = UpdateDownloadThread(self.download_url, dest_path, self)
        self.downloader.progress.connect(self.on_download_progress)
        self.downloader.finished.connect(self.on_download_finished)
        self.downloader.error.connect(self.on_download_error)
        self.downloader.start()
        
    def on_download_progress(self, percent):
        self.pbar.setValue(percent)
        self.lbl_progress.setText(f"Downloading Update: {percent}%")
        
    def on_download_finished(self, local_path):
        self.lbl_progress.setText("Download complete! Installing updates...")
        self.pbar.setValue(100)
        
        import os
        import subprocess
        
        # Inno Setup silent background installation parameters
        cmd = [local_path, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"]
        try:
            subprocess.Popen(cmd, shell=True)
        except Exception as e:
            QMessageBox.critical(self, "Installation Error", f"Could not launch silent installer: {e}")
            self.reject()
            return
            
        # Close PyQt application immediately so that the installer can overwrite active files
        QApplication.quit()
        
    def on_download_error(self, err_msg):
        QMessageBox.critical(self, "Download Failed", f"An error occurred while downloading: {err_msg}")
        
        # Restore layout
        self.pbar.hide()
        self.lbl_progress.hide()
        self.txt_changelog.show()
        self.btn_later.show()
        self.btn_update.show()
        self.sub.show()


class RealtimeUpdateDialog(QDialog):
    def __init__(self, current_version, update_url, parent=None):
        super().__init__(parent)
        self.current_version = current_version
        self.update_url = update_url
        self.latest_version = None
        self.download_url = None
        self.changelog = None
        
        self.setWindowTitle("Check for Updates")
        self.setFixedSize(360, 240)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #12131C;
                border: 2px solid #C5A059;
                border-radius: 8px;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Inter', sans-serif;
            }
            QComboBox {
                background-color: #06070B;
                border: 1px solid #1F2231;
                border-radius: 4px;
                padding: 4px 8px;
                color: #FFFFFF;
                font-size: 9.5pt;
                min-width: 100px;
            }
            QPushButton#btn_action {
                background-color: #0A66C2;
                color: #FFFFFF;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px 16px;
                border: none;
                font-size: 9.5pt;
            }
            QPushButton#btn_action:hover {
                background-color: #004182;
            }
            QProgressBar {
                background-color: #161722;
                border: 1px solid #1F2231;
                border-radius: 4px;
                text-align: center;
                color: #FFFFFF;
                font-weight: bold;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #C5A059;
                border-radius: 4px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header Row
        header = QHBoxLayout()
        self.title_lbl = QLabel("Check for Updates", self)
        self.title_lbl.setStyleSheet("font-family: 'Outfit', 'Inter', sans-serif; font-size: 12pt; font-weight: bold; color: #C5A059;")
        header.addWidget(self.title_lbl)
        header.addStretch()
        
        # Refresh button
        self.btn_refresh = QPushButton(self)
        self.btn_refresh.setFixedSize(20, 20)
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setStyleSheet("background: transparent; border: none; image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI0M1QTA1OSI+PHBhdGggZD0iTTEyIDRDNy41OCA0IDQgNy41OCA0IDEyUzcuNTggMjAgMTIgMjBDMTYuNDIgMjAgMjAgMTYuNDIgMjAgMTJIMThDMTggMTUuMzEgMTUuMzEgMTggMTIgMThDOC42OSAxOCA2IDE1LjMxIDYgMTZDNiA4LjY5IDguNjkgNiAxMiA2QzEzLjY2IDYgMTUuMTQgNi43MyAxNi4yNCA3Ljc2TDEzIDExSDIyVjJMMTcuNjUgNi4zNUNNMTcuNjUgNi4zNUMxNi4yIDQuOSAxNC4wNyA0IDEyIDRaIi8+PC9zdmc+);")
        self.btn_refresh.clicked.connect(self.start_check)
        header.addWidget(self.btn_refresh)
        
        layout.addLayout(header)
        
        # Divider
        divider = QFrame(self)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #1F2231; max-height: 1px; border: none;")
        layout.addWidget(divider)
        
        # Info Area
        self.info_widget = QWidget(self)
        self.info_lay = QHBoxLayout(self.info_widget)
        self.info_lay.setContentsMargins(0, 5, 0, 5)
        self.info_lay.setSpacing(10)
        
        self.lbl_desc = QLabel("Available update version list", self)
        self.lbl_desc.setStyleSheet("font-size: 9.5pt; color: #E2E8F0;")
        self.info_lay.addWidget(self.lbl_desc)
        
        self.cb_versions = QComboBox(self)
        self.info_lay.addWidget(self.cb_versions)
        self.info_lay.addStretch()
        layout.addWidget(self.info_widget)
        
        # Status Label
        self.lbl_status = QLabel("Checking...", self)
        self.lbl_status.setStyleSheet("font-size: 9.5pt; font-weight: bold; color: #D4AF37;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_status)
        
        # Progress Bar (Hidden initially)
        self.pbar = QProgressBar(self)
        self.pbar.setRange(0, 100)
        self.pbar.setValue(0)
        self.pbar.setTextVisible(False)
        self.pbar.hide()
        layout.addWidget(self.pbar)
        
        # Action Button at Bottom
        self.btn_action = QPushButton("Download and Install", self)
        self.btn_action.setObjectName("btn_action")
        self.btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_action.clicked.connect(self.action_clicked)
        self.btn_action.hide()
        layout.addWidget(self.btn_action)
        
        # Start initial check
        self.start_check()
        
    def start_check(self):
        self.btn_refresh.setEnabled(False)
        self.lbl_status.setText("Checking for updates...")
        self.lbl_status.setStyleSheet("font-size: 9.5pt; font-weight: bold; color: #D4AF37;")
        self.btn_action.hide()
        self.cb_versions.clear()
        self.latest_version = None
        
        self.checker = UpdateCheckerThread(self.current_version, self.update_url, self)
        self.checker.update_available.connect(self.on_update_found)
        self.checker.finished.connect(self.on_check_finished)
        self.checker.start()
        
    def on_update_found(self, version, download_url, changelog):
        self.latest_version = version
        self.download_url = download_url
        self.changelog = changelog
        
    def on_check_finished(self):
        self.btn_refresh.setEnabled(True)
        if self.latest_version:
            self.cb_versions.addItem(self.latest_version)
            self.lbl_status.setText("Updates Ready!")
            self.lbl_status.setStyleSheet("font-size: 9.5pt; font-weight: bold; color: #C5A059;")
            self.btn_action.show()
        else:
            self.cb_versions.addItem(self.current_version)
            self.lbl_status.setText("Your software is up to date!")
            self.lbl_status.setStyleSheet("font-size: 9.5pt; font-weight: bold; color: #10B981;")
            self.btn_action.hide()
            
    def action_clicked(self):
        if not self.download_url:
            return
        self.btn_action.hide()
        self.info_widget.hide()
        self.btn_refresh.hide()
        self.pbar.show()
        self.lbl_status.setText("Downloading Update: 0%")
        
        import tempfile
        import os
        dest_path = os.path.join(tempfile.gettempdir(), "akira_setup_update.exe")
        
        self.downloader = UpdateDownloadThread(self.download_url, dest_path, self)
        self.downloader.progress.connect(self.on_download_progress)
        self.downloader.finished.connect(self.on_download_finished)
        self.downloader.error.connect(self.on_download_error)
        self.downloader.start()
        
    def on_download_progress(self, percent):
        self.pbar.setValue(percent)
        self.lbl_status.setText(f"Downloading Update: {percent}%")
        
    def on_download_finished(self, local_path):
        self.lbl_status.setText("Download complete! Installing...")
        self.pbar.setValue(100)
        
        import subprocess
        cmd = [local_path, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"]
        try:
            subprocess.Popen(cmd, shell=True)
        except Exception as e:
            QMessageBox.critical(self, "Installation Error", f"Could not launch silent installer: {e}")
            self.reject()
            return
        QApplication.quit()
        
    def on_download_error(self, err_msg):
        QMessageBox.critical(self, "Download Failed", f"An error occurred: {err_msg}")
        self.pbar.hide()
        self.btn_refresh.show()
        self.info_widget.show()
        self.btn_action.show()
        self.lbl_status.setText("Updates Ready!")


# --- BITCOIN PAYMENT DETAIL POPUP DIALOG ---
class PaymentDialog(QDialog):
    def __init__(self, btc_address, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Buy Subscription")
        self.setFixedSize(400, 320)
        self.setStyleSheet("""
            QDialog {
                background-color: #111827;
                border: 1px solid #1D263B;
                border-radius: 12px;
            }
            QLabel {
                color: #F3F4F6;
                font-family: 'Inter', sans-serif;
            }
            QPushButton {
                background-color: #8B5CF6;
                color: #FFFFFF;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #A78BFA;
            }
        """)
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(15)
        
        title = QLabel("Manual Payment Instructions", self)
        title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #FFFFFF;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)
        
        desc = QLabel(
            "To buy or renew your subscription, please send payment\n"
            "to the Bitcoin address below. Once completed, send\n"
            "your Device ID and proof of payment to Malik Zia.",
            self
        )
        desc.setStyleSheet("font-size: 9.5pt; color: #9CA3AF;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(desc)
        
        btc_lbl = QLabel("Bitcoin Wallet Address:", self)
        btc_lbl.setStyleSheet("font-weight: bold; font-size: 8.5pt; color: #8B5CF6;")
        lay.addWidget(btc_lbl)
        
        btc_box = QHBoxLayout()
        self.btc_edit = QLineEdit(btc_address, self)
        self.btc_edit.setReadOnly(True)
        self.btc_edit.setStyleSheet("background-color: #070A13; color: #34D399; font-weight: bold; font-family: monospace;")
        
        btn_copy = QPushButton("Copy", self)
        btn_copy.setFixedWidth(60)
        btn_copy.clicked.connect(self.copy_btc)
        btc_box.addWidget(self.btc_edit)
        btc_box.addWidget(btn_copy)
        lay.addLayout(btc_box)
        
        btn_ok = QPushButton("OK, Got It", self)
        btn_ok.clicked.connect(self.accept)
        lay.addWidget(btn_ok)

    def copy_btc(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.btc_edit.text())
        QMessageBox.information(self, "Copied", "Bitcoin address copied to clipboard!")


# --- PROFESSIONAL AKIRA LOCK SCREEN & BILLING WIZARD ---
class PricingCard(QFrame):
    clicked = pyqtSignal(str, int)  # plan_name, price_usd
    
    def __init__(self, plan_name, subtitle, price, original_price, badge_text, icon_text, is_contact=False, parent=None):
        super().__init__(parent)
        self.plan_name = plan_name
        self.price = price
        self.is_contact = is_contact
        
        self.setObjectName("PricingCard")
        self.setStyleSheet("""
            QFrame#PricingCard {
                background-color: #12131C;
                border: 1px solid #2A2518;
                border-radius: 12px;
            }
            QFrame#PricingCard:hover {
                border-color: #C5A059;
                background-color: #1A1810;
            }
        """)
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(15, 15, 15, 15)
        lay.setSpacing(10)
        
        # Badge
        if badge_text:
            badge = QLabel(badge_text.upper(), self)
            badge.setStyleSheet("""
                font-size: 7pt;
                font-weight: bold;
                color: #12131C;
                background-color: #C5A059;
                padding: 3px 8px;
                border-radius: 4px;
                border: none;
            """)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(badge, 0, Qt.AlignmentFlag.AlignLeft)
        else:
            lay.addSpacing(15)
            
        # Icon
        icon_lbl = QLabel(icon_text, self)
        icon_lbl.setStyleSheet("""
            font-size: 16pt;
            color: #C5A059;
            background-color: rgba(197, 160, 89, 0.1);
            border-radius: 15px;
            min-width: 30px;
            max-width: 30px;
            min-height: 30px;
            max-height: 30px;
            border: none;
        """)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(icon_lbl)
        
        # Titles
        title_lbl = QLabel(plan_name, self)
        title_lbl.setStyleSheet("font-size: 11pt; font-weight: bold; color: #FFFFFF; border: none; background: transparent;")
        lay.addWidget(title_lbl)
        
        # Prices
        price_lay = QHBoxLayout()
        if not is_contact:
            orig = QLabel(f"${original_price}", self)
            orig.setStyleSheet("font-size: 10pt; color: #6B7280; text-decoration: line-through; border: none; background: transparent;")
            
            cur = QLabel(f"${price}", self)
            cur.setStyleSheet("font-size: 16pt; font-weight: bold; color: #FFFFFF; border: none; background: transparent;")
            
            price_lay.addWidget(orig)
            price_lay.addWidget(cur)
            price_lay.addStretch()
        else:
            cur = QLabel("Bulk", self)
            cur.setStyleSheet("font-size: 14pt; font-weight: bold; color: #9CA3AF; border: none; background: transparent;")
            
            val = QLabel("Custom", self)
            val.setStyleSheet("font-size: 16pt; font-weight: bold; color: #FFFFFF; border: none; background: transparent;")
            price_lay.addWidget(cur)
            price_lay.addWidget(val)
            price_lay.addStretch()
        lay.addLayout(price_lay)
        
        sub = QLabel(subtitle, self)
        sub.setStyleSheet("font-size: 8pt; color: #9CA3AF; border: none; background: transparent;")
        sub.setWordWrap(True)
        lay.addWidget(sub)
        
        # Action button
        btn_text = "Contact Us" if is_contact else "⚡  Get Access Now"
        btn = QPushButton(btn_text, self)
        if is_contact:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1A1810;
                    border: 1px solid #2A2518;
                    color: #C5A059;
                    font-weight: bold;
                    border-radius: 8px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #221F14;
                    border-color: #C5A059;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #C5A059, stop:1 #A0793A);
                    color: #0D0D0D;
                    font-weight: bold;
                    border-radius: 8px;
                    padding: 10px;
                    border: none;
                    font-size: 9.5pt;
                }
                QPushButton:hover {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #D4AF6A, stop:1 #B08848);
                }
            """)
        btn.clicked.connect(self.on_btn_clicked)
        lay.addWidget(btn)

    def on_btn_clicked(self):
        self.clicked.emit(self.plan_name, self.price)


class PaymentMethodButton(QPushButton):
    def __init__(self, name, icon_text, is_active=True, parent=None):
        super().__init__(parent)
        self.name = name
        self.is_active = is_active
        self.icon_text = icon_text
        self.setCheckable(True)
        self.set_state(is_active)

    def set_state(self, active):
        self.is_active = active
        if active:
            self.setText(f" {self.icon_text}  {self.name}\n AVAILABLE NOW")
            self.setStyleSheet("""
                QPushButton {
                    background-color: #1F2937;
                    border: 1px solid #374151;
                    color: #FFFFFF;
                    font-weight: bold;
                    text-align: left;
                    padding: 10px 15px;
                    border-radius: 8px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    border-color: #8B5CF6;
                    background-color: #131B2E;
                }
                QPushButton:checked {
                    background-color: #131B2E;
                    border-color: #8B5CF6;
                }
            """)
            self.setEnabled(True)
        else:
            self.setText(f" {self.icon_text}  {self.name}\n CLICK TO SWITCH CURRENCY")
            self.setStyleSheet("""
                QPushButton {
                    background-color: #111827;
                    border: 1px solid #1D263B;
                    color: #4B5563;
                    text-align: left;
                    padding: 10px 15px;
                    border-radius: 8px;
                    font-size: 8.5pt;
                }
            """)
            self.setEnabled(False)


class AkiraWorkflowStepWidget(QWidget):
    def __init__(self, current_step, detail_text="", parent=None):
        super().__init__(parent)
        self.current_step = current_step # 1 to 5
        self.detail_text = detail_text
        self.steps = ["Setup", "Config", "Submit", "Render", "Save"]
        self.setFixedHeight(38)
        
        # Spinning loading indicator setup
        from PyQt6.QtCore import QTimer
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate_spinner)
        self.timer.start(45) # ~22 FPS rotation
        
    def rotate_spinner(self):
        self.angle = (self.angle + 8) % 360
        self.update()
        
    def set_step(self, step, detail_text=""):
        self.current_step = step
        self.detail_text = detail_text
        self.update()
        
    def paintEvent(self, event):
        from PyQt6.QtCore import QPoint, QRect, Qt
        from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Paint transparent background so table selection styles show through
        painter.fillRect(self.rect(), QColor("transparent"))
        
        width = self.width()
        height = self.height()
        
        # Margins
        margin = 35
        spacing = (width - 2 * margin) / 4
        
        # 1. Draw connecting lines
        for i in range(4):
            x1 = int(margin + i * spacing)
            x2 = int(margin + (i + 1) * spacing)
            y = 11
            
            pen = QPen()
            pen.setWidth(2)
            if i + 1 < self.current_step:
                pen.setColor(QColor("#10B981")) # Completed (Green)
            elif i + 1 == self.current_step:
                pen.setColor(QColor("#8B5CF6")) # Active (Purple)
            else:
                pen.setColor(QColor("#1D263B")) # Waiting (Dark Gray)
            painter.setPen(pen)
            painter.drawLine(x1, y, x2, y)
            
        # 2. Draw nodes
        for i, name in enumerate(self.steps):
            x = int(margin + i * spacing)
            y = 11
            step_num = i + 1
            
            # Check state
            if step_num < self.current_step:
                # Completed state (Green)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor("#10B981")))
                painter.drawEllipse(QPoint(x, y), 5, 5)
                
                # Draw checkmark inside
                painter.setPen(QPen(QColor("#FFFFFF"), 1.2))
                painter.drawLine(x - 2, y, x - 1, y + 1)
                painter.drawLine(x - 1, y + 1, x + 2, y - 2)
            elif step_num == self.current_step:
                # Active state (Purple with outer spinning loading arc)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                
                # Draw outer track circle
                painter.setPen(QPen(QColor("#1D263B"), 1.2))
                painter.drawEllipse(QPoint(x, y), 7, 7)
                
                # Draw spinning arc (Purple)
                painter.setPen(QPen(QColor("#8B5CF6"), 1.5))
                painter.drawArc(x - 7, y - 7, 14, 14, self.angle * 16, 120 * 16)
                
                # Inner solid node (Purple)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor("#8B5CF6")))
                painter.drawEllipse(QPoint(x, y), 4, 4)
            else:
                # Waiting state (Gray)
                painter.setPen(QPen(QColor("#374151"), 1.5))
                painter.setBrush(QBrush(QColor("#111827")))
                painter.drawEllipse(QPoint(x, y), 4, 4)
                
        # 3. Draw a single centered dynamic status label below the timeline
        display_text = self.detail_text if self.detail_text else self.steps[self.current_step - 1]
        painter.setFont(QFont("Inter", 8, QFont.Weight.Medium))
        painter.setPen(QColor("#FFFFFF"))
        rect = QRect(0, 22, width, 14)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, display_text)


class AkiraLockScreen(QWidget):
    def __init__(self, device_id, config_data, reason=None):
        super().__init__()
        self.device_id = device_id
        self.config_data = config_data
        self.reason = reason or "Your subscription has expired or is invalid. Please renew to continue."
        
        self.setWindowTitle("AKIRA PRO — License Activation")
        self.setFixedSize(550, 540)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Load window icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.drag_position = None
        self.selected_plan = "1 Month — AKIRA PRO"
        self.price_usd = 15
        self.selected_method = "Binance (USDT)"
        self.selected_screenshot_path = None
        
        # Navigation Stack
        self.stacked_widget = QStackedWidget(self)
        self.init_screens()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stacked_widget)
        
        self.show_screen(0)

    def init_screens(self):
        # ---------------------------------------------
        # SCREEN 0: LOCK STATUS VIEW
        # ---------------------------------------------
        self.screen_lock = QFrame(self)
        self.screen_lock.setStyleSheet("background-color: #0D0D12; border: 1px solid #2A2518; border-radius: 16px;")
        lock_lay = QVBoxLayout(self.screen_lock)
        lock_lay.setContentsMargins(30, 20, 30, 25)
        lock_lay.setSpacing(12)
        
        # Close Bar
        bar = QHBoxLayout()
        bar.addStretch()
        btn_cls = QPushButton("✕", self)
        btn_cls.setStyleSheet("background: transparent; border: none; color: #9CA3AF; font-size: 11pt; min-width: 24px; max-width: 24px;")
        btn_cls.clicked.connect(self.close)
        bar.addWidget(btn_cls)
        lock_lay.addLayout(bar)
        
        # Header Brand
        logo = QLabel(self)
        logo.setObjectName("LockScreenLogo")
        logo.setFixedSize(45, 45)
        logo.setStyleSheet("border: none; background: transparent;")
        logo.setPixmap(get_logo_pixmap(45))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Akira", self)
        title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #FFFFFF; border: none; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("AI Video Generator - Developed by Malik Zia", self)
        subtitle.setStyleSheet("font-size: 9pt; color: #9CA3AF; border: none; background: transparent;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lock_lay.addWidget(logo, 0, Qt.AlignmentFlag.AlignCenter)
        lock_lay.addWidget(title)
        lock_lay.addWidget(subtitle)
        
        # Warning/Crown Card
        alert_box = QFrame(self)
        alert_box.setStyleSheet("background-color: rgba(197, 160, 89, 0.07); border: 1px solid rgba(197, 160, 89, 0.2); border-radius: 10px;")
        alert_lay = QVBoxLayout(alert_box)
        alert_lay.setContentsMargins(15, 12, 15, 12)
        alert_lay.setSpacing(6)
        
        crown = QLabel("👑", self)
        crown.setStyleSheet("font-size: 14pt; border: none; background: transparent;")
        crown.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        req_title = QLabel("Subscription Required", self)
        req_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #FFFFFF; border: none; background: transparent;")
        req_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        req_desc = QLabel(self.reason, self)
        req_desc.setStyleSheet("font-size: 8.5pt; color: #9CA3AF; border: none; background: transparent;")
        req_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        alert_lay.addWidget(crown)
        alert_lay.addWidget(req_title)
        alert_lay.addWidget(req_desc)
        lock_lay.addWidget(alert_box)
        
        # Actions
        btn_buy = QPushButton("⚡  Get AKIRA PRO — $15/month", self)
        btn_buy.setStyleSheet("background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #C5A059, stop:1 #A0793A); color: #0D0D0D; font-weight: bold; font-size: 10pt; border-radius: 8px; padding: 12px; border: none;")
        btn_buy.clicked.connect(lambda: self.show_screen(1))
        lock_lay.addWidget(btn_buy)
        
        hwid_lbl = QLabel("YOUR DEVICE ID (SEND TO SUPPORT)", self)
        hwid_lbl.setStyleSheet("font-size: 8pt; font-weight: bold; color: #6B7280; letter-spacing: 0.5px; border: none; background: transparent;")
        hwid_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lock_lay.addWidget(hwid_lbl)
        
        hwid_box = QHBoxLayout()
        hwid_edit = QLineEdit(self.device_id, self)
        hwid_edit.setReadOnly(True)
        hwid_edit.setStyleSheet("background-color: #070A13; border: 1px solid #1D263B; border-radius: 6px; padding: 6px; color: #9CA3AF; font-family: monospace; font-size: 8pt;")
        btn_copy = QPushButton("📋", self)
        btn_copy.setFixedSize(30, 30)
        btn_copy.setStyleSheet("background-color: #1F2937; border: 1px solid #1D263B; color: #FFFFFF; border-radius: 6px; font-size: 10pt;")
        btn_copy.clicked.connect(self.copy_hwid)
        hwid_box.addWidget(hwid_edit)
        hwid_box.addWidget(btn_copy)
        lock_lay.addLayout(hwid_box)
        
        self.btn_check = QPushButton("🔄  Check Activation Status", self)
        self.btn_check.setStyleSheet("background-color: #1F2937; border: 1px solid #1D263B; color: #FFFFFF; font-weight: bold; font-size: 9.5pt; border-radius: 8px; padding: 10px;")
        self.btn_check.clicked.connect(self.run_activation_check)
        lock_lay.addWidget(self.btn_check)
        
        self.stacked_widget.addWidget(self.screen_lock)

        # ---------------------------------------------
        # SCREEN 1: PRICING SCREEN
        # ---------------------------------------------
        self.screen_pricing = QFrame(self)
        self.screen_pricing.setStyleSheet("background-color: #0D0D12; border: 1px solid #2A2518; border-radius: 16px;")
        price_lay = QVBoxLayout(self.screen_pricing)
        price_lay.setContentsMargins(25, 20, 25, 25)
        price_lay.setSpacing(12)
        
        # Header block
        price_hdr = QHBoxLayout()
        btn_back0 = QPushButton("← Back", self)
        btn_back0.setStyleSheet("background: transparent; border: none; color: #8B5CF6; font-weight: bold; font-size: 9pt;")
        btn_back0.clicked.connect(lambda: self.show_screen(0))
        
        lbl_pr_title = QLabel("AKIRA PRO — Subscription", self)
        lbl_pr_title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #C5A059; border: none; background: transparent;")
        
        btn_cls1 = QPushButton("✕", self)
        btn_cls1.setStyleSheet("background: transparent; border: none; color: #9CA3AF; font-size: 11pt; min-width: 24px; max-width: 24px;")
        btn_cls1.clicked.connect(self.close)
        
        price_hdr.addWidget(btn_back0)
        price_hdr.addSpacing(10)
        price_hdr.addWidget(lbl_pr_title)
        price_hdr.addStretch()
        price_hdr.addWidget(btn_cls1)
        price_lay.addLayout(price_hdr)
        
        desc_lbl = QLabel("Professional AI Video Generator. Automate unlimited Dola AI videos from prompts — hands-free.", self)
        desc_lbl.setStyleSheet("font-size: 9.5pt; color: #9CA3AF; border: none; background: transparent;")
        price_lay.addWidget(desc_lbl)

        # Single plan card (centered, wide)
        single_card_row = QHBoxLayout()
        single_card_row.setContentsMargins(30, 0, 30, 0)
        self.card1 = PricingCard(
            "1 Month — AKIRA PRO",
            "Full access to all automation features.",
            15, 25, "Most Popular 🔥", "🎬", False, self
        )
        self.card1.clicked.connect(self.on_plan_selected)
        single_card_row.addWidget(self.card1)
        price_lay.addLayout(single_card_row)

        # Features list
        feats_box = QFrame(self)
        feats_box.setStyleSheet("background-color: #12131C; border: 1px solid #2A2518; border-radius: 10px;")
        feats_lay = QVBoxLayout(feats_box)
        feats_lay.setContentsMargins(18, 14, 18, 14)
        feats_lay.setSpacing(6)
        feats_title = QLabel("WHAT'S INCLUDED", self)
        feats_title.setStyleSheet("font-size: 7.5pt; font-weight: bold; color: #C5A059; letter-spacing: 1px; border: none; background: transparent;")
        feats_lay.addWidget(feats_title)

        # USP highlight row — Seedance 2.0
        usp_row = QHBoxLayout()
        usp_row.setSpacing(8)
        usp_dot = QLabel("★", self)
        usp_dot.setStyleSheet("color: #C5A059; font-size: 10pt; font-weight: bold; border: none; background: transparent;")
        usp_dot.setFixedWidth(16)
        usp_txt = QLabel("Generate 15-second AI videos using Seedance 2.0 — industry's best quality", self)
        usp_txt.setStyleSheet("font-size: 9pt; font-weight: bold; color: #C5A059; border: none; background: transparent;")
        usp_row.addWidget(usp_dot)
        usp_row.addWidget(usp_txt)
        usp_row.addStretch()
        feats_lay.addLayout(usp_row)

        sep = QFrame(self)
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #2A2518; max-height: 1px; border: none; margin: 2px 0;")
        feats_lay.addWidget(sep)

        features = [
            "Fully automated video generation from text prompts — no manual steps",
            "Batch generate multiple videos in one click",
            "Automatic video download directly to your PC",
            "Smart prompt optimization for best Dola AI results",
            "Multi-threaded engine — generate videos in parallel",
            "Built-in proxy support per account for safety",
            "PC desktop notification on every successful download",
            "Session vault — manage multiple Dola accounts",
            "Live log console — real-time progress tracking",
            "Headless / hidden browser mode for silent operation",
            "1-month full access + free updates during period",
        ]
        for feat in features:
            row = QHBoxLayout()
            row.setSpacing(8)
            dot = QLabel("✦", self)
            dot.setStyleSheet("color: #C5A059; font-size: 8pt; border: none; background: transparent;")
            dot.setFixedWidth(14)
            txt = QLabel(feat, self)
            txt.setStyleSheet("font-size: 8.5pt; color: #D1D5DB; border: none; background: transparent;")
            row.addWidget(dot)
            row.addWidget(txt)
            row.addStretch()
            feats_lay.addLayout(row)
        price_lay.addWidget(feats_box)
        
        # HWID Display at bottom
        hw_box = QHBoxLayout()
        hw_lbl = QLabel("DEVICE ID FOR UPGRADES:", self)
        hw_lbl.setStyleSheet("font-size: 8pt; font-weight: bold; color: #6B7280; border: none; background: transparent;")
        hw_val = QLineEdit(self.device_id, self)
        hw_val.setReadOnly(True)
        hw_val.setStyleSheet("background-color: #070A13; border: 1px solid #1D263B; color: #6B7280; padding: 4px; font-family: monospace; font-size: 8pt; border-radius: 4px;")
        hw_box.addWidget(hw_lbl)
        hw_box.addWidget(hw_val)
        price_lay.addLayout(hw_box)
        
        self.stacked_widget.addWidget(self.screen_pricing)

        # ---------------------------------------------
        # SCREEN 2: CHECKOUT WINDOW (Payment Methods)
        # ---------------------------------------------
        self.screen_checkout = QFrame(self)
        self.screen_checkout.setStyleSheet("background-color: #0D0D12; border: 1px solid #2A2518; border-radius: 16px;")
        chk_lay = QVBoxLayout(self.screen_checkout)
        chk_lay.setContentsMargins(25, 20, 25, 25)
        chk_lay.setSpacing(15)
        
        # Checkout Header with Wizards
        chk_hdr = QHBoxLayout()
        btn_back1 = QPushButton("← Back to Pricing", self)
        btn_back1.setStyleSheet("background: transparent; border: none; color: #8B5CF6; font-weight: bold; font-size: 9pt;")
        btn_back1.clicked.connect(lambda: self.show_screen(1))
        
        btn_cls2 = QPushButton("✕", self)
        btn_cls2.setStyleSheet("background: transparent; border: none; color: #9CA3AF; font-size: 11pt; min-width: 24px; max-width: 24px;")
        btn_cls2.clicked.connect(self.close)
        
        chk_hdr.addWidget(btn_back1)
        chk_hdr.addStretch()
        chk_hdr.addWidget(btn_cls2)
        chk_lay.addLayout(chk_hdr)
        
        # Step Wizard indicator
        wizard_lay = QHBoxLayout()
        wizard_lay.setContentsMargins(50, 0, 50, 0)
        self.wiz_step1 = QLabel("✓ Plan Summary", self)
        self.wiz_step1.setStyleSheet("color: #C5A059; font-weight: bold; font-size: 8.5pt; border: none; background: transparent;")
        self.wiz_step2 = QLabel("✓ Make Payment", self)
        self.wiz_step2.setStyleSheet("color: #C5A059; font-weight: bold; font-size: 8.5pt; border: none; background: transparent;")
        self.wiz_step3 = QLabel("3. Submit Proof", self)
        self.wiz_step3.setStyleSheet("color: #4B5563; font-size: 8.5pt; border: none; background: transparent;")
        
        div1 = QFrame(self)
        div1.setFrameShape(QFrame.Shape.HLine)
        div1.setStyleSheet("background-color: #C5A059; max-height: 2px; border: none;")
        div2 = QFrame(self)
        div2.setFrameShape(QFrame.Shape.HLine)
        div2.setStyleSheet("background-color: #2A2518; max-height: 2px; border: none;")
        
        wizard_lay.addWidget(self.wiz_step1)
        wizard_lay.addWidget(div1)
        wizard_lay.addWidget(self.wiz_step2)
        wizard_lay.addWidget(div2)
        wizard_lay.addWidget(self.wiz_step3)
        chk_lay.addLayout(wizard_lay)
        
        # Summary Header Panel
        self.summary_card = QFrame(self)
        self.summary_card.setStyleSheet("background-color: #12131C; border: 1px solid #2A2518; border-radius: 12px;")
        sum_lay = QHBoxLayout(self.summary_card)
        sum_lay.setContentsMargins(15, 12, 15, 12)
        
        sum_icon = QLabel("🛡️", self)
        sum_icon.setStyleSheet("font-size: 14pt; border: none; background: transparent;")
        
        self.lbl_selected_plan = QLabel("1 Month — AKIRA PRO", self)
        self.lbl_selected_plan.setStyleSheet("font-size: 12pt; font-weight: bold; color: #FFFFFF; border: none; background: transparent;")
        
        # Currency buttons layout
        curr_box = QHBoxLayout()
        curr_box.setSpacing(4)
        self.btn_usd = QPushButton("USD", self)
        self.btn_pkr = QPushButton("PKR", self)
        
        for b in [self.btn_usd, self.btn_pkr]:
            b.setFixedWidth(50)
            b.clicked.connect(self.on_currency_changed)
        self.set_active_currency_button(self.btn_usd)
        curr_box.addWidget(self.btn_usd)
        curr_box.addWidget(self.btn_pkr)
        
        self.lbl_amount = QLabel("$15", self)
        self.lbl_amount.setStyleSheet("font-size: 14pt; font-weight: bold; color: #C5A059; border: none; background: transparent;")
        
        sum_lay.addWidget(sum_icon)
        sum_lay.addWidget(self.lbl_selected_plan)
        sum_lay.addStretch()
        sum_lay.addLayout(curr_box)
        sum_lay.addWidget(self.lbl_amount)
        chk_lay.addWidget(self.summary_card)
        
        # Choose Payment Method section
        meth_hdr = QHBoxLayout()
        meth_title = QLabel("CHOOSE PAYMENT METHOD", self)
        meth_title.setStyleSheet("font-size: 9pt; font-weight: bold; color: #C5A059; border: none; background: transparent;")
        meth_note = QLabel("INSTANT ACTIVATION SUPPORT", self)
        meth_note.setStyleSheet("font-size: 7.5pt; color: #6B7280; border: none; background: transparent;")
        meth_hdr.addWidget(meth_title)
        meth_hdr.addStretch()
        meth_hdr.addWidget(meth_note)
        chk_lay.addLayout(meth_hdr)
        
        # Grid of payment method options — only 3 methods
        pm_grid = QGridLayout()
        pm_grid.setSpacing(12)
        
        self.pm_binance = PaymentMethodButton("Binance (USDT)", "🟡", True, self)
        self.pm_easypaisa = PaymentMethodButton("Easypaisa (PKR)", "💚", False, self)
        self.pm_jazzcash = PaymentMethodButton("JazzCash (PKR)", "🔴", False, self)
        
        # Connect actions
        for pm in [self.pm_binance, self.pm_easypaisa, self.pm_jazzcash]:
            pm.clicked.connect(self.on_pm_clicked)
            
        pm_grid.addWidget(self.pm_binance, 0, 0)
        pm_grid.addWidget(self.pm_easypaisa, 0, 1)
        pm_grid.addWidget(self.pm_jazzcash, 0, 2)
        chk_lay.addLayout(pm_grid)
        
        self.stacked_widget.addWidget(self.screen_checkout)

        # ---------------------------------------------
        # SCREEN 3: SUBMIT PROOF & VERIFICATION WINDOW
        # ---------------------------------------------
        self.screen_proof = QFrame(self)
        self.screen_proof.setStyleSheet("background-color: #0D0D12; border: 1px solid #2A2518; border-radius: 16px;")
        prf_lay = QVBoxLayout(self.screen_proof)
        prf_lay.setContentsMargins(25, 20, 25, 25)
        prf_lay.setSpacing(15)
        
        # Header with navigation
        prf_hdr = QHBoxLayout()
        btn_back2 = QPushButton("← Change Payment Method", self)
        btn_back2.setStyleSheet("background: transparent; border: none; color: #8B5CF6; font-weight: bold; font-size: 9pt;")
        btn_back2.clicked.connect(lambda: self.show_screen(2))
        
        btn_cls3 = QPushButton("✕", self)
        btn_cls3.setStyleSheet("background: transparent; border: none; color: #9CA3AF; font-size: 11pt; min-width: 24px; max-width: 24px;")
        btn_cls3.clicked.connect(self.close)
        
        prf_hdr.addWidget(btn_back2)
        prf_hdr.addStretch()
        prf_hdr.addWidget(btn_cls3)
        prf_lay.addLayout(prf_hdr)
        
        # Step Wizard 3 indicator
        wizard_lay3 = QHBoxLayout()
        wizard_lay3.setContentsMargins(50, 0, 50, 0)
        self.wiz3_1 = QLabel("✓ Plan Summary", self)
        self.wiz3_1.setStyleSheet("color: #C5A059; font-weight: bold; font-size: 8.5pt; border: none; background: transparent;")
        self.wiz3_2 = QLabel("✓ Make Payment", self)
        self.wiz3_2.setStyleSheet("color: #C5A059; font-weight: bold; font-size: 8.5pt; border: none; background: transparent;")
        self.wiz3_3 = QLabel("✓ Submit Proof", self)
        self.wiz3_3.setStyleSheet("color: #C5A059; font-weight: bold; font-size: 8.5pt; border: none; background: transparent;")
        
        div1_3 = QFrame(self)
        div1_3.setFrameShape(QFrame.Shape.HLine)
        div1_3.setStyleSheet("background-color: #C5A059; max-height: 2px; border: none;")
        div2_3 = QFrame(self)
        div2_3.setFrameShape(QFrame.Shape.HLine)
        div2_3.setStyleSheet("background-color: #C5A059; max-height: 2px; border: none;")
        
        wizard_lay3.addWidget(self.wiz3_1)
        wizard_lay3.addWidget(div1_3)
        wizard_lay3.addWidget(self.wiz3_2)
        wizard_lay3.addWidget(div2_3)
        wizard_lay3.addWidget(self.wiz3_3)
        prf_lay.addLayout(wizard_lay3)
        
        # Summary Header Panel for Proof Screen
        self.summary_card3 = QFrame(self)
        self.summary_card3.setStyleSheet("background-color: #12131C; border: 1px solid #2A2518; border-radius: 12px;")
        sum_lay3 = QHBoxLayout(self.summary_card3)
        sum_lay3.setContentsMargins(15, 12, 15, 12)
        
        sum_icon3 = QLabel("🛡️", self)
        sum_icon3.setStyleSheet("font-size: 14pt; border: none; background: transparent;")
        
        self.lbl_selected_plan3 = QLabel("1 Month — AKIRA PRO", self)
        self.lbl_selected_plan3.setStyleSheet("font-size: 12pt; font-weight: bold; color: #FFFFFF; border: none; background: transparent;")
        
        self.lbl_amount3 = QLabel("$15", self)
        self.lbl_amount3.setStyleSheet("font-size: 14pt; font-weight: bold; color: #C5A059; border: none; background: transparent;")
        
        sum_lay3.addWidget(sum_icon3)
        sum_lay3.addWidget(self.lbl_selected_plan3)
        sum_lay3.addStretch()
        sum_lay3.addWidget(self.lbl_amount3)
        prf_lay.addWidget(self.summary_card3)
        
        # Split Split Panel (Account details vs Upload widgets)
        split_box = QHBoxLayout()
        split_box.setSpacing(15)
        
        # Left Panel (Account Details)
        self.account_panel = QFrame(self)
        self.account_panel.setStyleSheet("background-color: #12131C; border: 1px solid #2A2518; border-radius: 12px;")
        acc_lay = QVBoxLayout(self.account_panel)
        acc_lay.setContentsMargins(15, 15, 15, 15)
        acc_lay.setSpacing(10)
        
        self.lbl_pm_title = QLabel("JAZZCASH (PKR)", self)
        self.lbl_pm_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #FFFFFF; border: none; background: transparent;")
        
        pm_net = QLabel("PKR NETWORK", self)
        pm_net.setStyleSheet("font-size: 6.5pt; font-weight: bold; color: #FF007F; background-color: rgba(255, 0, 127, 0.1); border-radius: 4px; padding: 2px 6px; border: none;")
        
        hdr_lay = QHBoxLayout()
        hdr_lay.addWidget(self.lbl_pm_title)
        hdr_lay.addStretch()
        hdr_lay.addWidget(pm_net)
        acc_lay.addLayout(hdr_lay)
        
        acc_sub = QLabel("Send exact amount to this verified account.", self)
        acc_sub.setStyleSheet("font-size: 8.5pt; color: #9CA3AF; border: none; background: transparent;")
        acc_lay.addWidget(acc_sub)
        
        # Account detail boxes with copy button
        acc_num_lbl = QLabel("ACCOUNT NUMBER:", self)
        acc_num_lbl.setStyleSheet("font-size: 7.5pt; font-weight: bold; color: #6B7280; border: none; background: transparent;")
        acc_lay.addWidget(acc_num_lbl)
        
        box_num = QHBoxLayout()
        self.edit_acc_num = QLineEdit("03244481248", self)
        self.edit_acc_num.setReadOnly(True)
        self.edit_acc_num.setStyleSheet("background-color: #070A13; border: 1px solid #1D263B; color: #34D399; font-family: monospace; font-size: 9pt; padding: 6px; border-radius: 6px;")
        btn_copy_num = QPushButton("📋", self)
        btn_copy_num.setFixedSize(30, 30)
        btn_copy_num.setStyleSheet("background-color: #1F2937; border: 1px solid #1D263B; color: #FFFFFF; border-radius: 6px; font-size: 10pt;")
        btn_copy_num.clicked.connect(lambda: self.copy_to_clipboard(self.edit_acc_num.text()))
        box_num.addWidget(self.edit_acc_num)
        box_num.addWidget(btn_copy_num)
        acc_lay.addLayout(box_num)
        
        acc_name_lbl = QLabel("ACCOUNT NAME:", self)
        acc_name_lbl.setStyleSheet("font-size: 7.5pt; font-weight: bold; color: #6B7280; border: none; background: transparent;")
        acc_lay.addWidget(acc_name_lbl)
        
        box_name = QHBoxLayout()
        self.edit_acc_name = QLineEdit("Zia Ullah", self)
        self.edit_acc_name.setReadOnly(True)
        self.edit_acc_name.setStyleSheet("background-color: #070A13; border: 1px solid #1D263B; color: #FFFFFF; font-weight: bold; font-size: 9pt; padding: 6px; border-radius: 6px;")
        btn_copy_name = QPushButton("📋", self)
        btn_copy_name.setFixedSize(30, 30)
        btn_copy_name.setStyleSheet("background-color: #1F2937; border: 1px solid #1D263B; color: #FFFFFF; border-radius: 6px; font-size: 10pt;")
        btn_copy_name.clicked.connect(lambda: self.copy_to_clipboard(self.edit_acc_name.text()))
        box_name.addWidget(self.edit_acc_name)
        box_name.addWidget(btn_copy_name)
        acc_lay.addLayout(box_name)

        # WhatsApp Channel link below the number
        channel_lbl = QLabel("WHATSAPP CHANNEL:", self)
        channel_lbl.setStyleSheet("font-size: 7.5pt; font-weight: bold; color: #6B7280; border: none; background: transparent;")
        acc_lay.addWidget(channel_lbl)
        
        box_chan = QHBoxLayout()
        edit_chan = QLineEdit("https://whatsapp.com/channel/0029VbCFttnEVccAgEEkGY1u", self)
        edit_chan.setReadOnly(True)
        edit_chan.setStyleSheet("background-color: #070A13; border: 1px solid #1D263B; color: #3B82F6; font-size: 8.5pt; padding: 6px; border-radius: 6px;")
        btn_copy_chan = QPushButton("📋", self)
        btn_copy_chan.setFixedSize(30, 30)
        btn_copy_chan.setStyleSheet("background-color: #1F2937; border: 1px solid #1D263B; color: #FFFFFF; border-radius: 6px; font-size: 10pt;")
        btn_copy_chan.clicked.connect(lambda: self.copy_to_clipboard(edit_chan.text()))
        box_chan.addWidget(edit_chan)
        box_chan.addWidget(btn_copy_chan)
        acc_lay.addLayout(box_chan)
        
        # Warning card
        warn_card = QFrame(self)
        warn_card.setStyleSheet("background-color: rgba(217, 119, 6, 0.08); border: 1px solid rgba(217, 119, 6, 0.2); border-radius: 8px;")
        warn_lay = QVBoxLayout(warn_card)
        warn_lay.setContentsMargins(10, 10, 10, 10)
        warn_lbl = QLabel("⚠️ WARNING: REQUIRED STEP", self)
        warn_lbl.setStyleSheet("font-size: 7.5pt; font-weight: bold; color: #F59E0B; border: none; background: transparent;")
        warn_desc = QLabel("Screenshot is mandatory. Account will not be activated without valid payment proof.", self)
        warn_desc.setStyleSheet("font-size: 7.5pt; color: #D1D5DB; border: none; background: transparent;")
        warn_desc.setWordWrap(True)
        warn_lay.addWidget(warn_lbl)
        warn_lay.addWidget(warn_desc)
        acc_lay.addWidget(warn_card)
        
        split_box.addWidget(self.account_panel)
        
        # Right Panel (Upload Proof Widget)
        self.upload_panel = QFrame(self)
        self.upload_panel.setStyleSheet("background-color: #12131C; border: 1px solid #2A2518; border-radius: 12px;")
        upl_lay = QVBoxLayout(self.upload_panel)
        upl_lay.setContentsMargins(15, 15, 15, 15)
        upl_lay.setSpacing(10)
        
        upl_title = QLabel("📤 UPLOAD VERIFICATION", self)
        upl_title.setStyleSheet("font-size: 9pt; font-weight: bold; color: #FFFFFF; border: none; background: transparent;")
        upl_lay.addWidget(upl_title)
        
        # Dotted Drag & Drop click zone
        self.drop_zone = QPushButton(self)
        self.drop_zone.setStyleSheet("""
            QPushButton {
                background-color: #0D0D12;
                border: 2px dashed #2A2518;
                border-radius: 8px;
                color: #9CA3AF;
                padding: 20px;
                font-size: 8.5pt;
                text-align: center;
            }
            QPushButton:hover {
                border-color: #C5A059;
                color: #C5A059;
            }
        """)
        self.drop_zone.setText("☁️\nSELECT PAYMENT SCREENSHOT\nLIMIT: 10MB (PNG/JPG)")
        self.drop_zone.clicked.connect(self.select_screenshot)
        upl_lay.addWidget(self.drop_zone)
        
        # Reference Text Input
        self.edit_ref = QLineEdit(self)
        self.edit_ref.setPlaceholderText("Optional: Proof ID or Reference Name")
        self.edit_ref.setStyleSheet("background-color: #070A13; border: 1px solid #1D263B; color: #FFFFFF; padding: 6px; border-radius: 6px; font-size: 8.5pt;")
        upl_lay.addWidget(self.edit_ref)
        
        # Action Buttons
        self.btn_submit_proof = QPushButton("✓  SUBMIT PROOF", self)
        self.btn_submit_proof.setStyleSheet("background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #C5A059, stop:1 #A0793A); color: #0D0D0D; font-weight: bold; font-size: 9.5pt; border-radius: 8px; padding: 10px; border: none;")
        self.btn_submit_proof.clicked.connect(self.submit_proof)
        
        btn_chat = QPushButton("💬  CHAT WITH ADMIN", self)
        btn_chat.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #374151;
                color: #10B981;
                font-weight: bold;
                font-size: 9pt;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(16, 185, 129, 0.08);
                border-color: #10B981;
            }
        """)
        btn_chat.clicked.connect(self.chat_with_admin)
        
        upl_lay.addWidget(self.btn_submit_proof)
        upl_lay.addWidget(btn_chat)
        
        split_box.addWidget(self.upload_panel)
        prf_lay.addLayout(split_box)
        
        self.stacked_widget.addWidget(self.screen_proof)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def copy_hwid(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.device_id)
        QMessageBox.information(self, "Copied", "Device ID copied to clipboard!")

    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "Copied", "Copied to clipboard!")

    def show_screen(self, index):
        if index == 0:
            self.setFixedSize(550, 520)
        else:
            self.setFixedSize(920, 650)
            
        # Center the window on screen after resize
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)
        
        self.stacked_widget.setCurrentIndex(index)

    def on_plan_selected(self, plan_name, price_usd):
        self.selected_plan = plan_name
        self.price_usd = price_usd
        
        self.lbl_selected_plan.setText(plan_name)
        self.lbl_selected_plan3.setText(plan_name)
        
        # Toggle default currency back to USD on new plan selection
        self.on_currency_changed(target_btn=self.btn_usd)
        self.show_screen(2)

    def set_active_currency_button(self, active_btn):
        for btn in [self.btn_usd, self.btn_pkr]:
            if btn == active_btn:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #C5A059;
                        color: #0D0D0D;
                        font-weight: bold;
                        border: none;
                        border-radius: 4px;
                        padding: 4px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1A1810;
                        color: #9CA3AF;
                        border: 1px solid #2A2518;
                        border-radius: 4px;
                        padding: 4px;
                    }
                    QPushButton:hover {
                        background-color: #221F14;
                        color: #C5A059;
                    }
                """)

    def on_currency_changed(self, target_btn=None):
        if not target_btn:
            target_btn = self.sender()
            
        self.set_active_currency_button(target_btn)
        
        # $15 USD → ~4,200 PKR (approx 280 PKR per $1)
        is_usd = (target_btn == self.btn_usd)
        is_pkr = (target_btn == self.btn_pkr)
        
        if is_usd:
            self.lbl_amount.setText(f"${self.price_usd}")
            self.lbl_amount3.setText(f"${self.price_usd}")
        elif is_pkr:
            pkr_val = int(self.price_usd * 280)
            self.lbl_amount.setText(f"{pkr_val:,} PKR")
            self.lbl_amount3.setText(f"{pkr_val:,} PKR")
            
        # Enable / Disable payment buttons based on currency
        self.pm_binance.set_state(is_usd)
        self.pm_easypaisa.set_state(is_pkr)
        self.pm_jazzcash.set_state(is_pkr)

    def on_pm_clicked(self):
        pm_btn = self.sender()
        if not pm_btn.is_active:
            return
            
        self.selected_method = pm_btn.name
        self.lbl_pm_title.setText(self.selected_method.upper())
        
        # Configure account details based on selected payment platform
        # For JazzCash / Easypaisa: Zia Ullah, 03244481248
        if "jazzcash" in self.selected_method.lower() or "easypaisa" in self.selected_method.lower():
            self.edit_acc_num.setText("03244481248")
            self.edit_acc_name.setText("Zia Ullah")
        elif "binance" in self.selected_method.lower():
            self.edit_acc_num.setText(self.config_data.get("usdt_address", "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"))
            self.edit_acc_name.setText("Binance USDT (BEP20 Network)")
        else:
            self.edit_acc_num.setText("03244481248")
            self.edit_acc_name.setText("Zia Ullah")
            
        # Reset upload zone style and text
        self.drop_zone.setText("☁️\nSELECT PAYMENT SCREENSHOT\nLIMIT: 10MB (PNG/JPG)")
        self.drop_zone.setStyleSheet("""
            QPushButton {
                background-color: #070A13;
                border: 2px dashed #374151;
                border-radius: 8px;
                color: #9CA3AF;
                padding: 20px;
                font-size: 8.5pt;
                text-align: center;
            }
            QPushButton:hover {
                border-color: #8B5CF6;
                color: #FFFFFF;
            }
        """)
        self.selected_screenshot_path = None
        
        self.show_screen(3)

    def select_screenshot(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Payment Screenshot", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.selected_screenshot_path = path
            self.drop_zone.setText(f"✓ Screenshot Selected:\n{os.path.basename(path)}")
            self.drop_zone.setStyleSheet("""
                QPushButton {
                    background-color: #070A13;
                    border: 2px dashed #10B981;
                    border-radius: 8px;
                    color: #10B981;
                    padding: 20px;
                    font-size: 8.5pt;
                    text-align: center;
                }
            """)

    def submit_proof(self):
        if not getattr(self, "selected_screenshot_path", None):
            QMessageBox.warning(self, "Screenshot Required", "Please select your payment screenshot proof first.")
            return
            
        ref_name = self.edit_ref.text().strip()
        ref_text = f" (Ref: {ref_name})" if ref_name else ""
        
        # Prepopulate direct support chat details
        msg = f"Hello Admin, I have submitted a subscription payment proof for Akira.\n\n" \
              f"Device ID: {self.device_id}\n" \
              f"Plan Selected: {self.selected_plan}\n" \
              f"Payment Method: {self.selected_method}{ref_text}\n\n" \
              f"Please verify my activation status."
              
        QMessageBox.information(
            self, 
            "Proof Submitted", 
            "Your proof details have been recorded.\n"
            "Opening Support Chat now so you can send the payment receipt screenshot directly to Zia Ullah."
        )
        
        # Open contact url (whatsapp/telegram link)
        contact_url = self.config_data.get("admin_contact_url", "https://wa.me/923477399073")
        full_url = f"{contact_url}?text={urllib.parse.quote(msg)}"
        
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl(full_url))

    def chat_with_admin(self):
        contact_url = self.config_data.get("admin_contact_url", "https://wa.me/923477399073")
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl(contact_url))

    def run_activation_check(self):
        self.btn_check.setText("Verifying with Cloud...")
        self.btn_check.setEnabled(False)
        QApplication.processEvents()
        
        web_url = self.config_data.get("web_app_url", "")
        if not web_url or "PASTE_YOUR_DEPLOYED" in web_url:
            QMessageBox.critical(
                self, 
                "Configuration Error", 
                "Google Sheet Web App URL is not configured.\n"
                "Please configure it inside 'license_config.json' file first."
            )
            self.btn_check.setText("🔄  Check Activation Status")
            self.btn_check.setEnabled(True)
            return
            
        res = check_license_status(web_url, self.device_id)
        if res.get("status") == "active":
            QMessageBox.information(self, "Activated", "License verified successfully! Unlocking Akira.")
            self.accept_unlock(res)
        else:
            reason = res.get("message", "Your license is inactive, expired, or invalid. Please check your subscription status or contact support.")
            QMessageBox.warning(self, "Access Denied", f"Activation Failed: {reason}")
            self.btn_check.setText("🔄  Check Activation Status")
            self.btn_check.setEnabled(True)

    def accept_unlock(self, res_data):
        # Save activation state locally next to executable
        try:
            import sys
            import json
            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(sys.executable)
            else:
                exe_dir = os.path.dirname(os.path.abspath(__file__))
            state_path = os.path.join(exe_dir, "activation_state.json")
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump({"activated": True}, f)
        except Exception:
            pass

        self.main_win = NexusAutomatorWindow()
        
        # Pass subscription metadata to main window
        plan = res_data.get("plan", "Trial")
        time_left_sec = res_data.get("time_left_seconds", 0)
        
        plan_text = format_license_plan_text(plan, time_left_sec)
        self.main_win.lbl_sub.setText(plan_text)
        self.main_win.show()
        self.close()

# --- SPLASH SCREEN AND BACKGROUND ACTIVATION CHECKER ---
class ActivationCheckThread(QThread):
    finished_signal = pyqtSignal(dict)
    
    def __init__(self, web_url, device_id):
        super().__init__()
        self.web_url = web_url
        self.device_id = device_id
        
    def run(self):
        import time
        start_time = time.time()
        try:
            res = check_license_status(self.web_url, self.device_id)
        except Exception:
            res = {}
        elapsed = time.time() - start_time
        if elapsed < 1.5:
            time.sleep(1.5 - elapsed)
        self.finished_signal.emit(res)

class AkiraSplashScreen(QWidget):
    def __init__(self, device_id, config_data):
        super().__init__()
        self.device_id = device_id
        self.config_data = config_data
        
        self.setWindowTitle("Akira AI Video Generator")
        self.setFixedSize(500, 270)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Load window icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.init_ui()
        
    def init_ui(self):
        container = QFrame(self)
        container.setObjectName("SplashContainer")
        container.setStyleSheet("""
            QFrame#SplashContainer {
                background-color: #0C0D14;
                border: 1px solid #C5A059;
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(25, 25, 25, 20)
        layout.setSpacing(15)
        
        # Top half: 2-column layout (Left: Logo + Name, Right: Text details)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)
        
        # Left side: Logo only
        left_layout = QVBoxLayout()
        left_layout.setSpacing(0)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.logo = QLabel(self)
        self.logo.setFixedSize(80, 80)
        self.logo.setPixmap(get_logo_pixmap(80))
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.logo)
        name_lbl = QLabel("AKIRA PRO", self)
        name_lbl.setStyleSheet("font-family: 'Outfit', 'Inter', sans-serif; font-size: 12pt; font-weight: bold; color: #C5A059;")
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(name_lbl)
        
        # Vertical divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setStyleSheet("background-color: #374151; max-width: 1px; min-height: 120px;")
        
        # Right side: Detail labels (all capitals)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(6)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_lbl = QLabel("AKIRA", self)
        title_lbl.setStyleSheet("font-family: 'Outfit', 'Inter', sans-serif; font-size: 24pt; font-weight: 800; color: #FFFFFF; letter-spacing: 2px;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(title_lbl)
        
        dev_name = QLabel("MALIK ZIA", self)
        dev_name.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 10pt; font-weight: 600; color: #D1D5DB; letter-spacing: 0.5px;")
        dev_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(dev_name)
        
        team_name = QLabel("AKIRA DEVELOPMENT TEAM", self)
        team_name.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 9pt; font-weight: 500; color: #9CA3AF; letter-spacing: 0.5px;")
        team_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(team_name)
        
        version_lbl = QLabel(f"VERSION {AKIRA_APP_VERSION}", self)
        version_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 9pt; font-weight: 500; color: #C5A059; letter-spacing: 0.5px;")
        version_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(version_lbl)
        
        # Assemble columns
        top_layout.addLayout(left_layout, 1)
        top_layout.addWidget(divider)
        top_layout.addLayout(right_layout, 1)
        layout.addLayout(top_layout)
        
        # Bottom progress bar (flat, sharp corners)
        self.pbar = QProgressBar(self)
        self.pbar.setFixedHeight(6)
        self.pbar.setTextVisible(False)
        self.pbar.setRange(0, 0)
        self.pbar.setStyleSheet("""
            QProgressBar {
                background-color: #161722;
                border: none;
                border-radius: 0px;
            }
            QProgressBar::chunk {
                background-color: #C5A059;
                border-radius: 0px;
            }
        """)
        layout.addWidget(self.pbar)
        
        # Status details label below the progress bar
        self.lbl_status = QLabel("Setup Environment...", self)
        self.lbl_status.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 9pt; color: #9CA3AF;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_status)
        
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.addWidget(container)
        
        self.center_on_screen()
        
    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(
            int((screen.width() - self.width()) / 2),
            int((screen.height() - self.height()) / 2)
        )
        
    def start_check(self, web_url):
        self.thread = ActivationCheckThread(web_url, self.device_id)
        self.thread.finished_signal.connect(self.on_check_finished)
        self.thread.start()
        
    def on_check_finished(self, res):
        self.close()
        
        # Only allow entry if status is active
        if res.get("status") == "active":
            self.main_win = NexusAutomatorWindow()
            plan = res.get("plan", "Free Trial")
            time_left_sec = res.get("time_left_seconds", 0)
            plan_text = format_license_plan_text(plan, time_left_sec)
            self.main_win.lbl_sub.setText(plan_text)
            self.main_win.show()
        else:
            # Capture specific error message/reason from web app response
            reason = res.get("message")
            if not reason:
                if res.get("status") == "expired":
                    reason = "Your subscription has expired. Please renew your plan."
                elif res.get("status") == "locked":
                    reason = "This device has been locked by admin support."
                elif res.get("status") == "unauthorized":
                    reason = "Unauthorized device signature detected."
                else:
                    reason = "Unable to connect to activation server. Please check your internet connection."
            
            self.lock_screen = AkiraLockScreen(self.device_id, self.config_data, reason=reason)
            self.lock_screen.show()

# --- APP BOOTSTRAP ---
if __name__ == "__main__":
    # Programmatically hide the Windows command prompt console (black screen) immediately on launch
    try:
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0) # 0 = SW_HIDE
    except Exception:
        pass

    # Runtime Anti-Debugging Security Checks
    import sys
    import ctypes
    try:
        if hasattr(ctypes, "windll") and hasattr(ctypes.windll, "kernel32"):
            # 1. Standard WinAPI IsDebuggerPresent check
            if ctypes.windll.kernel32.IsDebuggerPresent() != 0:
                sys.exit(1)
            # 2. CheckRemoteDebuggerPresent (detects attached debuggers like x64dbg/IDA)
            is_remote = ctypes.c_int(0)
            ctypes.windll.kernel32.CheckRemoteDebuggerPresent(
                ctypes.windll.kernel32.GetCurrentProcess(), 
                ctypes.byref(is_remote)
            )
            if is_remote.value != 0:
                sys.exit(1)
    except Exception:
        pass
        
    if sys.gettrace() is not None:
        sys.exit(1)

    # Force Windows to display the custom window icon in Taskbar
    try:
        import ctypes
        myappid = 'malikzia.akira.videogenerator.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    app = QApplication(sys.argv)
    
    # 1. Fetch hardware unique Device ID
    device_id = get_device_id()
    
    # 2. Use embedded configurations
    config_data = CONFIG_DATA
    web_url = config_data.get("web_app_url", "")
    
    # 3. Check local activation state
    local_activated = False
    try:
        import json
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
        else:
            exe_dir = os.path.dirname(os.path.abspath(__file__))
        state_path = os.path.join(exe_dir, "activation_state.json")
        if os.path.exists(state_path):
            with open(state_path, "r", encoding="utf-8") as f:
                state_data = json.load(f)
                local_activated = state_data.get("activated", False)
    except Exception:
        pass

    if web_url and "PASTE_YOUR_DEPLOYED" not in web_url:
        # Show engaging Splash Screen while doing activation check in background!
        splash = AkiraSplashScreen(device_id, config_data)
        splash.show()
        splash.start_check(web_url)
    else:
        # Show main workspace window directly
        main_win = NexusAutomatorWindow()
        main_win.show()
        
    sys.exit(app.exec())

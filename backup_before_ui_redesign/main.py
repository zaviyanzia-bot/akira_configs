# main.py — PyQt6 Application for Nexus Automator

import sys
import os
import random
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QLabel, QLineEdit,
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame, QFileDialog, QTextEdit,
                             QProgressBar, QListWidget, QListWidgetItem, QSizePolicy,
                             QDialog, QMessageBox, QStackedWidget, QScrollArea,
                             QAbstractItemView)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer, QRectF, QByteArray, QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QPainter, QPen, QBrush, QLinearGradient, QPixmap

from logo_data import LOGO_PNG_B64

# Hardcoded configuration for license check and support links
CONFIG_DATA = {
    "web_app_url": "https://script.google.com/macros/s/AKfycbwnVLyth13MpEXA0Clh79Vr7VyuIJZMAb9R_fmn5SX1Biwxakr_4g5AmUQ5Jyxny9v-tA/exec",
    "bitcoin_address": "1BvBMSEYstNvjT25AnUiZA2F4t6yy42yX",
    "usdt_address": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
    "admin_contact_url": "https://wa.me/923477399073"
}

def get_logo_pixmap(size=32):
    pix = QPixmap()
    pix.loadFromData(QByteArray.fromBase64(LOGO_PNG_B64.encode()))
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
        
        # Right text block
        self.text_widget = QWidget(self)
        self.text_widget.setStyleSheet("background: transparent; border: none;")
        self.text_lay = QVBoxLayout(self.text_widget)
        self.text_lay.setContentsMargins(0, 0, 0, 0)
        self.text_lay.setSpacing(1)
        
        self.lbl_title = QLabel(self.title, self)
        self.lbl_title.setStyleSheet("font-weight: bold; border: none; background: transparent;")
        
        self.lbl_sub = QLabel(self.subtitle, self)
        self.lbl_sub.setStyleSheet("border: none; background: transparent;")
        
        self.text_lay.addWidget(self.lbl_title)
        self.text_lay.addWidget(self.lbl_sub)
        self.lay.addWidget(self.text_widget, 1)
        
        self.update_state()

    def set_active(self, active):
        self.active = active
        self.update_state()
        self.update() # Force repaint

    def update_state(self):
        if self.active:
            self.lbl_title.setStyleSheet("font-weight: bold; color: #FFFFFF; font-size: 9.5pt; border: none; background: transparent;")
            self.lbl_sub.setStyleSheet("color: #C084FC; font-size: 8.0pt; border: none; background: transparent;")
            
            # Draw raw white vector icon
            pix = QPixmap()
            pix.loadFromData(QByteArray.fromBase64(self.icon_svg_base64.encode()))
            self.icon_lbl.setPixmap(pix.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.lbl_title.setStyleSheet("font-weight: bold; color: #9CA3AF; font-size: 9.5pt; border: none; background: transparent;")
            self.lbl_sub.setStyleSheet("color: #6B7280; font-size: 8.0pt; border: none; background: transparent;")
            
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
            
            # Background dark transparent gradient
            grad_bg = QLinearGradient(0, 0, self.width(), 0)
            grad_bg.setColorAt(0.0, QColor(17, 24, 39, 230))
            grad_bg.setColorAt(1.0, QColor(139, 92, 246, 40))
            
            painter.setBrush(QBrush(grad_bg))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)
            
            # Glowing gradient outline border
            grad_border = QLinearGradient(0, 0, self.width(), 0)
            grad_border.setColorAt(0.0, QColor("#3B82F6"))
            grad_border.setColorAt(1.0, QColor("#8B5CF6"))
            
            pen = QPen(QBrush(grad_border), 1.5)
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
        
        # Draw background ring (dark grey border)
        pen_bg = QPen(QColor("#1E293B"), 6)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 0, 360 * 16)
        
        # Calculate percentage span angle
        percentage = (self.value / self.max_value) if self.max_value > 0 else 0
        span_angle = -int(percentage * 360 * 16)
        
        # Draw progress arc (purple/blue gradient accent)
        pen_fg = QPen(QColor("#8B5CF6"), 6)
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
        painter.setPen(QColor("#9CA3AF"))
        painter.drawText(QRectF(6, 48, 78, 16), Qt.AlignmentFlag.AlignCenter, self.text_label)

from styles import UI_MASTER_QSS
from automation import DolaAutomationBot

# --- WORKER THREAD FOR PLAYWRIGHT RUNS ---
class PlaywrightWorker(QThread):
    log_signal = pyqtSignal(str, str)         # (type, message)
    status_signal = pyqtSignal(int, str, str) # (row_id, status, action)
    finished_signal = pyqtSignal(int, bool)   # (row_id, success)

    def __init__(self, bot, row_id, prompt, model, duration, ratio, setup_mode=False, is_image=False, proxy_list=None, sms_key=None, sms_country="0"):
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
            sms_country=self.sms_country
        )
        self.error_reason = getattr(self.bot, "last_error_reason", None)
        self.finished_signal.emit(self.row_id, success)


# --- MAIN APPLICATION WINDOW ---
class NexusAutomatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Akira")
        
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
        self.setWindowTitle("Akira AI Video Generator")
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

        # Check license config for client mode
        self.client_mode = False
        try:
            if getattr(sys, 'frozen', False):
                config_dir = os.path.dirname(sys.executable)
            else:
                config_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(config_dir, "license_config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    cfg = json.load(f)
                    self.client_mode = cfg.get("client_mode", False)
        except Exception:
            pass

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

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)



    def init_ui(self):
        # Base central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout: Sidebar + Workspace
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==========================================
        # LEFT SIDEBAR
        # ==========================================
        sidebar = QFrame()
        sidebar.setObjectName("SidebarPanel")
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(14, 20, 14, 14)
        sidebar_layout.setSpacing(15)

        # Brand header
        brand_layout = QHBoxLayout()
        self.brand_logo = QLabel()
        self.brand_logo.setObjectName("ProfileAvatar")
        self.brand_logo.setPixmap(get_logo_pixmap(32))
        self.brand_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        brand_info = QVBoxLayout()
        brand_name = QLabel("Akira")
        brand_name.setObjectName("SidebarBrandName")
        brand_version = QLabel("AI ENGINE V1.0.0")
        brand_version.setObjectName("SidebarBrandVersion")
        brand_info.addWidget(brand_name)
        brand_info.addWidget(brand_version)
        brand_info.setSpacing(2)
        
        brand_layout.addWidget(self.brand_logo)
        brand_layout.addLayout(brand_info)
        brand_layout.addStretch()
        sidebar_layout.addLayout(brand_layout)

        # Menu items layout
        self.sidebar_menu = QListWidget(self)
        self.sidebar_menu.setObjectName("SidebarMenu")
        self.sidebar_menu.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sidebar_menu.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Vector Icons in Base64
        sparkles_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI0ZGRkZGRiI+PHBhdGggZD0iTTEyIDJMMTQuNSA5LjVMMjIgMTJMMTQuNSAxNC41TDEyIDIyTDkuNSAxNC41TDIgMTJMOS41IDkuNUwxMiAyWiBNMTkgMTRMMjAuMTUgMTcuNUwyMyAxOEwyMC4xNSAxOC41TDE5IDIyTDE3Ljg1IDE4LjVMMTUgMThMMTcuODUgMTcuNUwxOSAxNFogTTcgNkw4LjE1IDkuNUwxMCAxTDguMTUgMTAuNUw3IDEyTDUuODUgMTAuNUwzIDEwTDUuODUgOS41TDcgNloiLz48L3N2Zz4="
        home_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI0ZGRkZGRiI+PHBhdGggZD0iTTEwIDIwdi-2aDR2Nmg1di04aDNMMTIgMyAyIDEyaDN2OHoiLz48L3N2Zz4="
        image_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI0ZGRkZGRiI+PHBhdGggZD0iTTIxIDE5VjVjMC0xLjEtLjktMi0yLTJINWMtMS4xIDAgLTIgLjktMiAydjE0YzAgMS4xLjkgMiAyIDJoMTRjMS4xIDAgMi0uOSAyLTJ6TTguNSAxMy41bDIuNSAzLjAxTDE0LjUgMTJsNC41IDZINWwzLjUtNC41eiIvPjwvc3ZnPg=="

        # Dashboard item
        item_dash = QListWidgetItem()
        item_dash.setSizeHint(QSize(210, 54))
        self.sidebar_menu.addItem(item_dash)
        self.dash_widget = SidebarTabWidget("Dashboard", "Control Panel", home_svg, self)
        self.sidebar_menu.setItemWidget(item_dash, self.dash_widget)
        
        # AI VIDEO ENGINE Section
        item_eng_hdr = QListWidgetItem()
        item_eng_hdr.setFlags(Qt.ItemFlag.NoItemFlags)
        lbl_eng = QLabel("AI VIDEO ENGINE")
        lbl_eng.setObjectName("MenuLabel")
        self.sidebar_menu.addItem(item_eng_hdr)
        self.sidebar_menu.setItemWidget(item_eng_hdr, lbl_eng)
        
        # Seedance Vid Gen item
        item_seed = QListWidgetItem()
        item_seed.setSizeHint(QSize(210, 54))
        self.sidebar_menu.addItem(item_seed)
        self.seed_widget = SidebarTabWidget("Seedance Vid Gen", "Video Generator", sparkles_svg, self)
        self.sidebar_menu.setItemWidget(item_seed, self.seed_widget)

        # AI IMAGE ENGINE Section
        item_img_hdr = QListWidgetItem()
        item_img_hdr.setFlags(Qt.ItemFlag.NoItemFlags)
        lbl_img = QLabel("AI IMAGE ENGINE")
        lbl_img.setObjectName("MenuLabel")
        self.sidebar_menu.addItem(item_img_hdr)
        self.sidebar_menu.setItemWidget(item_img_hdr, lbl_img)
        
        # Dola Image Gen item
        item_image = QListWidgetItem()
        item_image.setSizeHint(QSize(210, 54))
        self.sidebar_menu.addItem(item_image)
        self.image_widget = SidebarTabWidget("Dola Image Gen", "Image Generator", image_svg, self)
        self.sidebar_menu.setItemWidget(item_image, self.image_widget)

        # ACCOUNTS & PROXIES Section Header
        item_vault_hdr = QListWidgetItem()
        item_vault_hdr.setFlags(Qt.ItemFlag.NoItemFlags)
        lbl_vault_hdr = QLabel("ACCOUNTS & PROXIES")
        lbl_vault_hdr.setObjectName("MenuLabel")
        self.sidebar_menu.addItem(item_vault_hdr)
        self.sidebar_menu.setItemWidget(item_vault_hdr, lbl_vault_hdr)

        # Session Vault item
        vault_svg = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI0ZGRkZGRiI+PHBhdGggZD0iTTEyIDFMMy4zMiA3LjI3bC40MiA3LjI4TDEyIDIzbDguMjYtOC40NS40Mi03LjI4TDEyIDF6bTAgMy41NWw1Ljg5IDMuNzgtLjMxIDUuMjlMMTIgMTcuNjhsLTUuNTgtNS4wNi0uMzEtNS4yOUwxMiA0LjU1ek0xMiA4YTIgMiAwIDEgMCAwIDQgMiAyIDAgMCAwIDAtNHoiLz48L3N2Zz4="
        item_vault = QListWidgetItem()
        item_vault.setSizeHint(QSize(210, 54))
        self.sidebar_menu.addItem(item_vault)
        self.vault_widget = SidebarTabWidget("Session Vault", "Accounts & Proxies", vault_svg, self)
        self.sidebar_menu.setItemWidget(item_vault, self.vault_widget)

        # Select Seedance Vid Gen by default (which is row 2 in the list)
        self.sidebar_menu.setCurrentRow(2)
        self.seed_widget.set_active(True)
        sidebar_layout.addWidget(self.sidebar_menu)
        
        # Spacer stretch
        sidebar_layout.addStretch()

        # Secondary footer items (SUPPORT)
        self.secondary_menu = QListWidget(self)
        self.secondary_menu.setObjectName("SidebarMenu")
        
        item_sup_hdr = QListWidgetItem()
        item_sup_hdr.setFlags(Qt.ItemFlag.NoItemFlags)
        lbl_sup = QLabel("SUPPORT")
        lbl_sup.setObjectName("MenuLabel")
        self.secondary_menu.addItem(item_sup_hdr)
        self.secondary_menu.setItemWidget(item_sup_hdr, lbl_sup)
        
        self.secondary_menu.addItem(QListWidgetItem("About"))
        self.secondary_menu.addItem(QListWidgetItem("Billing & Plans"))
        self.secondary_menu.addItem(QListWidgetItem("Contact Us"))
        self.secondary_menu.setFixedHeight(150)
        sidebar_layout.addWidget(self.secondary_menu)

        # Restart Button
        self.btn_restart = QPushButton("🔄  Restart Tool")
        self.btn_restart.setObjectName("PromptActionButton")
        self.btn_restart.setFixedHeight(36)
        self.btn_restart.setStyleSheet("margin-top: 5px; margin-bottom: 5px;")
        sidebar_layout.addWidget(self.btn_restart)

        # Profile Box
        profile_box = QFrame()
        profile_box.setObjectName("ProfileBox")
        profile_layout = QHBoxLayout(profile_box)
        profile_layout.setContentsMargins(10, 8, 10, 8)
        
        avatar = QLabel()
        avatar.setObjectName("ProfileAvatar")
        avatar.setPixmap(get_logo_pixmap(32))
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        details = QVBoxLayout()
        name = QLabel("Akira")
        name.setObjectName("ProfileName")
        self.lbl_sub = QLabel("AI Video Generator")
        self.lbl_sub.setObjectName("ProfilePlan")
        details.addWidget(name)
        details.addWidget(self.lbl_sub)
        details.setSpacing(2)
        
        profile_layout.addWidget(avatar)
        profile_layout.addLayout(details)
        sidebar_layout.addWidget(profile_box)

        # Footer Divider Line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #1F2937; max-height: 1px; border: none; margin-top: 5px; margin-bottom: 5px;")
        sidebar_layout.addWidget(divider)
        
        # Custom Developer Footer Container
        footer_widget = QWidget()
        footer_widget.setStyleSheet("background: transparent; border: none;")
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(10, 4, 10, 8)
        footer_layout.setSpacing(6)
        
        lbl_pkmade = QLabel()
        lbl_pkmade.setText("<font color='#4B5563'>PK</font> <font color='#10B981'><b>MADE IN PAKISTAN</b></font>")
        lbl_pkmade.setStyleSheet("font-size: 8.5pt; font-weight: bold; letter-spacing: 0.5px; border: none; background: transparent;")
        
        lbl_devby = QLabel("DEVELOPED BY MALIK ZIA")
        lbl_devby.setStyleSheet("font-size: 8pt; color: #9CA3AF; font-weight: bold; letter-spacing: 0.5px; border: none; background: transparent;")
        
        lbl_wp = QLabel()
        lbl_wp.setText("<a href='https://wa.me/923477399073' style='color: #10B981; text-decoration: none;'>📱 WhatsApp (+92 347 7399073)</a>")
        lbl_wp.setStyleSheet("font-size: 8.5pt; font-weight: bold; border: none; background: transparent;")
        lbl_wp.setOpenExternalLinks(True)
        
        lbl_chan = QLabel()
        lbl_chan.setText("<a href='https://whatsapp.com/channel/0029VbCFttnEVccAgEEkGY1u' style='color: #10B981; text-decoration: none;'>📢 WhatsApp Channel</a>")
        lbl_chan.setStyleSheet("font-size: 8.5pt; font-weight: bold; border: none; background: transparent;")
        lbl_chan.setOpenExternalLinks(True)
        
        footer_layout.addWidget(lbl_pkmade)
        footer_layout.addWidget(lbl_devby)
        footer_layout.addSpacing(2)
        footer_layout.addWidget(lbl_wp)
        footer_layout.addWidget(lbl_chan)
        
        sidebar_layout.addWidget(footer_widget)
        main_layout.addWidget(sidebar)

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
        left_col.setSpacing(20)

        # Generation Settings
        settings_card = QFrame()
        settings_card.setObjectName("SettingsCard")
        settings_card.setMinimumHeight(280)
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(14, 12, 14, 12)
        settings_layout.setSpacing(8)

        settings_hdr = QLabel("GENERATION SETTINGS")
        settings_hdr.setObjectName("PanelTitle")
        settings_layout.addWidget(settings_hdr)

        form_grid = QGridLayout()
        form_grid.setSpacing(10)
        form_grid.setColumnStretch(0, 1)
        form_grid.setColumnStretch(1, 1)

        lbl_model = QLabel("MODEL")
        lbl_model.setObjectName("FormInputLabel")
        self.cb_model = QComboBox()
        self.cb_model.setObjectName("cb_model")
        self.cb_model.addItems(["Seedance 2.0"])
        self.cb_model.setEnabled(True)

        lbl_dur = QLabel("DURATION")
        lbl_dur.setObjectName("FormInputLabel")
        self.cb_dur = QComboBox()
        self.cb_dur.addItems(["15", "10", "5"])
        self.cb_dur.setEnabled(True)

        lbl_ratio = QLabel("ASPECT RATIO")
        lbl_ratio.setObjectName("FormInputLabel")
        self.cb_ratio = QComboBox()
        self.cb_ratio.addItems(["9:16", "16:9", "1:1", "4:3", "3:4", "2:3", "3:2", "21:9"])
        self.cb_ratio.setEnabled(True)

        lbl_batch = QLabel("BATCH SIZE")
        lbl_batch.setObjectName("FormInputLabel")
        self.inp_batch = QLineEdit("30")
        self.inp_batch.setEnabled(True)

        # Row 0: Labels
        form_grid.addWidget(lbl_model, 0, 0)
        form_grid.addWidget(lbl_dur, 0, 1)
        # Row 1: Controls
        form_grid.addWidget(self.cb_model, 1, 0)
        form_grid.addWidget(self.cb_dur, 1, 1)
        # Row 2: Labels
        form_grid.addWidget(lbl_ratio, 2, 0)
        form_grid.addWidget(lbl_batch, 2, 1)
        # Row 3: Controls
        form_grid.addWidget(self.cb_ratio, 3, 0)
        form_grid.addWidget(self.inp_batch, 3, 1)
        settings_layout.addLayout(form_grid)

        # Remove cb_vpn_mode — VPN mode is always Desktop App by default (no Chrome extension needed)
        self.cb_vpn_mode = QComboBox(self)  # kept as attribute for compatibility, hidden
        self.cb_vpn_mode.addItems(["Desktop App"])
        self.cb_vpn_mode.hide()

        lbl_speed = QLabel("SUBMIT SPEED (CONCURRENT CONNECTIONS)", self)
        lbl_speed.setObjectName("FormInputLabel")
        self.inp_speed = QLineEdit("Default: 1")
        self.inp_speed.setEnabled(True)
        settings_layout.addWidget(lbl_speed)
        settings_layout.addWidget(self.inp_speed)

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
        settings_layout.addWidget(self.btn_start)

        left_col.addWidget(settings_card)

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
        self.btn_ctrl_start.setFixedWidth(120)
        
        self.btn_ctrl_pause = QPushButton("⏸ Pause")
        self.btn_ctrl_pause.setObjectName("PauseBtn")
        self.btn_ctrl_pause.setFixedWidth(90)
        
        self.btn_ctrl_clear = QPushButton("🗑 Clear Queue")
        self.btn_ctrl_clear.setObjectName("ClearQueueBtn")
        self.btn_ctrl_clear.setFixedWidth(135)
        
        queue_btn_layout.addWidget(self.btn_ctrl_start)
        queue_btn_layout.addWidget(self.btn_ctrl_pause)
        queue_btn_layout.addWidget(self.btn_ctrl_clear)
        queue_btn_layout.addStretch()
        
        queue_layout.addLayout(queue_btn_layout)
        
        left_col.addWidget(queue_card, 1) # Stretch table card
        cols_grid.addLayout(left_col, 1)

        # RIGHT COLUMN (Prompts & Logs Terminal)
        right_col = QVBoxLayout()
        right_col.setSpacing(20)

        # Prompts editor
        prompts_card = QFrame()
        prompts_card.setObjectName("PromptsCard")
        prompts_card.setMinimumHeight(200)
        prompts_layout = QVBoxLayout(prompts_card)
        prompts_layout.setSpacing(6)

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
        prompts_layout.addLayout(prompts_hdr_lay)

        self.prompts_editor = QTextEdit()
        self.prompts_editor.setObjectName("PromptsEditor")
        self.prompts_editor.setEnabled(True)
        prompts_layout.addWidget(self.prompts_editor)
        
        prompts_note = QLabel("One prompt per line = one video. Import from .txt or .csv files using the buttons above.")
        prompts_note.setObjectName("ProfilePlan")
        prompts_layout.addWidget(prompts_note)

        right_col.addWidget(prompts_card, 5)

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

        right_col.addWidget(logs_card, 6) # Logs get slightly more space
        cols_grid.addLayout(right_col, 1)

        workspace_layout.addLayout(cols_grid)
        self.scroll_area.setWidget(workspace)
        
        # Introduce stacked widget for main workspace area
        self.workspace_stack = QStackedWidget(self)
        
        # Page 0: Dashboard (beautifully styled)
        self.dashboard_page = self.create_dashboard_page()
        self.workspace_stack.addWidget(self.dashboard_page)
        
        # Page 1: Video Generator (existing scroll_area)
        self.workspace_stack.addWidget(self.scroll_area)
        
        # Page 2: Image Generator (new layout)
        self.image_scroll_area = self.create_image_generator_page()
        self.workspace_stack.addWidget(self.image_scroll_area)

        # Page 3: Session Vault (Accounts & Proxies Manager)
        self.vault_page = self.create_session_vault_page()
        self.workspace_stack.addWidget(self.vault_page)
        
        # Default to page 1 (Video Generator) to match self.sidebar_menu default row (2)
        self.workspace_stack.setCurrentIndex(1)
        
        main_layout.addWidget(self.workspace_stack)

    def connect_actions(self):
        self.btn_start.clicked.connect(self.toggle_generation)
        self.btn_change_folder.clicked.connect(self.change_folder)
        self.btn_open_folder.clicked.connect(self.open_folder)
        
        self.btn_refresh.clicked.connect(self.check_updates_clicked)
        self.btn_support.clicked.connect(self.support_clicked)
        self.btn_bell.clicked.connect(self.bell_clicked)
        self.btn_client_mode.clicked.connect(self.toggle_client_mode)
        self.btn_restart.clicked.connect(self.restart_tool)
        self.btn_copy_logs.clicked.connect(self.copy_logs)
        self.btn_clear_logs.clicked.connect(self.clear_logs)
        self.btn_download_logs.clicked.connect(self.download_logs)
        self.console_search.textChanged.connect(self.filter_logs)
        
        self.btn_txt.clicked.connect(self.import_txt)
        self.btn_csv.clicked.connect(self.import_csv)
        self.btn_clear.clicked.connect(self.clear_prompts)
        self.prompts_editor.textChanged.connect(self.update_prompts_count)
        

        # Connect horizontal control bar buttons
        self.btn_ctrl_start.clicked.connect(self.control_start_clicked)
        self.btn_ctrl_pause.clicked.connect(self.control_pause_clicked)
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
        reply = QMessageBox.question(self, "Restart Akira",
            "Are you sure you want to restart Akira?",
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
            
        mode_str = "Client Mode (Clean)" if self.client_mode else "Developer Mode (Verbose)"
        self.log("SYSTEM", f"Switched to {mode_str}. Log display layout updated.")

    def control_start_clicked(self):
        if self.is_queue_paused:
            self.is_queue_paused = False
            self.log("SYSTEM", "Resuming queue processing...")
            
            # Determine maximum concurrency level
            try:
                text = self.inp_speed.text().strip().lower()
                if "default" in text or not text.isdigit():
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
            self.toggle_generation()



    def control_pause_clicked(self):
        if self.is_generating:
            self.is_queue_paused = True
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
            self.workspace_stack.setCurrentIndex(0) # Dashboard
        elif row == 2:
            self.workspace_stack.setCurrentIndex(1) # Video Generator
        elif row == 4:
            self.workspace_stack.setCurrentIndex(2) # Image Generator
        elif row == 6:
            self.workspace_stack.setCurrentIndex(3) # Session Vault

    def initialize_empty_state(self):
        self.action_text_cache = {}

        self.console.clear()
        self.log_counter = 0
        self.log("SYSTEM", "Akira v1.0.0 initialized successfully.")
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
            message = message.replace("dola.com", "akira.ai").replace("Dola", "Akira").replace("dola", "akira")
            
            # 1. Discard watermark coordinates completely
            if "Watermark detected at:" in message:
                return
            
            # 2. Silently drop the 15-second rendering updates
            if "Still rendering video (elapsed:" in message:
                return
                
            # 3. For all other INFO logs, only keep the ones we explicitly want
            if type_str == "INFO":
                # Check if it contains important updates
                is_important = False
                if "[*] Removing watermark..." in message or "Removing watermark..." in message:
                    is_important = True
                    # Clean up: remove [*] prefix
                    row_prefix = ""
                    if ":" in message:
                        parts = message.split(":")
                        if "Row" in parts[0]:
                            row_prefix = f"{parts[0]}: "
                    message = f"{row_prefix}Removing watermark..."
                elif "Downloading video..." in message or "Downloaded and cleaned" in message:
                    is_important = True
                elif "Spawning automated Google Chrome" in message:
                    is_important = True
                    row_prefix = ""
                    if ":" in message:
                        parts = message.split(":")
                        if "Row" in parts[0]:
                            row_prefix = f"{parts[0]}: "
                    message = f"{row_prefix}Starting browser engine..."
                
                # If it's not important, discard it completely
                if not is_important:
                    return

            # 4. Extract clean confirmation message for SUCCESS
            if type_str == "SUCCESS" and "CONFIRMED:" in message:
                row_prefix = ""
                if ":" in message:
                    parts = message.split(":")
                    if "Row" in parts[0]:
                        row_prefix = f"{parts[0]}: "
                
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
            self.log("SYSTEM", f"Akira is up to date (v{current}).")
            QMessageBox.information(self, "Up to Date", f"Akira is up to date! (v{current})")
            
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
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                cleaned = []
                for l in lines:
                    val = l.strip().strip('"').strip("'").strip(",")
                    if val:
                        cleaned.append(val)
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
        self.log("SYSTEM", "Prompts workspace cleared.")

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
            
            # Unlock inputs
            self.cb_model.setEnabled(True)
            self.cb_dur.setEnabled(True)
            self.cb_ratio.setEnabled(True)
            self.inp_batch.setEnabled(True)
            self.inp_speed.setEnabled(True)
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
                self.prompts_editor.setEnabled(False)
                self.btn_txt.setEnabled(False)
                self.btn_csv.setEnabled(False)
                self.btn_clear.setEnabled(False)

                self.btn_start.setText("STOP GENERATION")
                self.btn_start.setObjectName("StopCTA")
                self.btn_start.parentWidget().setStyleSheet(UI_MASTER_QSS)

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
                    text = self.inp_speed.text().strip().lower()
                    if "default" in text or not text.isdigit():
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
            bot.use_extension_vpn = False  # VPN mode always desktop/no extension

            # Get HeroSMS details
            sms_key = self.inp_sms_key.text().strip()
            sms_country = self.cb_sms_country.currentData() or "0"

            worker = PlaywrightWorker(
                bot=bot,
                row_id=row_id,
                prompt=next_item["prompt"],
                model=self.cb_model.currentText(),
                duration=self.cb_dur.currentText(),
                ratio=self.cb_ratio.currentText(),
                setup_mode=setup_mode,
                is_image=False,
                proxy_list=proxy_list,
                sms_key=sms_key,
                sms_country=sms_country
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

        self.btn_vault_proxy_clear = QPushButton("  ✕  Clear")
        self.btn_vault_proxy_clear.setObjectName("PromptActionButtonDanger")
        self.btn_vault_proxy_clear.setFixedHeight(36)

        proxy_btn_row.addWidget(self.btn_vault_proxy_save)
        proxy_btn_row.addWidget(self.btn_vault_proxy_load)
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
        layout.addStretch()

        scroll.setWidget(page)

        # Connect vault actions
        self.btn_vault_add.clicked.connect(self.vault_add_account)
        self.btn_vault_import_folder.clicked.connect(self.vault_import_folder)
        self.btn_vault_remove.clicked.connect(self.vault_remove_selected)
        self.btn_vault_clear_all.clicked.connect(self.vault_clear_all)
        self.btn_vault_reload.clicked.connect(self.vault_reload_accounts)
        self.btn_vault_proxy_save.clicked.connect(self.vault_save_proxies)
        self.btn_vault_proxy_load.clicked.connect(self.vault_load_proxies_file)
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

    def vault_reload_accounts(self):
        import json
        from datetime import date
        cookies_dir = self._vault_cookies_dir()
        usage = self._load_usage()
        today = str(date.today())

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
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cookies = data.get("cookies", data) if isinstance(data, dict) else data
                for c in cookies:
                    if c.get("name") in ("sessionid", "sid_tt", "sid_guard"):
                        session_preview = c.get("value", "")[:22] + "..."
                        break
            except:
                session_preview = "⚠ Parse Error"
                expired_count += 1

            u = usage.get(fname, {})
            uses_today = u.get("uses_today", 0) if u.get("date") == today else 0
            is_full = uses_today >= limit

            if is_full:
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
        btn_open_vid.clicked.connect(lambda: self.sidebar_menu.setCurrentRow(2))
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
        btn_open_img.clicked.connect(lambda: self.sidebar_menu.setCurrentRow(4))
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

        self.btn_load_proxies.setParent(proxy_dash_card)
        self.btn_load_proxies.setStyleSheet("""
            QPushButton {
                background-color: #1F2937; border: 1px solid #1D263B; color: #FFFFFF;
                font-weight: bold; font-size: 8.5pt; border-radius: 6px;
                padding: 6px 12px; max-width: 150px;
            }
            QPushButton:hover { background-color: #374151; }
        """)
        self.btn_load_proxies.show()
        proxy_dash_layout.addWidget(self.btn_load_proxies)
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
        from datetime import datetime
        try:
            self.dash_last_updated.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        except Exception:
            pass

        # Performance Metrics
        total_hrs = self.dash_total_time_sec / 3600.0 if self.dash_total_time_sec > 0 else 0
        gen_per_hr = self.dash_total_generated / total_hrs if total_hrs > 0 else 0.0
        self.dash_metric_gen_hr.setText(f"{gen_per_hr:.1f}")

        if self.dash_total_time_sec < 60:
            self.dash_metric_time.setText(f"{int(self.dash_total_time_sec)}s")
        elif self.dash_total_time_sec < 3600:
            self.dash_metric_time.setText(f"{int(self.dash_total_time_sec // 60)}m {int(self.dash_total_time_sec % 60)}s")
        else:
            hrs = int(self.dash_total_time_sec // 3600)
            mins = int((self.dash_total_time_sec % 3600) // 60)
            self.dash_metric_time.setText(f"{hrs}h {mins}m")

        self.dash_metric_prompts.setText(str(self.dash_total_prompts))
        self.dash_metric_sessions.setText(str(len(self.dash_sessions)))
        self.dash_metric_best.setText(f"{self.dash_best_rate:.0f}%")
        self.dash_metric_errors.setText(str(self.dash_total_failed))

        # Session count badge
        self.dash_session_count_badge.setText(f"{len(self.dash_sessions)} session(s)")

        # Session History Table
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
        
        lbl_model = QLabel("MODEL")
        lbl_model.setObjectName("FormInputLabel")
        self.cb_img_model = QComboBox()
        self.cb_img_model.setObjectName("cb_model")
        self.cb_img_model.addItems(["Dola Image"])
        self.cb_img_model.setEnabled(True)
        
        lbl_style = QLabel("STYLE")
        lbl_style.setObjectName("FormInputLabel")
        self.cb_img_style = QComboBox()
        self.cb_img_style.addItems([
            "Portraits", "Landscape", "Anime", "3D", "Cyberpunk", "Oil Painting", 
            "Watercolor", "Flat Illustration", "Children's Drawing", "Pixel", 
            "Colored Pencil", "Ink Wash", "Ink Print"
        ])
        self.cb_img_style.setEnabled(True)
        
        lbl_ratio = QLabel("ASPECT RATIO")
        lbl_ratio.setObjectName("FormInputLabel")
        self.cb_img_ratio = QComboBox()
        self.cb_img_ratio.addItems(["1:1", "9:16", "16:9", "3:4", "4:3", "2:3"])
        self.cb_img_ratio.setEnabled(True)
        
        lbl_batch = QLabel("BATCH SIZE")
        lbl_batch.setObjectName("FormInputLabel")
        self.inp_img_batch = QLineEdit("30")
        self.inp_img_batch.setEnabled(True)
        
        form_grid.addWidget(lbl_model, 0, 0)
        form_grid.addWidget(self.cb_img_model, 1, 0, 1, 2)
        form_grid.addWidget(lbl_style, 0, 2)
        form_grid.addWidget(self.cb_img_style, 1, 2)
        
        form_grid.addWidget(lbl_ratio, 2, 0)
        form_grid.addWidget(self.cb_img_ratio, 3, 0, 1, 2)
        form_grid.addWidget(lbl_batch, 2, 2)
        form_grid.addWidget(self.inp_img_batch, 3, 2)
        settings_layout.addLayout(form_grid)
        
        self.cb_img_vpn_mode = QComboBox(self)
        self.cb_img_vpn_mode.addItems(["Chrome Extension (PIA)", "Desktop App (Surfshark/PIA)"])
        self.cb_img_vpn_mode.setCurrentIndex(1)
        
        lbl_speed = QLabel("SUBMIT SPEED (CONCURRENT CONNECTIONS)", self)
        lbl_speed.setObjectName("FormInputLabel")
        self.inp_img_speed = QLineEdit("Default: 1")
        self.inp_img_speed.setEnabled(True)
        settings_layout.addWidget(lbl_speed)
        settings_layout.addWidget(self.inp_img_speed)

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
        settings_layout.addWidget(self.btn_img_start)
        
        left_col.addWidget(settings_card)
        
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
        
        left_col.addWidget(queue_card, 1)
        cols_grid.addLayout(left_col, 1)
        
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
        
        right_col.addWidget(prompts_card, 5)
        
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
        
        right_col.addWidget(logs_card, 6)
        cols_grid.addLayout(right_col, 1)
        
        workspace_layout.addLayout(cols_grid)
        scroll.setWidget(workspace)
        
        return scroll

    def img_log(self, type_str, message):
        if self.client_mode:
            if " Redirected to: " in message and ("dola.com" in message or "dola" in message.lower()):
                message = message.split(" Redirected to: ")[0]
            message = message.replace("dola.com", "akira.ai").replace("Dola", "Akira").replace("dola", "akira")
            
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
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                cleaned = []
                for l in lines:
                    val = l.strip().strip('"').strip("'").strip(",")
                    if val:
                        cleaned.append(val)
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
                text = self.inp_img_speed.text().strip().lower()
                if "default" in text or not text.isdigit():
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
            self.cb_img_style.setEnabled(True)
            self.cb_img_ratio.setEnabled(True)
            
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
        
        self.cb_img_style.setEnabled(False)
        self.cb_img_ratio.setEnabled(False)
        
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
            speed_text = self.inp_img_speed.text().strip().lower()
            if "default" in speed_text or not speed_text.isdigit():
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
            
            # Image tab doesn't have SMS inputs, fallback to empty/none
            worker = PlaywrightWorker(
                bot=bot,
                row_id=row_id,
                prompt=next_item["prompt"],
                model=self.cb_img_style.currentText(),
                duration="0",
                ratio=self.cb_img_ratio.currentText(),
                setup_mode=setup_mode,
                is_image=True,
                proxy_list=proxy_list,
                sms_key=None,
                sms_country="0"
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
        url = f"{web_app_url}?device_id={urllib.parse.quote(device_id)}"
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_bytes = response.read()
            raw_text = raw_bytes.decode('utf-8', errors='ignore').strip()
            try:
                res_data = json.loads(raw_text)
                return res_data
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
    return "Akira Premium License - Lifetime Active"

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
                background-color: #111827;
                border: 1px solid #1D263B;
                border-radius: 12px;
            }
            QFrame#PricingCard:hover {
                border-color: #8B5CF6;
                background-color: #131B2E;
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
                color: #FFFFFF;
                background-color: #8B5CF6;
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
            color: #8B5CF6;
            background-color: rgba(139, 92, 246, 0.1);
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
        btn_text = "Contact Us" if is_contact else "Buy Now"
        btn = QPushButton(btn_text, self)
        if is_contact:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1F2937;
                    border: 1px solid #1D263B;
                    color: #FFFFFF;
                    font-weight: bold;
                    border-radius: 8px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #374151;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    color: #111827;
                    font-weight: bold;
                    border-radius: 8px;
                    padding: 8px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #F3F4F6;
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
    def __init__(self, device_id, config_data):
        super().__init__()
        self.device_id = device_id
        self.config_data = config_data
        
        self.setWindowTitle("Akira License Activation")
        self.setFixedSize(550, 520)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Load window icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.drag_position = None
        self.selected_plan = "3 Month Premium"
        self.price_usd = 50
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
        self.screen_lock.setStyleSheet("background-color: #090D1A; border: 1px solid #1D263B; border-radius: 16px;")
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
        alert_box.setStyleSheet("background-color: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 10px;")
        alert_lay = QVBoxLayout(alert_box)
        alert_lay.setContentsMargins(15, 12, 15, 12)
        alert_lay.setSpacing(6)
        
        crown = QLabel("👑", self)
        crown.setStyleSheet("font-size: 14pt; border: none; background: transparent;")
        crown.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        req_title = QLabel("Subscription Required", self)
        req_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #FFFFFF; border: none; background: transparent;")
        req_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        req_desc = QLabel("Your subscription has expired or is invalid. Please renew to continue.", self)
        req_desc.setStyleSheet("font-size: 8.5pt; color: #9CA3AF; border: none; background: transparent;")
        req_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        alert_lay.addWidget(crown)
        alert_lay.addWidget(req_title)
        alert_lay.addWidget(req_desc)
        lock_lay.addWidget(alert_box)
        
        # Actions
        btn_buy = QPushButton("⚡  Buy Subscription", self)
        btn_buy.setStyleSheet("background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #8B5CF6); color: #FFFFFF; font-weight: bold; font-size: 10pt; border-radius: 8px; padding: 10px; border: none;")
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
        self.screen_pricing.setStyleSheet("background-color: #090D1A; border: 1px solid #1D263B; border-radius: 16px;")
        price_lay = QVBoxLayout(self.screen_pricing)
        price_lay.setContentsMargins(25, 20, 25, 25)
        price_lay.setSpacing(12)
        
        # Header block
        price_hdr = QHBoxLayout()
        btn_back0 = QPushButton("← Back", self)
        btn_back0.setStyleSheet("background: transparent; border: none; color: #8B5CF6; font-weight: bold; font-size: 9pt;")
        btn_back0.clicked.connect(lambda: self.show_screen(0))
        
        lbl_pr_title = QLabel("Manage your License", self)
        lbl_pr_title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #FFFFFF; border: none; background: transparent;")
        
        btn_cls1 = QPushButton("✕", self)
        btn_cls1.setStyleSheet("background: transparent; border: none; color: #9CA3AF; font-size: 11pt; min-width: 24px; max-width: 24px;")
        btn_cls1.clicked.connect(self.close)
        
        price_hdr.addWidget(btn_back0)
        price_hdr.addSpacing(10)
        price_hdr.addWidget(lbl_pr_title)
        price_hdr.addStretch()
        price_hdr.addWidget(btn_cls1)
        price_lay.addLayout(price_hdr)
        
        desc_lbl = QLabel("Upgrade your plan to unlock unlimited Seedance 2.0 Video Generation and premium tools.", self)
        desc_lbl.setStyleSheet("font-size: 9.5pt; color: #9CA3AF; border: none; background: transparent;")
        price_lay.addWidget(desc_lbl)
        
        # Grid of 6 packages (2 rows, 3 columns)
        grid_lay = QGridLayout()
        grid_lay.setSpacing(12)
        
        self.card1 = PricingCard("1 Month Premium", "Perfect to test out all automation features.", 20, 29, "Starter Plan ⚡", "📁", False, self)
        self.card2 = PricingCard("3 Month Premium", "Perfect for short-term projects and growth.", 50, 69, "Great Value ✨", "⚡", False, self)
        self.card3 = PricingCard("6 Month Premium", "Optimal choice for medium-term automation.", 75, 99, "Popular Choice 🚀", "🛡️", False, self)
        self.card4 = PricingCard("1 Year Premium", "Extended access with maximum savings.", 120, 159, "Best Value 🔥", "💎", False, self)
        self.card5 = PricingCard("Lifetime Deal", "One payment. Infinite updates forever.", 1000, 1499, "Limited Slots 👑", "👑", False, self)
        self.card6 = PricingCard("Enterprise Plan", "All custom power and bulk license for teams.", 0, 0, "Bulk License 🚀", "🏢", True, self)
        
        # Connect pricing cards to checkout transitions
        for card in [self.card1, self.card2, self.card3, self.card4, self.card5, self.card6]:
            card.clicked.connect(self.on_plan_selected)
            
        grid_lay.addWidget(self.card1, 0, 0)
        grid_lay.addWidget(self.card2, 0, 1)
        grid_lay.addWidget(self.card3, 0, 2)
        grid_lay.addWidget(self.card4, 1, 0)
        grid_lay.addWidget(self.card5, 1, 1)
        grid_lay.addWidget(self.card6, 1, 2)
        price_lay.addLayout(grid_lay)
        
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
        self.screen_checkout.setStyleSheet("background-color: #090D1A; border: 1px solid #1D263B; border-radius: 16px;")
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
        self.wiz_step1.setStyleSheet("color: #8B5CF6; font-weight: bold; font-size: 8.5pt; border: none; background: transparent;")
        self.wiz_step2 = QLabel("✓ Make Payment", self)
        self.wiz_step2.setStyleSheet("color: #8B5CF6; font-weight: bold; font-size: 8.5pt; border: none; background: transparent;")
        self.wiz_step3 = QLabel("3. Submit Proof", self)
        self.wiz_step3.setStyleSheet("color: #4B5563; font-size: 8.5pt; border: none; background: transparent;")
        
        div1 = QFrame(self)
        div1.setFrameShape(QFrame.Shape.HLine)
        div1.setStyleSheet("background-color: #8B5CF6; max-height: 2px; border: none;")
        div2 = QFrame(self)
        div2.setFrameShape(QFrame.Shape.HLine)
        div2.setStyleSheet("background-color: #1D263B; max-height: 2px; border: none;")
        
        wizard_lay.addWidget(self.wiz_step1)
        wizard_lay.addWidget(div1)
        wizard_lay.addWidget(self.wiz_step2)
        wizard_lay.addWidget(div2)
        wizard_lay.addWidget(self.wiz_step3)
        chk_lay.addLayout(wizard_lay)
        
        # Summary Header Panel
        self.summary_card = QFrame(self)
        self.summary_card.setStyleSheet("background-color: #111827; border: 1px solid #1D263B; border-radius: 12px;")
        sum_lay = QHBoxLayout(self.summary_card)
        sum_lay.setContentsMargins(15, 12, 15, 12)
        
        sum_icon = QLabel("🛡️", self)
        sum_icon.setStyleSheet("font-size: 14pt; border: none; background: transparent;")
        
        self.lbl_selected_plan = QLabel("3 Month Premium", self)
        self.lbl_selected_plan.setStyleSheet("font-size: 12pt; font-weight: bold; color: #FFFFFF; border: none; background: transparent;")
        
        # Currency buttons layout
        curr_box = QHBoxLayout()
        curr_box.setSpacing(4)
        self.btn_usd = QPushButton("USD", self)
        self.btn_bdt = QPushButton("BDT", self)
        self.btn_pkr = QPushButton("PKR", self)
        
        for b in [self.btn_usd, self.btn_bdt, self.btn_pkr]:
            b.setFixedWidth(50)
            b.clicked.connect(self.on_currency_changed)
        self.set_active_currency_button(self.btn_usd)
        curr_box.addWidget(self.btn_usd)
        curr_box.addWidget(self.btn_bdt)
        curr_box.addWidget(self.btn_pkr)
        
        self.lbl_amount = QLabel("$50", self)
        self.lbl_amount.setStyleSheet("font-size: 14pt; font-weight: bold; color: #10B981; border: none; background: transparent;")
        
        sum_lay.addWidget(sum_icon)
        sum_lay.addWidget(self.lbl_selected_plan)
        sum_lay.addStretch()
        sum_lay.addLayout(curr_box)
        sum_lay.addWidget(self.lbl_amount)
        chk_lay.addWidget(self.summary_card)
        
        # Choose Payment Method section
        meth_title = QLabel("CHOOSE PAYMENT METHOD", self)
        meth_title.setStyleSheet("font-size: 9pt; font-weight: bold; color: #FFFFFF; border: none; background: transparent;")
        chk_lay.addWidget(meth_title)
        
        # Grid of payment method options
        pm_grid = QGridLayout()
        pm_grid.setSpacing(12)
        
        self.pm_binance = PaymentMethodButton("Binance (USDT)", "🟢", True, self)
        self.pm_usdt_bep = PaymentMethodButton("USDT (BEP20)", "🟢", True, self)
        self.pm_redotpay = PaymentMethodButton("RedotPay (USDT)", "🟢", True, self)
        self.pm_bank_bdt = PaymentMethodButton("Bank Transfer (BDT)", "🏦", False, self)
        self.pm_mob_bdt = PaymentMethodButton("Mobile Banking (BDT)", "📱", False, self)
        self.pm_easypaisa = PaymentMethodButton("Easypaisa (PKR)", "👛", False, self)
        self.pm_jazzcash = PaymentMethodButton("JazzCash (PKR)", "👛", False, self)
        self.pm_ubl = PaymentMethodButton("UBL Bank (PKR)", "🏦", False, self)
        self.pm_meezan = PaymentMethodButton("Meezan Bank (PKR)", "🏦", False, self)
        
        # Connect actions
        for pm in [self.pm_binance, self.pm_usdt_bep, self.pm_redotpay, self.pm_bank_bdt, 
                   self.pm_mob_bdt, self.pm_easypaisa, self.pm_jazzcash, self.pm_ubl, self.pm_meezan]:
            pm.clicked.connect(self.on_pm_clicked)
            
        pm_grid.addWidget(self.pm_binance, 0, 0)
        pm_grid.addWidget(self.pm_usdt_bep, 0, 1)
        pm_grid.addWidget(self.pm_redotpay, 0, 2)
        pm_grid.addWidget(self.pm_bank_bdt, 1, 0)
        pm_grid.addWidget(self.pm_mob_bdt, 1, 1)
        pm_grid.addWidget(self.pm_easypaisa, 1, 2)
        pm_grid.addWidget(self.pm_jazzcash, 2, 0)
        pm_grid.addWidget(self.pm_ubl, 2, 1)
        pm_grid.addWidget(self.pm_meezan, 2, 2)
        chk_lay.addLayout(pm_grid)
        
        self.stacked_widget.addWidget(self.screen_checkout)

        # ---------------------------------------------
        # SCREEN 3: SUBMIT PROOF & VERIFICATION WINDOW
        # ---------------------------------------------
        self.screen_proof = QFrame(self)
        self.screen_proof.setStyleSheet("background-color: #090D1A; border: 1px solid #1D263B; border-radius: 16px;")
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
        self.wiz3_1.setStyleSheet("color: #8B5CF6; font-weight: bold; font-size: 8.5pt; border: none; background: transparent;")
        self.wiz3_2 = QLabel("✓ Make Payment", self)
        self.wiz3_2.setStyleSheet("color: #8B5CF6; font-weight: bold; font-size: 8.5pt; border: none; background: transparent;")
        self.wiz3_3 = QLabel("✓ Submit Proof", self)
        self.wiz3_3.setStyleSheet("color: #8B5CF6; font-weight: bold; font-size: 8.5pt; border: none; background: transparent;")
        
        div1_3 = QFrame(self)
        div1_3.setFrameShape(QFrame.Shape.HLine)
        div1_3.setStyleSheet("background-color: #8B5CF6; max-height: 2px; border: none;")
        div2_3 = QFrame(self)
        div2_3.setFrameShape(QFrame.Shape.HLine)
        div2_3.setStyleSheet("background-color: #8B5CF6; max-height: 2px; border: none;")
        
        wizard_lay3.addWidget(self.wiz3_1)
        wizard_lay3.addWidget(div1_3)
        wizard_lay3.addWidget(self.wiz3_2)
        wizard_lay3.addWidget(div2_3)
        wizard_lay3.addWidget(self.wiz3_3)
        prf_lay.addLayout(wizard_lay3)
        
        # Summary Header Panel for Proof Screen
        self.summary_card3 = QFrame(self)
        self.summary_card3.setStyleSheet("background-color: #111827; border: 1px solid #1D263B; border-radius: 12px;")
        sum_lay3 = QHBoxLayout(self.summary_card3)
        sum_lay3.setContentsMargins(15, 12, 15, 12)
        
        sum_icon3 = QLabel("🛡️", self)
        sum_icon3.setStyleSheet("font-size: 14pt; border: none; background: transparent;")
        
        self.lbl_selected_plan3 = QLabel("3 Month Premium", self)
        self.lbl_selected_plan3.setStyleSheet("font-size: 12pt; font-weight: bold; color: #FFFFFF; border: none; background: transparent;")
        
        self.lbl_amount3 = QLabel("14,000 PKR", self)
        self.lbl_amount3.setStyleSheet("font-size: 14pt; font-weight: bold; color: #10B981; border: none; background: transparent;")
        
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
        self.account_panel.setStyleSheet("background-color: #111827; border: 1px solid #1D263B; border-radius: 12px;")
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
        self.edit_acc_num = QLineEdit("03477399073", self)
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
        self.upload_panel.setStyleSheet("background-color: #111827; border: 1px solid #1D263B; border-radius: 12px;")
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
        self.btn_submit_proof.setStyleSheet("background-color: #8B5CF6; color: #FFFFFF; font-weight: bold; font-size: 9.5pt; border-radius: 8px; padding: 10px; border: none;")
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
        for btn in [self.btn_usd, self.btn_bdt, self.btn_pkr]:
            if btn == active_btn:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #8B5CF6;
                        color: #FFFFFF;
                        font-weight: bold;
                        border: none;
                        border-radius: 4px;
                        padding: 4px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1F2937;
                        color: #9CA3AF;
                        border: 1px solid #374151;
                        border-radius: 4px;
                        padding: 4px;
                    }
                    QPushButton:hover {
                        background-color: #374151;
                        color: #FFFFFF;
                    }
                """)

    def on_currency_changed(self, target_btn=None):
        if not target_btn:
            target_btn = self.sender()
            
        self.set_active_currency_button(target_btn)
        
        # Calculate dynamic conversions
        # USD base rates: 1M ($20), 3M ($50), 6M ($75), 1Y ($120), Lifetime ($1000)
        # BDT rates: 1M (2400), 3M (6000), 6M (9000), 1Y (14400), Lifetime (120000)
        # PKR rates: 1M (5600), 3M (14000), 6M (21000), 1Y (33600), Lifetime (280000)
        
        is_usd = (target_btn == self.btn_usd)
        is_bdt = (target_btn == self.btn_bdt)
        is_pkr = (target_btn == self.btn_pkr)
        
        if is_usd:
            self.lbl_amount.setText(f"${self.price_usd}")
            self.lbl_amount3.setText(f"${self.price_usd}")
        elif is_bdt:
            bdt_val = int(self.price_usd * 120)
            self.lbl_amount.setText(f"{bdt_val:,} BDT")
            self.lbl_amount3.setText(f"{bdt_val:,} BDT")
        elif is_pkr:
            pkr_val = int(self.price_usd * 280)
            self.lbl_amount.setText(f"{pkr_val:,} PKR")
            self.lbl_amount3.setText(f"{pkr_val:,} PKR")
            
        # Enable / Disable (grey out) payment buttons based on currency
        self.pm_binance.set_state(is_usd)
        self.pm_usdt_bep.set_state(is_usd)
        self.pm_redotpay.set_state(is_usd)
        
        self.pm_bank_bdt.set_state(is_bdt)
        self.pm_mob_bdt.set_state(is_bdt)
        
        self.pm_easypaisa.set_state(is_pkr)
        self.pm_jazzcash.set_state(is_pkr)
        self.pm_ubl.set_state(is_pkr)
        self.pm_meezan.set_state(is_pkr)

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
        elif "binance" in self.selected_method.lower() or "usdt" in self.selected_method.lower() or "redotpay" in self.selected_method.lower():
            self.edit_acc_num.setText(self.config_data.get("usdt_address", "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"))
            self.edit_acc_name.setText("USDT (BEP20 Network)")
        else:
            # Fallback for other banks
            self.edit_acc_num.setText("03244481248")
            self.edit_acc_name.setText("Zia Ullah (UBL/Meezan Bank Account)")
            
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
        self.setFixedSize(450, 250)
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
                background-color: #090D1A;
                border: 1px solid #1D263B;
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.logo = QLabel(self)
        self.logo.setFixedSize(64, 64)
        self.logo.setPixmap(get_logo_pixmap(64))
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo, 0, Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(15)
        
        title = QLabel("AKIRA AI ENGINE", self)
        title.setStyleSheet("font-family: 'Outfit', 'Inter', sans-serif; font-size: 14pt; font-weight: bold; color: #FFFFFF;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.lbl_status = QLabel("Initializing systems...", self)
        self.lbl_status.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 9pt; color: #9CA3AF;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_status)
        
        layout.addSpacing(15)
        
        self.pbar = QProgressBar(self)
        self.pbar.setFixedHeight(6)
        self.pbar.setTextVisible(False)
        self.pbar.setRange(0, 0)
        self.pbar.setStyleSheet("""
            QProgressBar {
                background-color: #111827;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B5CF6, stop:1 #EC4899);
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.pbar)
        
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
        
        # Remote kill/lock switch check
        if res.get("status") in ["locked", "unauthorized"]:
            self.lock_screen = AkiraLockScreen(self.device_id, self.config_data)
            self.lock_screen.show()
        else:
            self.main_win = NexusAutomatorWindow()
            plan = res.get("plan", "Free Trial")
            time_left_sec = res.get("time_left_seconds", 9999999)
            plan_text = format_license_plan_text(plan, time_left_sec)
            self.main_win.lbl_sub.setText(plan_text)
            self.main_win.show()

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
            if ctypes.windll.kernel32.IsDebuggerPresent() != 0:
                print("[SECURITY ALERT] Debugger detected. Exiting process.")
                sys.exit(1)
    except Exception:
        pass
        
    if sys.gettrace() is not None:
        print("[SECURITY ALERT] Debug trace active. Exiting process.")
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

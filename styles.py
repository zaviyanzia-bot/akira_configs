# styles.py — QSS (Qt Style Sheets) for Nexus Automator GUI

UI_MASTER_QSS = """
    /* ==========================================
       GLOBAL BASE WINDOW STYLES
       ========================================== */
    QMainWindow { 
        background-color: #0C0D14; 
    }
    QScrollArea#MainScrollArea, QWidget#MainWorkspace {
        background-color: transparent;
        border: none;
    }
    QWidget { 
        font-family: 'Inter', 'Outfit', 'Segoe UI', sans-serif; 
        color: #E5E7EB; 
        font-size: 9.5pt;
    }
    
    /* Scrollbars Customization */
    QScrollBar:vertical {
        background: transparent;
        width: 8px;
        border: none;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #1F2231;
        border-radius: 4px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #2D314A;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        height: 0px;
        background: transparent;
    }
    
    QScrollBar:horizontal {
        background: transparent;
        height: 8px;
        border: none;
        margin: 0px;
    }
    QScrollBar::handle:horizontal {
        background: #1F2231;
        border-radius: 4px;
        min-width: 20px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #2D314A;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        width: 0px;
        background: transparent;
    }
    
    /* ==========================================
       SIDEBAR NAV PANEL
       ========================================== */
    QFrame#SidebarPanel { 
        background-color: #12131C; 
        border-bottom: 1px solid #1F2231; 
    }
    
    QLabel#SidebarBrandName {
        font-size: 13pt;
        font-weight: bold;
        color: #C5A059; /* Brand name in Gold */
    }
    
    QPushButton#VersionBtn {
        background-color: #161722;
        color: #C5A059;
        font-size: 7.5pt;
        font-weight: bold;
        border: 1px solid #C5A059;
        padding: 2px 8px;
        border-radius: 4px;
        text-align: center;
    }
    QPushButton#VersionBtn:hover {
        background-color: #C5A059;
        color: #0C0D14;
    }

    QLabel#MenuLabel {
        font-size: 7.5pt;
        font-weight: bold;
        color: #4D516A;
        letter-spacing: 1.5px;
        margin-top: 10px;
        margin-left: 14px;
    }
    
    /* Sidebar List Items */
    QListWidget#SidebarMenu { 
        background-color: transparent; 
        border: none; 
        outline: none;
    }
    QListWidget#SidebarMenu::item { 
        background: transparent;
        border: none;
        padding: 0px;
        margin-right: 6px;
    }
    QListWidget#SidebarMenu::item:hover { 
        background: transparent;
        border: none;
    }
    QListWidget#SidebarMenu::item:selected { 
        background: transparent;
        border: none;
        outline: none;
    }
    QListWidget#SidebarMenu QScrollBar:vertical {
        background: #0C0D14;
        width: 4px;
        border-radius: 2px;
        margin: 0px;
    }
    QListWidget#SidebarMenu QScrollBar::handle:vertical {
        background: #C5A059;
        border-radius: 2px;
        min-height: 20px;
    }
    QListWidget#SidebarMenu QScrollBar::add-line:vertical,
    QListWidget#SidebarMenu QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    /* Profile Box */
    QFrame#ProfileBox {
        background-color: #161722;
        border: 1px solid #1F2231;
        border-radius: 12px;
    }
    
    QLabel#ProfileAvatar {
        background-color: transparent;
        color: #0C0D14;
        font-weight: bold;
        font-size: 8.5pt;
        border-radius: 16px;
        min-width: 32px;
        max-width: 32px;
        min-height: 32px;
        max-height: 32px;
    }
    
    QLabel#ProfileName {
        font-weight: 600;
        font-size: 9.5pt;
        color: #FFFFFF;
    }
    
    QLabel#ProfilePlan {
        font-size: 8.0pt;
        color: #C5A059; /* Active plan in Gold */
    }
    
    /* ==========================================
       PANEL CARDS (CONTAINERS)
       ========================================== */
    QFrame#PanelCard {
        background-color: #161722;
        border: 1px solid #1F2231;
        border-radius: 12px;
    }
    
    /* Elegant Gold Card Borders */
    QFrame#PromptsCard {
        background-color: #161722;
        border: 1px solid #C5A059; /* Gold border */
        border-radius: 12px;
    }
    QFrame#SettingsCard {
        background-color: #161722;
        border: 1px solid #C5A059; /* Gold border */
        border-radius: 12px;
    }
    
    QLabel#PanelTitle {
        font-size: 10pt;
        font-weight: bold;
        color: #C5A059; /* Titles in Gold */
        letter-spacing: 0.5px;
    }
    
    /* ==========================================
       TOP HEADER NAV
       ========================================== */
    QLabel#MainHeaderTitle {
        font-size: 14pt;
        font-weight: bold;
        color: #FFFFFF;
    }
    QLabel#MainHeaderSubtitle {
        font-size: 9.5pt;
        color: #9CA3AF;
    }
    
    QPushButton#HeaderActionButton {
        background-color: #161722;
        border: 1px solid #1F2231;
        border-radius: 8px;
        padding: 6px;
        min-width: 34px;
        max-width: 34px;
        min-height: 34px;
        max-height: 34px;
    }
    QPushButton#HeaderActionButton:hover {
        background-color: rgba(197, 160, 89, 0.05);
        border-color: #C5A059;
    }
    
    /* Frameless Title Bar Windows Controls */
    QPushButton#WindowControlBtn {
        background-color: transparent;
        border: none;
        color: #9CA3AF;
        min-width: 34px;
        max-width: 34px;
        min-height: 34px;
        max-height: 34px;
        font-size: 11pt;
    }
    QPushButton#WindowControlBtn:hover {
        background-color: rgba(255, 255, 255, 0.06);
        color: #FFFFFF;
    }
    QPushButton#WindowCloseBtn {
        background-color: transparent;
        border: none;
        color: #9CA3AF;
        min-width: 34px;
        max-width: 34px;
        min-height: 34px;
        max-height: 34px;
        font-size: 11pt;
    }
    QPushButton#WindowCloseBtn:hover {
        background-color: #EF4444;
        color: #FFFFFF;
    }
    
    /* ==========================================
       STATS ROW CARDS
       ========================================== */
    QLabel#StatLbl {
        font-size: 7.5pt;
        font-weight: bold;
        color: #9CA3AF;
        letter-spacing: 0.5px;
    }
    QLabel#StatVal {
        font-size: 18pt;
        font-weight: bold;
        color: #FFFFFF;
    }
    QLabel#StatSub {
        font-size: 8.0pt;
        color: #C5A059; /* Stats subtext in Gold */
    }
    
    /* Stats Circular Icon Badges - Flat solid style with thin gold border */
    QLabel#IconTotal {
        background-color: rgba(197, 160, 89, 0.1);
        border: 1px solid #C5A059;
        border-radius: 18px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
    }
    QLabel#IconQueued {
        background-color: rgba(197, 160, 89, 0.1);
        border: 1px solid #C5A059;
        border-radius: 18px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
    }
    QLabel#IconGenerating {
        background-color: rgba(16, 185, 129, 0.15);
        border: 1px solid #10B981;
        border-radius: 18px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
    }
    QLabel#IconDone {
        background-color: rgba(16, 185, 129, 0.15);
        border: 1px solid #10B981;
        border-radius: 18px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
    }
    QLabel#IconFailed {
        background-color: rgba(239, 68, 68, 0.15);
        border: 1px solid #EF4444;
        border-radius: 18px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
    }
    QLabel#IconSkipped {
        background-color: rgba(156, 163, 175, 0.15);
        border: 1px solid #9CA3AF;
        border-radius: 18px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
    }
    
    /* Progress bar */
    QProgressBar {
        background-color: #161722;
        border: 1px solid #1F2231;
        border-radius: 3px;
        max-height: 6px;
        text-align: right;
    }
    QProgressBar::chunk {
        background-color: #C5A059; /* Gold progress bar */
        border-radius: 3px;
    }
    
    /* ==========================================
       INPUT FORM CONTROLS
       ========================================== */
    QLabel#FormInputLabel {
        font-size: 8pt;
        font-weight: bold;
        color: #9CA3AF;
        letter-spacing: 0.5px;
    }
    
    QToolTip {
        background-color: #12131C;
        border: 1px solid #C5A059;
        border-radius: 6px;
        padding: 8px;
        color: #E5E7EB;
        font-family: 'Inter', 'Outfit', 'Segoe UI', sans-serif;
        font-size: 8.5pt;
    }
    
    QComboBox, QLineEdit, QSpinBox {
        background-color: #06070B;
        border: 1px solid #1F2231;
        border-radius: 8px;
        padding: 4px 10px;
        color: #FFFFFF;
        font-size: 9.5pt;
        min-height: 34px;
        max-height: 34px;
    }
    QComboBox:focus, QLineEdit:focus, QSpinBox:focus {
        border-color: #C5A059; /* Gold focus border */
    }
    QComboBox::drop-down {
        border: none;
        width: 24px;
    }
    
    /* Pixel-perfect Base64 SVG Dropdown Chevron Arrow for cross-platform compliance */
    QComboBox::down-arrow {
        image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMCIgaGVpZ2h0PSI2IiB2aWV3Qm94PSIwIDAgMTAgNiI+PHBhdGggZmlsbD0iIzk0QTNBRiIgZD0iTTAgMEw1IDZMMTAgMFoiLz48L3N2Zz4=);
        width: 10px;
        height: 6px;
        margin-right: 10px;
    }
    
    /* Style QComboBox dropdown popup explicitly to fix text visibility issues */
    QComboBox QAbstractItemView {
        background-color: #06070B;
        color: #FFFFFF;
        border: 1px solid #1F2231;
        selection-background-color: #C5A059;
        selection-color: #0C0D14;
        padding: 4px;
    }
    QComboBox QAbstractItemView::item {
        min-height: 24px;
        padding-left: 8px;
        color: #FFFFFF;
    }
    
    /* Specific model styling to hide arrow dropdown */
    QComboBox#cb_model::drop-down {
        width: 0px;
        border: none;
    }
    QComboBox#cb_model::down-arrow {
        image: none;
    }
    QCheckBox {
        color: #E5E7EB;
        font-size: 9.5pt;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        background-color: #06070B;
        border: 1px solid #1F2231;
        border-radius: 4px;
    }
    QCheckBox::indicator:checked {
        background-color: #C5A059;
        border-color: #C5A059;
        image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4IiBoZWlnaHQ9IjYiIHZpZXdCb3g9IjAgMCA4IDYiPjxwYXRoIGZpbGw9IiMwQzBEMTQiIGQ9Ik0zIDZMMC0zTDEuNS00LjVMMy0zTDYuNS02TDggNC41WiIvPjwvc3ZnPg==);
    }
    QCheckBox::indicator:hover {
        border-color: #C5A059;
    }
    
    /* ==========================================
       PROMPTS & TEXT AREA
       ========================================== */
    QTextEdit#PromptsEditor {
        background-color: #06070B;
        border: 1px solid #1F2231;
        border-radius: 8px;
        padding: 10px;
        color: #E5E7EB;
        font-size: 9.5pt;
    }
    QTextEdit#PromptsEditor:focus {
        border-color: #C5A059;
    }
    
    /* ==========================================
       BUTTON STYLES
       ========================================== */
    /* START GENERATION (Gold CTA) */
    QPushButton#LaunchCTA {
        background-color: #C5A059; /* Solid Gold */
        color: #0C0D14; /* Dark text */
        font-weight: bold;
        font-size: 10pt;
        border-radius: 8px;
        padding: 10px;
        border: none;
    }
    QPushButton#LaunchCTA:hover {
        background-color: #D8B97C; /* Lighter Gold on hover */
    }
    QPushButton#LaunchCTA:pressed {
        background-color: #B28F46; /* Darker Gold on press */
    }
    
    /* STOP GENERATION (Red CTA) */
    QPushButton#StopCTA {
        background-color: #EF4444; /* Solid Red */
        color: #FFFFFF;
        font-weight: bold;
        font-size: 10pt;
        border-radius: 8px;
        padding: 10px;
        border: none;
    }
    QPushButton#StopCTA:hover {
        background-color: #F87171;
    }
    QPushButton#StopCTA:pressed {
        background-color: #DC2626;
    }
    
    QPushButton#PromptActionButton {
        background-color: #161722;
        border: 1px solid #1F2231;
        color: #D1D5DB;
        font-weight: bold;
        font-size: 8pt;
        border-radius: 6px;
        padding: 5px 10px;
    }
    QPushButton#PromptActionButton:hover {
        background-color: rgba(197, 160, 89, 0.05);
        border-color: #C5A059;
        color: #FFFFFF;
    }
    
    QPushButton#PromptActionButtonDanger {
        background-color: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.2);
        color: #F87171;
        font-weight: bold;
        font-size: 8pt;
        border-radius: 6px;
        padding: 5px 10px;
    }
    QPushButton#PromptActionButtonDanger:hover {
        background-color: rgba(239, 68, 68, 0.2);
        border-color: rgba(239, 68, 68, 0.4);
    }
    
    QPushButton#DeleteRowBtn {
        background-color: transparent;
        border: none;
        color: #9CA3AF;
        font-weight: bold;
        font-size: 10pt;
        border-radius: 4px;
    }
    QPushButton#DeleteRowBtn:hover {
        background-color: rgba(239, 68, 68, 0.15);
        color: #EF4444;
    }

    
    /* ==========================================
       CONTROL PANEL ACTION BUTTONS
       ========================================== */
    QPushButton#StartBtn {
        background-color: #C5A059;
        color: #0C0D14;
        font-weight: bold;
        border-radius: 8px;
        padding: 8px 16px;
        border: none;
    }
    QPushButton#StartBtn:hover {
        background-color: #D8B97C;
    }
    
    QPushButton#PauseBtn {
        background-color: #C5A059;
        color: #0C0D14;
        font-weight: bold;
        border-radius: 8px;
        padding: 8px 16px;
        border: none;
    }
    QPushButton#PauseBtn:hover {
        background-color: #D8B97C;
    }
    
    QPushButton#StopBtn {
        background-color: #EF4444;
        color: #FFFFFF;
        font-weight: bold;
        border-radius: 8px;
        padding: 8px 16px;
        border: none;
    }
    QPushButton#StopBtn:hover {
        background-color: #DC2626;
    }
    
    QPushButton#ClearQueueBtn {
        background-color: #161722;
        color: #C5A059;
        font-weight: bold;
        border-radius: 8px;
        padding: 8px 16px;
        border: 1px solid #C5A059;
    }
    QPushButton#ClearQueueBtn:hover {
        background-color: #C5A059;
        color: #0C0D14;
    }
 
    /* ==========================================
       QUEUE GRID / DATA TABLE STYLES
       ========================================== */
    QTableWidget {
        background-color: #161722;
        border: none;
        gridline-color: transparent;
        color: #E5E7EB;
        font-size: 9pt;
    }
    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #1F2231;
    }
    QTableWidget::item:selected {
        background-color: rgba(255, 255, 255, 0.02);
        color: #FFFFFF;
    }
    QHeaderView::section {
        background-color: #161722;
        color: #9CA3AF;
        padding: 8px;
        font-weight: bold;
        font-size: 8.5pt;
        border: none;
        border-bottom: 2px solid #1F2231;
    }
    
    /* Pill status badges inside table */
    QLabel#BadgeGenerating {
        background-color: rgba(197, 160, 89, 0.15);
        color: #C5A059;
        border: 1px solid rgba(197, 160, 89, 0.3);
        border-radius: 6px;
        font-size: 8pt;
        font-weight: bold;
        padding: 3px 8px;
    }
    QLabel#BadgeDownloading {
        background-color: rgba(197, 160, 89, 0.15);
        color: #E8D5B5;
        border: 1px solid rgba(197, 160, 89, 0.3);
        border-radius: 6px;
        font-size: 8pt;
        font-weight: bold;
        padding: 3px 8px;
    }
    QLabel#BadgeSubmitting {
        background-color: rgba(197, 160, 89, 0.15);
        color: #C5A059;
        border: 1px solid rgba(197, 160, 89, 0.3);
        border-radius: 6px;
        font-size: 8pt;
        font-weight: bold;
        padding: 3px 8px;
    }
    QLabel#BadgeQueued {
        background-color: rgba(255, 255, 255, 0.05);
        color: #D1D5DB;
        border: 1px solid #1F2231;
        border-radius: 6px;
        font-size: 8pt;
        font-weight: bold;
        padding: 3px 8px;
    }
    QLabel#BadgeSuccess {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 6px;
        font-size: 8pt;
        font-weight: bold;
        padding: 3px 8px;
    }
    QLabel#BadgeFailed {
        background-color: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 6px;
        font-size: 8pt;
        font-weight: bold;
        padding: 3px 8px;
    }
    QLabel#BadgeSkipped {
        background-color: rgba(156, 163, 175, 0.15);
        color: #9CA3AF;
        border: 1px solid rgba(156, 163, 175, 0.3);
        border-radius: 6px;
        font-size: 8pt;
        font-weight: bold;
        padding: 3px 8px;
    }
    
    /* ==========================================
       LIVE LOG CONSOLE TERMINAL
       ========================================== */
    QTextEdit#ConsoleTerminal {
        background-color: #06070B;
        border: 1px solid #1F2231;
        border-radius: 8px;
        padding: 10px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 8.5pt;
        color: #E5E7EB;
    }
    QLineEdit#ConsoleSearchBox {
        background-color: #06070B;
        border: 1px solid #1F2231;
        border-radius: 6px;
        padding: 4px 8px;
        color: #FFFFFF;
        font-size: 8.5pt;
    }
    QPushButton#ConsoleActionButton {
        background-color: #161722;
        border: 1px solid #1F2231;
        border-radius: 6px;
        padding: 4px;
        min-width: 24px;
        max-width: 24px;
        min-height: 24px;
        max-height: 24px;
    }
    QPushButton#ConsoleActionButton:hover {
        background-color: rgba(197, 160, 89, 0.05);
        border-color: #C5A059;
    }
 
    /* ==========================================
       DIALOGS & POPUPS STYLING (QMessageBox / QDialog)
       ========================================== */
    QDialog, QMessageBox {
        background-color: #12131C;
        border: 1px solid #1F2231;
    }
    QMessageBox QLabel {
        color: #E5E7EB;
        font-size: 9.5pt;
    }
    QMessageBox QPushButton {
        background-color: #161722;
        border: 1px solid #1F2231;
        color: #D1D5DB;
        font-weight: bold;
        font-size: 8.5pt;
        border-radius: 6px;
        padding: 6px 14px;
        min-width: 70px;
    }
    QMessageBox QPushButton:hover {
        background-color: rgba(197, 160, 89, 0.05);
        border-color: #C5A059;
        color: #FFFFFF;
    }
    
    /* ==========================================
       QTabWidget / QTabBar Styles
       ========================================== */
    QTabWidget::pane {
        border: none;
        background: transparent;
    }
    QTabBar::tab {
        background: #12131C;
        border: 1px solid #1F2231;
        border-bottom-color: #1F2231;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        padding: 5px 12px;
        font-weight: bold;
        font-size: 8.5pt;
        color: #9CA3AF;
        margin-right: 4px;
    }
    QTabBar::tab:hover {
        background: #161722;
        color: #E5E7EB;
        border-color: #2D314A;
    }
    QTabBar::tab:selected {
        background: #161722;
        color: #C5A059; /* Gold */
        border-color: #1F2231;
        border-top-color: #C5A059;
        border-bottom: none;
    }
"""

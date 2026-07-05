# styles.py — QSS (Qt Style Sheets) for Nexus Automator GUI

UI_MASTER_QSS = """
    /* ==========================================
       GLOBAL BASE WINDOW STYLES
       ========================================== */
    QMainWindow { 
        background-color: #090D1A; 
    }
    QScrollArea#MainScrollArea, QWidget#MainWorkspace {
        background-color: transparent;
        border: none;
    }
    QWidget { 
        font-family: 'Inter', 'Outfit', 'Segoe UI', sans-serif; 
        color: #F3F4F6; 
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
        background: #1E293B;
        border-radius: 4px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #334155;
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
        background: #1E293B;
        border-radius: 4px;
        min-width: 20px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #334155;
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
        background-color: #0B0F19; 
        border-right: 1px solid #1D263B; 
    }
    
    QLabel#SidebarBrandName {
        font-size: 13pt;
        font-weight: bold;
        color: #FFFFFF;
    }
    
    QLabel#SidebarBrandVersion {
        font-size: 7.5pt;
        font-weight: bold;
        color: #8B5CF6;
    }

    QLabel#MenuLabel {
        font-size: 7.5pt;
        font-weight: bold;
        color: #4B5563;
        letter-spacing: 1.5px;
        margin-top: 10px;
        margin-left: 14px;
    }
    
    /* Sidebar List Items - Set transparent to prevent double borders selection glitch */
    QListWidget#SidebarMenu { 
        background-color: transparent; 
        border: none; 
        outline: none;
    }
    QListWidget#SidebarMenu::item { 
        background: transparent;
        border: none;
        padding: 0px;
        margin-bottom: 6px;
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
        background: #0D1117;
        width: 4px;
        border-radius: 2px;
        margin: 0px;
    }
    QListWidget#SidebarMenu QScrollBar::handle:vertical {
        background: #1E3A4A;
        border-radius: 2px;
        min-height: 20px;
    }
    QListWidget#SidebarMenu QScrollBar::add-line:vertical,
    QListWidget#SidebarMenu QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    /* Profile Box */
    QFrame#ProfileBox {
        background-color: #111827;
        border: 1px solid #1E293B;
        border-radius: 12px;
    }
    
    QLabel#ProfileAvatar {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8B5CF6, stop:1 #3B82F6);
        color: #FFFFFF;
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
        color: #9CA3AF;
    }
    
    /* ==========================================
       PANEL CARDS (CONTAINERS)
       ========================================== */
    QFrame#PanelCard {
        background-color: #111827;
        border: 1px solid #1D263B;
        border-radius: 12px;
    }
    
    /* Highlighted / Glowing Card Borders from Mockup */
    QFrame#PromptsCard {
        background-color: #111827;
        border: 1px solid rgba(139, 92, 246, 0.5); /* Purple glowing border */
        border-radius: 12px;
    }
    QFrame#SettingsCard {
        background-color: #111827;
        border: 1px solid rgba(59, 130, 246, 0.5); /* Blue glowing border */
        border-radius: 12px;
    }
    
    QLabel#PanelTitle {
        font-size: 10pt;
        font-weight: bold;
        color: #FFFFFF;
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
        background-color: #111827;
        border: 1px solid #1D263B;
        border-radius: 8px;
        padding: 6px;
        min-width: 34px;
        max-width: 34px;
        min-height: 34px;
        max-height: 34px;
    }
    QPushButton#HeaderActionButton:hover {
        background-color: rgba(255, 255, 255, 0.02);
        border-color: #3B82F6;
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
        color: #6B7280;
    }
    
    /* Stats Circular Icon Badges (glowing semi-transparent circles with outline borders) */
    QLabel#IconTotal {
        background-color: rgba(37, 99, 235, 0.2);
        border: 1.5px solid rgba(37, 99, 235, 0.4);
        border-radius: 18px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
    }
    QLabel#IconQueued {
        background-color: rgba(124, 58, 237, 0.2);
        border: 1.5px solid rgba(124, 58, 237, 0.4);
        border-radius: 18px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
    }
    QLabel#IconGenerating {
        background-color: rgba(5, 150, 105, 0.2);
        border: 1.5px solid rgba(5, 150, 105, 0.4);
        border-radius: 18px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
    }
    QLabel#IconDone {
        background-color: rgba(5, 150, 105, 0.2);
        border: 1.5px solid rgba(5, 150, 105, 0.4);
        border-radius: 18px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
    }
    QLabel#IconFailed {
        background-color: rgba(220, 38, 38, 0.2);
        border: 1.5px solid rgba(220, 38, 38, 0.4);
        border-radius: 18px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
    }
    QLabel#IconSkipped {
        background-color: rgba(75, 85, 99, 0.2);
        border: 1.5px solid rgba(75, 85, 99, 0.4);
        border-radius: 18px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
    }
    
    /* Progress bar */
    QProgressBar {
        background-color: rgba(255, 255, 255, 0.03);
        border: none;
        border-radius: 3px;
        max-height: 5px;
        text-align: right;
    }
    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B5CF6, stop:1 #3B82F6);
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
    
    QComboBox, QLineEdit, QSpinBox {
        background-color: #070A13;
        border: 1px solid #1D263B;
        border-radius: 8px;
        padding: 8px 12px;
        color: #FFFFFF;
        font-size: 9.5pt;
    }
    QComboBox:focus, QLineEdit:focus, QSpinBox:focus {
        border-color: #3B82F6;
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
        background-color: #070A13;
        color: #FFFFFF;
        border: 1px solid #1D263B;
        selection-background-color: #8B5CF6;
        selection-color: #FFFFFF;
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
    
    /* ==========================================
       PROMPTS & TEXT AREA
       ========================================== */
    QTextEdit#PromptsEditor {
        background-color: #070A13;
        border: 1px solid #1D263B;
        border-radius: 8px;
        padding: 10px;
        color: #F3F4F6;
        font-size: 9.5pt;
    }
    QTextEdit#PromptsEditor:focus {
        border-color: #3B82F6;
    }
    
    /* ==========================================
       BUTTON STYLES
       ========================================== */
    /* START GENERATION (Gradient CTA) */
    QPushButton#LaunchCTA {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B5CF6, stop:1 #3B82F6);
        color: #FFFFFF;
        font-weight: bold;
        font-size: 10pt;
        border-radius: 8px;
        padding: 10px;
        border: none;
    }
    QPushButton#LaunchCTA:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9F7AEA, stop:1 #4299E1);
    }
    QPushButton#LaunchCTA:pressed {
        background-color: #8B5CF6;
    }
    
    /* STOP GENERATION (Red Gradient CTA) */
    QPushButton#StopCTA {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EF4444, stop:1 #B91C1C);
        color: #FFFFFF;
        font-weight: bold;
        font-size: 10pt;
        border-radius: 8px;
        padding: 10px;
        border: none;
    }
    QPushButton#StopCTA:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F87171, stop:1 #DC2626);
    }
    QPushButton#StopCTA:pressed {
        background-color: #DC2626;
    }
    
    QPushButton#PromptActionButton {
        background-color: #1F2937;
        border: 1px solid #1D263B;
        color: #D1D5DB;
        font-weight: bold;
        font-size: 8pt;
        border-radius: 6px;
        padding: 5px 10px;
    }
    QPushButton#PromptActionButton:hover {
        background-color: #374151;
        border-color: #4B5563;
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
    
    /* ==========================================
       CONTROL PANEL ACTION BUTTONS
       ========================================== */
    QPushButton#StartBtn {
        background-color: #10B981;
        color: #FFFFFF;
        font-weight: bold;
        border-radius: 8px;
        padding: 8px 16px;
        border: none;
    }
    QPushButton#StartBtn:hover {
        background-color: #059669;
    }
    
    QPushButton#PauseBtn {
        background-color: #D97706;
        color: #FFFFFF;
        font-weight: bold;
        border-radius: 8px;
        padding: 8px 16px;
        border: none;
    }
    QPushButton#PauseBtn:hover {
        background-color: #B45309;
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
        background-color: #374151;
        color: #D1D5DB;
        font-weight: bold;
        border-radius: 8px;
        padding: 8px 16px;
        border: 1px solid #4B5563;
    }
    QPushButton#ClearQueueBtn:hover {
        background-color: #4B5563;
        color: #FFFFFF;
    }

    /* ==========================================
       QUEUE GRID / DATA TABLE STYLES
       ========================================== */
    QTableWidget {
        background-color: #111827;
        border: none;
        gridline-color: transparent;
        color: #E5E7EB;
        font-size: 9pt;
    }
    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #1F2937;
    }
    QTableWidget::item:selected {
        background-color: rgba(255, 255, 255, 0.02);
        color: #FFFFFF;
    }
    QHeaderView::section {
        background-color: #111827;
        color: #9CA3AF;
        padding: 8px;
        font-weight: bold;
        font-size: 8.5pt;
        border: none;
        border-bottom: 2px solid #1F2937;
    }
    
    /* Pill status badges inside table */
    QLabel#BadgeGenerating {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 6px;
        font-size: 8pt;
        font-weight: bold;
        padding: 3px 8px;
    }
    QLabel#BadgeDownloading {
        background-color: rgba(59, 130, 246, 0.15);
        color: #3B82F6;
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 6px;
        font-size: 8pt;
        font-weight: bold;
        padding: 3px 8px;
    }
    QLabel#BadgeSubmitting {
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 6px;
        font-size: 8pt;
        font-weight: bold;
        padding: 3px 8px;
    }
    QLabel#BadgeQueued {
        background-color: rgba(139, 92, 246, 0.15);
        color: #A78BFA;
        border: 1px solid rgba(139, 92, 246, 0.3);
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
        background-color: #070A13;
        border: 1px solid #1D263B;
        border-radius: 8px;
        padding: 10px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 8.5pt;
        color: #E5E7EB;
    }
    QLineEdit#ConsoleSearchBox {
        background-color: #070A13;
        border: 1px solid #1D263B;
        border-radius: 6px;
        padding: 4px 8px;
        color: #FFFFFF;
        font-size: 8.5pt;
    }
    QPushButton#ConsoleActionButton {
        background-color: #1F2937;
        border: 1px solid #1D263B;
        border-radius: 6px;
        padding: 4px;
        min-width: 24px;
        max-width: 24px;
        min-height: 24px;
        max-height: 24px;
    }
    QPushButton#ConsoleActionButton:hover {
        background-color: #374151;
        border-color: #4B5563;
    }

    /* ==========================================
       DIALOGS & POPUPS STYLING (QMessageBox / QDialog)
       ========================================== */
    QDialog, QMessageBox {
        background-color: #0B0F19;
        border: 1px solid #1D263B;
    }
    QMessageBox QLabel {
        color: #F3F4F6;
        font-size: 9.5pt;
    }
    QMessageBox QPushButton {
        background-color: #1F2937;
        border: 1px solid #1D263B;
        color: #D1D5DB;
        font-weight: bold;
        font-size: 8.5pt;
        border-radius: 6px;
        padding: 6px 14px;
        min-width: 70px;
    }
    QMessageBox QPushButton:hover {
        background-color: #374151;
        border-color: #4B5563;
        color: #FFFFFF;
    }
"""

# admin_ui_config.py — QSS (Qt Style Sheets) for AKIRA Admin Creator Tool

UI_ADMIN_QSS = """
    QMainWindow { 
        background-color: #0C0D14; 
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
    
    /* Cards & Frames */
    QFrame#CardPanel {
        background-color: #12131C;
        border: 1px solid #1F2231;
        border-radius: 8px;
    }
    QFrame#ConsoleBox {
        background-color: #090A10;
        border: 1px solid #1F2231;
        border-radius: 6px;
    }

    /* Labels & Headers */
    QLabel#TitleLabel {
        font-size: 14pt;
        font-weight: bold;
        color: #C5A059;
    }
    QLabel#SubtitleLabel {
        font-size: 8.5pt;
        color: #8C91A7;
    }
    QLabel#FormLabel {
        font-weight: bold;
        font-size: 9.0pt;
        color: #E5E7EB;
    }

    /* Form Fields */
    QLineEdit {
        background-color: #171822;
        border: 1px solid #1F2231;
        border-radius: 6px;
        padding: 8px 12px;
        color: #FFFFFF;
        font-size: 9.5pt;
    }
    QLineEdit:focus {
        border: 1px solid #C5A059;
        background-color: #1A1C28;
    }
    
    QTextEdit {
        background-color: #08090E;
        border: 1px solid #1F2231;
        border-radius: 6px;
        padding: 10px;
        color: #E5E7EB;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 9.0pt;
    }
    
    /* Dropdown ComboBox styling */
    QComboBox {
        background-color: #171822;
        border: 1px solid #1F2231;
        border-radius: 6px;
        padding: 6px 12px;
        color: #FFFFFF;
    }
    QComboBox:focus {
        border: 1px solid #C5A059;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox QAbstractItemView {
        background-color: #12131C;
        border: 1px solid #1F2231;
        selection-background-color: #C5A059;
        selection-color: #0C0D14;
        color: #E5E7EB;
        outline: none;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 9.0pt;
    }
    
    /* Checkbox */
    QCheckBox {
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #1F2231;
        border-radius: 4px;
        background-color: #171822;
    }
    QCheckBox::indicator:checked {
        background-color: #C5A059;
        border: 1px solid #C5A059;
    }

    /* Buttons */
    QPushButton#PrimaryButton {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #D4AF37, stop:1 #A68015);
        color: #0C0D14;
        font-weight: bold;
        font-size: 9.5pt;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
    }
    QPushButton#PrimaryButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #E5C158, stop:1 #B89222);
    }
    QPushButton#PrimaryButton:pressed {
        background-color: #A68015;
    }
    QPushButton#PrimaryButton:disabled {
        background-color: #2E303B;
        color: #6B7280;
    }

    QPushButton#SecondaryButton {
        background-color: #161722;
        color: #C5A059;
        font-weight: bold;
        font-size: 9.5pt;
        border: 1px solid #C5A059;
        border-radius: 6px;
        padding: 8px 16px;
    }
    QPushButton#SecondaryButton:hover {
        background-color: #C5A059;
        color: #0C0D14;
    }
    QPushButton#SecondaryButton:pressed {
        background-color: #A68015;
        color: #0C0D14;
    }
    
    /* Status Labels */
    QLabel#SuccessLabel {
        color: #10B981;
        font-weight: bold;
    }
    QLabel#WarningLabel {
        color: #F59E0B;
        font-weight: bold;
    }
    QLabel#ErrorLabel {
        color: #EF4444;
        font-weight: bold;
    }
"""

"""A modern light theme for the whole app, applied once via app.setStyleSheet()."""

INDIGO = "#4F46E5"
INDIGO_DARK = "#4338CA"
INDIGO_LIGHT = "#EEF2FF"
BG = "#F4F5F9"
CARD = "#FFFFFF"
BORDER = "#DCDFE6"
TEXT = "#1F2430"
TEXT_MUTED = "#6B7280"
DANGER = "#DC2626"
DANGER_DARK = "#B91C1C"

STYLESHEET = f"""
* {{
    font-family: -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: {TEXT};
}}

QMainWindow, QDialog {{
    background: {BG};
}}

QWidget#formHeading {{
    font-size: 18px;
    font-weight: 600;
    color: {TEXT};
}}

QLabel {{
    background: transparent;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    background: {CARD};
    top: -1px;
}}

QTabBar::tab {{
    background: transparent;
    color: {TEXT_MUTED};
    padding: 10px 18px;
    margin-right: 4px;
    border-bottom: 2px solid transparent;
    font-weight: 500;
}}

QTabBar::tab:selected {{
    color: {INDIGO};
    border-bottom: 2px solid {INDIGO};
}}

QTabBar::tab:hover:!selected {{
    color: {TEXT};
}}

QLineEdit, QTextEdit, QDateEdit, QTimeEdit, QComboBox {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: {INDIGO};
}}

QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QTimeEdit:focus, QComboBox:focus {{
    border: 1px solid {INDIGO};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background: {CARD};
    border: 1px solid {BORDER};
    selection-background-color: {INDIGO_LIGHT};
    selection-color: {TEXT};
    outline: none;
}}

QPushButton {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
}}

QPushButton:hover {{
    background: {INDIGO_LIGHT};
    border-color: {INDIGO};
}}

QPushButton:pressed {{
    background: {INDIGO_LIGHT};
}}

QPushButton:disabled {{
    color: {TEXT_MUTED};
    background: {BG};
}}

QPushButton#primaryButton {{
    background: {INDIGO};
    color: white;
    border: 1px solid {INDIGO};
}}

QPushButton#primaryButton:hover {{
    background: {INDIGO_DARK};
    border-color: {INDIGO_DARK};
}}

QPushButton#dangerButton {{
    color: {DANGER};
}}

QPushButton#dangerButton:hover {{
    background: #FEF2F2;
    border-color: {DANGER_DARK};
}}

QTableView, QListWidget {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    gridline-color: {BORDER};
    alternate-background-color: #FAFBFC;
    selection-background-color: {INDIGO_LIGHT};
    selection-color: {TEXT};
}}

QHeaderView::section {{
    background: {BG};
    color: {TEXT_MUTED};
    padding: 8px;
    border: none;
    border-bottom: 1px solid {BORDER};
    font-weight: 600;
}}

QMenuBar {{
    background: {CARD};
    border-bottom: 1px solid {BORDER};
}}

QMenuBar::item:selected {{
    background: {INDIGO_LIGHT};
}}

QMenu {{
    background: {CARD};
    border: 1px solid {BORDER};
}}

QMenu::item:selected {{
    background: {INDIGO_LIGHT};
}}

QStatusBar {{
    background: {BG};
    color: {TEXT_MUTED};
}}

QCheckBox {{
    spacing: 6px;
}}
"""

"""FCG (Figaro Culinary Group) themed look: Figaro Coffee's own trademark
registration specifies yellow and brown with black design elements, so the
palette below is built around a warm coffee brown + gold rather than a
generic SaaS blue."""

BROWN = "#6B3F2A"
BROWN_DARK = "#4E2E1E"
BROWN_LIGHT = "#F4E9DD"
GOLD = "#C8912A"
GOLD_LIGHT = "#FBF0DC"
BG = "#FAF6F1"
CARD = "#FFFFFF"
BORDER = "#E4D9CC"
TEXT = "#2B2117"
TEXT_MUTED = "#8A7865"
DANGER = "#B3261E"
DANGER_DARK = "#8C1D17"


def build_palette():
    """An explicit QPalette as a safety net underneath the stylesheet.
    The stylesheet alone didn't fully override every widget state (a
    read-only QLineEdit still picked a near-invisible gray from the
    inherited palette on some native styles) -- setting the palette
    directly for every color group closes that gap app-wide instead of
    patching each widget as it turns up."""
    from PySide6.QtGui import QColor, QPalette

    palette = QPalette()
    roles = {
        QPalette.Window: BG,
        QPalette.WindowText: TEXT,
        QPalette.Base: CARD,
        QPalette.AlternateBase: BROWN_LIGHT,
        QPalette.Text: TEXT,
        QPalette.Button: CARD,
        QPalette.ButtonText: TEXT,
        QPalette.ToolTipBase: CARD,
        QPalette.ToolTipText: TEXT,
        QPalette.Highlight: GOLD,
        QPalette.HighlightedText: TEXT,
        QPalette.PlaceholderText: TEXT_MUTED,
    }
    for group in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
        for role, color in roles.items():
            palette.setColor(group, role, QColor(color))
    for group in (QPalette.Active, QPalette.Inactive):
        palette.setColor(group, QPalette.Text, QColor(TEXT))
        palette.setColor(group, QPalette.WindowText, QColor(TEXT))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(TEXT_MUTED))
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(TEXT_MUTED))
    return palette

STYLESHEET = f"""
* {{
    font-family: "Segoe UI", "Helvetica Neue", -apple-system, Arial, sans-serif;
    font-size: 13px;
    color: {TEXT};
}}

QMainWindow, QDialog {{
    background: {BG};
}}

QWidget#formHeading {{
    font-size: 19px;
    font-weight: 600;
    color: {BROWN_DARK};
}}

QWidget#sectionHeading {{
    font-size: 13px;
    font-weight: 700;
    color: {GOLD};
    letter-spacing: 1px;
}}

QLabel {{
    background: transparent;
}}

QFrame#sectionDivider {{
    background: {BORDER};
    max-height: 1px;
    min-height: 1px;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 10px;
    background: {CARD};
    top: -1px;
}}

QTabBar {{
    font-size: 13px;
}}

QTabBar::tab {{
    background: transparent;
    color: {TEXT_MUTED};
    padding: 11px 20px;
    margin-right: 4px;
    border-bottom: 3px solid transparent;
    font-weight: 600;
}}

QTabBar::tab:selected {{
    color: {BROWN};
    border-bottom: 3px solid {GOLD};
}}

QTabBar::tab:hover:!selected {{
    color: {BROWN_DARK};
}}

QLineEdit, QTextEdit, QDateEdit, QTimeEdit, QComboBox {{
    background: {CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 7px 11px;
    selection-background-color: {GOLD};
    selection-color: {TEXT};
}}

QLineEdit:read-only {{
    color: {TEXT};
    background: {CARD};
}}

QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QTimeEdit:focus, QComboBox:focus {{
    border: 1.5px solid {BROWN};
}}

QComboBox::drop-down {{
    border: none;
    width: 26px;
}}

QComboBox::down-arrow {{
    width: 10px;
    height: 10px;
}}

/* Unscoped on purpose: QCompleter's popup is a top-level QListView, not a
descendant of the QComboBox it belongs to, so a "QComboBox QAbstractItemView"
selector never matches it -- it was falling back to the OS's native (and on
Windows, dark-mode-tinted) popup colors, rendering as unreadable dark text on
a near-black background. */
QAbstractItemView {{
    background: {CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    outline: none;
    selection-background-color: {GOLD_LIGHT};
    selection-color: {TEXT};
}}

QAbstractItemView::item {{
    padding: 5px 8px;
    color: {TEXT};
}}

QAbstractItemView::item:hover {{
    background: {BROWN_LIGHT};
}}

QAbstractItemView::item:selected {{
    background: {GOLD_LIGHT};
    color: {TEXT};
}}

QPushButton {{
    background: {CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: 600;
}}

QPushButton:hover {{
    background: {BROWN_LIGHT};
    border-color: {BROWN};
}}

QPushButton:pressed {{
    background: {GOLD_LIGHT};
}}

QPushButton:disabled {{
    color: {TEXT_MUTED};
    background: {BG};
}}

QPushButton#primaryButton {{
    background: {BROWN};
    color: white;
    border: 1px solid {BROWN};
}}

QPushButton#primaryButton:hover {{
    background: {BROWN_DARK};
    border-color: {BROWN_DARK};
}}

QPushButton#dangerButton {{
    color: {DANGER};
}}

QPushButton#dangerButton:hover {{
    background: #FDECEA;
    border-color: {DANGER_DARK};
}}

QTableView, QListWidget {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    gridline-color: {BORDER};
    alternate-background-color: #FBF8F4;
    selection-background-color: {GOLD_LIGHT};
    selection-color: {TEXT};
}}

QHeaderView::section {{
    background: {BROWN_LIGHT};
    color: {BROWN_DARK};
    padding: 9px 8px;
    border: none;
    border-bottom: 1px solid {BORDER};
    font-weight: 700;
}}

QMenuBar {{
    background: {CARD};
    border-bottom: 1px solid {BORDER};
}}

QMenuBar::item:selected {{
    background: {BROWN_LIGHT};
}}

QMenu {{
    background: {CARD};
    border: 1px solid {BORDER};
}}

QMenu::item:selected {{
    background: {BROWN_LIGHT};
}}

QStatusBar {{
    background: {BG};
    color: {TEXT_MUTED};
    border-top: 1px solid {BORDER};
}}

QCheckBox {{
    spacing: 6px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 12px;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {TEXT_MUTED};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* QCalendarWidget (the QDateEdit popup): Qt applies its own red weekend
text color programmatically (see entry_form.py's _style_calendar), QSS
alone can't override that part -- this covers the chrome around it. */
QCalendarWidget QWidget#qt_calendar_navigationbar {{
    background: {BROWN};
}}

QCalendarWidget QToolButton {{
    color: white;
    background: transparent;
    border: none;
    font-weight: 600;
    padding: 6px;
    border-radius: 6px;
}}

QCalendarWidget QToolButton:hover {{
    background: rgba(255, 255, 255, 0.18);
}}

QCalendarWidget QMenu {{
    background: {CARD};
    color: {TEXT};
}}

QCalendarWidget QSpinBox {{
    background: white;
    color: {TEXT};
    border-radius: 4px;
    padding: 2px 4px;
}}

QCalendarWidget QAbstractItemView {{
    background: {CARD};
    color: {TEXT};
    selection-background-color: {BROWN};
    selection-color: white;
    border: none;
}}
"""

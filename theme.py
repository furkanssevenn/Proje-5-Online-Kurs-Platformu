"""
═══════════════════════════════════════════════════════════════════════════
  MODERN TEMA — QSS Stil Sayfaları (Dark / Light)
═══════════════════════════════════════════════════════════════════════════
  • Indigo marka rengi (#6366f1)
  • Inter / Segoe UI / SF Pro fallback'i
  • Modern kartlar, gradient butonlar, hover/focus state'leri
"""

# ═════════════════════════════════════════════════════════════════════════
#  PALET
# ═════════════════════════════════════════════════════════════════════════
DARK = {
    "bg":             "#0b0d12",
    "bg_alt":         "#13151c",
    "card":           "#1a1d27",
    "card_hover":     "#21242f",
    "border":         "#2a2e3a",
    "border_strong":  "#363b4a",
    "text":           "#e7e9ee",
    "text_muted":     "#9aa0ad",
    "text_dim":       "#6b7280",
    "brand":          "#6366f1",
    "brand_hover":    "#7376f6",
    "brand_dim":      "#3b3f7a",
    "success":        "#10b981",
    "warning":        "#f59e0b",
    "danger":         "#ef4444",
    "info":           "#3b82f6",
    "shadow":         "rgba(0, 0, 0, 0.4)",
    # Chip palet (yüksek kontrast için ayrı renkler)
    "chip_brand_bg":   "rgba(99, 102, 241, 0.22)",
    "chip_brand_fg":   "#a5b4fc",
    "chip_info_bg":    "rgba(59, 130, 246, 0.22)",
    "chip_info_fg":    "#93c5fd",
    "chip_success_bg": "rgba(16, 185, 129, 0.22)",
    "chip_success_fg": "#6ee7b7",
    "chip_warning_bg": "rgba(245, 158, 11, 0.22)",
    "chip_warning_fg": "#fcd34d",
    "chip_danger_bg":  "rgba(239, 68, 68, 0.22)",
    "chip_danger_fg":  "#fca5a5",
}

LIGHT = {
    "bg":             "#f7f8fb",
    "bg_alt":         "#ffffff",
    "card":           "#ffffff",
    "card_hover":     "#fafbff",
    "border":         "#e5e7eb",
    "border_strong":  "#d1d5db",
    "text":           "#111827",
    "text_muted":     "#6b7280",
    "text_dim":       "#9ca3af",
    "brand":          "#4f46e5",
    "brand_hover":    "#4338ca",
    "brand_dim":      "#c7d2fe",
    "success":        "#059669",
    "warning":        "#d97706",
    "danger":         "#dc2626",
    "info":           "#2563eb",
    "shadow":         "rgba(15, 23, 42, 0.08)",
    # Chip palet (yüksek kontrast için ayrı renkler)
    "chip_brand_bg":   "#e0e7ff",
    "chip_brand_fg":   "#4338ca",
    "chip_info_bg":    "#dbeafe",
    "chip_info_fg":    "#1d4ed8",
    "chip_success_bg": "#d1fae5",
    "chip_success_fg": "#047857",
    "chip_warning_bg": "#fef3c7",
    "chip_warning_fg": "#b45309",
    "chip_danger_bg":  "#fee2e2",
    "chip_danger_fg":  "#b91c1c",
}


def qss(p: dict) -> str:
    """QSS string'ini palet üzerinden üretir."""
    return f"""
/* ──────────── GLOBAL ──────────── */
* {{
    font-family: "Inter", "Segoe UI", "SF Pro Display", "Helvetica Neue", sans-serif;
    color: {p['text']};
    outline: none;
}}

QMainWindow, QDialog, QWidget#RootBg {{
    background-color: {p['bg']};
}}

/* ─── Stacked content + scroll area background propagation ─── */
/* The QStackedWidget that hosts page views, and every page widget       */
/* directly inside it, must use the main background so titles and labels */
/* are not rendered on a default-light surface.                          */
QStackedWidget {{
    background-color: {p['bg']};
    border: none;
}}
QStackedWidget > QWidget {{
    background-color: {p['bg']};
}}
/* Scroll areas + their internal viewport + the user-supplied content
   widget all stay transparent, so the page-level dark background shows
   through cleanly regardless of objectName. */
QScrollArea > QWidget#qt_scrollarea_viewport {{
    background: transparent;
}}
QScrollArea > QWidget#qt_scrollarea_viewport > QWidget {{
    background: transparent;
}}

/* ──────────── ETİKETLER ──────────── */
QLabel {{
    background: transparent;
    color: {p['text']};
}}
QLabel[heroTitle="true"] {{
    font-size: 32px; font-weight: 800; color: {p['text']};
}}
QLabel[pageTitle="true"] {{
    font-size: 24px; font-weight: 700; color: {p['text']};
}}
QLabel[sectionTitle="true"] {{
    font-size: 17px; font-weight: 600; color: {p['text']};
}}
QLabel[textStyle="bold13"] {{ font-size: 13px; font-weight: 700; color: {p['text']}; }}
QLabel[textStyle="bold14"] {{ font-size: 14px; font-weight: 700; color: {p['text']}; }}
QLabel[textStyle="bold16"] {{ font-size: 16px; font-weight: 700; color: {p['text']}; }}
QLabel[textStyle="bold28"] {{ font-size: 28px; font-weight: 800; color: {p['text']}; }}
QLabel[textStyle="bold32"] {{ font-size: 32px; font-weight: 800; color: {p['text']}; }}
QLabel[muted="true"] {{
    color: {p['text_muted']};
}}
QLabel[dim="true"] {{
    color: {p['text_dim']}; font-size: 12px;
}}
QLabel[badge="true"] {{
    background: {p['brand_dim']};
    color: {p['brand']};
    padding: 4px 10px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 600;
}}

/* ──────────── KART ──────────── */
QFrame[card="true"], QWidget[card="true"] {{
    background-color: {p['card']};
    border: 1px solid {p['border']};
    border-radius: 14px;
}}
QFrame[card="true"]:hover, QWidget[cardHover="true"]:hover {{
    background-color: {p['card_hover']};
    border-color: {p['border_strong']};
}}

/* ──────────── BUTONLAR ──────────── */
QPushButton {{
    background-color: {p['card']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 10px;
    padding: 9px 18px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover  {{ background-color: {p['card_hover']}; border-color: {p['border_strong']}; }}
QPushButton:pressed {{ background-color: {p['border']}; }}
QPushButton:disabled {{ color: {p['text_dim']}; }}

QPushButton[actionBtn="true"] {{
    padding: 6px 14px;
    font-size: 12px;
    border-radius: 8px;
}}

QPushButton[primary="true"] {{
    background-color: {p['brand']};
    color: white;
    border: none;
    font-weight: 600;
}}
QPushButton[primary="true"]:hover  {{ background-color: {p['brand_hover']}; }}
QPushButton[primary="true"]:pressed {{ background-color: {p['brand_dim']}; }}

QPushButton[ghost="true"] {{
    background: transparent;
    border: none;
    color: {p['text_muted']};
}}
QPushButton[ghost="true"]:hover {{ color: {p['text']}; }}

QPushButton[danger="true"] {{
    background-color: {p['danger']};
    color: white; border: none; font-weight: 600;
}}
QPushButton[success="true"] {{
    background-color: {p['success']};
    color: white; border: none; font-weight: 600;
}}

QPushButton[icon="true"] {{
    padding: 0px;
    border-radius: 10px;
    background: transparent;
    border: 1px solid transparent;
}}
QPushButton[icon="true"]:hover {{
    background: {p['card_hover']}; border-color: {p['border']};
}}

QPushButton[sidebar="true"] {{
    background: transparent;
    border: none;
    color: {p['text_muted']};
    text-align: left;
    padding: 11px 16px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 500;
}}
QPushButton[sidebar="true"]:hover {{
    background: {p['card_hover']}; color: {p['text']};
}}
QPushButton[sidebar="true"][active="true"] {{
    background: {p['brand_dim']};
    color: {p['brand']};
    font-weight: 600;
}}

/* ──────────── INPUT ──────────── */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {p['bg_alt']};
    border: 1.5px solid {p['border']};
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    color: {p['text']};
    selection-background-color: {p['brand']};
    selection-color: white;
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border-color: {p['brand']};
}}
QLineEdit:disabled, QTextEdit:disabled {{
    background-color: {p['card']};
    color: {p['text_dim']};
}}

QLineEdit[search="true"] {{
    padding-left: 38px;
    background-color: {p['card']};
    border-radius: 12px;
}}

QComboBox::drop-down {{ border: none; width: 28px; }}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {p['text_muted']};
    margin-right: 10px;
}}
QComboBox QAbstractItemView {{
    background-color: {p['card']};
    border: 1px solid {p['border']};
    border-radius: 10px;
    selection-background-color: {p['brand_dim']};
    padding: 4px;
    outline: none;
}}

/* ──────────── SCROLLBAR ──────────── */
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{
    background: transparent; width: 10px; margin: 4px 0;
}}
QScrollBar::handle:vertical {{
    background: {p['border_strong']};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {p['text_dim']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}

QScrollBar:horizontal {{
    background: transparent; height: 10px; margin: 0 4px;
}}
QScrollBar::handle:horizontal {{
    background: {p['border_strong']};
    border-radius: 5px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{ background: {p['text_dim']}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ──────────── PROGRESS BAR ──────────── */
QProgressBar {{
    background-color: {p['card']};
    border: none; border-radius: 4px;
    height: 8px; text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background-color: {p['brand']};
    border-radius: 4px;
}}

/* ──────────── TABLO ──────────── */
QTableWidget, QTableView {{
    background-color: {p['card']};
    border: 1px solid {p['border']};
    border-radius: 12px;
    gridline-color: {p['border']};
    selection-background-color: {p['brand_dim']};
    selection-color: {p['text']};
    alternate-background-color: {p['bg_alt']};
}}
QTableWidget::item, QTableView::item {{
    padding: 10px 8px;
    border: none;
    border-bottom: 1px solid {p['border']};
}}
QTableWidget::item:selected {{ background: {p['brand_dim']}; }}
QHeaderView::section {{
    background-color: {p['bg_alt']};
    color: {p['text_muted']};
    padding: 10px 8px;
    border: none;
    border-bottom: 1px solid {p['border']};
    font-weight: 600;
    font-size: 12px;
}}

/* ──────────── LISTBOX ──────────── */
QListWidget {{
    background-color: {p['card']};
    border: 1px solid {p['border']};
    border-radius: 12px;
    padding: 6px;
    outline: none;
}}
QListWidget::item {{
    padding: 10px;
    border-radius: 8px;
    margin: 2px 0;
}}
QListWidget::item:hover {{ background: {p['card_hover']}; }}
QListWidget::item:selected {{
    background: {p['brand_dim']};
    color: {p['brand']};
}}

/* ──────────── TAB ──────────── */
QTabWidget::pane {{
    border: 1px solid {p['border']};
    border-radius: 12px;
    background-color: {p['card']};
    top: -1px;
}}
QTabBar::tab {{
    background: transparent;
    color: {p['text_muted']};
    padding: 10px 22px;
    border: none;
    font-weight: 500;
    margin-right: 4px;
}}
QTabBar::tab:hover {{ color: {p['text']}; }}
QTabBar::tab:selected {{
    background: {p['card']};
    color: {p['brand']};
    border: 1px solid {p['border']};
    border-bottom: 1px solid {p['card']};
    border-radius: 8px 8px 0 0;
    font-weight: 600;
}}

/* ──────────── CHECKBOX ──────────── */
QCheckBox {{ spacing: 8px; color: {p['text']}; }}
QCheckBox::indicator {{
    width: 18px; height: 18px;
    border-radius: 5px;
    border: 1.5px solid {p['border_strong']};
    background: {p['bg_alt']};
}}
QCheckBox::indicator:hover {{ border-color: {p['brand']}; }}
QCheckBox::indicator:checked {{
    background: {p['brand']};
    border-color: {p['brand']};
    image: none;
}}

/* ──────────── DİĞER ──────────── */
QToolTip {{
    background-color: {p['card']};
    color: {p['text']};
    border: 1px solid {p['border']};
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 12px;
}}
QMenu {{
    background-color: {p['card']};
    border: 1px solid {p['border']};
    border-radius: 10px;
    padding: 6px;
}}
QMenu::item {{
    padding: 8px 22px 8px 14px;
    border-radius: 6px;
}}
QMenu::item:selected {{ background: {p['brand_dim']}; color: {p['brand']}; }}
QMenu::separator {{
    height: 1px; background: {p['border']}; margin: 4px 8px;
}}

QFrame[separator="true"] {{
    background-color: {p['border']};
    max-height: 1px; min-height: 1px;
    border: none;
}}

QLabel[chip="true"] {{
    padding: 4px 12px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 700;
}}
QLabel[chipSuccess="true"] {{ background: {p['chip_success_bg']}; color: {p['chip_success_fg']}; }}
QLabel[chipWarning="true"] {{ background: {p['chip_warning_bg']}; color: {p['chip_warning_fg']}; }}
QLabel[chipDanger="true"]  {{ background: {p['chip_danger_bg']};  color: {p['chip_danger_fg']}; }}
QLabel[chipInfo="true"]    {{ background: {p['chip_info_bg']};    color: {p['chip_info_fg']}; }}
QLabel[chipBrand="true"]   {{ background: {p['chip_brand_bg']};   color: {p['chip_brand_fg']}; }}

QFrame#Sidebar {{
    background-color: {p['bg_alt']};
    border-right: 1px solid {p['border']};
}}

QFrame#TopBar {{
    background-color: {p['bg_alt']};
    border-bottom: 1px solid {p['border']};
}}
"""


def get_qss(dark: bool = True) -> str:
    return qss(DARK if dark else LIGHT)


def get_palette(dark: bool = True) -> dict:
    return DARK if dark else LIGHT

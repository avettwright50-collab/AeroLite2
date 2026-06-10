"""
AeroLite Browser
A minimal, clean browser built in Python.
Dependencies: pip install PyQt5 PyQtWebEngine
Run:          python aerolite.py
"""

import sys
import os
from PyQt5.QtCore import Qt, QUrl, QSize, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QPixmap, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLineEdit, QPushButton, QShortcut, QStatusBar,
    QProgressBar, QLabel, QMenu, QAction, QFrame,
    QDialog, QListWidget, QDialogButtonBox, QToolButton, QMessageBox,
    QSizePolicy
)
from PyQt5.QtWebEngineWidgets import (
    QWebEnginePage, QWebEngineView, QWebEngineSettings,
    QWebEngineProfile, QWebEngineDownloadItem
)

APP_NAME    = "AeroLite"
APP_VERSION = "1.0"
HOME_URL    = "aerolite://newtab"

# ── AeroLite minimalist palette ───────────────────────────────────────────────
# Off-white base, near-black text, single cool accent, nothing else.
C = {
    "bg":             "#F7F7F8",   # main background — warm off-white
    "bg_deep":        "#EFEFEF",   # slightly darker panels
    "tab_bar":        "#EBEBEC",   # tab strip
    "tab_active":     "#F7F7F8",   # active tab matches toolbar
    "tab_inactive":   "#DCDCDD",   # inactive tab
    "tab_hover":      "#E2E2E3",   # tab hover
    "border":         "#E0E0E1",   # subtle borders
    "text":           "#1A1A1A",   # primary text — near-black
    "text_dim":       "#8A8A8E",   # secondary / placeholder
    "accent":         "#5B8DEF",   # single accent — calm blue
    "accent_dim":     "#D6E4FF",   # accent tint for focus rings
    "secure":         "#3DAA6E",   # green for HTTPS
    "insecure":       "#D95F5F",   # red for HTTP
    "danger":         "#D95F5F",
    "btn_hover":      "#E4E4E5",
    "btn_press":      "#D8D8D9",
    "addr_bg":        "#FFFFFF",
    "addr_border":    "#E0E0E1",
    "addr_focus":     "#5B8DEF",
    "download_bg":    "#1E1E20",
    "download_text":  "#E8E8EA",
    "tab_text":       "#4A4A4E",
    "tab_text_active":"#1A1A1A",
}

# ── New-tab HTML page ─────────────────────────────────────────────────────────
NEW_TAB_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>New Tab</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: #F7F7F8;
    font-family: -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    color: #1A1A1A;
    user-select: none;
  }

  .logo {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #8A8A8E;
    margin-bottom: 40px;
  }

  .logo span {
    color: #5B8DEF;
  }

  .clock {
    font-size: 72px;
    font-weight: 200;
    letter-spacing: -2px;
    color: #1A1A1A;
    line-height: 1;
    margin-bottom: 8px;
  }

  .date {
    font-size: 14px;
    color: #8A8A8E;
    font-weight: 400;
    letter-spacing: 0.04em;
    margin-bottom: 52px;
  }

  .search-wrap {
    width: 480px;
    position: relative;
  }

  .search-wrap input {
    width: 100%;
    padding: 14px 20px;
    border: 1.5px solid #E0E0E1;
    border-radius: 32px;
    font-size: 15px;
    color: #1A1A1A;
    background: #fff;
    outline: none;
    transition: border-color 0.15s, box-shadow 0.15s;
  }

  .search-wrap input:focus {
    border-color: #5B8DEF;
    box-shadow: 0 0 0 3px #D6E4FF;
  }

  .search-wrap input::placeholder { color: #AEAEB2; }

  .shortcuts {
    margin-top: 52px;
    display: flex;
    gap: 16px;
  }

  .shortcut {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    text-decoration: none;
  }

  .shortcut-icon {
    width: 52px;
    height: 52px;
    background: #fff;
    border: 1.5px solid #E0E0E1;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    transition: border-color 0.15s, transform 0.1s;
  }

  .shortcut:hover .shortcut-icon {
    border-color: #5B8DEF;
    transform: translateY(-2px);
  }

  .shortcut-label {
    font-size: 11px;
    color: #8A8A8E;
    font-weight: 500;
    letter-spacing: 0.02em;
  }

  .tagline {
    position: fixed;
    bottom: 28px;
    font-size: 11px;
    color: #C7C7CC;
    letter-spacing: 0.06em;
  }
</style>
</head>
<body>

<div class="logo">Aero<span>Lite</span></div>

<div class="clock" id="clock">00:00</div>
<div class="date"  id="date">Monday, January 1</div>

<div class="search-wrap">
  <input id="search" type="text" placeholder="Search or type a URL…"
         autofocus autocomplete="off"
         onkeydown="if(event.key==='Enter') navigate(this.value)">
</div>

<div class="shortcuts">
  <a class="shortcut" onclick="navigate('https://youtube.com')">
    <div class="shortcut-icon">▶</div>
    <span class="shortcut-label">YouTube</span>
  </a>
  <a class="shortcut" onclick="navigate('https://github.com')">
    <div class="shortcut-icon">⌥</div>
    <span class="shortcut-label">GitHub</span>
  </a>
  <a class="shortcut" onclick="navigate('https://reddit.com')">
    <div class="shortcut-icon">◈</div>
    <span class="shortcut-label">Reddit</span>
  </a>
  <a class="shortcut" onclick="navigate('https://google.com')">
    <div class="shortcut-icon">◎</div>
    <span class="shortcut-label">Google</span>
  </a>
  <a class="shortcut" onclick="navigate('https://twitter.com')">
    <div class="shortcut-icon">◇</div>
    <span class="shortcut-label">X</span>
  </a>
</div>

<div class="tagline">AeroLite · Minimal by design</div>

<script>
  function navigate(val) {
    val = val.trim();
    if (!val) return;
    if (val.includes('.') && !val.includes(' ')) {
      if (!val.startsWith('http')) val = 'https://' + val;
      location.href = val;
    } else {
      location.href = 'https://www.google.com/search?q=' + encodeURIComponent(val);
    }
  }

  function tick() {
    const now  = new Date();
    const h    = String(now.getHours()).padStart(2, '0');
    const m    = String(now.getMinutes()).padStart(2, '0');
    document.getElementById('clock').textContent = h + ':' + m;
    const days   = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
    const months = ['January','February','March','April','May','June',
                    'July','August','September','October','November','December'];
    document.getElementById('date').textContent =
      days[now.getDay()] + ', ' + months[now.getMonth()] + ' ' + now.getDate();
  }
  tick();
  setInterval(tick, 10000);
</script>
</body>
</html>
"""

# ── SVG icons ─────────────────────────────────────────────────────────────────
ICONS = {
    "back":     "M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z",
    "forward":  "M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z",
    "reload":   "M17.65 6.35A7.958 7.958 0 0 0 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0 1 12 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z",
    "stop":     "M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z",
    "home":     "M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z",
    "star":     "M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z",
    "star_out": "M22 9.24l-7.19-.62L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21 12 17.27 18.18 21l-1.63-7.03L22 9.24zM12 15.4l-3.76 2.27 1-4.28-3.32-2.88 4.38-.38L12 6.1l1.71 4.04 4.38.38-3.32 2.88 1 4.28L12 15.4z",
    "lock":     "M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z",
    "unlock":   "M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6h2c0-1.66 1.34-3 3-3s3 1.34 3 3v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z",
    "info":     "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z",
    "menu":     "M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z",
    "download": "M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z",
    "bookmark": "M17 3H7c-1.1 0-1.99.9-1.99 2L5 21l7-3 7 3V5c0-1.1-.9-2-2-2z",
    "history":  "M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z",
    "newtab":   "M19 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10h-4v4h-2v-4H7v-2h4V7h2v4h4v2z",
    "devtools": "M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z",
    "focus":    "M3 9H1v14h14v-2H3V9zm18-6H7v14h14V3zm-2 12H9V5h10v10z",
}


def make_icon(name, color="#8A8A8E", size=18):
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"'
        ' width="{s}" height="{s}"><path fill="{c}" d="{d}"/></svg>'
    ).format(s=size, c=color, d=ICONS[name])
    px = QPixmap()
    px.loadFromData(svg.encode(), "SVG")
    return QIcon(px)


def icon_btn(icon_name, tip, size=30, color=None):
    color = color or C["text_dim"]
    btn = QPushButton()
    btn.setIcon(make_icon(icon_name, color, 16))
    btn.setIconSize(QSize(16, 16))
    btn.setToolTip(tip)
    btn.setFixedSize(size, size)
    btn.setStyleSheet(
        "QPushButton {{"
        "  background: transparent; border: none; border-radius: {r}px;"
        "}}"
        "QPushButton:hover   {{ background: {h}; }}"
        "QPushButton:pressed {{ background: {p}; }}"
        "QPushButton:disabled {{ opacity: 0.3; }}"
        .format(r=size // 2, h=C["btn_hover"], p=C["btn_press"])
    )
    return btn


# ── Web profile ───────────────────────────────────────────────────────────────

_PROFILE = None

def get_profile():
    global _PROFILE
    if _PROFILE is None:
        _PROFILE = QWebEngineProfile("AeroLite", QApplication.instance())
        _PROFILE.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
        _PROFILE.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        s = _PROFILE.settings()
        s.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        s.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        s.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        s.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        s.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        s.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        s.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        s.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        s.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        s.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        s.setAttribute(QWebEngineSettings.ShowScrollBars, True)
        s.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, False)
    return _PROFILE


# ── Custom URL scheme handler (aerolite://newtab) ─────────────────────────────

class NewTabPage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)

    def acceptNavigationRequest(self, url, nav_type, is_main):
        if url.scheme() == "aerolite" and url.host() == "newtab":
            self.setHtml(NEW_TAB_HTML, QUrl("aerolite://newtab"))
            return False
        return True


# ── Browser tab ───────────────────────────────────────────────────────────────

class BrowserTab(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        page = NewTabPage(get_profile(), self)
        self.setPage(page)

    def createWindow(self, win_type):
        win = self.window()
        if isinstance(win, MainWindow):
            return win.add_tab()
        return None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()

    def load_url(self, url):
        """Load a URL, intercepting aerolite:// scheme."""
        if isinstance(url, str):
            url = QUrl(url)
        if url.scheme() == "aerolite" and url.host() == "newtab":
            self.setHtml(NEW_TAB_HTML, QUrl("aerolite://newtab"))
        else:
            self.setUrl(url)


# ── Security badge ────────────────────────────────────────────────────────────

class SecurityBadge(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(22, 22)
        self.setCursor(Qt.ArrowCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet("QToolButton { border: none; background: transparent; padding: 0; }")
        self._set_unknown()

    def _set_secure(self):
        self.setIcon(make_icon("lock", C["secure"], 14))
        self.setToolTip("Secure connection")

    def _set_insecure(self):
        self.setIcon(make_icon("unlock", C["insecure"], 14))
        self.setToolTip("Not secure")

    def _set_unknown(self):
        self.setIcon(make_icon("info", C["text_dim"], 14))
        self.setToolTip("Site info")

    def update_for_url(self, url):
        scheme = url.scheme().lower()
        if scheme == "https":
            self._set_secure()
        elif scheme == "http":
            self._set_insecure()
        else:
            self._set_unknown()


# ── Bookmark button ───────────────────────────────────────────────────────────

class BookmarkButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(22, 22)
        self.setFocusPolicy(Qt.NoFocus)
        self.setCheckable(True)
        self.setStyleSheet("QToolButton { border: none; background: transparent; padding: 0; }")
        self._bookmarks = set()
        self._current_url = ""
        self.toggled.connect(self._on_toggled)
        self._refresh()

    def set_url(self, url):
        self._current_url = url.toString()
        self.blockSignals(True)
        self.setChecked(self._current_url in self._bookmarks)
        self.blockSignals(False)
        self._refresh()

    def _on_toggled(self, checked):
        if self._current_url:
            if checked:
                self._bookmarks.add(self._current_url)
            else:
                self._bookmarks.discard(self._current_url)
        self._refresh()

    def _refresh(self):
        if self.isChecked():
            self.setIcon(make_icon("star", C["accent"], 14))
            self.setToolTip("Bookmarked")
        else:
            self.setIcon(make_icon("star_out", C["text_dim"], 14))
            self.setToolTip("Bookmark this page  (Ctrl+D)")


# ── Address bar ───────────────────────────────────────────────────────────────

class AddressBar(QWidget):
    returnPressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(34)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._frame = QFrame()
        self._frame.setObjectName("addrFrame")
        self._frame.setStyleSheet(
            "QFrame#addrFrame {"
            "  background: " + C["addr_bg"] + ";"
            "  border: 1px solid " + C["addr_border"] + ";"
            "  border-radius: 17px;"
            "}"
            "QFrame#addrFrame:focus-within {"
            "  border-color: " + C["addr_focus"] + ";"
            "}"
        )

        inner = QHBoxLayout(self._frame)
        inner.setContentsMargins(10, 0, 10, 0)
        inner.setSpacing(6)

        self.security = SecurityBadge()

        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Search or type a URL")
        self.edit.setStyleSheet(
            "QLineEdit {"
            "  border: none; background: transparent;"
            "  font-size: 13px; color: " + C["text"] + ";"
            "  selection-background-color: " + C["accent_dim"] + ";"
            "  padding: 0; letter-spacing: 0.01em;"
            "}"
        )
        self.edit.returnPressed.connect(self.returnPressed)
        self.edit.focusInEvent = self._edit_focus_in

        self.bookmark_btn = BookmarkButton()

        inner.addWidget(self.security)
        inner.addWidget(self.edit, 1)
        inner.addWidget(self.bookmark_btn)
        outer.addWidget(self._frame)

    def _edit_focus_in(self, event):
        QLineEdit.focusInEvent(self.edit, event)
        QTimer.singleShot(0, self.edit.selectAll)

    def text(self):
        return self.edit.text()

    def setText(self, t):
        # Show aerolite://newtab as empty — cleaner look
        self.edit.setText("" if t.startswith("aerolite://") else t)

    def setFocus(self):
        self.edit.setFocus()
        QTimer.singleShot(0, self.edit.selectAll)

    def update_for_url(self, url):
        self.security.update_for_url(url)
        self.bookmark_btn.set_url(url)


# ── Download bar ──────────────────────────────────────────────────────────────

class DownloadBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(38)
        self.setStyleSheet(
            "background: " + C["download_bg"] + ";"
            "border-top: 1px solid #2E2E30;"
        )
        h = QHBoxLayout(self)
        h.setContentsMargins(16, 0, 16, 0)
        h.setSpacing(10)

        icon_lbl = QLabel("↓")
        icon_lbl.setStyleSheet(
            "color: " + C["accent"] + "; font-size: 15px; font-weight: 600;"
        )
        self._name = QLabel("Downloading…")
        self._name.setStyleSheet(
            "color: " + C["download_text"] + "; font-size: 12px;"
        )
        self._bar = QProgressBar()
        self._bar.setMaximumWidth(180)
        self._bar.setMaximumHeight(4)
        self._bar.setTextVisible(False)
        self._bar.setStyleSheet(
            "QProgressBar { background: #3A3A3C; border-radius: 2px; border: none; }"
            "QProgressBar::chunk { background: " + C["accent"] + "; border-radius: 2px; }"
        )
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(22, 22)
        close_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #6A6A6E; border: none; font-size: 12px; }"
            "QPushButton:hover { color: " + C["download_text"] + "; }"
        )
        close_btn.clicked.connect(self.hide)

        h.addWidget(icon_lbl)
        h.addWidget(self._name)
        h.addWidget(self._bar, 1)
        h.addWidget(close_btn)
        self.hide()

    def start_download(self, item):
        self._name.setText(item.downloadFileName() or "Downloading…")
        self._bar.setValue(0)
        self.show()
        item.downloadProgress.connect(self._on_progress)
        item.stateChanged.connect(lambda s, i=item: self._on_state(s, i))

    def _on_progress(self, received, total):
        if total > 0:
            self._bar.setValue(int(received / total * 100))

    def _on_state(self, state, item):
        if state == QWebEngineDownloadItem.DownloadCompleted:
            self._name.setText("Done  —  " + (item.downloadFileName() or "file"))
            QTimer.singleShot(4000, self.hide)
        elif state == QWebEngineDownloadItem.DownloadInterrupted:
            self._name.setText("Download failed")
            QTimer.singleShot(3000, self.hide)


# ── List dialog (bookmarks / history) ─────────────────────────────────────────

class ListDialog(QDialog):
    def __init__(self, title, items, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(500, 400)
        self.chosen = ""
        self.setStyleSheet(
            "QDialog { background: " + C["bg"] + "; }"
            "QListWidget {"
            "  border: 1px solid " + C["border"] + ";"
            "  border-radius: 8px; font-size: 13px;"
            "  background: #fff; color: " + C["text"] + ";"
            "}"
            "QListWidget::item { padding: 9px 12px; }"
            "QListWidget::item:selected {"
            "  background: " + C["accent_dim"] + "; color: " + C["accent"] + ";"
            "}"
            "QPushButton {"
            "  background: " + C["accent"] + "; color: #fff;"
            "  border: none; border-radius: 6px;"
            "  padding: 7px 20px; font-size: 13px;"
            "}"
            "QPushButton:hover { background: #4A7DE0; }"
        )
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        count = QLabel("{} {}".format(len(items), "item" if len(items) == 1 else "items") if items else "Nothing here yet.")
        count.setStyleSheet("color: " + C["text_dim"] + "; font-size: 12px;")
        self.lw = QListWidget()
        for item in items:
            self.lw.addItem(item)
        self.lw.itemDoubleClicked.connect(self._accept_item)
        btns = QDialogButtonBox(QDialogButtonBox.Open | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._accept_selected)
        btns.rejected.connect(self.reject)
        layout.addWidget(count)
        layout.addWidget(self.lw)
        layout.addWidget(btns)

    def _accept_selected(self):
        sel = self.lw.selectedItems()
        if sel:
            self.chosen = sel[0].text()
            self.accept()

    def _accept_item(self, item):
        self.chosen = item.text()
        self.accept()


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 800)
        self._history = []
        self._focus_mode = False
        self._build_ui()
        self._build_shortcuts()
        self.add_tab()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.setStyleSheet("QMainWindow { background: " + C["bg"] + "; }")

        container = QWidget()
        self.setCentralWidget(container)
        root = QVBoxLayout(container)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._toolbar = self._build_toolbar()
        root.addWidget(self._toolbar)

        self.tabs = self._build_tabs()
        root.addWidget(self.tabs)

        self.download_bar = DownloadBar()
        root.addWidget(self.download_bar)

        # Status bar — minimal, almost invisible
        status = QStatusBar()
        status.setMaximumHeight(20)
        status.setStyleSheet(
            "QStatusBar { background: " + C["bg"] + "; "
            "border-top: 1px solid " + C["border"] + "; }"
        )
        self.setStatusBar(status)
        self.status_label = QLabel()
        self.status_label.setStyleSheet(
            "font-size: 11px; color: " + C["text_dim"] + "; padding: 0 8px;"
        )
        self.load_progress = QProgressBar()
        self.load_progress.setMaximumWidth(80)
        self.load_progress.setMaximumHeight(3)
        self.load_progress.setTextVisible(False)
        self.load_progress.setVisible(False)
        self.load_progress.setStyleSheet(
            "QProgressBar { background: " + C["border"] + "; border: none; border-radius: 1px; }"
            "QProgressBar::chunk { background: " + C["accent"] + "; border-radius: 1px; }"
        )
        status.addPermanentWidget(self.status_label, 1)
        status.addPermanentWidget(self.load_progress)

        QWebEngineProfile.defaultProfile().downloadRequested.connect(self._on_download)
        get_profile().downloadRequested.connect(self._on_download)

    def _build_toolbar(self):
        bar = QWidget()
        bar.setFixedHeight(46)
        bar.setStyleSheet(
            "background: " + C["bg"] + ";"
            "border-bottom: 1px solid " + C["border"] + ";"
        )
        h = QHBoxLayout(bar)
        h.setContentsMargins(10, 0, 10, 0)
        h.setSpacing(2)

        # Nav buttons — smaller and more refined
        self.btn_back    = icon_btn("back",    "Back  (Alt+Left)")
        self.btn_forward = icon_btn("forward", "Forward  (Alt+Right)")
        self.btn_reload  = icon_btn("reload",  "Reload  (Ctrl+R)")

        # Thin spacer
        sp = QWidget()
        sp.setFixedWidth(6)

        self.address_bar = AddressBar()

        sp2 = QWidget()
        sp2.setFixedWidth(6)

        # Right side
        self.btn_focus    = icon_btn("focus",    "Focus mode  (Ctrl+Shift+F)")
        self.btn_history  = icon_btn("history",  "History  (Ctrl+H)")
        self.btn_bookmark = icon_btn("bookmark", "Bookmarks  (Ctrl+B)")
        self.btn_devtools = icon_btn("devtools", "Developer tools  (F12)")
        self.btn_menu     = icon_btn("menu",     "Menu")

        self.btn_back.clicked.connect(self.go_back)
        self.btn_forward.clicked.connect(self.go_forward)
        self.btn_reload.clicked.connect(self.reload_tab)
        self.address_bar.returnPressed.connect(self._navigate_from_bar)
        self.btn_focus.clicked.connect(self._toggle_focus_mode)
        self.btn_history.clicked.connect(self._show_history)
        self.btn_bookmark.clicked.connect(self._show_bookmarks)
        self.btn_devtools.clicked.connect(self._open_devtools)
        self.btn_menu.clicked.connect(self._show_menu)

        for w in [self.btn_back, self.btn_forward, self.btn_reload, sp,
                  self.address_bar, sp2,
                  self.btn_focus, self.btn_history, self.btn_bookmark,
                  self.btn_devtools, self.btn_menu]:
            h.addWidget(w)

        return bar

    def _build_tabs(self):
        tw = QTabWidget()
        tw.setDocumentMode(True)
        tw.setTabsClosable(True)
        tw.setMovable(True)
        tw.tabCloseRequested.connect(self.close_tab)
        tw.currentChanged.connect(self._on_tab_changed)
        tw.setStyleSheet(
            "QTabWidget::pane { border: none; }"
            "QTabBar {"
            "  background: " + C["tab_bar"] + ";"
            "  border-bottom: 1px solid " + C["border"] + ";"
            "}"
            "QTabBar::tab {"
            "  background: " + C["tab_inactive"] + ";"
            "  color: " + C["tab_text"] + ";"
            "  padding: 6px 14px 6px 12px;"
            "  border: none;"
            "  border-top-left-radius: 7px;"
            "  border-top-right-radius: 7px;"
            "  min-width: 70px; max-width: 180px;"
            "  font-size: 12px;"
            "  margin-right: 1px; margin-top: 3px;"
            "}"
            "QTabBar::tab:selected {"
            "  background: " + C["tab_active"] + ";"
            "  color: " + C["tab_text_active"] + ";"
            "  margin-top: 0; font-weight: 500;"
            "}"
            "QTabBar::tab:hover:!selected {"
            "  background: " + C["tab_hover"] + ";"
            "}"
        )
        new_btn = QPushButton()
        new_btn.setIcon(make_icon("newtab", C["text_dim"], 14))
        new_btn.setIconSize(QSize(14, 14))
        new_btn.setFixedSize(26, 26)
        new_btn.setToolTip("New tab  (Ctrl+T)")
        new_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 13px; }"
            "QPushButton:hover   { background: " + C["btn_hover"] + "; }"
            "QPushButton:pressed { background: " + C["btn_press"] + "; }"
        )
        new_btn.clicked.connect(lambda: self.add_tab())
        tw.setCornerWidget(new_btn, Qt.TopRightCorner)
        return tw

    def _build_shortcuts(self):
        pairs = [
            ("Ctrl+T",         lambda: self.add_tab()),
            ("Ctrl+W",         self.close_current_tab),
            ("Ctrl+R",         self.reload_tab),
            ("F5",             self.reload_tab),
            ("Ctrl+L",         self.focus_address_bar),
            ("Alt+Left",       self.go_back),
            ("Alt+Right",      self.go_forward),
            ("Ctrl+Tab",       self._next_tab),
            ("Ctrl+Shift+Tab", self._prev_tab),
            ("Ctrl+D",         self._bookmark_current),
            ("Ctrl+H",         self._show_history),
            ("Ctrl+B",         self._show_bookmarks),
            ("F12",            self._open_devtools),
            ("Ctrl+Shift+F",   self._toggle_focus_mode),
            ("Ctrl+Equal",     self._zoom_in),
            ("Ctrl+Minus",     self._zoom_out),
            ("Ctrl+0",         self._zoom_reset),
        ]
        for key, fn in pairs:
            QShortcut(QKeySequence(key), self, fn)

    # ── Tab management ────────────────────────────────────────────────────────

    def add_tab(self, url=None):
        view = BrowserTab(self)
        if url is None:
            view.setHtml(NEW_TAB_HTML, QUrl("aerolite://newtab"))
        elif isinstance(url, str) and url.startswith("aerolite://"):
            view.setHtml(NEW_TAB_HTML, QUrl("aerolite://newtab"))
        else:
            view.setUrl(url if isinstance(url, QUrl) else QUrl(url))

        view.titleChanged.connect(lambda t, v=view: self._update_tab_title(v, t))
        view.urlChanged.connect(lambda u, v=view: self._update_address(v, u))
        view.iconChanged.connect(lambda ic, v=view: self._update_tab_icon(v, ic))
        view.loadStarted.connect(lambda v=view: self._load_started(v))
        view.loadProgress.connect(lambda p, v=view: self._load_progress(v, p))
        view.loadFinished.connect(lambda ok, v=view: self._load_finished(v, ok))
        view.page().linkHovered.connect(self.status_label.setText)

        idx = self.tabs.addTab(view, "  New Tab")
        self.tabs.setCurrentIndex(idx)
        return view

    def close_tab(self, idx):
        if self.tabs.count() <= 1:
            self.close()
            return
        w = self.tabs.widget(idx)
        self.tabs.removeTab(idx)
        if w:
            w.deleteLater()

    def close_current_tab(self):
        self.close_tab(self.tabs.currentIndex())

    def current_view(self):
        return self.tabs.currentWidget()

    # ── Navigation ────────────────────────────────────────────────────────────

    def go_back(self):
        v = self.current_view()
        if v: v.back()

    def go_forward(self):
        v = self.current_view()
        if v: v.forward()

    def reload_tab(self):
        v = self.current_view()
        if v: v.reload()

    def focus_address_bar(self):
        self.address_bar.setFocus()

    def _next_tab(self):
        self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % self.tabs.count())

    def _prev_tab(self):
        self.tabs.setCurrentIndex((self.tabs.currentIndex() - 1) % self.tabs.count())

    def _navigate_from_bar(self):
        text = self.address_bar.text().strip()
        if not text:
            return
        if "." in text.split("/")[0] and " " not in text:
            if not text.startswith(("http://", "https://")):
                text = "https://" + text
            url = QUrl(text)
        else:
            encoded = QUrl.toPercentEncoding(text).data().decode()
            url = QUrl("https://www.google.com/search?q=" + encoded)
        v = self.current_view()
        if v:
            v.setUrl(url)

    # ── Focus mode ────────────────────────────────────────────────────────────

    def _toggle_focus_mode(self):
        self._focus_mode = not self._focus_mode
        self._toolbar.setVisible(not self._focus_mode)
        self.tabs.tabBar().setVisible(not self._focus_mode)
        self.statusBar().setVisible(not self._focus_mode)
        # Tint the focus button to show state
        color = C["accent"] if self._focus_mode else C["text_dim"]
        self.btn_focus.setIcon(make_icon("focus", color, 16))

    # ── Zoom ──────────────────────────────────────────────────────────────────

    def _zoom_in(self):
        v = self.current_view()
        if v: v.setZoomFactor(min(v.zoomFactor() + 0.1, 5.0))

    def _zoom_out(self):
        v = self.current_view()
        if v: v.setZoomFactor(max(v.zoomFactor() - 0.1, 0.25))

    def _zoom_reset(self):
        v = self.current_view()
        if v: v.setZoomFactor(1.0)

    # ── Bookmarks ─────────────────────────────────────────────────────────────

    def _bookmark_current(self):
        bm = self.address_bar.bookmark_btn
        bm.setChecked(not bm.isChecked())

    def _show_bookmarks(self):
        items = sorted(self.address_bar.bookmark_btn._bookmarks)
        dlg = ListDialog("Bookmarks", items, self)
        if dlg.exec_() == QDialog.Accepted and dlg.chosen:
            v = self.current_view()
            if v: v.setUrl(QUrl(dlg.chosen))

    # ── History ───────────────────────────────────────────────────────────────

    def _show_history(self):
        items = [h["url"] for h in reversed(self._history[-300:])]
        dlg = ListDialog("History", items, self)
        if dlg.exec_() == QDialog.Accepted and dlg.chosen:
            v = self.current_view()
            if v: v.setUrl(QUrl(dlg.chosen))

    def _clear_history(self):
        self._history.clear()

    # ── Downloads ─────────────────────────────────────────────────────────────

    def _on_download(self, item):
        item.accept()
        self.download_bar.start_download(item)

    # ── Dev tools ─────────────────────────────────────────────────────────────

    def _open_devtools(self):
        v = self.current_view()
        if not v:
            return
        dev = BrowserTab(self)
        v.page().setDevToolsPage(dev.page())
        dev.resize(900, 600)
        dev.setWindowTitle("AeroLite DevTools")
        dev.show()

    # ── Menu ──────────────────────────────────────────────────────────────────

    def _show_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu {"
            "  background: #fff;"
            "  border: 1px solid " + C["border"] + ";"
            "  border-radius: 10px; padding: 6px 0; font-size: 13px;"
            "}"
            "QMenu::item { padding: 9px 28px; color: " + C["text"] + "; }"
            "QMenu::item:selected { background: " + C["bg"] + "; color: " + C["accent"] + "; }"
            "QMenu::separator { height: 1px; background: " + C["border"] + "; margin: 5px 0; }"
        )

        def add(label, shortcut, fn):
            a = QAction(label, self)
            if shortcut:
                a.setShortcut(QKeySequence(shortcut))
            a.triggered.connect(fn)
            menu.addAction(a)

        add("New Tab",       "Ctrl+T",       lambda: self.add_tab())
        add("New Window",    "",             self._new_window)
        menu.addSeparator()
        add("Focus Mode",    "Ctrl+Shift+F", self._toggle_focus_mode)
        menu.addSeparator()
        add("Zoom In",       "Ctrl+=",       self._zoom_in)
        add("Zoom Out",      "Ctrl+-",       self._zoom_out)
        add("Reset Zoom",    "Ctrl+0",       self._zoom_reset)
        menu.addSeparator()
        add("Bookmarks",     "Ctrl+B",       self._show_bookmarks)
        add("History",       "Ctrl+H",       self._show_history)
        add("Clear History", "",             self._clear_history)
        menu.addSeparator()
        add("Developer Tools","F12",         self._open_devtools)
        add("Print to PDF",  "Ctrl+P",       self._print_page)
        menu.addSeparator()
        add("About AeroLite","",             self._show_about)

        pos = self.btn_menu.mapToGlobal(self.btn_menu.rect().bottomLeft())
        menu.exec_(pos)

    def _new_window(self):
        w = MainWindow()
        w.show()

    def _print_page(self):
        v = self.current_view()
        if v:
            path = os.path.join(os.path.expanduser("~"), "aerolite_print.pdf")
            v.page().printToPdf(path)

    def _show_about(self):
        QMessageBox.about(
            self, "About AeroLite",
            "<div style='font-family: Segoe UI, sans-serif;'>"
            "<h2 style='margin:0 0 4px 0; color:#1A1A1A;'>AeroLite</h2>"
            "<p style='color:#8A8A8E; margin:0 0 12px 0;'>Version " + APP_VERSION + "</p>"
            "<p style='color:#4A4A4E;'>A minimal browser built in Python.</p>"
            "<p style='color:#4A4A4E; margin-top:8px;'>"
            "Powered by PyQt5 &amp; Chromium.</p>"
            "</div>"
        )

    # ── Signal handlers ───────────────────────────────────────────────────────

    def _update_tab_title(self, view, title):
        idx = self.tabs.indexOf(view)
        if idx >= 0:
            if not title or title == "about:blank":
                title = "New Tab"
            label = title[:20] + "…" if len(title) > 22 else title
            self.tabs.setTabText(idx, "  " + label)
            if view is self.current_view():
                self.setWindowTitle(title + "  —  " + APP_NAME)

    def _update_tab_icon(self, view, icon):
        idx = self.tabs.indexOf(view)
        if idx >= 0 and not icon.isNull():
            self.tabs.setTabIcon(idx, icon)

    def _update_address(self, view, url):
        url_str = url.toString()
        if url_str and url_str not in ("about:blank", "aerolite://newtab"):
            if not self._history or self._history[-1]["url"] != url_str:
                self._history.append({"url": url_str, "title": view.title() or url_str})
        if view is self.current_view():
            self.address_bar.setText(url_str)
            self.address_bar.update_for_url(url)
            self.btn_back.setEnabled(view.history().canGoBack())
            self.btn_forward.setEnabled(view.history().canGoForward())

    def _on_tab_changed(self, idx):
        view = self.tabs.widget(idx)
        if view:
            self._update_address(view, view.url())
            title = view.title() or "New Tab"
            self.setWindowTitle(title + "  —  " + APP_NAME)

    def _load_started(self, view):
        if view is not self.current_view():
            return
        self.load_progress.setVisible(True)
        self.load_progress.setValue(0)
        self.btn_reload.setIcon(make_icon("stop", C["text_dim"], 16))
        self.btn_reload.setToolTip("Stop")
        try:
            self.btn_reload.clicked.disconnect()
        except TypeError:
            pass
        self.btn_reload.clicked.connect(view.stop)

    def _load_progress(self, view, p):
        if view is self.current_view():
            self.load_progress.setValue(p)

    def _load_finished(self, view, ok):
        if view is not self.current_view():
            return
        self.load_progress.setVisible(False)
        self.btn_reload.setIcon(make_icon("reload", C["text_dim"], 16))
        self.btn_reload.setToolTip("Reload  (Ctrl+R)")
        try:
            self.btn_reload.clicked.disconnect()
        except TypeError:
            pass
        self.btn_reload.clicked.connect(self.reload_tab)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", " ".join([
        "--disable-gpu",
        "--disable-gpu-compositing",
        "--disable-software-rasterizer",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--autoplay-policy=no-user-gesture-required",
    ]))

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_NAME)
    app.setFont(QFont("Segoe UI", 10))
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

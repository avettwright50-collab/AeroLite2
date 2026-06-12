"""
AeroLite Core (headless / no-UI)
---------------------------------
Pure browser-engine layer stripped of every Qt widget, stylesheet,
icon, palette constant, and dialog.  Only the web profile, page
subclass, tab view, download handling, history/bookmark stores, and
the programmatic navigation helpers remain.

Dependencies:
    pip install PyQt5 PyQtWebEngine

Minimal usage example
---------------------
    from aerolite_core import start_engine, Engine

    engine = start_engine()          # boots QApplication + profile
    tab    = engine.new_tab()
    tab.load_url("https://example.com")
    engine.run()                     # enters the Qt event loop
"""

import sys
import os

from PyQt5.QtCore    import QUrl, QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import (
    QWebEnginePage,
    QWebEngineView,
    QWebEngineSettings,
    QWebEngineProfile,
    QWebEngineDownloadItem,
)

APP_NAME    = "AeroLite"
APP_VERSION = "1.0"
HOME_URL    = "aerolite://newtab"

# ── New-tab fallback HTML (minimal — no styling, no clock widget) ─────────────

_NEW_TAB_HTML = """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>New Tab</title></head>
<body>
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
</script>
</body>
</html>
"""

# ── Shared web profile ────────────────────────────────────────────────────────

_PROFILE: QWebEngineProfile | None = None


def get_profile() -> QWebEngineProfile:
    """Return (and lazily create) the single shared QWebEngineProfile."""
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
        s.setAttribute(QWebEngineSettings.JavascriptEnabled,           True)
        s.setAttribute(QWebEngineSettings.PluginsEnabled,              True)
        s.setAttribute(QWebEngineSettings.FullScreenSupportEnabled,    True)
        s.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled,       True)
        s.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows,    True)
        s.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard,True)
        s.setAttribute(QWebEngineSettings.LocalStorageEnabled,         True)
        s.setAttribute(QWebEngineSettings.WebGLEnabled,                True)
        s.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled,  True)
        s.setAttribute(QWebEngineSettings.AutoLoadImages,              True)
        s.setAttribute(QWebEngineSettings.ShowScrollBars,              True)
        s.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, False)
    return _PROFILE


# ── Custom page — intercepts aerolite:// scheme ───────────────────────────────

class NewTabPage(QWebEnginePage):
    """QWebEnginePage that intercepts aerolite://newtab and serves the
    built-in new-tab HTML without needing a registered URL scheme handler."""

    def __init__(self, profile: QWebEngineProfile, parent=None):
        super().__init__(profile, parent)

    def acceptNavigationRequest(
        self, url: QUrl, nav_type, is_main_frame: bool
    ) -> bool:
        if url.scheme() == "aerolite" and url.host() == "newtab":
            self.setHtml(_NEW_TAB_HTML, QUrl("aerolite://newtab"))
            return False
        return True


# ── Browser tab (headless-friendly QWebEngineView) ────────────────────────────

class BrowserTab(QWebEngineView):
    """
    A single browser tab.  Accepts an optional *engine* reference so that
    ``createWindow`` can hand popup requests back to the Engine's tab list.
    """

    def __init__(self, engine: "Engine | None" = None, parent=None):
        super().__init__(parent)
        self._engine = engine
        page = NewTabPage(get_profile(), self)
        self.setPage(page)

    # Called by the web engine when a page opens a new window / tab
    def createWindow(self, win_type):
        if self._engine is not None:
            return self._engine.new_tab()
        return None

    # ── Programmatic navigation ───────────────────────────────────────────────

    def load_url(self, url: str | QUrl) -> None:
        """Navigate to *url*, resolving bare strings and aerolite:// URIs."""
        if isinstance(url, str):
            url = QUrl(url)
        if url.scheme() == "aerolite" and url.host() == "newtab":
            self.setHtml(_NEW_TAB_HTML, QUrl("aerolite://newtab"))
        else:
            self.setUrl(url)

    def navigate(self, text: str) -> None:
        """
        Resolve *text* the same way the address bar did:
        - looks like a domain  →  prepend https://
        - contains spaces      →  Google search
        """
        text = text.strip()
        if not text:
            return
        if "." in text.split("/")[0] and " " not in text:
            if not text.startswith(("http://", "https://")):
                text = "https://" + text
            self.load_url(QUrl(text))
        else:
            encoded = QUrl.toPercentEncoding(text).data().decode()
            self.load_url(QUrl("https://www.google.com/search?q=" + encoded))


# ── Download handler ──────────────────────────────────────────────────────────

class DownloadManager:
    """
    Accepts every download request and writes files to *download_dir*
    (defaults to ~/Downloads).  Calls the optional *on_progress* and
    *on_complete* callbacks.

    Callbacks
    ---------
    on_progress(item, received: int, total: int) -> None
    on_complete(item, success: bool)             -> None
    """

    def __init__(
        self,
        download_dir: str | None = None,
        on_progress=None,
        on_complete=None,
    ):
        self.download_dir = download_dir or os.path.join(
            os.path.expanduser("~"), "Downloads"
        )
        self._on_progress = on_progress
        self._on_complete = on_complete
        os.makedirs(self.download_dir, exist_ok=True)

    def connect_profile(self, profile: QWebEngineProfile) -> None:
        profile.downloadRequested.connect(self._handle)

    def _handle(self, item: QWebEngineDownloadItem) -> None:
        path = os.path.join(self.download_dir, item.downloadFileName())
        item.setPath(path)
        item.accept()
        if self._on_progress:
            item.downloadProgress.connect(
                lambda recv, total, i=item: self._on_progress(i, recv, total)
            )
        item.stateChanged.connect(lambda s, i=item: self._on_state_changed(s, i))

    def _on_state_changed(self, state, item: QWebEngineDownloadItem) -> None:
        if self._on_complete is None:
            return
        if state == QWebEngineDownloadItem.DownloadCompleted:
            self._on_complete(item, True)
        elif state == QWebEngineDownloadItem.DownloadInterrupted:
            self._on_complete(item, False)


# ── History store ─────────────────────────────────────────────────────────────

class HistoryStore:
    """In-memory browsing history (URL + title pairs, newest last)."""

    def __init__(self, max_entries: int = 1000):
        self._entries: list[dict] = []
        self._max = max_entries

    def record(self, url: str, title: str = "") -> None:
        if not url or url in ("about:blank", "aerolite://newtab"):
            return
        if self._entries and self._entries[-1]["url"] == url:
            return  # deduplicate consecutive identical URLs
        self._entries.append({"url": url, "title": title or url})
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max :]

    def recent(self, n: int = 100) -> list[dict]:
        return list(reversed(self._entries[-n:]))

    def clear(self) -> None:
        self._entries.clear()

    def all_urls(self) -> list[str]:
        return [e["url"] for e in reversed(self._entries)]


# ── Bookmark store ────────────────────────────────────────────────────────────

class BookmarkStore:
    """Simple in-memory set of bookmarked URLs."""

    def __init__(self):
        self._urls: set[str] = set()

    def add(self, url: str) -> None:
        self._urls.add(url)

    def remove(self, url: str) -> None:
        self._urls.discard(url)

    def toggle(self, url: str) -> bool:
        """Add if absent, remove if present.  Returns True if now bookmarked."""
        if url in self._urls:
            self._urls.discard(url)
            return False
        self._urls.add(url)
        return True

    def is_bookmarked(self, url: str) -> bool:
        return url in self._urls

    def all(self) -> list[str]:
        return sorted(self._urls)


# ── Engine — top-level coordinator ───────────────────────────────────────────

class Engine:
    """
    Owns the QApplication, web profile, all open tabs, and the shared
    history/bookmark/download stores.

    Typical headless usage
    ----------------------
        engine = Engine()
        tab = engine.new_tab("https://example.com")
        tab.loadFinished.connect(lambda ok: engine.quit())
        engine.run()
    """

    def __init__(self, download_dir: str | None = None):
        if QApplication.instance() is None:
            _setup_env()
            self._app = QApplication(sys.argv)
        else:
            self._app = QApplication.instance()

        self._app.setApplicationName(APP_NAME)
        self._app.setOrganizationName(APP_NAME)

        self.profile   = get_profile()
        self.history   = HistoryStore()
        self.bookmarks = BookmarkStore()
        self.downloads = DownloadManager(
            download_dir=download_dir,
            on_progress=self._on_dl_progress,
            on_complete=self._on_dl_complete,
        )
        self.downloads.connect_profile(self.profile)
        self.downloads.connect_profile(QWebEngineProfile.defaultProfile())

        self._tabs: list[BrowserTab] = []

    # ── Tab management ────────────────────────────────────────────────────────

    def new_tab(self, url: str | QUrl | None = None) -> BrowserTab:
        """Create, wire, and return a new BrowserTab."""
        tab = BrowserTab(engine=self)

        # Wire history recording
        tab.urlChanged.connect(
            lambda u, t=tab: self.history.record(
                u.toString(), t.title()
            )
        )

        if url is None:
            tab.setHtml(_NEW_TAB_HTML, QUrl("aerolite://newtab"))
        else:
            tab.load_url(url)

        self._tabs.append(tab)
        return tab

    def close_tab(self, tab: BrowserTab) -> None:
        if tab in self._tabs:
            self._tabs.remove(tab)
            tab.deleteLater()

    @property
    def tabs(self) -> list[BrowserTab]:
        return list(self._tabs)

    # ── Navigation helpers ────────────────────────────────────────────────────

    def go_back(self, tab: BrowserTab) -> None:
        tab.back()

    def go_forward(self, tab: BrowserTab) -> None:
        tab.forward()

    def reload(self, tab: BrowserTab) -> None:
        tab.reload()

    def stop(self, tab: BrowserTab) -> None:
        tab.stop()

    def zoom_in(self, tab: BrowserTab, step: float = 0.1) -> None:
        tab.setZoomFactor(min(tab.zoomFactor() + step, 5.0))

    def zoom_out(self, tab: BrowserTab, step: float = 0.1) -> None:
        tab.setZoomFactor(max(tab.zoomFactor() - step, 0.25))

    def zoom_reset(self, tab: BrowserTab) -> None:
        tab.setZoomFactor(1.0)

    def print_to_pdf(self, tab: BrowserTab, path: str | None = None) -> None:
        if path is None:
            path = os.path.join(os.path.expanduser("~"), "aerolite_print.pdf")
        tab.page().printToPdf(path)

    def open_devtools(self, tab: BrowserTab) -> BrowserTab:
        """Attach DevTools to *tab* and return the DevTools view."""
        dev = BrowserTab(engine=self)
        tab.page().setDevToolsPage(dev.page())
        return dev

    # ── Event-loop helpers ────────────────────────────────────────────────────

    def run(self) -> int:
        """Enter the Qt event loop.  Returns the exit code."""
        return self._app.exec_()

    def quit(self) -> None:
        self._app.quit()

    def call_later(self, ms: int, fn) -> QTimer:
        """Schedule *fn()* to run after *ms* milliseconds (one-shot)."""
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(fn)
        timer.start(ms)
        return timer

    # ── Internal callbacks ────────────────────────────────────────────────────

    def _on_dl_progress(self, item, received: int, total: int) -> None:
        # Override or subclass to react to download progress
        pass

    def _on_dl_complete(self, item, success: bool) -> None:
        # Override or subclass to react to completed / failed downloads
        pass


# ── Environment setup (GPU / sandbox flags) ───────────────────────────────────

def _setup_env() -> None:
    os.environ.setdefault(
        "QTWEBENGINE_CHROMIUM_FLAGS",
        " ".join([
            "--disable-gpu",
            "--disable-gpu-compositing",
            "--disable-software-rasterizer",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--autoplay-policy=no-user-gesture-required",
        ]),
    )


# ── Convenience factory ───────────────────────────────────────────────────────

def start_engine(download_dir: str | None = None) -> Engine:
    """Create and return a ready-to-use Engine instance."""
    _setup_env()
    return Engine(download_dir=download_dir)


# ── Minimal self-test entry point ─────────────────────────────────────────────

def main():
    engine = start_engine()

    tab = engine.new_tab("https://example.com")

    # Quit automatically 3 seconds after the page finishes loading
    tab.loadFinished.connect(lambda ok: engine.call_later(3000, engine.quit))

    sys.exit(engine.run())


if __name__ == "__main__":
    main()

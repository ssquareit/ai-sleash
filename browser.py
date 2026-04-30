import json
import os

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QIcon
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

HOME_URL = "https://duckduckgo.com"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
BOOKMARKS_FILE = os.path.join(DATA_DIR, "bookmarks.json")

BTN_CSS = """
    QPushButton {
        background: transparent;
        color: #a9b1d6;
        border: none;
        padding: 2px 4px;
        font-size: 18px;
        border-radius: 5px;
        min-width: 30px;
    }
    QPushButton:hover { background: #24253a; }
    QPushButton:disabled { color: #3a3b52; }
"""

BTN_SHIELD_ON = BTN_CSS + "QPushButton { color: #a6e3a1; }"   # green — ad-block ON
BTN_SHIELD_OFF = BTN_CSS + "QPushButton { color: #565f89; }"  # grey  — ad-block OFF


class BrowserTab(QWebEngineView):
    def __init__(self, browser_window, parent=None):
        super().__init__(parent)
        self.browser_window = browser_window

        s = self.settings()
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)
        s.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)

    def createWindow(self, window_type):
        return self.browser_window.add_tab("about:blank")


class BrowserWindow(QMainWindow):
    def __init__(self, interceptor):
        super().__init__()
        self.interceptor = interceptor
        self.setWindowTitle("Sleash")
        self.setMinimumSize(800, 500)
        self.resize(1200, 800)
        self._loading_tabs: set[int] = set()

        # Set window icon (shows in taskbar)
        _ico = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.ico")
        if os.path.exists(_ico):
            self.setWindowIcon(QIcon(_ico))

        self._build_ui()
        self._setup_shortcuts()
        self._start_block_counter()
        self.add_tab(HOME_URL)

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_toolbar())
        root.addWidget(self._make_progress_bar())
        root.addWidget(self._make_tab_widget())

        self._make_status_bar()

    def _make_toolbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(44)
        bar.setStyleSheet("background:#1a1b26; border-bottom:1px solid #2a2b3e;")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.setSpacing(3)

        self.btn_back = QPushButton("‹")
        self.btn_back.setToolTip("Back  Alt+Left")
        self.btn_forward = QPushButton("›")
        self.btn_forward.setToolTip("Forward  Alt+Right")
        self.btn_reload = QPushButton("↻")
        self.btn_reload.setToolTip("Reload  F5")
        self.btn_home = QPushButton("⌂")
        self.btn_home.setToolTip("Home")

        for btn in (self.btn_back, self.btn_forward, self.btn_reload, self.btn_home):
            btn.setStyleSheet(BTN_CSS)
            btn.setFixedWidth(32)

        self.btn_back.clicked.connect(self.go_back)
        self.btn_forward.clicked.connect(self.go_forward)
        self.btn_reload.clicked.connect(self.reload_or_stop)
        self.btn_home.clicked.connect(self.go_home)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter web address…")
        self.url_bar.setStyleSheet(
            "QLineEdit { background:#24253a; color:#c0caf5; border:1px solid #3a3b52;"
            " border-radius:7px; padding:5px 12px; font-size:13px;"
            " selection-background-color:#3d59a1; }"
            "QLineEdit:focus { border:1px solid #7aa2f7; }"
        )
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        # Ad-block shield button
        self.btn_shield = QPushButton("⚔")
        self.btn_shield.setToolTip("Ad Blocker ON — click to disable")
        self.btn_shield.setFixedWidth(32)
        self.btn_shield.setStyleSheet(BTN_SHIELD_ON)
        self.btn_shield.clicked.connect(self.toggle_adblock)

        self.btn_bmark = QPushButton("☆")
        self.btn_bmark.setToolTip("Bookmark  Ctrl+D")
        self.btn_bmark.setStyleSheet(BTN_CSS)
        self.btn_bmark.setFixedWidth(32)
        self.btn_bmark.clicked.connect(self.toggle_bookmark)

        self.btn_new_tab = QPushButton("+")
        self.btn_new_tab.setToolTip("New Tab  Ctrl+T")
        self.btn_new_tab.setStyleSheet(BTN_CSS)
        self.btn_new_tab.setFixedWidth(32)
        self.btn_new_tab.clicked.connect(lambda: self.add_tab(HOME_URL))

        lay.addWidget(self.btn_back)
        lay.addWidget(self.btn_forward)
        lay.addWidget(self.btn_reload)
        lay.addWidget(self.btn_home)
        lay.addSpacing(4)
        lay.addWidget(self.url_bar)
        lay.addSpacing(4)
        lay.addWidget(self.btn_shield)
        lay.addWidget(self.btn_bmark)
        lay.addWidget(self.btn_new_tab)
        return bar

    def _make_progress_bar(self) -> QProgressBar:
        self.progress = QProgressBar()
        self.progress.setFixedHeight(2)
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 100)
        self.progress.setStyleSheet(
            "QProgressBar { background:transparent; border:none; }"
            "QProgressBar::chunk { background:#7aa2f7; }"
        )
        self.progress.hide()
        return self.progress

    def _make_tab_widget(self) -> QTabWidget:
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setStyleSheet(
            "QTabWidget::pane { border:none; margin:0; }"
            "QTabBar { background:#1a1b26; }"
            "QTabBar::tab { background:#1a1b26; color:#565f89; padding:7px 16px 7px 12px;"
            " min-width:80px; max-width:200px; border-right:1px solid #2a2b3e; font-size:12px; }"
            "QTabBar::tab:selected { background:#24253a; color:#c0caf5; border-top:2px solid #7aa2f7; }"
            "QTabBar::tab:hover:!selected { background:#1e1f2e; }"
            "QTabBar::close-button { subcontrol-position:right; margin:2px; }"
        )
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        return self.tabs

    def _make_status_bar(self):
        self.status = QStatusBar()
        self.status.setStyleSheet(
            "QStatusBar { background:#1a1b26; color:#565f89; font-size:11px;"
            " border-top:1px solid #2a2b3e; }"
        )
        self.setStatusBar(self.status)

        self._block_label = QLabel()
        self._block_label.setStyleSheet("color:#a6e3a1; font-size:11px; padding:0 10px;")
        self.status.addPermanentWidget(self._block_label)
        self._refresh_block_label()

    def _setup_shortcuts(self):
        shortcuts = {
            "Ctrl+T": lambda: self.add_tab(HOME_URL),
            "Ctrl+W": lambda: self.close_tab(self.tabs.currentIndex()),
            "Ctrl+L": self._focus_url_bar,
            "Ctrl+R": self.reload_or_stop,
            "Ctrl+D": self.toggle_bookmark,
            "Alt+Left": self.go_back,
            "Alt+Right": self.go_forward,
            "F5": self.reload_or_stop,
            "F11": self.toggle_fullscreen,
        }
        for key, slot in shortcuts.items():
            QShortcut(QKeySequence(key), self).activated.connect(slot)

    def _start_block_counter(self):
        timer = QTimer(self)
        timer.timeout.connect(self._refresh_block_label)
        timer.start(1500)

    # ── Navigation ────────────────────────────────────────────────────────────

    def current_view(self) -> BrowserTab | None:
        return self.tabs.currentWidget()

    def add_tab(self, url: str) -> BrowserTab:
        view = BrowserTab(self)
        view.setUrl(QUrl(url))
        view.titleChanged.connect(lambda t, v=view: self._on_title_changed(v, t))
        view.urlChanged.connect(lambda u, v=view: self._on_url_changed(v, u))
        view.loadStarted.connect(lambda v=view: self._on_load_started(v))
        view.loadProgress.connect(lambda p, v=view: self._on_load_progress(v, p))
        view.loadFinished.connect(lambda ok, v=view: self._on_load_finished(v, ok))

        idx = self.tabs.addTab(view, "New Tab")
        self.tabs.setCurrentIndex(idx)
        return view

    def close_tab(self, index: int):
        if self.tabs.count() == 1:
            self.add_tab(HOME_URL)
        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)
        if widget:
            widget.deleteLater()

    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return
        if text.startswith(("http://", "https://", "file://")):
            url = text
        elif " " not in text and "." in text:
            url = "https://" + text
        else:
            url = "https://duckduckgo.com/?q=" + text.replace(" ", "+")
        v = self.current_view()
        if v:
            v.setUrl(QUrl(url))

    def go_back(self):
        v = self.current_view()
        if v:
            v.back()

    def go_forward(self):
        v = self.current_view()
        if v:
            v.forward()

    def reload_or_stop(self):
        v = self.current_view()
        if not v:
            return
        if id(v) in self._loading_tabs:
            v.stop()
        else:
            v.reload()

    def go_home(self):
        v = self.current_view()
        if v:
            v.setUrl(QUrl(HOME_URL))

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _focus_url_bar(self):
        self.url_bar.setFocus()
        self.url_bar.selectAll()

    # ── Ad Blocker ────────────────────────────────────────────────────────────

    def toggle_adblock(self):
        self.interceptor.enabled = not self.interceptor.enabled
        if self.interceptor.enabled:
            self.btn_shield.setStyleSheet(BTN_SHIELD_ON)
            self.btn_shield.setToolTip("Ad Blocker ON — click to disable")
            msg = f"Ad Blocker enabled  ({self.interceptor.rule_count:,} rules loaded)"
        else:
            self.btn_shield.setStyleSheet(BTN_SHIELD_OFF)
            self.btn_shield.setToolTip("Ad Blocker OFF — click to enable")
            msg = "Ad Blocker disabled"
        self.status.showMessage(msg, 3000)
        self._refresh_block_label()

    def _refresh_block_label(self):
        if self.interceptor.enabled:
            n = self.interceptor.blocked_count
            self._block_label.setText(f"⚔ {n:,} blocked")
            self._block_label.show()
        else:
            self._block_label.hide()

    # ── Bookmarks ─────────────────────────────────────────────────────────────

    def toggle_bookmark(self):
        v = self.current_view()
        if not v:
            return
        url = v.url().toString()
        title = v.title() or url
        bmarks = self._load_bookmarks()
        if any(b["url"] == url for b in bmarks):
            bmarks = [b for b in bmarks if b["url"] != url]
            self.btn_bmark.setText("☆")
            self.status.showMessage("Bookmark removed", 2000)
        else:
            bmarks.append({"url": url, "title": title})
            self.btn_bmark.setText("★")
            self.status.showMessage(f"Bookmarked: {title[:60]}", 2000)
        self._save_bookmarks(bmarks)

    def _update_bookmark_btn(self, url: str):
        bmarks = self._load_bookmarks()
        self.btn_bmark.setText("★" if any(b["url"] == url for b in bmarks) else "☆")

    def _load_bookmarks(self) -> list:
        if os.path.exists(BOOKMARKS_FILE):
            try:
                with open(BOOKMARKS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def _save_bookmarks(self, bookmarks: list):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(BOOKMARKS_FILE, "w", encoding="utf-8") as f:
            json.dump(bookmarks, f, indent=2, ensure_ascii=False)

    # ── Tab & load event handlers ─────────────────────────────────────────────

    def on_tab_changed(self, index: int):
        v = self.tabs.widget(index)
        if not v:
            return
        url = v.url().toString()
        if url in ("about:blank", ""):
            self.url_bar.setText("")
            self.url_bar.setFocus()
        else:
            self.url_bar.setText(url)
        self._update_bookmark_btn(url)
        self.btn_reload.setText("✕" if id(v) in self._loading_tabs else "↻")

    def _on_title_changed(self, view: BrowserTab, title: str):
        idx = self.tabs.indexOf(view)
        if idx >= 0:
            label = (title[:22] + "…") if len(title) > 22 else title
            self.tabs.setTabText(idx, label or "New Tab")
        if view == self.current_view():
            self.setWindowTitle(f"{title} — Sleash" if title else "Sleash")

    def _on_url_changed(self, view: BrowserTab, qurl: QUrl):
        if view == self.current_view():
            url = qurl.toString()
            self.url_bar.setText(url)
            self._update_bookmark_btn(url)

    def _on_load_started(self, view: BrowserTab):
        self._loading_tabs.add(id(view))
        if view == self.current_view():
            self.btn_reload.setText("✕")
            self.progress.show()
            self.progress.setValue(0)

    def _on_load_progress(self, view: BrowserTab, p: int):
        if view == self.current_view():
            self.progress.setValue(p)

    def _on_load_finished(self, view: BrowserTab, ok: bool):
        self._loading_tabs.discard(id(view))
        if view == self.current_view():
            self.btn_reload.setText("↻")
            self.progress.hide()
            if not ok:
                self.status.showMessage("Page could not be loaded", 3000)

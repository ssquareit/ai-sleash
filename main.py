import os
import sys

# ── Windows taskbar icon fix ──────────────────────────────────────────────────
if sys.platform == "win32":
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Sleash.Browser.1.0")

# ── Fix SSL for QtWebEngine on Windows (must run BEFORE any Qt imports) ───────
if sys.platform == "win32":
    try:
        import PySide6 as _p6
        _p6_dir = os.path.dirname(_p6.__file__)
        os.environ["PATH"] = _p6_dir + os.pathsep + os.environ.get("PATH", "")
    except Exception:
        pass
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--no-proxy-server --ignore-certificate-errors --disable-quic"
    )

# ── PyInstaller frozen-build fixes (must run BEFORE any Qt imports) ───────────
if getattr(sys, "frozen", False):
    import shutil
    base = sys._MEIPASS                              # dist/Sleash/_internal/
    exe_dir = os.path.dirname(sys.executable)        # dist/Sleash/

    # Point Chromium to the helper process — must be in PySide6/ alongside Qt DLLs
    os.environ.setdefault(
        "QTWEBENGINEPROCESS_PATH",
        os.path.join(base, "PySide6", "QtWebEngineProcess.exe"),
    )
    # Qt looks for icudtl.dat in the exe directory — copy it there on first launch
    icu_src = os.path.join(base, "PySide6", "resources", "icudtl.dat")
    icu_dst = os.path.join(exe_dir, "icudtl.dat")
    if os.path.exists(icu_src) and not os.path.exists(icu_dst):
        shutil.copy2(icu_src, icu_dst)
    # Disable Chromium sandbox — required in most packaged Windows environments
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
# ─────────────────────────────────────────────────────────────────────────────

from PySide6.QtGui import QIcon
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtWidgets import QApplication

from adblock import AdBlockInterceptor
from browser import BrowserWindow

_ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.ico")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Sleash")
    app.setOrganizationName("Sleash")
    if os.path.exists(_ICON_PATH):
        app.setWindowIcon(QIcon(_ICON_PATH))

    # Set a standard Chrome user agent so Google and other sites don't block us
    QWebEngineProfile.defaultProfile().setHttpUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    interceptor = AdBlockInterceptor()
    QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(interceptor)

    window = BrowserWindow(interceptor)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

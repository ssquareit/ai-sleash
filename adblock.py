import os

from PySide6.QtWebEngineCore import QWebEngineUrlRequestInfo, QWebEngineUrlRequestInterceptor

BLOCKLIST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "blocklist.txt")


class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    """
    Intercepts network requests and blocks known ad/tracker domains.
    Rules file: data/blocklist.txt — one domain per line.
    Supports EasyList ||domain.com^ format and plain domain format.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.enabled = True
        self.blocked_count = 0
        self._domains: set[str] = set()
        self._load()

    def _load(self):
        if not os.path.exists(BLOCKLIST_FILE):
            print("[AdBlock] blocklist.txt not found — ad-blocking inactive")
            return
        with open(BLOCKLIST_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # EasyList network rule: ||domain.com^
                if line.startswith("||"):
                    line = line[2:].split("^")[0].split("/")[0]
                self._domains.add(line.lower())
        print(f"[AdBlock] {len(self._domains):,} rules loaded")

    def interceptRequest(self, info: QWebEngineUrlRequestInfo) -> None:
        if not self.enabled:
            return
        host = info.requestUrl().host().lower()
        if self._match(host):
            info.block(True)
            self.blocked_count += 1

    def _match(self, host: str) -> bool:
        """Returns True if host or any of its parent domains is in the blocklist."""
        if not host:
            return False
        parts = host.split(".")
        # Check from most-specific to least-specific, but never check a bare TLD
        for i in range(len(parts) - 1):
            if ".".join(parts[i:]) in self._domains:
                return True
        return False

    @property
    def rule_count(self) -> int:
        return len(self._domains)

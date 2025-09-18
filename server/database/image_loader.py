from __future__ import annotations
import weakref
from pathlib import Path
from typing import Optional, Dict, Set
from PySide6.QtCore import QObject, Signal, QUrl, QSize, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkRequest,
    QNetworkDiskCache,
)
from PySide6.QtWidgets import QLabel
from shiboken6 import isValid as _sbk_is_valid

# ------------------------------ helpers -------------------------------------

def _as_int(x) -> Optional[int]:
    """
    Best-effort conversion of a value (including Qt enums/variants) to int.
    Returns None when conversion is not possible.
    """
    try:
        return int(x)
    except Exception:
        try:
            v = getattr(x, "value", None)
            return int(v) if v is not None else None
        except Exception:
            return None

def _is_valid(obj) -> bool:
    """
    Return True if the Qt object is still alive and valid.
    Using shiboken6.isValid prevents calling into deleted QObject wrappers.
    """
    if obj is None:
        return False
    return bool(_sbk_is_valid(obj))

# ------------------------------ core loader ---------------------------------

class ImageLoader(QObject):
    """
    Asynchronous image loader with:
      • On-disk HTTP cache (QNetworkDiskCache)
      • In-memory pixmap cache (by *origin* URL)
      • In-flight de-duplication per origin URL
      • Redirect handling that works across Qt 5.15 and Qt 6

    Signals
    -------
    pixmapReady(origin: str, pixmap: QPixmap)
        Emitted when a pixmap requested for `origin` is ready. `origin` is
        the original URL key, preserved across HTTP redirects.
    """

    pixmapReady = Signal(str, QPixmap)

    def __init__(self, cache_dir: Path, parent=None):
        """
        Create a loader with both disk and RAM caching.

        Parameters
        ----------
        cache_dir : Path - Directory used by QNetworkDiskCache to persist HTTP responses.
        parent - Optional QObject parent.
        """
        super().__init__(parent)

        # Ensure cache directory exists
        cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Network stack + disk cache
        self.nam = QNetworkAccessManager(self)
        disk = QNetworkDiskCache(self)
        disk.setCacheDirectory(str(cache_dir))
        self.nam.setCache(disk)

        # Simple in-memory cache: origin_url -> QPixmap
        self._mem: Dict[str, QPixmap] = {}

        # Tracks URLs currently being fetched (by origin) to avoid duplicate requests
        self._inflight: Set[str] = set()

    # ------------------------------ internals --------------------------------

    def _set_follow_redirects(self, req: QNetworkRequest) -> None:
        """
        Enable follow-redirects on both Qt 5.15 and Qt 6.
        If the relevant attributes are missing (older/newer Qt), do nothing.
        """
        try:
            QNR = QNetworkRequest
            # Qt 5.15 style
            if hasattr(QNR, "FollowRedirectsAttribute"):
                req.setAttribute(QNR.FollowRedirectsAttribute, True)
                return

            # Qt 6 style(s)
            attr = getattr(QNR, "RedirectPolicyAttribute", None)
            policy = getattr(QNR, "NoLessSafeRedirectPolicy", None)
            if policy is None:
                # Older Qt6 placed enums under QNetworkRequest.RedirectPolicy
                RP = getattr(QNR, "RedirectPolicy", None)
                policy = getattr(RP, "NoLessSafeRedirectPolicy", None) if RP else None
            if attr is not None and policy is not None:
                req.setAttribute(attr, policy)
        except Exception:
            # Be permissive: failure here is not fatal, manual redirect follows later
            pass

    # ------------------------------ public API --------------------------------

    def fetch(self, url: str, *, origin: Optional[str] = None) -> None:
        """
        Fetch `url` asynchronously. If a redirect occurs, the original `origin`
        is preserved so listeners receive the same key they requested.

        Parameters:
        url : str
            The actual URL to request.
        origin : Optional[str]
            The logical key under which the result will be emitted and cached.
            Defaults to `url`. Pass the *original* URL when following redirects.
        """
        origin = origin or url

        # 1) In-memory cache hit
        if origin in self._mem:
            print("[IMG] mem-hit:", origin)
            self.pixmapReady.emit(origin, self._mem[origin])
            return

        # 2) Already being fetched → skip duplicate request
        if origin in self._inflight:
            print("[IMG] inflight-skip:", origin)
            return

        # 3) Made a network request
        self._inflight.add(origin)
        print("[IMG] fetch:", url, "(origin:", origin, ")")

        req = QNetworkRequest(QUrl(url))
        self._set_follow_redirects(req)
        req.setRawHeader(b"User-Agent", b"QtImageLoader/1.0")

        reply = self.nam.get(req)
        reply.finished.connect(lambda r=reply, u=url, o=origin: self._on_finished(u, o, r))

    # ------------------------------ slots -------------------------------------

    def _on_finished(self, url: str, origin: str, reply) -> None:
        """
        Handle a finished network reply:
          • Follow redirects (manually, for cross-version consistency)
          • Convert payload to QPixmap
          • Update caches and emit pixmapReady
        """
        QNR = QNetworkRequest

        status = _as_int(reply.attribute(QNR.HttpStatusCodeAttribute))
        err = reply.error()
        err_i = _as_int(err)
        print(f"[IMG] done: {url} | status={status} err={err_i} ({err})")

        # Manual redirect handling (works the same on 5.15/6.x)
        try:
            redir = reply.attribute(QNR.RedirectionTargetAttribute)
        except Exception:
            redir = None

        if status in (301, 302, 303, 307, 308) and redir:
            new_url = QUrl(redir).toString()
            print("[IMG] redirect ->", new_url, "| origin:", origin)
            reply.deleteLater()
            # Keep the original origin so the cache/signal key remains stable
            self.fetch(new_url, origin=origin)
            return

        # Network error → clear inflight & bail
        if err_i not in (None, 0):
            self._inflight.discard(origin)
            reply.deleteLater()
            return

        # Read all data and attempt to decode into a pixmap
        data = reply.readAll()
        pm = QPixmap()
        pm.loadFromData(bytes(data))
        reply.deleteLater()

        self._inflight.discard(origin)

        # Success: store in RAM cache and notify listeners
        if not pm.isNull():
            self._mem[origin] = pm
            self.pixmapReady.emit(origin, pm)


# ------------------------------ singleton + view helper ----------------------

BASE_DIR = Path(__file__).resolve().parent
IMAGE_LOADER = ImageLoader(BASE_DIR / "http_cache")


def load_into(
    label: QLabel,
    url: str,
    placeholder: Optional[Path] = None,
    size: Optional[QSize] = None,
) -> None:
    """
    Convenience helper for views.

    Behavior:
      1) Immediately shows a placeholder, if provided.
      2) Loads the image asynchronously with on-disk and in-memory caching.
      3) Updates the QLabel only if it is still alive and still expects `url`.

    Parameters
    ----------
    label : QLabel - The label to render the image into.
    url : str - The image URL to fetch.
    placeholder : Optional[Path] - A local placeholder image to show immediately while loading.
    size : Optional[QSize] - Target size for scaling. Defaults to the label's current size.
    """
    # Record the requested URL on the label to prevent races (e.g., reused views)
    label.setProperty("img_url", url)

    # 1) Show placeholder immediately (if provided and valid)
    if placeholder:
        ph = QPixmap(str(placeholder))
        if not ph.isNull():
            target = size or label.size()
            label.setPixmap(
                ph.scaled(target, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            )

    # 2) Connect to the loader signal safely using a weak reference
    wref = weakref.ref(label)

    def _safe_disconnect(slot):
        """Disconnect defensively (ignore if already disconnected)."""
        try:
            IMAGE_LOADER.pixmapReady.disconnect(slot)
        except Exception:
            pass

    def _on_ready(origin: str, pm: QPixmap):
        """
        Slot that updates the QLabel only if:
          • origin matches the requested URL
          • pixmap is valid
          • the label is still alive and valid
          • the label hasn't been repointed to a different URL
        """
        if origin != url or pm.isNull():
            return

        lbl = wref()  # becomes None if the label was destroyed
        if lbl is None or not _is_valid(lbl):
            _safe_disconnect(_on_ready)
            return

        # If the label now expects a different URL, do not overwrite it
        if lbl.property("img_url") != url:
            _safe_disconnect(_on_ready)
            return

        target = size or lbl.size()
        lbl.setPixmap(
            pm.scaled(target, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        )
        _safe_disconnect(_on_ready)

    # Connect and ensure we disconnect if the label dies
    IMAGE_LOADER.pixmapReady.connect(_on_ready)
    label.destroyed.connect(lambda *_: _safe_disconnect(_on_ready))

    # 3) Trigger the fetch
    IMAGE_LOADER.fetch(url, origin=url)
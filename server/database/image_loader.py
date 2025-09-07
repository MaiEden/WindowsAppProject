# server/database/image_loader.py
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

# --- utils ------------------------------------------------------------------


def _as_int(x) -> Optional[int]:
    """Try to coerce enums/variants to int; return None if not possible."""
    try:
        return int(x)
    except Exception:
        try:
            v = getattr(x, "value", None)
            return int(v) if v is not None else None
        except Exception:
            return None


# Validity check that survives deleted Qt objects
try:
    from shiboken6 import isValid as _sbk_is_valid  # type: ignore
except Exception:  # shiboken not found (unlikely on PySide6)
    _sbk_is_valid = None


def _is_valid(obj) -> bool:
    if obj is None:
        return False
    if _sbk_is_valid is not None:
        try:
            return bool(_sbk_is_valid(obj))
        except Exception:
            return False
    # best-effort fallback
    try:
        return hasattr(obj, "metaObject") and obj.metaObject() is not None
    except Exception:
        return False


# --- core loader -------------------------------------------------------------


class ImageLoader(QObject):
    """
    Async image loader with:
      - on-disk cache (QNetworkDiskCache)
      - in-memory cache
      - in-flight de-dup per origin URL
      - redirect handling for Qt5/Qt6
    """
    pixmapReady = Signal(str, QPixmap)  # (origin_url, pixmap)

    def __init__(self, cache_dir: Path, parent=None):
        super().__init__(parent)

        cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

        self.nam = QNetworkAccessManager(self)

        disk = QNetworkDiskCache(self)
        disk.setCacheDirectory(str(cache_dir))
        self.nam.setCache(disk)

        self._mem: Dict[str, QPixmap] = {}   # RAM cache by origin url
        self._inflight: Set[str] = set()     # URLs currently loading (by origin)

    # ----- helpers -----------------------------------------------------------

    def _set_follow_redirects(self, req: QNetworkRequest) -> None:
        """Enable follow-redirects on both Qt5.15 and Qt6; ignore if unavailable."""
        try:
            QNR = QNetworkRequest
            if hasattr(QNR, "FollowRedirectsAttribute"):                # Qt 5.15
                req.setAttribute(QNR.FollowRedirectsAttribute, True)
                return

            # Qt6 styles
            attr = getattr(QNR, "RedirectPolicyAttribute", None)
            policy = getattr(QNR, "NoLessSafeRedirectPolicy", None)
            if policy is None:
                RP = getattr(QNR, "RedirectPolicy", None)
                policy = getattr(RP, "NoLessSafeRedirectPolicy", None) if RP else None
            if attr is not None and policy is not None:
                req.setAttribute(attr, policy)
        except Exception:
            pass

    # ----- public API --------------------------------------------------------

    def fetch(self, url: str, *, origin: Optional[str] = None) -> None:
        """
        Fetch URL asynchronously. If redirected, keep the original 'origin'
        so listeners that ביקשו את ה־URL יקבלו בחזרה את אותו מפתח.
        """
        origin = origin or url

        # RAM cache hit
        if origin in self._mem:
            print("[IMG] mem-hit:", origin)
            self.pixmapReady.emit(origin, self._mem[origin])
            return

        # already loading
        if origin in self._inflight:
            print("[IMG] inflight-skip:", origin)
            return

        self._inflight.add(origin)
        print("[IMG] fetch:", url, " (origin:", origin, ")")

        req = QNetworkRequest(QUrl(url))
        self._set_follow_redirects(req)
        req.setRawHeader(b"User-Agent", b"QtImageLoader/1.0")

        reply = self.nam.get(req)
        reply.finished.connect(lambda r=reply, u=url, o=origin: self._on_finished(u, o, r))

    def _on_finished(self, url: str, origin: str, reply) -> None:
        QNR = QNetworkRequest

        status = _as_int(reply.attribute(QNR.HttpStatusCodeAttribute))
        err = reply.error()
        err_i = _as_int(err)
        print(f"[IMG] done: {url} | status={status} err={err_i} ({err})")

        # Manual redirect follow (works cross-versions)
        try:
            redir = reply.attribute(QNR.RedirectionTargetAttribute)
        except Exception:
            redir = None
        if status in (301, 302, 303, 307, 308) and redir:
            new_url = QUrl(redir).toString()
            print("[IMG] redirect ->", new_url, "| origin:", origin)
            reply.deleteLater()
            self.fetch(new_url, origin=origin)
            return

        if err_i not in (None, 0):
            # network error
            self._inflight.discard(origin)
            reply.deleteLater()
            return

        data = reply.readAll()
        pm = QPixmap()
        pm.loadFromData(bytes(data))
        reply.deleteLater()

        self._inflight.discard(origin)

        if not pm.isNull():
            self._mem[origin] = pm
            self.pixmapReady.emit(origin, pm)


# --- singleton + high-level helper for views --------------------------------

BASE_DIR = Path(__file__).resolve().parent
IMAGE_LOADER = ImageLoader(BASE_DIR / "http_cache")


def load_into(
    label: QLabel,
    url: str,
    placeholder: Optional[Path] = None,
    size: Optional[QSize] = None,
) -> None:
    """
    שימוש מתוך ה-View:
      load_into(image_label, url, placeholder=BASE_DIR/'placeholder_card.png', size=QSize(420,160))

    ההתנהגות:
      - מציג placeholder מיד (אם הועבר)
      - טוען את התמונה ברקע עם מטמון
      - מעדכן את ה-QLabel רק אם הוא עדיין חי ורלוונטי ל-URL הזה
    """
    # נרשום את ה-URL המבוקש על ה-label כדי למנוע מירוצים
    label.setProperty("img_url", url)

    # 1) placeholder מייד
    if placeholder:
        ph = QPixmap(str(placeholder))
        if not ph.isNull():
            target = size or label.size()
            label.setPixmap(ph.scaled(target, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

    # 2) התחברות בטוחה עם weakref
    wref = weakref.ref(label)

    def _safe_disconnect(slot):
        try:
            IMAGE_LOADER.pixmapReady.disconnect(slot)
        except Exception:
            pass

    def _on_ready(origin: str, pm: QPixmap):
        # לא תואם ל-URL שלנו או התמונה לא תקפה
        if origin != url or pm.isNull():
            return

        lbl = wref()  # None אם נהרס
        if lbl is None or not _is_valid(lbl):
            _safe_disconnect(_on_ready)
            return

        # אם בזמן הזה ה-label עבר ל-URL אחר – לא לעדכן
        if lbl.property("img_url") != url:
            _safe_disconnect(_on_ready)
            return

        target = size or lbl.size()
        lbl.setPixmap(pm.scaled(target, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        _safe_disconnect(_on_ready)

    IMAGE_LOADER.pixmapReady.connect(_on_ready)
    # אם ה-label נהרס – ננתק את ה-slot כדי שלא ייקרא מאוחר יותר
    label.destroyed.connect(lambda *_: _safe_disconnect(_on_ready))

    # 3) שליחה לטעינה
    IMAGE_LOADER.fetch(url, origin=url)

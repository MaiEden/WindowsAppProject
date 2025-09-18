# chat_view.py
"""
View for the Chat screen (MVP).
- Pure UI. No business logic or assistant calls.
- Emits signals for user actions.
- Presents a small API for the Presenter to update the screen.
- Fixed-width bubbles, auto height, disposable "Thinking…" bubble.
- Markdown answers are rendered as HTML.
- Timestamp is outside the bubble (no bubble background behind time).
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QTextOption, QGuiApplication
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QTextEdit, QScrollArea, QTextBrowser, QSizePolicy
)

# ---------- Markdown renderer ----------
def _render_markdown(md_text: str) -> str:
    """
    Convert Markdown to HTML. Prefer python-markdown if installed.
    Fallback handles headings, bold/italics, lists, code fences.
    """
    try:
        import markdown as _markdown
        return _markdown.markdown(md_text or "", extensions=["extra", "sane_lists"])
    except Exception:
        import re
        text = (md_text or "")
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # code fences ```lang\n...\n```
        code_pat = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
        def _code(m):
            lang = m.group(1) or ""
            body = m.group(2)
            return f"<pre><code class='lang-{lang}'>{body}</code></pre>"
        text = code_pat.sub(_code, text)

        # inline code `...`
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

        # headings
        for i in range(6, 0, -1):
            hpat = re.compile(rf"^{'#'*i}\s+(.*)$", re.MULTILINE)
            text = hpat.sub(lambda m: f"<h{i}>{m.group(1)}</h{i}>", text)

        # bold/italics
        text = re.sub(r"\*\*([^\*]+)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"\*([^\*]+)\*", r"<em>\1</em>", text)

        # simple lists and paragraphs
        lines = text.splitlines()
        html_lines, in_ul = [], False
        for ln in lines:
            if re.match(r"^\s*[-\*]\s+.+", ln):
                if not in_ul:
                    html_lines.append("<ul>")
                    in_ul = True
                item = re.sub(r"^\s*[-\*]\s+", "", ln)
                html_lines.append(f"<li>{item}</li>")
            else:
                if in_ul:
                    html_lines.append("</ul>")
                    in_ul = False
                if ln.strip() == "":
                    html_lines.append("<br>")
                else:
                    html_lines.append(f"<p>{ln}</p>")
        if in_ul:
            html_lines.append("</ul>")
        return "\n".join(html_lines)

# inline CSS for content inside QTextBrowser
MD_INLINE_CSS = """
<style>
  h1 { font-size: 20px; margin: 6px 0 6px; }
  h2 { font-size: 18px; margin: 6px 0 6px; }
  h3 { font-size: 16px; margin: 6px 0 4px; }
  h4, h5, h6 { font-size: 14px; margin: 4px 0 2px; }
  p  { font-size: 14px; line-height: 1.5; margin: 0 0 8px; }
  ul { margin: 0 0 8px 18px; padding: 0; }
  li { margin: 2px 0; }
  strong { font-weight: 700; }
  em { font-style: italic; }
  a { color: #2563EB; text-decoration: none; }
  a:hover { text-decoration: underline; }
  code {
    font-family: Consolas, 'Courier New', monospace;
    background: rgba(0,0,0,0.06);
    padding: 1px 4px;
    border-radius: 4px;
  }
  pre {
    background: rgba(0,0,0,0.06);
    padding: 10px;
    border-radius: 8px;
    overflow: auto;
    margin: 6px 0 10px;
  }
</style>
"""

# ----- Theme -----
THEME = {
    "bg": "#F7FAFF",
    "surface": "#FFFFFF",
    "card": "#FFFFFF",
    "accent": "#3B82F6",
    "text": "#0F172A",
    "muted": "#475569",
    "userBubble": "#E5E7EB",      # gray-200
    "assistantBubble": "#BFDBFE", # blue-200
    "typingBubble": "#BFDBFE",    # blue-200
    "radius": "18px",
    "font": "Segoe UI, Arial"
}

GLOBAL_QSS = f"""
* {{
  font-family: {THEME['font']};
  color: {THEME['text']};
}}
QWidget {{
  background: {THEME['bg']};
}}
QScrollArea {{ border: none; background: transparent; }}
QFrame#Composer {{
  background: {THEME['surface']};
  border-top: 1px solid #E5E7EB;
}}
QTextEdit#Input {{
  background: {THEME['card']};
  border: 1px solid #E5E7EB;
  border-radius: {THEME['radius']};
  padding: 10px;
  font-size: 13px;
}}
QPushButton#SendBtn {{
  background: {THEME['accent']}; color: white; border: none;
  border-radius: 16px; padding: 10px 16px; font-weight: 700; min-width: 88px;
}}
QPushButton#SendBtn:disabled {{ background: #93C5FD; color: white; }}
QFrame#BubbleUser {{
  background: {THEME['userBubble']}; border-radius: {THEME['radius']}; padding: 12px;
}}
QFrame#BubbleAssistant {{
  background: {THEME['assistantBubble']}; border-radius: {THEME['radius']}; padding: 12px;
}}
QFrame#BubbleTyping {{
  background: {THEME['typingBubble']}; border-radius: {THEME['radius']}; padding: 10px;
}}
QLabel#Meta {{ color: {THEME['muted']}; font-size: 10px; }}
QFrame#Sources {{
  background: #EEF2F7; border-radius: 12px; padding: 8px 10px;
}}
"""

# ----- Message bubble (fixed width, auto height, no inner scrollbars) -----
class _MessageBubble(QWidget):
    """UI widget used internally by the view for each message bubble."""
    FIXED_W = 520
    PADDING_LR = 24

    def __init__(self, role: str, text: str, timestamp: Optional[datetime] = None, sources: Optional[str] = None):
        super().__init__()
        self.role = role
        self.text = text
        self.sources = sources
        self.timestamp = timestamp or datetime.now()

        # root layout
        container = QVBoxLayout(self)
        container.setContentsMargins(0, 6, 0, 6)
        container.setSpacing(2)

        # row for bubble
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        # bubble frame
        self.bubble = QFrame()
        self.bubble.setObjectName(
            "BubbleTyping" if role == "typing" else ("BubbleUser" if role == "user" else "BubbleAssistant")
        )
        self.bubble.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.bubble.setFixedWidth(self.FIXED_W)

        # bubble layout
        vb = QVBoxLayout(self.bubble)
        vb.setContentsMargins(12, 10, 12, 8)
        vb.setSpacing(6)

        # bubble body (QTextBrowser for rich text, links, selectable)
        self.body = QTextBrowser()
        self.body.setOpenExternalLinks(True)
        self.body.setWordWrapMode(QTextOption.WordWrap)
        self.body.setFrameStyle(QFrame.NoFrame)
        self.body.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        self.body.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.body.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.body.setStyleSheet("background: transparent; border: none;")

        # set HTML content
        html = _render_markdown(text)
        self.body.setHtml(MD_INLINE_CSS + html)
        vb.addWidget(self.body)

        # add sources box if any
        if role == "assistant" and sources:
            src = QFrame(); src.setObjectName("Sources")
            src_layout = QVBoxLayout(src); src_layout.setContentsMargins(8,6,8,6)
            src_title = QLabel("Sources"); src_title.setStyleSheet("font-weight:600;")
            src_text = QLabel(sources); src_text.setWordWrap(True)
            src_layout.addWidget(src_title); src_layout.addWidget(src_text)
            vb.addWidget(src)

        # add bubble row
        if role == "user":
            row.addStretch()
            row.addWidget(self.bubble, 0, Qt.AlignRight | Qt.AlignTop)
        else:
            row.addWidget(self.bubble, 0, Qt.AlignLeft | Qt.AlignTop)
            row.addStretch()
        container.addLayout(row)

        # timestamp row (outside bubble so no bubble background)
        if role != "typing":
            meta_row = QHBoxLayout()
            meta_row.setContentsMargins(0, 0, 0, 0)
            meta = QLabel(self.timestamp.strftime("%H:%M"))
            meta.setObjectName("Meta")
            if role == "user":
                meta_row.addStretch()
                meta_row.addWidget(meta, 0, Qt.AlignRight)
            else:
                meta_row.addWidget(meta, 0, Qt.AlignLeft)
                meta_row.addStretch()
            container.addLayout(meta_row)

        # compute final height for the text browser
        self._autosize_height()

    def _autosize_height(self):
        """Let the document compute the exact height, so the bubble grows vertically."""
        text_w = self.FIXED_W - self.PADDING_LR
        doc = self.body.document()
        doc.setTextWidth(text_w)
        h = int(doc.size().height())
        self.body.setFixedSize(text_w, h + 2)  # small padding for internal margins

# ----- View -----
class ChatView(QWidget):
    """
    View: UI only (no business logic).
    Signals are connected by the Presenter.
    """

    # View → Presenter
    send_clicked = Signal(str)  # emits the text to send

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat")
        self.resize(980, 740)
        self.setStyleSheet(GLOBAL_QSS)

        # Root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # Messages area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.messages_host = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_host)
        self.messages_layout.setContentsMargins(20, 14, 20, 14)
        self.messages_layout.setSpacing(6)
        self.messages_layout.addStretch()
        self.scroll.setWidget(self.messages_host)

        # Composer
        composer = QFrame(objectName="Composer")
        comp_l = QHBoxLayout(composer)
        comp_l.setContentsMargins(20, 12, 20, 12)
        comp_l.setSpacing(12)

        # Text input
        self.input = QTextEdit(objectName="Input")
        self.input.setPlaceholderText("Type a message... (Enter to send, Shift+Enter for newline)")
        self.input.setFixedHeight(110)
        self.input.setFontPointSize(11)
        self.input.installEventFilter(self)  # capture Enter for send

        self.send_btn = QPushButton("Send", objectName="SendBtn")

        comp_l.addWidget(self.input, 1)
        comp_l.addWidget(self.send_btn, 0)

        # Assemble
        root.addWidget(self.scroll, 1)
        root.addWidget(composer)

        # Typing bubble ref
        self._typing_bubble: Optional[_MessageBubble] = None

        # Wire UI events (UI → View signal)
        self.send_btn.clicked.connect(self._emit_send)

        # Initial assistant welcome
        self.add_assistant("Hello! I can help you with event planning questions.")

    # -------- Public API used by Presenter --------
    def add_user(self, text: str) -> None:
        self._insert_message(_MessageBubble("user", text))

    def add_assistant(self, text: str, sources: Optional[str] = None) -> None:
        self._insert_message(_MessageBubble("assistant", text, sources=sources))

    def show_typing(self) -> None:
        self._typing_bubble = _MessageBubble("typing", "Thinking…")
        self._insert_message(self._typing_bubble)

    def hide_typing(self) -> None:
        if self._typing_bubble is not None:
            self._typing_bubble.setParent(None)
            self._typing_bubble.deleteLater()
            self._typing_bubble = None

    def clear_input(self) -> None:
        self.input.clear()

    def set_enabled(self, enabled: bool) -> None:
        self.input.setEnabled(enabled)
        self.send_btn.setEnabled(enabled)

    # -------- Internal helpers --------
    def _insert_message(self, w: QWidget) -> None:
        idx = self.messages_layout.count() - 1
        self.messages_layout.insertWidget(idx, w)
        QGuiApplication.processEvents()
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

    def _emit_send(self) -> None:
        text = self.input.toPlainText().strip()
        if not text:
            return
        self.send_clicked.emit(text)

    # Send on Enter, newline on Shift+Enter
    def eventFilter(self, obj, ev):
        if obj is self.input and ev.type() == QEvent.KeyPress:
            if ev.key() in (Qt.Key_Return, Qt.Key_Enter):
                if ev.modifiers() & Qt.ShiftModifier:
                    return False  # allow newline
                self._emit_send()
                return True
        return super().eventFilter(obj, ev)

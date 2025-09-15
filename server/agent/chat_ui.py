# chat_ui.py
# Minimal chat UI (LTR, English-only)
# - No top menu, no header — only messages + composer
# - Modern, higher-contrast bubble colors (emerald + blue)
# - Fixed bubble width, auto height (no inner scrollbars)
# - Temporary "Thinking…" bubble that disappears on answer
# - Uses an external Python interpreter to call llm_agent.MultiPDFRAGAssistant

import sys
import json
import subprocess
import traceback
from datetime import datetime
from typing import Optional, Tuple

from PySide6.QtCore import Qt, QEvent, QThread, Signal
from PySide6.QtGui import QFont, QTextOption, QGuiApplication, QClipboard
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QPushButton, QTextEdit, QScrollArea, QFileDialog, QMessageBox,
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QTextBrowser, QSizePolicy
)

# ---------------------------
# Theme tokens (light mode, higher contrast)
# ---------------------------
THEME = {
    "bg": "#F7FAFF",
    "surface": "#FFFFFF",
    "card": "#FFFFFF",
    "accent": "#3B82F6",        # blue-500 for Send button
    "text": "#0F172A",          # slate-900 (good contrast)
    "muted": "#475569",         # slate-600
    "danger": "#EF4444",
    # higher-contrast bubbles (still soft/modern)
    "userBubble": "#E5E7EB",     # gray-200
    "assistantBubble": "#BFDBFE", # blue-200
    "typingBubble": "#BFDBFE",   # blue-200
    "radius": "18px",
    "font": "Segoe UI, Arial"
}

GLOBAL_QSS = f"""
* {{
  font-family: {THEME['font']};
  color: {THEME['text']};
}}
QMainWindow {{
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

# ---------------------------
# Inline runner for external interpreter
# ---------------------------
def build_inline_runner(question: str, model: str, host: str, cache_dir: str) -> str:
    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace('"', '\\"')
    q = esc(question); mdl = esc(model); h = esc(host); cdir = esc(cache_dir)
    return f"""
import json, sys, traceback
try:
    from llm_agent import MultiPDFRAGAssistant
    a = MultiPDFRAGAssistant(source_paths=[], ollama_host="{h}", model="{mdl}", cache_dir="{cdir}")
    if not a.load_from_cache_only():
        print(json.dumps({{"ok": False, "error": "Failed to load from cache. Run initialize() once."}}))
        sys.exit(0)
    ans = a.ask("{q}")
    print(json.dumps({{"ok": True, "answer": ans}}))
except Exception as e:
    print(json.dumps({{"ok": False, "error": str(e) + "\\n" + traceback.format_exc()}}))
"""

class ExternalAskWorker(QThread):
    finished = Signal(str, str, str)  # question, answer, error
    def __init__(self, python_exe: str, question: str, model: str, host: str, cache_dir: str):
        super().__init__(); self.python_exe=python_exe; self.question=question
        self.model=model; self.host=host; self.cache_dir=cache_dir
    def run(self):
        try:
            code = build_inline_runner(self.question, self.model, self.host, self.cache_dir)
            proc = subprocess.run([self.python_exe, "-c", code], capture_output=True, text=True)
            stdout = proc.stdout.strip(); stderr = proc.stderr.strip()
            if not stdout:
                self.finished.emit(self.question, "", f"No output from helper. Stderr:\\n{stderr}"); return
            try:
                payload = json.loads(stdout)
            except Exception:
                lines = [ln for ln in stdout.splitlines() if ln.strip().startswith("{") and ln.strip().endswith("}")]
                if not lines:
                    self.finished.emit(self.question, "", f"Invalid output:\\n{stdout}\\n\\nStderr:\\n{stderr}"); return
                payload = json.loads(lines[-1])
            if payload.get("ok"):
                self.finished.emit(self.question, payload.get("answer",""), "")
            else:
                self.finished.emit(self.question, "", payload.get("error","Unknown error"))
        except Exception as e:
            self.finished.emit(self.question, "", f"{e}\\n{traceback.format_exc()}")

# ---------------------------
# Message bubble (fixed width, auto-height, no inner scrollbars)
# ---------------------------
class MessageBubble(QWidget):
    """
    Chat bubble with fixed width and automatic height that fits the text.
    role: 'user' | 'assistant' | 'typing'
    """
    FIXED_W = 520     # bubble outer width (padding included)
    PADDING_LR = 24   # left+right padding inside bubble (matches QSS 12+12)

    def __init__(self, role: str, text: str, timestamp: Optional[datetime] = None,
                 sources: Optional[str] = None):
        super().__init__()
        self.role = role
        self.text = text
        self.sources = sources
        self.timestamp = timestamp or datetime.now()

        container = QVBoxLayout(self)
        container.setContentsMargins(0, 6, 0, 6)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        self.bubble = QFrame()
        self.bubble.setObjectName(
            "BubbleTyping" if role == "typing"
            else ("BubbleUser" if role == "user" else "BubbleAssistant")
        )
        # fixed width, let height grow with content
        self.bubble.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.bubble.setFixedWidth(self.FIXED_W)

        vb = QVBoxLayout(self.bubble)
        vb.setContentsMargins(12, 10, 12, 8)
        vb.setSpacing(6)

        self.body = QTextBrowser()
        self.body.setOpenExternalLinks(True)
        self.body.setWordWrapMode(QTextOption.WordWrap)  # wrap at word boundaries
        self.body.setFrameStyle(QFrame.NoFrame)
        self.body.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        self.body.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.body.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.body.setStyleSheet("background: transparent; border: none;")
        self.body.setHtml(self._to_html(text))
        vb.addWidget(self.body)

        if role == "assistant" and sources:
            src = QFrame(); src.setObjectName("Sources")
            src_layout = QVBoxLayout(src); src_layout.setContentsMargins(8,6,8,6)
            src_title = QLabel("Sources"); src_title.setStyleSheet("font-weight:600;")
            src_text = QLabel(sources); src_text.setWordWrap(True)
            src_layout.addWidget(src_title); src_layout.addWidget(src_text)
            vb.addWidget(src)

        if role != "typing":
            meta = QLabel(self.timestamp.strftime("%H:%M"))
            meta.setObjectName("Meta"); meta.setAlignment(Qt.AlignRight)
            vb.addWidget(meta)

        # align like chat apps
        if role == "user":
            row.addStretch()
            row.addWidget(self.bubble, 0, Qt.AlignRight | Qt.AlignTop)
        else:  # assistant or typing
            row.addWidget(self.bubble, 0, Qt.AlignLeft | Qt.AlignTop)
            row.addStretch()

        container.addLayout(row)

        # autosize height to fit text (no inner scrollbars)
        self._autosize_height()

    def _autosize_height(self):
        """Set text width and compute exact height so the bubble grows vertically."""
        text_w = self.FIXED_W - self.PADDING_LR
        doc = self.body.document()
        doc.setTextWidth(text_w)  # wrap here
        h = int(doc.size().height())
        self.body.setFixedSize(text_w, h + 2)  # +2 for internal margins

    def _to_html(self, text: str) -> str:
        safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe = safe.replace("\n", "<br>")
        return f"<div style='font-size:14px; line-height:1.5'>{safe}</div>"

# ---------------------------
# Settings dialog (kept for Python/model/host/cache)
# ---------------------------
class SettingsDialog(QDialog):
    def __init__(self, python_exe: str, model: str, host: str, cache_dir: str, parent=None):
        super().__init__(parent); self.setWindowTitle("Settings")
        form = QFormLayout(self)
        self.python_edit = QLineEdit(python_exe)
        self.model_edit = QLineEdit(model)
        self.host_edit = QLineEdit(host)
        self.cache_edit = QLineEdit(cache_dir)
        form.addRow("Python Executable", self.python_edit)
        form.addRow("Model", self.model_edit)
        form.addRow("Ollama Host", self.host_edit)
        form.addRow("Cache Dir", self.cache_edit)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept); self.buttons.rejected.connect(self.reject)
        form.addWidget(self.buttons)
    def values(self) -> Tuple[str, str, str, str]:
        return (self.python_edit.text().strip(), self.model_edit.text().strip(),
                self.host_edit.text().strip(), self.cache_edit.text().strip())

# ---------------------------
# Chat window (no top menu/header)
# ---------------------------
class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat")
        self.resize(980, 740)
        self.setLayoutDirection(Qt.LeftToRight)
        self.setStyleSheet(GLOBAL_QSS)

        # Hide the menu bar entirely (no top menu)
        if self.menuBar():
            self.menuBar().hide()

        # Settings
        self.python_exe = sys.executable
        self.model = "gemma:2b-instruct"
        self.ollama_host = "http://localhost:11434"
        self.cache_dir = "multi_source_cache"

        # Messages area
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.messages_host = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_host)
        self.messages_layout.setContentsMargins(20, 14, 20, 14)
        self.messages_layout.setSpacing(6)
        self.messages_layout.addStretch()
        self.scroll.setWidget(self.messages_host)

        # Composer
        composer = QFrame(); composer.setObjectName("Composer")
        comp_l = QHBoxLayout(composer); comp_l.setContentsMargins(20, 12, 20, 12); comp_l.setSpacing(12)

        self.input = QTextEdit(); self.input.setObjectName("Input")
        self.input.setPlaceholderText("Type a message... (Enter to send, Shift+Enter for newline)")
        self.input.setFixedHeight(110); self.input.setFontPointSize(11)
        self.input.installEventFilter(self)

        self.send_btn = QPushButton("Send"); self.send_btn.setObjectName("SendBtn")
        self.send_btn.clicked.connect(self.on_send)

        comp_l.addWidget(self.input, 1); comp_l.addWidget(self.send_btn, 0)

        # Layout (no top bar/header)
        central = QWidget(); v = QVBoxLayout(central); v.setContentsMargins(0,0,0,0)
        v.addWidget(self.scroll, 1); v.addWidget(composer)
        self.setCentralWidget(central)

        # Welcome
        self.add_assistant("Hello! I can help you with event planning questions.")

        # typing bubble ref
        self._typing_bubble: Optional[MessageBubble] = None

    # ---- Chat mechanics ----
    def eventFilter(self, obj, ev):
        if obj is self.input and ev.type() == QEvent.KeyPress:
            if ev.key() in (Qt.Key_Return, Qt.Key_Enter):
                if ev.modifiers() & Qt.ShiftModifier: return False
                self.on_send(); return True
        return super().eventFilter(obj, ev)

    def add_user(self, text: str):
        self._insert_message(MessageBubble("user", text))

    def add_assistant(self, text: str, sources: Optional[str] = None):
        self._insert_message(MessageBubble("assistant", text, sources=sources))

    def add_typing(self):
        self._typing_bubble = MessageBubble("typing", "Thinking…")
        self._insert_message(self._typing_bubble)

    def remove_typing(self):
        if self._typing_bubble is not None:
            self._typing_bubble.setParent(None)
            self._typing_bubble.deleteLater()
            self._typing_bubble = None

    def _insert_message(self, w: QWidget):
        idx = self.messages_layout.count() - 1
        self.messages_layout.insertWidget(idx, w)
        QGuiApplication.processEvents()
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

    def on_send(self):
        text = self.input.toPlainText().strip()
        if not text: return
        self.input.clear()
        self.add_user(text)
        self.add_typing()
        self.send_btn.setDisabled(True)

        self.worker = ExternalAskWorker(
            python_exe=self.python_exe, question=text,
            model=self.model, host=self.ollama_host, cache_dir=self.cache_dir
        )
        self.worker.finished.connect(self.on_answer)
        self.worker.start()

    def on_answer(self, question: str, answer: str, err: str):
        self.remove_typing()
        self.send_btn.setDisabled(False)
        if err:
            self.add_assistant("❌ Error:\n" + err); return
        sources_text = None; body = answer
        if "\nSources:" in answer:
            parts = answer.split("\nSources:"); body = parts[0].strip(); sources_text = parts[1].strip()
        self.add_assistant(body, sources_text)

    # ---- Utilities (still useful without menu) ----
    def keyPressEvent(self, event):
        # Ctrl+S to save chat; Ctrl+, to open settings
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_S:
                self.save_chat(); return
            if event.key() == Qt.Key_Comma:
                self.open_settings(); return
        super().keyPressEvent(event)

    def save_chat(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Chat as JSON", filter="JSON (*.json)")
        if not path: return
        transcript = []
        for i in range(self.messages_layout.count() - 1):
            w = self.messages_layout.itemAt(i).widget()
            if isinstance(w, MessageBubble):
                transcript.append({"role": w.role, "time": w.timestamp.isoformat(), "text": w.text, "sources": w.sources})
        with open(path, "w", encoding="utf-8") as f:
            json.dump(transcript, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "Saved", "Chat saved successfully.")

    def open_settings(self):
        dlg = SettingsDialog(self.python_exe, self.model, self.ollama_host, self.cache_dir, self)
        if dlg.exec() == QDialog.Accepted:
            py, model, host, cache = dlg.values()
            changed = (py != self.python_exe) or (model != self.model) or (host != self.ollama_host) or (cache != self.cache_dir)
            self.python_exe, self.model, self.ollama_host, self.cache_dir = py, model, host, cache
            if changed:
                QMessageBox.information(self, "Updated", "Settings updated. The next question will use the new interpreter and settings.")

# ---------------------------
def main():
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LeftToRight)
    app.setFont(QFont("Segoe UI", 10))
    w = ChatWindow(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

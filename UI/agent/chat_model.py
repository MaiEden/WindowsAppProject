# chat_model.py
from __future__ import annotations

import json
import subprocess
import traceback
from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import QObject, QThread, Signal


def _build_inline_runner(question: str, model: str, host: str, cache_dir: str, llm_dir: str) -> str:
    """Create the inline Python code that runs in the external interpreter."""
    def esc(s: str) -> str:
        return (s or "").replace("\\", "\\\\").replace('"', '\\"')
    q = esc(question)
    mdl = esc(model)
    h = esc(host)
    cdir = esc(cache_dir)
    ldir = esc(llm_dir)
    return f"""
import json, sys, traceback
# Ensure we can import llm_agent.py from server/agent
if r"{ldir}" not in sys.path:
    sys.path.insert(0, r"{ldir}")
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


class _ExternalAskWorker(QThread):
    finished = Signal(str, str)  # (answer, error)

    def __init__(self, python_exe: str, question: str, model: str, host: str, cache_dir: str, llm_dir: str):
        super().__init__()
        self.python_exe = python_exe
        self.question = question
        self.model = model
        self.host = host
        self.cache_dir = cache_dir
        self.llm_dir = llm_dir

    def run(self):
        try:
            code = _build_inline_runner(self.question, self.model, self.host, self.cache_dir, self.llm_dir)
            proc = subprocess.run([self.python_exe, "-c", code], capture_output=True, text=True)
            stdout = (proc.stdout or "").strip()
            stderr = (proc.stderr or "").strip()
            if not stdout:
                self.finished.emit("", f"No output from helper. Stderr:\n{stderr}")
                return
            try:
                payload = json.loads(stdout)
            except Exception:
                lines = [ln for ln in stdout.splitlines() if ln.strip().startswith("{") and ln.strip().endswith("}")]
                if not lines:
                    self.finished.emit("", f"Invalid output:\n{stdout}\n\nStderr:\n{stderr}")
                    return
                payload = json.loads(lines[-1])
            if payload.get("ok"):
                self.finished.emit(payload.get("answer", ""), "")
            else:
                self.finished.emit("", payload.get("error", "Unknown error"))
        except Exception as e:
            self.finished.emit("", f"{e}\n{traceback.format_exc()}")


@dataclass
class ChatSettings:
    """Runtime configuration injected by the Presenter."""
    python_exe: str
    model: str = "gemma:2b-instruct"
    ollama_host: str = "http://localhost:11434"
    cache_dir: str = ""           # absolute path to server/agent/multi_source_cache
    llm_agent_dir: str = ""       # absolute path to server/agent (for llm_agent.py)


class ChatModel(QObject):
    """Chat Model (MVP)."""
    answer_ready = Signal(str, str)  # (answer, error)

    def __init__(self, settings: ChatSettings):
        super().__init__()
        self.settings = settings
        self._worker: Optional[_ExternalAskWorker] = None

    def ask(self, question: str) -> None:
        if self._worker and self._worker.isRunning():
            return
        self._worker = _ExternalAskWorker(
            python_exe=self.settings.python_exe,
            question=question,
            model=self.settings.model,
            host=self.settings.ollama_host,
            cache_dir=self.settings.cache_dir,
            llm_dir=self.settings.llm_agent_dir,
        )
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.start()

    def _on_worker_finished(self, answer: str, error: str) -> None:
        self.answer_ready.emit(answer, error)
        self._worker = None

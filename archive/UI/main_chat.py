# main_chat.py
"""
Entry point for the minimal Chat MVP (Model–View–Presenter).
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from chat_model import ChatModel, ChatSettings
from chat_view import ChatView
from chat_presenter import ChatPresenter


def main():
    """Boot the Chat MVP and start the Qt event loop."""
    app = QApplication(sys.argv)
    # Force Left-to-Right UI and a consistent base font for the whole app
    app.setLayoutDirection(Qt.LeftToRight)
    app.setFont(QFont("Segoe UI", 10))

    # --- Resolve absolute paths from project root ---
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    LLM_AGENT_DIR = str(PROJECT_ROOT / "server" / "agent")
    CACHE_DIR = str(PROJECT_ROOT / "server" / "agent" / "multi_source_cache")

    # Settings consumed by ChatModel / external worker:
    settings = ChatSettings(
        python_exe=sys.executable,
        model="gemma:2b-instruct",
        ollama_host="http://localhost:11434",
        cache_dir=CACHE_DIR,         # absolute cache path (consistent across apps/tools)
        llm_agent_dir=LLM_AGENT_DIR  # ensures helper can import llm_agent.py
    )

    # MVP wiring: the presenter coordinates user actions (View) and data/IO (Model)
    model = ChatModel(settings=settings)
    view = ChatView()
    presenter = ChatPresenter(model, view)

    view.show()
    sys.exit(app.exec())  # hand control to Qt's event loop


if __name__ == "__main__":
    main()

# main_chat.py
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from chat_model import ChatModel, ChatSettings
from chat_view import ChatView
from chat_presenter import ChatPresenter


def main():
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LeftToRight)
    app.setFont(QFont("Segoe UI", 10))

    # --- Resolve absolute paths from project root ---
    # main_chat.py is in: WindowsAppProject/UI/agent/
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    LLM_AGENT_DIR = str(PROJECT_ROOT / "server" / "agent")  # where llm_agent.py lives
    CACHE_DIR = str(PROJECT_ROOT / "server" / "agent" / "multi_source_cache")

    settings = ChatSettings(
        python_exe=sys.executable,
        model="gemma:2b-instruct",
        ollama_host="http://localhost:11434",
        cache_dir=CACHE_DIR,         # absolute cache path (same for builder and MVP)
        llm_agent_dir=LLM_AGENT_DIR  # so the helper can import llm_agent.py
    )

    model = ChatModel(settings=settings)
    view = ChatView()
    presenter = ChatPresenter(model, view)

    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

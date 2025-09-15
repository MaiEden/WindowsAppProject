# UI/agent/chat_factory.py
from __future__ import annotations

import sys
from pathlib import Path
from typing import Tuple

from chat_model import ChatModel, ChatSettings
from chat_view import ChatView
from chat_presenter import ChatPresenter


def build_chat_module(project_root: Path, python_exe: str) -> Tuple[ChatView, ChatPresenter]:
    """
    Composition/factory for the Chat MVP.
    - Computes absolute paths so cache import works regardless of where you run from.
    - Creates Model, View, Presenter and wires them.
    - Returns (view, presenter); keep a ref to presenter so signals stay alive.
    """
    cache_dir     = str(project_root / "server" / "agent" / "multi_source_cache")
    llm_agent_dir = str(project_root / "server" / "agent")

    settings = ChatSettings(
        python_exe=python_exe,
        model="gemma:2b-instruct",
        ollama_host="http://localhost:11434",
        cache_dir=cache_dir,
        llm_agent_dir=llm_agent_dir,
    )

    model = ChatModel(settings=settings)
    view  = ChatView()
    pres  = ChatPresenter(model, view)
    return view, pres

"""
Presenter for the Chat screen (MVP).
- Wires up the view and the model.
- Forwards user actions (send) to the model.
- Applies model results back to the view (answer or error).
"""
from __future__ import annotations
from chat_model import ChatModel
from chat_view import ChatView

class ChatPresenter:
    def __init__(self, model: ChatModel, view: ChatView):
        self.model = model
        self.view = view
        self._connect_signals()

    def _connect_signals(self) -> None:
        # View → Presenter
        self.view.send_clicked.connect(self.on_send)
        # Model → Presenter
        self.model.answer_ready.connect(self.on_answer_ready)

    # ----- Handlers -----
    def on_send(self, text: str) -> None:
        """User clicked send (or pressed Enter)."""
        self.view.add_user(text)
        self.view.clear_input()
        self.view.set_enabled(False)
        self.view.show_typing()
        self.model.ask(text)

    def on_answer_ready(self, answer: str, error: str) -> None:
        """Model finished the async request."""
        self.view.hide_typing()
        self.view.set_enabled(True)
        if error:
            self.view.add_assistant("Error:\n" + error)
            return

        # Split out "Sources:" footer if present (preserves your existing behavior).
        body = answer
        sources = None
        if "\nSources:" in answer:
            parts = answer.split("\nSources:")
            body = parts[0].strip()
            sources = parts[1].strip()
        self.view.add_assistant(body, sources)
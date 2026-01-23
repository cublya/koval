from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Static, Label
from textual.message import Message

class ChatBubble(Static):
    """A widget to display a chat message."""

    def __init__(self, role: str, content: str):
        super().__init__()
        self.role = role
        self.content = content
        self.classes = f"bubble-{role}"

    def compose(self) -> ComposeResult:
        yield Label(f"[{self.role.upper()}]", classes="bubble-header")
        yield Label(self.content, classes="bubble-content")

class AgentThinking(Static):
    """A widget showing that the agent is working."""
    def compose(self) -> ComposeResult:
        yield Label("Agent is thinking...", classes="thinking-label")

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, DirectoryTree, Static
from textual.containers import Container, VerticalScroll
from apps.cli.ui_components import ChatBubble
from libs.core.agent import Agent
import os

class KovalApp(App):
    CSS_PATH = "style.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-layout"):
            yield DirectoryTree("./", id="sidebar")
            with Container(id="chat-area"):
                yield VerticalScroll(id="chat-history")
                yield Input(placeholder="Ask Koval...", id="input-box")
        yield Footer()

    def on_mount(self) -> None:
        try:
            self.agent = Agent()
        except Exception:
            self.agent = None

        # Initial greeting
        self.query_one("#chat-history").mount(ChatBubble("assistant", "Hello! I am Koval. How can I help you?"))

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        user_input = event.value
        if not user_input.strip():
            return

        event.input.value = ""

        # Display user message
        await self.query_one("#chat-history").mount(ChatBubble("user", user_input))

        # Run agent in worker thread
        self.run_worker(self.agent_task(user_input), thread=True)

    def agent_task(self, user_input: str):
        def task():
            if not self.agent:
                 self.call_from_thread(self.update_chat, "Error: Agent not initialized.")
                 return

            try:
                response = self.agent.chat(user_input)
                self.call_from_thread(self.update_chat, str(response))
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                self.call_from_thread(self.update_chat, error_msg)
        return task

    def update_chat(self, message: str):
        self.query_one("#chat-history").mount(ChatBubble("assistant", message))

def run_cli():
    app = KovalApp()
    app.run()

from libs.drivers.base import Driver
from libs.core.agent import Agent
import os

class NativeDriver(Driver):
    def __init__(self, config=None):
        super().__init__(config)
        self.agent = Agent(model_name=self.config.get("model"))

    def run(self, task: str, path: str = ".") -> str:
        # NOTE: Changing CWD in a threaded environment (SwarmPipeline) is unsafe because
        # CWD is shared across the process.
        # We must explicitly instruct the agent to use the provided absolute path
        # for all its operations.

        abs_path = os.path.abspath(path)
        prompt = (
            f"Task: {task}\n"
            f"You are working in the directory: {abs_path}\n"
            f"IMPORTANT: You MUST use this path ({abs_path}) as the base for all file operations and searches.\n"
            f"Do not assume you are in this directory. Always pass it explicitly to tools."
        )

        try:
            response = self.agent.chat(prompt)
            return response
        except Exception as e:
            return f"Error in Native Driver: {str(e)}"

    def is_interactive(self) -> bool:
        return False

from libs.drivers.base import Driver
from libs.core.agent import Agent
import os

class NativeDriver(Driver):
    def __init__(self, config=None):
        super().__init__(config)
        self.agent = Agent(model_name=self.config.get("model"))

    def run(self, task: str, path: str = ".") -> str:
        # Ensure we are in the correct path?
        # The agent tools allow specifying path, or we can change cwd.
        # Changing cwd might be risky for the host process if not careful,
        # but for a driver running in a swarm process, it's fine.
        # For now, I'll pass the path info in the prompt or rely on tools.

        # Alternatively, change directory context manager
        original_cwd = os.getcwd()
        try:
            if os.path.exists(path):
                os.chdir(path)

            response = self.agent.chat(f"Task: {task}\nYou are working in {os.getcwd()}")
            return response
        except Exception as e:
            return f"Error in Native Driver: {str(e)}"
        finally:
            os.chdir(original_cwd)

    def is_interactive(self) -> bool:
        return False

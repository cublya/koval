from libs.drivers.base import Driver
import subprocess

class CodexDriver(Driver):
    """
    Adapter for OpenAI Codex / OpenAI CLI.
    https://github.com/openai/codex (or generally openai-python CLI)
    """
    def run(self, task: str, path: str = ".") -> str:
        # Assuming `openai` CLI is available.
        # openai api chat.completions.create -m gpt-4 ...

        # However, "Codex" specifically usually refers to older models or the engine behind Copilot.
        # If the user means the `openai` CLI:

        cmd = [
            "openai", "api", "chat.completions.create",
            "-m", "gpt-4",
            "-g", "user", task
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Codex/OpenAI Error: {result.stderr}"
        except Exception as e:
            return f"Error executing Codex Driver: {str(e)}"

    def is_interactive(self) -> bool:
        return False

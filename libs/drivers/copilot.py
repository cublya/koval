from libs.drivers.base import Driver
import subprocess

class CopilotDriver(Driver):
    """
    Adapter for GitHub Copilot CLI.
    https://github.com/github/copilot-cli
    """
    def run(self, task: str, path: str = ".") -> str:
        # Copilot CLI usage: `gh copilot suggest "task"` or `gh copilot explain`
        # It is interactive by default.
        # For headless, we might need specific flags or piping.

        cmd = ["gh", "copilot", "suggest", "-t", "shell", task]

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
                return f"Copilot Error: {result.stderr}"
        except Exception as e:
            return f"Error executing Copilot Driver: {str(e)}"

    def is_interactive(self) -> bool:
        return True

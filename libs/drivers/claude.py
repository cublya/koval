from libs.drivers.base import Driver
import subprocess
import os

class ClaudeDriver(Driver):
    """
    Driver for Anthropic's 'claude-code' CLI.
    https://github.com/anthropics/claude-code
    """
    def run(self, task: str, path: str = ".") -> str:
        # Claude Code typically runs as `claude`
        # It's an interactive tool, but can we pipe input?
        # Docs usually suggest `claude "prompt"`

        cmd = ["claude", "--print", task] # Assuming --print or non-interactive flag exists or just passing prompt
        # NOTE: Claude Code is highly interactive. For headless use in Swarm, we rely on it processing the prompt and exiting.
        # If it enters a REPL, we might need `echo "task" | claude` or similar.

        # Checking best practices: Authentication via `claude login` expected to be done.

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
                return f"Claude Error: {result.stderr}"
        except Exception as e:
            return f"Error executing Claude Driver: {str(e)}"

    def is_interactive(self) -> bool:
        # Claude Code is primarily interactive, but we are adapting it for Swarm
        return True

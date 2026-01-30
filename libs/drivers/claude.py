from libs.drivers.base import Driver
import subprocess

class ClaudeDriver(Driver):
    """
    Driver for Anthropic's 'claude-code' CLI.
    https://github.com/anthropics/claude-code
    """
    def run(self, task: str, path: str = ".") -> str:
        # Use -p for non-interactive prompt execution
        cmd = ["claude", "-p", task]

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
        return True

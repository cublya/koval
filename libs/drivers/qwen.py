from libs.drivers.base import Driver
import subprocess

class QwenDriver(Driver):
    """
    Adapter for QwenLM Code.
    https://github.com/QwenLM/qwen-code
    """
    def run(self, task: str, path: str = ".") -> str:
        # Assuming a `qwen-cli` or similar exists.
        # This is speculative based on common patterns as I cannot install it.

        cmd = ["qwen-cli", "run", "--prompt", task]

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
                return f"Qwen Error: {result.stderr}"
        except Exception as e:
            return f"Error executing Qwen Driver: {str(e)}"

    def is_interactive(self) -> bool:
        return False

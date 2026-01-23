from libs.drivers.base import Driver
import subprocess
import shlex
import os

class GeminiDriver(Driver):
    def run(self, task: str, path: str = ".") -> str:
        # Check if gemini is installed
        # We assume 'gemini' is in the path

        # Build command: gemini -p "task"
        # We run it in the target path so it picks up the context of that folder

        cmd = ["gemini", "-p", task]

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
                return f"Gemini Error: {result.stderr}"

        except Exception as e:
            return f"Error executing Gemini Driver: {str(e)}"

    def is_interactive(self) -> bool:
        return False

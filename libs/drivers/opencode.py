from libs.drivers.base import Driver
import subprocess
import platform
import shlex
import os

class OpenCodeDriver(Driver):
    def run(self, task: str, path: str = ".") -> str:
        # Check if we are in headless mode (e.g. Swarm) vs Interactive
        # If is_interactive is True, we launch terminal.
        # But if Swarm calls this, it expects a result string.
        # OpenCode CLI might have a non-interactive mode?
        # Assuming `opencode start --headless` or similar exists for CI/CD.
        # If not, we fall back to launching it and returning a message.

        cmd = ["opencode", "start", "--dir", path, "--task", task]

        # NOTE: For Swarm, ideally we want to capture output.
        # If the user strictly wants to "connect to these clis", launching them is correct.
        # But for "giving instructions", passing --task is correct.

        system = platform.system()
        full_cmd = " ".join(shlex.quote(c) for c in cmd)

        try:
            if system == "Darwin":  # macOS
                # apple script to open terminal and run command
                script = f'''
                tell application "Terminal"
                    do script "{full_cmd}; exit"
                    activate
                end tell
                '''
                subprocess.run(["osascript", "-e", script], check=True)
                return "Launched OpenCode in new Terminal. Please check the window."

            elif system == "Linux":
                # Try common terminals
                terminals = ["gnome-terminal", "xterm", "konsole"]
                for term in terminals:
                    # simplistic check
                    if subprocess.run(["which", term], capture_output=True).returncode == 0:
                        if term == "gnome-terminal":
                             subprocess.run([term, "--", "bash", "-c", f"{full_cmd}; read -p 'Press Enter to close'"], check=True)
                        else:
                             subprocess.run([term, "-e", f"{full_cmd}"], check=True)
                        return f"Launched OpenCode in {term}."
                return "No supported terminal found to launch OpenCode."

            else:
                return "OS not supported for auto-launching OpenCode."

        except Exception as e:
            return f"Error launching OpenCode: {str(e)}"

    def is_interactive(self) -> bool:
        return True

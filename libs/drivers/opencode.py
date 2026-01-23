from libs.drivers.base import Driver
import subprocess
import platform
import shlex
import os

class OpenCodeDriver(Driver):
    def run(self, task: str, path: str = ".") -> str:
        cmd = ["opencode", "start", "--dir", path, "--task", task]

        # In a real scenario, we might want to launch a new terminal window.
        # For now, we'll try to run it in the current process if possible,
        # or simulate the launch command.

        # Note: Launching a TUI inside a subprocess without a TTY is tricky.
        # If this driver is running in a background worker (Swarm), it might fail to open a UI.
        # We will assume this is being run in a context where we can spawn a terminal or
        # just print the command for now if we are headless.

        # But per requirements: "Launches the tool in a new terminal tab/pane and waits for user exit."

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

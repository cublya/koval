import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

def run_shell(cmd: str, cwd: str = ".") -> Tuple[str, str, int]:
    """
    Executes a shell command and returns (stdout, stderr, return_code).
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            text=True,
            capture_output=True
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), -1

def read_file_with_lines(path: str) -> str:
    """
    Reads a file and returns its content with line numbers.
    Format:
    1 | import os
    2 | import sys
    ...
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        output = []
        for i, line in enumerate(lines, 1):
            output.append(f"{i} | {line.rstrip()}")
        return "\n".join(output)
    except FileNotFoundError:
        return f"Error: File '{path}' not found."
    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"

def read_file(path: str) -> str:
    """
    Reads a file and returns its raw content.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"

def search_project(query: str, path: str = ".") -> str:
    """
    Searches the project for a string using grep.
    """
    # Using grep -rn to show line numbers and recursive
    # Excluding .git, __pycache__, and other common ignore dirs
    # Use 'path' as the location for grep to start
    cmd = f"grep -rn \"{query}\" {path} --exclude-dir=.git --exclude-dir=__pycache__ --exclude-dir=.koval_worktrees"
    stdout, stderr, code = run_shell(cmd)
    if code == 0:
        return stdout
    elif code == 1:
        return "No matches found."
    else:
        return f"Error searching: {stderr}"

def edit_file_patch(path: str, search_block: str, replace_block: str) -> str:
    """
    Applies a search and replace patch to a file.
    The search_block must match exactly (whitespace matters).
    """
    try:
        if not os.path.exists(path):
            return f"Error: File '{path}' not found."

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if search block exists
        if search_block not in content:
            # Try to be a bit smarter? For now, strict match is requested for reliability.
            # But maybe we can normalize line endings?
            return f"Error: Search block not found in '{path}'. Make sure whitespace matches exactly."

        # Check if multiple occurrences
        if content.count(search_block) > 1:
            return f"Error: Search block matches multiple locations in '{path}'. Please be more specific."

        new_content = content.replace(search_block, replace_block)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return f"Successfully applied patch to '{path}'."

    except Exception as e:
        return f"Error patching file: {str(e)}"

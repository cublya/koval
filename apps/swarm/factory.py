import os
import shutil
import subprocess
import time
from pathlib import Path

class WorktreeFactory:
    def __init__(self, base_path: str = ".koval_worktrees"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)

    def _run_git(self, args: list, cwd: str = ".") -> None:
        try:
            subprocess.run(
                ["git"] + args,
                cwd=cwd,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git command failed: {e.stderr}")

    def create_worktree(self, task_name: str) -> str:
        """
        Creates a git worktree for the task.
        Returns the absolute path to the worktree.
        """
        sanitized_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in task_name)
        branch_name = f"koval/{sanitized_name}"
        worktree_path = self.base_path / sanitized_name

        # If worktree path exists, clean it up first (idempotency)
        if worktree_path.exists():
            self.cleanup(task_name)

        print(f"Creating worktree '{worktree_path}' on branch '{branch_name}'")

        try:
            # Create worktree and new branch
            self._run_git(["worktree", "add", "-b", branch_name, str(worktree_path.absolute())])
            return str(worktree_path.absolute())
        except RuntimeError as e:
            # Handle case where branch might already exist
            if "already exists" in str(e):
                print(f"Branch {branch_name} exists, checking it out.")
                self._run_git(["worktree", "add", str(worktree_path.absolute()), branch_name])
                return str(worktree_path.absolute())
            else:
                raise e

    def cleanup(self, task_name: str):
        sanitized_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in task_name)
        worktree_path = self.base_path / sanitized_name

        if worktree_path.exists():
            print(f"Cleaning up worktree at {worktree_path}")
            # Unlock worktree just in case (git worktree remove usually handles this, but forcing helps)
            try:
                self._run_git(["worktree", "remove", "--force", str(worktree_path.absolute())])
            except RuntimeError:
                # If git fails, might just be a folder
                pass

            # Ensure folder is gone
            if worktree_path.exists():
                shutil.rmtree(worktree_path)

        # Note: We are NOT deleting the branch here, as the user might want to merge the PR later.
        # Requirements say: "Cleanup: Delete the Worktree folder."

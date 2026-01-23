import os
import shutil

class WorktreeFactory:
    def __init__(self, base_path: str = ".koval_worktrees"):
        self.base_path = base_path

    def create_worktree(self, task_name: str) -> str:
        """
        Creates a git worktree for the task.
        Returns the path to the worktree.
        """
        # Placeholder
        print(f"Creating worktree for {task_name}")
        path = os.path.join(self.base_path, task_name)
        os.makedirs(path, exist_ok=True)
        return path

    def cleanup(self, task_name: str):
        print(f"Cleaning up {task_name}")
        # Placeholder
        path = os.path.join(self.base_path, task_name)
        if os.path.exists(path):
            shutil.rmtree(path)

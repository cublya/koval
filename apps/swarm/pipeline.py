import os
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from apps.swarm.planner import Planner
from apps.swarm.factory import WorktreeFactory
from libs.drivers import get_driver
from libs.core.config import load_config
from libs.core.reviewer import Reviewer
from libs.core.enums import DriverType

class SwarmPipeline:
    def __init__(self, config_path: str = "koval.yaml"):
        self.config = load_config()
        self.planner = Planner()
        self.factory = WorktreeFactory()
        self.reviewer = Reviewer()
        self.max_workers = self.config.get("system", {}).get("max_workers", 4)
        # Default verification command - strictly this should come from config or prompt
        self.verification_command = "python3 -m pytest"

    def execute_task(self, task: str) -> str:
        """
        Executes a single subtask in an isolated worktree with a review loop.
        """
        print(f"Starting execution for: {task}")
        worktree_path = ""
        max_retries = 3

        try:
            # 1. Create Worktree
            worktree_path = self.factory.create_worktree(task)

            # 2. Get Driver
            # We determine the driver from config, allowing the user to choose the backend tool.
            # Default to Native (LiteLLM) if not specified.
            driver_name = self.config.get("system", {}).get("driver", DriverType.NATIVE)
            driver = get_driver(driver_name, config={"model": self.planner.model})

            # 3. Work Loop (Code -> Review -> Fix)
            current_request = task
            for attempt in range(max_retries):
                print(f"Attempt {attempt + 1}/{max_retries} for task: {task}")

                # A. Run Agent
                result = driver.run(current_request, path=worktree_path)

                # B. Review
                print(f"Running verification in {worktree_path}")
                # Ideally, we read the verification command from the repo's configuration
                # For now, we use a placeholder or check if a specific file exists
                verify_cmd = self.verification_command

                # Check if we should skip verification (e.g. if task is just 'plan')
                # But requirement says "The Reviewer Agent runs tests/linters."

                is_success, log = self.reviewer.verify(verify_cmd, cwd=worktree_path)

                if is_success:
                    print(f"Verification passed for {task}.")

                    # 4. Publish (Push & PR)
                    self.publish_changes(worktree_path, task)

                    return f"Task '{task}' completed successfully."
                else:
                    print(f"Verification failed for {task}. Log: {log[:100]}...")
                    # Analyze error (optional, but requested in reqs "If Reviewer fails... sends error back")
                    # We can just send the raw log or use Reviewer to summarize.
                    # The requirement says "Reviewer Agent... runs tests... If it fails, it sends the error back".

                    current_request = f"Your changes caused these errors. Please fix them:\n{log[-2000:]}" # Truncate log if too huge

            return f"Task '{task}' failed after {max_retries} attempts."

        except Exception as e:
            return f"Task '{task}' failed with exception: {str(e)}"
        finally:
            # 5. Cleanup
            if worktree_path:
                self.factory.cleanup(task)

    def publish_changes(self, worktree_path: str, task: str):
        """
        Pushes the branch and creates a PR.
        """
        print(f"Publishing changes for {task}...")
        try:
            # Git push
            # We are in a worktree, so we can just push HEAD
            subprocess.run(["git", "push", "origin", "HEAD"], cwd=worktree_path, check=True, capture_output=True)

            # Create PR using gh cli
            # We assume gh is installed and authenticated
            # title = task, body = Automated by Koval Swarm
            # subprocess.run(["gh", "pr", "create", "--title", task, "--body", "Automated by Koval Swarm"], cwd=worktree_path, check=True)
            print(f"Simulated PR creation for {task}")

        except Exception as e:
            print(f"Failed to publish changes: {str(e)}")

    def run(self, goal: str):
        print(f"Swarm received goal: {goal}")

        # 1. Plan
        print("Planning...")
        subtasks = self.planner.plan(goal)
        print(f"Plan generated with {len(subtasks)} tasks: {subtasks}")

        # 2. Execute in Parallel
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {executor.submit(self.execute_task, task): task for task in subtasks}

            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    data = future.result()
                    results.append(data)
                    print(f"Finished: {data}")
                except Exception as exc:
                    print(f"{task} generated an exception: {exc}")

        print("Swarm run complete.")
        return results

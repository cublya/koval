import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from apps.swarm.planner import Planner
from apps.swarm.factory import WorktreeFactory
from libs.drivers import get_driver
from libs.core.config import load_config

class SwarmPipeline:
    def __init__(self, config_path: str = "koval.yaml"):
        self.config = load_config()
        self.planner = Planner()
        self.factory = WorktreeFactory()
        self.max_workers = self.config.get("system", {}).get("max_workers", 4)

    def execute_task(self, task: str) -> str:
        """
        Executes a single subtask in an isolated worktree.
        """
        print(f"Starting execution for: {task}")
        worktree_path = ""
        try:
            # 1. Create Worktree
            worktree_path = self.factory.create_worktree(task)

            # 2. Get Driver (Default to Native for now, or configurable)
            # In a real scenario, the planner might suggest which tool to use.
            driver = get_driver("native", config={"model": self.planner.model})

            # 3. Run Driver
            print(f"Running agent in {worktree_path} for task: {task}")
            # We need to inform the agent it is in a specific path or change cwd
            # The driver run method usually takes the path.

            result = driver.run(task, path=worktree_path)

            # 4. Review (Simplified for now - we assume success if no crash)
            # A real reviewer loop would go here.

            return f"Task '{task}' completed. Result: {result[:50]}..."

        except Exception as e:
            return f"Task '{task}' failed: {str(e)}"
        finally:
            # 5. Cleanup
            if worktree_path:
                self.factory.cleanup(task)

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

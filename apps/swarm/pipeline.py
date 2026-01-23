from apps.swarm.planner import Planner
from apps.swarm.factory import WorktreeFactory

class SwarmPipeline:
    def __init__(self):
        self.planner = Planner()
        self.factory = WorktreeFactory()

    def run(self, task: str):
        print(f"Swarm running for: {task}")
        plan = self.planner.plan(task)
        for subtask in plan:
            print(f"Executing subtask: {subtask}")
            # Dispatch to agents...

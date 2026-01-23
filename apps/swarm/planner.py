import json
import litellm
from typing import List
from libs.core.config import get_model_config

class Planner:
    def __init__(self, model_name: str = None):
        self.model_config = get_model_config(model_name)
        name = self.model_config.get("model_name", "gpt-4o")
        provider = self.model_config.get("provider")

        if provider and provider != "openai":
             self.model = f"{provider}/{name}"
        else:
             self.model = name

    def plan(self, goal: str) -> List[str]:
        """
        Breaks a goal into a list of specific subtasks using LLM.
        Returns a list of strings, where each string is a subtask.
        """
        prompt = f"""
        You are a Senior Project Manager for a software engineering team.
        Your goal is to break down a high-level request into smaller, isolated, actionable coding tasks.
        Each task must be able to be executed by a single developer on a single branch.

        Goal: {goal}

        Return the result STRICTLY as a JSON list of strings. Do not include markdown formatting.
        Example: ["Create utils.py file", "Add unit tests for utils.py", "Update main.py to use utils"]
        """

        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" } # Helps if model supports it, otherwise prompt instructions
            )
            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            try:
                # Some models might return {"tasks": [...]}, others just [...]
                data = json.loads(content)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                     # Search for the first list value
                     for val in data.values():
                         if isinstance(val, list):
                             return val
                     return [goal] # Fallback
                else:
                    return [goal]
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return [goal]

        except Exception as e:
            print(f"Planner Error: {str(e)}")
            return [goal]

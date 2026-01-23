from typing import Tuple
from libs.core.tools import run_shell
import litellm
from libs.core.config import get_model_config

class Reviewer:
    def __init__(self, model_name: str = None):
        self.model_config = get_model_config(model_name)
        name = self.model_config.get("model_name", "gpt-4o")
        provider = self.model_config.get("provider")

        if provider and provider != "openai":
             self.model = f"{provider}/{name}"
        else:
             self.model = name

    def verify(self, command: str, cwd: str = ".") -> Tuple[bool, str]:
        """
        Runs the verification command.
        Returns (is_success, output_log).
        """
        stdout, stderr, code = run_shell(command, cwd=cwd)
        output = stdout + "\n" + stderr
        return code == 0, output

    def analyze_error(self, error_log: str) -> str:
        """
        Analyzes the error log and suggests fixes.
        """
        prompt = f"""
        You are a Senior Code Reviewer.
        The following verification command failed. Analyze the output and provide a concise explanation and potential fix.

        Error Log:
        {error_log}
        """

        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing logs: {str(e)}"

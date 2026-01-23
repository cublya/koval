import json
import litellm
from typing import List, Dict, Any, Optional
from libs.core.config import get_model_config
from libs.core.tools import read_file_with_lines, search_project, edit_file_patch, run_shell

class Agent:
    def __init__(self, model_name: str = None):
        self.model_config = get_model_config(model_name)
        name = self.model_config.get("model_name", "gpt-4o")
        provider = self.model_config.get("provider")

        if provider and provider != "openai": # OpenAI is default for many names, but explicitly:
             # LiteLLM format: provider/model_name (e.g. ollama/llama3)
             self.model = f"{provider}/{name}"
        else:
             self.model = name

        self.history = []
        self.max_steps = 10

        # Tool mapping
        self.available_tools = {
            "read_file_with_lines": read_file_with_lines,
            "search_project": search_project,
            "edit_file_patch": edit_file_patch,
            "run_shell": run_shell
        }

        # Tool definitions for LLM
        self.tool_definitions = [
            {
                "type": "function",
                "function": {
                    "name": "read_file_with_lines",
                    "description": "Read a file and return its content with line numbers. Use this to examine code.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "The path to the file."}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_project",
                    "description": "Search the project for a string query (grep).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The string to search for."},
                            "path": {"type": "string", "description": "The path to search in (default is current directory)."}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "edit_file_patch",
                    "description": "Replace a specific block of text in a file with a new block. The search block must match exactly.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "The path to the file."},
                            "search_block": {"type": "string", "description": "The exact text block to find and replace."},
                            "replace_block": {"type": "string", "description": "The new text block."}
                        },
                        "required": ["path", "search_block", "replace_block"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_shell",
                    "description": "Run a shell command.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "cmd": {"type": "string", "description": "The command to run."}
                        },
                        "required": ["cmd"]
                    }
                }
            }
        ]

    def chat(self, user_input: str) -> str:
        """
        Send a message to the agent and get a response.
        Handles tool calls automatically.
        """
        self.history.append({"role": "user", "content": user_input})

        step = 0
        while step < self.max_steps:
            try:
                response = litellm.completion(
                    model=self.model,
                    messages=self.history,
                    tools=self.tool_definitions,
                    tool_choice="auto"
                )
            except Exception as e:
                return f"LLM Error: {str(e)}"

            message = response.choices[0].message
            self.history.append(message)

            if message.tool_calls:
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    if function_name in self.available_tools:
                        tool_func = self.available_tools[function_name]
                        # Call the tool
                        try:
                            # Handle optional args for search_project if needed, or rely on **function_args
                            result = tool_func(**function_args)
                        except Exception as e:
                            result = f"Error executing tool: {str(e)}"

                        self.history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": str(result)
                        })
                    else:
                         self.history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": f"Error: Tool {function_name} not found."
                        })
                step += 1
            else:
                # No tool calls, final response
                return message.content or ""

        return "Max steps reached without final answer."

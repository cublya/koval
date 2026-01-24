from enum import Enum

class DriverType(str, Enum):
    NATIVE = "native"
    OPENCODE = "opencode"
    GEMINI = "gemini"
    CLAUDE = "claude"
    CODEX = "codex"
    QWEN = "qwen"
    COPILOT = "copilot"

class ModelProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    VERTEX_AI = "vertex_ai"
    OLLAMA = "ollama"
    AZURE = "azure"

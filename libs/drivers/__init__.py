from libs.drivers.base import Driver
from libs.drivers.native import NativeDriver
from libs.drivers.opencode import OpenCodeDriver
from libs.drivers.gemini import GeminiDriver
from libs.drivers.claude import ClaudeDriver
from libs.drivers.codex import CodexDriver
from libs.drivers.qwen import QwenDriver
from libs.drivers.copilot import CopilotDriver
from libs.core.enums import DriverType

def get_driver(driver_type: DriverType, config: dict = None) -> Driver:
    if driver_type == DriverType.OPENCODE:
        return OpenCodeDriver(config)
    elif driver_type == DriverType.GEMINI:
        return GeminiDriver(config)
    elif driver_type == DriverType.CLAUDE:
        return ClaudeDriver(config)
    elif driver_type == DriverType.CODEX:
        return CodexDriver(config)
    elif driver_type == DriverType.QWEN:
        return QwenDriver(config)
    elif driver_type == DriverType.COPILOT:
        return CopilotDriver(config)
    else:
        return NativeDriver(config)

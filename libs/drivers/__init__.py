from libs.drivers.base import Driver
from libs.drivers.native import NativeDriver
from libs.drivers.opencode import OpenCodeDriver
from libs.drivers.gemini import GeminiDriver

def get_driver(name: str, config: dict = None) -> Driver:
    if name == "opencode":
        return OpenCodeDriver(config)
    elif name == "gemini":
        return GeminiDriver(config)
    else:
        return NativeDriver(config)

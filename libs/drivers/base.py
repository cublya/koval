from abc import ABC, abstractmethod
from typing import Any, Dict
from libs.core.enums import DriverType

class Driver(ABC):
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    @abstractmethod
    def run(self, task: str, path: str = ".") -> str:
        """
        Execute a task in the given path.
        Returns the result or status.
        """
        pass

    @abstractmethod
    def is_interactive(self) -> bool:
        """
        Returns True if the driver requires a separate terminal/interaction.
        """
        pass

"""
Base classes for math tools.
"""

from abc import ABC, abstractmethod
from typing import Optional, Protocol


class MathToolProtocol(Protocol):
    """Protocol interface for math evaluation tools."""

    @property
    def name(self) -> str:
        """Name identifier for this tool."""
        ...

    async def execute(self, expression: str) -> Optional[str]:
        """
        Execute the tool on the given expression.

        Args:
            expression: The mathematical expression to evaluate

        Returns:
            Formatted result string or None if execution failed
        """
        ...


class MathTool(ABC):
    """Abstract base class for math evaluation tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name identifier for this tool."""
        pass

    @abstractmethod
    async def execute(self, expression: str) -> Optional[str]:
        """
        Execute the tool on the given expression.

        Args:
            expression: The mathematical expression to evaluate

        Returns:
            Formatted result string or None if execution failed
        """
        pass

"""
Numeric evaluation tool implementation.
"""

from .base import MathTool
from math_solver.math_evaluators import evaluate_numerically


class NumericTool(MathTool):
    """Tool for high-precision numeric evaluation."""

    @property
    def name(self) -> str:
        return "numeric"

    async def execute(self, expression: str) -> str:
        """
        Execute high-precision numeric evaluation.

        Args:
            expression: The expression to evaluate numerically

        Returns:
            Formatted result string
        """
        return await evaluate_numerically(expression)

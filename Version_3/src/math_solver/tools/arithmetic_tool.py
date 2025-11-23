"""
Basic arithmetic tool implementation.
"""

from .base import MathTool
from math_solver.math_evaluators import evaluate_basic_arithmetic


class ArithmeticTool(MathTool):
    """Tool for evaluating basic arithmetic expressions."""

    @property
    def name(self) -> str:
        return "basic_arithmetic"

    async def execute(self, expression: str) -> str:
        """
        Execute basic arithmetic evaluation.

        Args:
            expression: The arithmetic expression to evaluate

        Returns:
            Formatted result string
        """
        return await evaluate_basic_arithmetic(expression)

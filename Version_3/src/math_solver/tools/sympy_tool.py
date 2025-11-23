"""
SymPy tool implementation for symbolic math.
"""

from .base import MathTool
from math_solver.math_evaluators import evaluate_with_sympy


class SymPyTool(MathTool):
    """Tool for evaluating symbolic mathematical expressions using SymPy."""

    @property
    def name(self) -> str:
        return "sympy"

    async def execute(self, expression: str) -> str:
        """
        Execute symbolic math evaluation using SymPy.

        Args:
            expression: The symbolic expression to evaluate

        Returns:
            Formatted result string
        """
        return await evaluate_with_sympy(expression)

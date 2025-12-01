"""
Math evaluation functions for the chatbot.
"""

import logging

import mpmath as mp
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

logger = logging.getLogger(__name__)


def safe_sympy_eval(expression: str, timeout: float = 5.0) -> tuple[bool, str]:
    """
    Safely evaluate a mathematical expression using SymPy.

    Returns (success: bool, result: str)
    """
    try:
        # Parse with safety transformations
        transformations = standard_transformations + (implicit_multiplication_application,)

        # Evaluate without timeout context since it runs in async context
        # First try to parse as a symbolic expression
        expr = parse_expr(expression, transformations=transformations)

        # Common SymPy operations
        if isinstance(expr, sp.Eq):
            # Equation solving
            if len(expr.free_symbols) == 1:
                var = list(expr.free_symbols)[0]
                solutions = sp.solve(expr, var)
                if solutions:
                    return True, f"Solutions: {solutions}"
            return True, f"Equation: {sp.latex(expr)}"

        elif hasattr(expr, 'is_Function') and expr.is_Function:
            # Function evaluation
            func_name = str(expr.func)
            if func_name in ['solve', 'simplify', 'factor', 'diff', 'integrate', 'limit', 'series']:
                result = expr.doit() if hasattr(expr, 'doit') else expr
                return True, f"Result: {sp.latex(result)}"
            else:
                return True, f"Function: {sp.latex(expr)}"

        else:
            # General symbolic evaluation
            simplified = sp.simplify(expr)
            return True, f"Result: {sp.latex(simplified)}"

    except (sp.SympifyError, ValueError, TypeError) as e:
        return False, f"SymPy evaluation failed: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in SymPy evaluation: {type(e).__name__}: {e}", exc_info=True)
        return False, f"Unexpected error in SymPy evaluation: {str(e)}"


def safe_numeric_eval(expression: str, precision: int = 50, timeout: float = 3.0) -> tuple[bool, str]:
    """
    Evaluate expressions numerically with high precision using mpmath.

    Returns (success: bool, result: str)
    """
    try:
        # Set high precision
        mp.mp.dps = precision

        # Evaluate without timeout context since it runs in async context
        # Try to evaluate with mpmath
        result = mp.eval(expression)

        # Format result nicely
        if isinstance(result, mp.mpf):
            # Float result
            return True, f"≈ {float(result):.{precision//2}g}"
        elif isinstance(result, mp.mpc):
            # Complex result
            return True, f"≈ {complex(result)}"
        else:
            # Other numeric types
            return True, f"Result: {result}"

    except (ValueError, TypeError, mp.NoConvergence) as e:
        return False, f"Numeric evaluation failed: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in numeric evaluation: {type(e).__name__}: {e}", exc_info=True)
        return False, f"Unexpected error in numeric evaluation: {str(e)}"


def safe_arithmetic_eval(expression: str, timeout: float = 2.0) -> tuple[bool, str]:
    """
    Safely evaluate basic arithmetic expressions.

    Uses a restricted environment to prevent code execution.
    Only allows basic arithmetic operations: +, -, *, /, **, ()

    Returns (success: bool, result: str)
    """
    try:
        # Define safe namespace with only basic math operations
        safe_dict = {
            "__builtins__": {},
            # Basic arithmetic operators are available by default in eval
        }

        # Clean the expression - remove spaces and validate characters
        cleaned_expr = expression.replace(" ", "")

        # Only allow digits, operators, and parentheses
        allowed_chars = set("0123456789+-*/().**")
        if not all(c in allowed_chars for c in cleaned_expr):
            return False, "Expression contains invalid characters"

        # Prevent division by zero (basic check)
        if "/0" in cleaned_expr or "/0." in cleaned_expr:
            return False, "Division by zero"

        # Evaluate without timeout since arithmetic is very fast and runs in async context
        result = eval(cleaned_expr, safe_dict)

        # Format the result nicely
        if isinstance(result, (int, float)):
            # For integers, show as integer if it's a whole number
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return True, f"Result: {result}"
        else:
            return True, f"Result: {result}"

    except ZeroDivisionError:
        return False, "Division by zero"
    except (ValueError, TypeError, SyntaxError) as e:
        return False, f"Invalid arithmetic expression: {str(e)}"
    except Exception as e:
        logger.error(f"Arithmetic evaluation failed: {type(e).__name__}: {e}", exc_info=True)
        return False, f"Arithmetic evaluation failed: {str(e)}"


async def evaluate_with_sympy(expression: str) -> str:
    """
    Async wrapper for safe SymPy evaluation.

    Returns formatted result string for the chatbot.
    """
    try:
        # Run the synchronous SymPy evaluation in a thread with timeout
        import asyncio
        success, result = await asyncio.wait_for(
            asyncio.to_thread(safe_sympy_eval, expression, 5.0),
            timeout=5.0
        )
        if success:
            return f"**SymPy Evaluation:**\n{result}"
        else:
            return f"**SymPy Error:** {result}"
    except asyncio.TimeoutError:
        return "**SymPy Error:** Evaluation timed out"
    except Exception as e:
        return f"**SymPy Error:** {str(e)}"


async def evaluate_numerically(expression: str) -> str:
    """
    Async wrapper for numeric evaluation with fallback to SymPy.

    Returns formatted result string for the chatbot.
    """
    try:
        # First try numeric evaluation with timeout
        import asyncio
        success, result = await asyncio.wait_for(
            asyncio.to_thread(safe_numeric_eval, expression, 50, 3.0),
            timeout=3.0
        )
        if success:
            return f"**Numeric Result:**\n{result}"

        # Fallback to SymPy for symbolic expressions with timeout
        success, result = await asyncio.wait_for(
            asyncio.to_thread(safe_sympy_eval, expression, 5.0),
            timeout=5.0
        )
        if success:
            return f"**Symbolic Result:**\n{result}"
        else:
            return f"**Evaluation Error:** {result}"
    except asyncio.TimeoutError:
        return "**Evaluation Error:** Calculation timed out"
    except Exception as e:
        return f"**Evaluation Error:** {str(e)}"


async def evaluate_basic_arithmetic(expression: str) -> str:
    """
    Async wrapper for safe basic arithmetic evaluation.

    Returns formatted result string for the chatbot.
    """
    success, result = safe_arithmetic_eval(expression)
    if success:
        return f"**Arithmetic Result:**\n{result}"
    else:
        return f"**Arithmetic Error:** {result}"

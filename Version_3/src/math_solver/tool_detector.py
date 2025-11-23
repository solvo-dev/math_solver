"""
Tool detection logic for the math solver chatbot.
"""

import re
from typing import Optional


def detect_math_expression(text: str) -> Optional[str]:
    """
    Detect mathematical expressions in text that should use SymPy evaluation.

    Returns the detected expression or None if no clear math expression found.
    """
    # Common patterns that indicate mathematical expressions
    patterns = [
        r'\b(?:solve|simplify|factor|diff|integrate|limit|series|matrix)\s*\([^)]+\)',  # Function calls
        r'\b\d+(?:\.\d+)?\s*[+\-*/^]\s*\d+(?:\.\d+)?',  # Basic arithmetic
        r'\b[a-zA-Z]+\s*=\s*[^=\n]+',  # Variable assignments
        r'\b[a-zA-Z]+\([^)]*\)\s*=\s*[^=\n]+',  # Function definitions
        r'\$.*\$',  # LaTeX expressions (extract content)
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Return the first substantial match
            for match in matches:
                if len(match.strip()) > 3:  # Ignore very short matches
                    if match.startswith('$') and match.endswith('$'):
                        return match[1:-1]  # Remove LaTeX delimiters
                    return match

    return None


def detect_basic_arithmetic(text: str) -> Optional[str]:
    """
    Detect basic arithmetic expressions that can be evaluated directly.

    Looks for expressions like "2+2", "10*5", "100/4", etc.
    Also handles natural language queries like "what is 5 plus 3"

    Returns the extracted arithmetic expression or None.
    """
    text_lower = text.lower().strip()

    # Direct arithmetic patterns (numbers with operators)
    arithmetic_patterns = [
        r'\d+(?:\.\d+)?\s*[+\-*/]\s*\d+(?:\.\d+)?(?:\s*[+\-*/]\s*\d+(?:\.\d+)?)*',  # Multiple operations
        r'\d+(?:\.\d+)?\s*\*\*\s*\d+(?:\.\d+)?',  # Exponentiation
        r'\(\s*\d+(?:\.\d+)?\s*[+\-*/]\s*\d+(?:\.\d+)?\s*\)',  # Parenthesized expressions
    ]

    # Check for direct arithmetic patterns first
    for pattern in arithmetic_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Return the longest match (most complex expression)
            return max(matches, key=len)

    # Natural language patterns
    nl_patterns = [
        # "what is X plus Y", "what is X minus Y", etc.
        r'what\s+is\s+(\d+(?:\.\d+)?)\s*(plus|minus|times|multiplied\s+by|divided\s+by)\s+(\d+(?:\.\d+)?)',
        # "calculate X + Y", "compute X * Y", etc.
        r'(?:calculate|compute)\s+(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)',
        # "X plus Y equals", "X times Y is", etc.
        r'(\d+(?:\.\d+)?)\s*(plus|minus|times|multiplied\s+by|divided\s+by)\s+(\d+(?:\.\d+)?)\s*(?:equals|is|=)',
    ]

    for pattern in nl_patterns:
        match = re.search(pattern, text_lower)
        if match:
            groups = match.groups()
            if len(groups) == 3:  # Natural language with word operators
                num1, op_word, num2 = groups
                # Convert word operators to symbols
                op_map = {
                    'plus': '+',
                    'minus': '-',
                    'times': '*',
                    'multiplied by': '*',
                    'divided by': '/'
                }
                if op_word in op_map:
                    return f"{num1}{op_map[op_word]}{num2}"
            elif len(groups) == 3 and groups[1] in '+-*/':  # Direct operators
                num1, op, num2 = groups
                return f"{num1}{op}{num2}"

    return None


def should_use_sympy(text: str) -> bool:
    """
    Determine if an expression should use SymPy vs numeric evaluation.

    Use SymPy for: symbolic math, equations, calculus, algebra
    Use numeric for: pure numerical calculations
    Use basic_arithmetic for: simple operations without variables
    """
    expression = detect_math_expression(text)
    if not expression:
        return False

    # Check for symbolic indicators
    symbolic_indicators = [
        'solve', 'simplify', 'factor', 'diff', 'integrate', 'limit', 'series',
        '=', 'x', 'y', 'z',  # Variables
        'sin', 'cos', 'tan', 'exp', 'log', 'sqrt',  # Functions
        'matrix', 'vector'  # Linear algebra
    ]

    expr_lower = expression.lower()
    return any(indicator in expr_lower for indicator in symbolic_indicators)


def is_basic_arithmetic(text: str) -> bool:
    """
    Check if the text contains basic arithmetic that should be evaluated directly.

    Returns True if the expression is simple arithmetic without variables or complex functions.
    """
    # First check if we can extract a basic arithmetic expression
    expr = detect_basic_arithmetic(text)
    if not expr:
        return False

    # Make sure it doesn't have variables or complex functions
    expr_lower = expr.lower()
    complex_indicators = [
        'solve', 'simplify', 'factor', 'diff', 'integrate', 'limit', 'series',
        '=', 'x', 'y', 'z', 'a', 'b', 'c',  # Variables
        'sin', 'cos', 'tan', 'exp', 'log', 'sqrt',  # Functions
        'matrix', 'vector'  # Linear algebra
    ]

    return not any(indicator in expr_lower for indicator in complex_indicators)

"""
Custom exception classes for the math solver chatbot.
"""


class MathSolverError(Exception):
    """Base exception class for math solver errors."""
    pass


class MathEvaluationError(MathSolverError):
    """Raised when mathematical evaluation fails."""
    pass


class ToolExecutionError(MathSolverError):
    """Raised when tool execution fails."""
    pass


class OllamaConnectionError(MathSolverError):
    """Raised when Ollama connection fails."""
    pass

"""
Utility functions for the math solver chatbot.
"""

import signal
from contextlib import contextmanager


@contextmanager
def timeout_context(seconds: float):
    """Context manager for timeout handling."""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(int(seconds))
    try:
        yield
    finally:
        signal.alarm(0)

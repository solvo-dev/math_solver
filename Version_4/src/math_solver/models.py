"""
Data models for the math solver chatbot.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ChatMessage:
    """Represents a chat message in the conversation."""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None

"""
Message formatting utilities for the UI.
"""

from typing import Dict, List, Any, TypedDict


class MessageChunk(TypedDict):
    """Type definition for message chunks."""
    type: str  # "chunk" or "tool_result"
    content: str
    tool: str  # Optional, present for tool_result


class MessageFormatter:
    """Handles formatting of messages and chat history for display."""

    @staticmethod
    def format_message_chunk(chunk: MessageChunk) -> str:
        """Format a message chunk for display."""
        if chunk.get("type") == "tool_result":
            tool_name = chunk.get("tool", "unknown")
            return f"[{tool_name.upper()}] {chunk['content']}"
        else:
            return chunk.get("content", "")

    @staticmethod
    def format_chat_history(history: List[List[str]]) -> str:
        """Format chat history for display."""
        if not history:
            return ""

        formatted_messages = []
        for user_msg, assistant_msg in history:
            if user_msg:
                formatted_messages.append(f"**You:** {user_msg}")
            if assistant_msg:
                formatted_messages.append(f"**Assistant:** {assistant_msg}")

        return "\n\n".join(formatted_messages)

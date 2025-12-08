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
            content = chunk.get("content", "")
            
            # Special formatting for classifier results
            if tool_name == "classifier":
                # Parse category and confidence from content
                # Expected format: "Category: algebra (confidence: 0.85)"
                try:
                    if "Category:" in content and "confidence:" in content:
                        # Extract parts
                        parts = content.split("(confidence:")
                        category_part = parts[0].replace("Category:", "").strip()
                        confidence_part = parts[1].replace(")", "").strip()
                        
                        # Map categories to emojis
                        category_emojis = {
                            "algebra": "🔢",
                            "calculus": "📐",
                            "geometry": "📏",
                            "number_theory": "🔢",
                            "number theory": "🔢"
                        }
                        emoji = category_emojis.get(category_part.lower(), "📊")
                        
                        # Create formatted badge
                        return f"\n\n🏷️ **Kategorie erkannt:** {emoji} **{category_part.title()}** (Konfidenz: {confidence_part})\n\n"
                except Exception:
                    pass
            
            # Default tool result formatting
            return f"\n\n💡 **[{tool_name.upper()}]** {content}\n\n"
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
                formatted_messages.append(f"**Du:** {user_msg}")
            if assistant_msg:
                formatted_messages.append(f"**Assistent:** {assistant_msg}")

        return "\n\n".join(formatted_messages)

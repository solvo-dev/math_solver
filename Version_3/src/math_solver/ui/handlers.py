"""
Message handling logic for the UI.
"""

import asyncio
import logging
from typing import AsyncGenerator, List, Tuple, Any

from math_solver.services import ChatbotService
from math_solver.ui.formatters import MessageFormatter, MessageChunk

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles message processing and chatbot interactions."""

    def __init__(self, chatbot_service: ChatbotService) -> None:
        """Initialize with chatbot service dependency."""
        self.chatbot_service = chatbot_service

    async def handle_message(self, message: str, history: List[List[str]]) -> str:
        """
        Handle a single message and return the full response.

        This is used by Gradio's ChatInterface.
        """
        if not message.strip():
            return ""

        chatbot = self.chatbot_service.get_chatbot()

        # Collect full response
        full_response = ""
        try:
            # Get streaming response and collect it
            async for response_chunk in chatbot.generate_response_with_tools(message):
                chunk_content = MessageFormatter.format_message_chunk(response_chunk)
                full_response += chunk_content
        except Exception as e:
            logger.error(f"Chat response error: {e}")
            full_response = f"Error: {str(e)}"

        return full_response

    async def handle_streaming_message(
        self,
        message: str,
        history: List[List[str]]
    ) -> AsyncGenerator[Tuple[str, List[List[str]]], None]:
        """
        Handle a streaming message and yield updates.

        This is used for real-time streaming responses.
        """
        if not message.strip():
            yield "", history
            return

        chatbot = self.chatbot_service.get_chatbot()

        # Add user message to history immediately
        history = history + [[message, None]]

        # Collect streaming response
        full_response = ""
        try:
            # Stream response with tool calls
            async for response_chunk in chatbot.generate_response_with_tools(message):
                chunk_content = MessageFormatter.format_message_chunk(response_chunk)
                full_response += chunk_content

                # Update the last message in history
                history[-1][1] = full_response
                yield MessageFormatter.format_chat_history(history), history

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            full_response = error_msg
            history[-1][1] = error_msg
            logger.error(f"Chat response error: {e}")
            yield MessageFormatter.format_chat_history(history), history

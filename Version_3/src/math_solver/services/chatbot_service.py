"""
Chatbot service for managing chatbot lifecycle and dependencies.
"""

from typing import Optional

from math_solver.config import ChatConfig
from math_solver.chatbot import MathTutorChatbot
from math_solver.ollama_client import OllamaClient
from math_solver.tools import ArithmeticTool, NumericTool, SymPyTool


class ChatbotService:
    """Service for managing chatbot lifecycle and dependencies."""

    def __init__(
        self,
        config: Optional[ChatConfig] = None,
        ollama_client: Optional[OllamaClient] = None
    ) -> None:
        """Initialize the chatbot service with dependencies."""
        self.config = config or ChatConfig()
        self.ollama_client = ollama_client or OllamaClient(
            base_url=self.config.ollama_base_url,
            timeout=60.0
        )

        # Create tool instances
        self.tools = {
            "basic_arithmetic": ArithmeticTool(),
            "sympy": SymPyTool(),
            "numeric": NumericTool()
        }

        # Initialize chatbot with all dependencies
        self.chatbot = MathTutorChatbot(
            config=self.config,
            ollama_client=self.ollama_client,
            tools=self.tools
        )

    def get_chatbot(self) -> MathTutorChatbot:
        """Get the chatbot instance."""
        return self.chatbot

    def get_config(self) -> ChatConfig:
        """Get the current configuration."""
        return self.config

    async def close(self):
        """Close the chatbot and clean up resources."""
        await self.chatbot.close()

"""
Chatbot service for managing chatbot lifecycle and dependencies.
"""

from typing import Optional
from pathlib import Path

from math_solver.config import ChatConfig
from math_solver.chatbot import MathTutorChatbot
from math_solver.ollama_client import OllamaClient
from math_solver.tools import ArithmeticTool, NumericTool, SymPyTool
from math_solver.services.classifier_service import ClassifierService
from math_solver.tools.classifier_tool import ClassifierTool


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

        # Optional classifier tool (opt-in)
        self.classifier_service: Optional[ClassifierService] = None
        if self.config.enable_classifier:
            try:
                model_path = Path(self.config.classifier_model_path)
                if model_path.exists():
                    self.classifier_service = ClassifierService.from_pretrained(model_path)
                else:
                    # Create service anyway; user may train it later
                    self.classifier_service = ClassifierService(model_path)
                self.tools["classifier"] = ClassifierTool(self.classifier_service, confidence_threshold=self.config.classifier_confidence_threshold)
            except Exception:
                # If classifier fails to instantiate, log and continue without classifier
                import logging
                logging.getLogger(__name__).exception("Failed to initialize classifier service; continuing without classifier")

        # Initialize chatbot with all dependencies
        self.chatbot = MathTutorChatbot(
            config=self.config,
            ollama_client=self.ollama_client,
            tools=self.tools,
            classifier_service=self.classifier_service
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

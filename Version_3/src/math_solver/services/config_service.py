"""
Configuration service for displaying chatbot settings.
"""

from typing import Optional

from math_solver.config import ChatConfig
from math_solver.services.chatbot_service import ChatbotService


class ConfigService:
    """Service for handling configuration display."""

    def __init__(self, chatbot_service: ChatbotService) -> None:
        """Initialize config service with chatbot service dependency."""
        self.chatbot_service = chatbot_service

    def get_config_display(self) -> str:
        """Get formatted configuration display."""
        config = self.chatbot_service.get_config()

        config_info = f"""
**Model-Einstellungen:**
- Modell: {config.model_name}
- Ollama URL: {config.ollama_base_url}
- Temperatur: {config.temperature}
- Max Tokens: {config.max_tokens}

**Datenschutzeinstellungen:**
- Telemetrie deaktiviert: {config.disable_telemetry}
- Do Not Track: {config.do_not_track}
"""
        return config_info

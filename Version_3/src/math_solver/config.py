"""
Configuration classes for the math solver chatbot.
"""

import os
from dataclasses import dataclass


@dataclass
class ChatConfig:
    """Configuration for the chat session."""
    model_name: str = os.getenv("MODEL_NAME", "llama3.2:latest")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    temperature: float = float(os.getenv("TEMPERATURE", "0.2"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "2048"))
    disable_telemetry: bool = os.getenv("DISABLE_TELEMETRY", "true").lower() == "true"
    do_not_track: bool = os.getenv("DO_NOT_TRACK", "1") == "1"

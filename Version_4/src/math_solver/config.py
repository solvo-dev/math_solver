"""
Configuration classes for the math solver chatbot.
"""

import os
from dataclasses import dataclass


@dataclass
class ChatConfig:
    """Configuration for the chat session."""
    model_name: str = os.getenv("MODEL_NAME", "gemma3:1b")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    temperature: float = float(os.getenv("TEMPERATURE", "0.2"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "2048"))
    disable_telemetry: bool = os.getenv("DISABLE_TELEMETRY", "true").lower() == "true"
    do_not_track: bool = os.getenv("DO_NOT_TRACK", "1") == "1"
    # Default language for the UI and assistant responses. Use ISO language codes, e.g. 'de' for German.
    language: str = os.getenv("LANGUAGE", "de")
    # Classifier options (opt-in to keep behavior non-invasive)
    enable_classifier: bool = True#os.getenv("ENABLE_CLASSIFIER", "false").lower() == "true"
    classifier_model_path: str = os.getenv("CLASSIFIER_MODEL_PATH", "models/classifier")
    classifier_confidence_threshold: float = float(os.getenv("CLASSIFIER_CONFIDENCE_THRESHOLD", "0.5"))

"""Classifier tool adapter for the chatbot tools registry.

Implements the `MathTool` interface so the classifier can be invoked like other tools.
"""
from __future__ import annotations

from typing import Optional
from math_solver.tools.base import MathTool
from math_solver.services.classifier_service import ClassifierService
import json


class ClassifierTool(MathTool):
    """Tool adapter to expose classification as a tool.

    The tool returns a JSON string with 'category', 'confidence', and 'reasoning' fields.
    """

    def __init__(self, classifier_service: ClassifierService, confidence_threshold: float = 0.5) -> None:
        self._svc = classifier_service
        self._threshold = float(confidence_threshold)

    @property
    def name(self) -> str:
        return "classifier"

    async def execute(self, expression: str) -> Optional[str]:
        # expression here is user input text
        result = self._svc.classify(expression)
        # Optionally apply threshold logic
        if result["confidence"] < self._threshold:
            result["reasoning"] += " (confidence below threshold)"
        return json.dumps(result, ensure_ascii=False)

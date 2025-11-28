"""
Math Tutor Chatbot - Core chatbot logic with Ollama integration
"""

import asyncio
import logging
import os
from typing import AsyncGenerator, Dict, List, Optional, Any

from typing import Dict

from math_solver.config import ChatConfig
from math_solver.models import ChatMessage
from math_solver.ollama_client import OllamaClient
from math_solver.tool_detector import is_basic_arithmetic, should_use_sympy, detect_basic_arithmetic, detect_math_expression
from math_solver.tools import ArithmeticTool, SymPyTool, NumericTool, MathTool
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




class MathTutorChatbot:
    """Main chatbot class with conversation management and tool routing."""

    def __init__(
        self,
        config: Optional[ChatConfig] = None,
        ollama_client: Optional[OllamaClient] = None,
        tools: Optional[Dict[str, MathTool]] = None
    ) -> None:
        self.config = config or ChatConfig()

        # Set telemetry preferences from config
        if self.config.disable_telemetry:
            os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
        if self.config.do_not_track:
            os.environ.setdefault("DO_NOT_TRACK", "1")

        # Dependency injection
        self.ollama_client = ollama_client or OllamaClient(
            base_url=self.config.ollama_base_url,
            timeout=60.0  # Longer timeout for math problems
        )

        # Tool registry with strategy pattern
        self.tools = tools or {
            "basic_arithmetic": ArithmeticTool(),
            "sympy": SymPyTool(),
            "numeric": NumericTool()
        }

        self.conversation: List[ChatMessage] = []
        self._system_prompt = self._build_system_prompt()
        # Load persisted corrections (user-taught fixes)
        self.corrections_file = Path.cwd() / "math_corrections.json"
        self.corrections: List[Dict[str, str]] = []
        self._load_corrections()

    async def close(self):
        """Close the Ollama client and clean up resources."""
        await self.ollama_client.close()


    def _build_system_prompt(self) -> str:
        """Build the system prompt for the math tutor persona."""
        # Build a German system prompt by default; the language can be changed via ChatConfig.language
        lang = getattr(self.config, "language", "de")
        if lang and lang.startswith("de"):
            return """Du bist ein hilfreicher Mathe-Tutor. Deine Aufgabe ist es, Schülerinnen und Schülern beim Lösen mathematischer Probleme mit klaren, schrittweisen Erklärungen zu helfen.

KERNPRINZIPIEN:
- Du MUSST immer Schritt für Schritt erklären. Gib NIEMALS eine Antwort ohne Rechenweg
- Du bist ein Mathe-Experte. Löse jede Aufgabe Schritt für Schritt.
- Erkläre erst den Rechenweg verständlich und sauber, dann die Lösung. Rate nie. Wenn Zahlen unklar sind, frage nach
- Zeige klare, prägnante Schritt-für-Schritt-Begründungen für alle mathematischen Schritte
- Bevorzuge exakte mathematische Formen (Brüche, Wurzeln) gegenüber Dezimaldarstellungen, wenn möglich
- Sei ermutigend und geduldig mit Lernenden auf allen Niveaus

TOOL-NUTZUNG:
- Wenn Lernende mathematische Ausdrücke oder Probleme präsentieren, benutze die verfügbaren Tools für genaue Berechnungen
- Für symbolische Mathematik (Algebra, Analysis) verwende das SymPy-Tool, wenn es angebracht ist
- Für numerische Berechnungen mit hoher Präzision verwende das numerische Evaluations-Tool
- Rate nie. Wenn Zahlen unklar sind, frage nach

ANTWORTFORMAT:
- Strukturiere deine Antworten mit klaren Schritten und Erklärungen
- Wenn du Tools verwendest, zeige deine Arbeit deutlich und führe an, welche Tools benutzt wurden
- Konzentriere dich darauf, Lernenden das Verständnis mathematischer Konzepte zu erleichtern

BEISPIELE:
- Wenn ein Schüler fragt: "Wie löse ich 25% von 250", antworte mit einer schrittweisen Erklärung:
1. Als erstes musst du berechnen wieviel 1% von 250 ist, also dividierst du zuerst 250 ÷ 100 = 2,5
2. Dann multiplizierst du 2,5 mit 25, also 2,5 × 25 = 62,5
- Wenn ein Schüler fragt: "Was ist 1/4 in Dezimalzahl?", antworte mit:
1. Um 1/4 in eine Dezimalzahl umzuwandeln, multiplizierst du 4 bis du auf eine 10tel eine 100stell oder 1000stell kommst. Also 4 × 25 = 100
2. Wenn du denn Nenner multipliziert hast, musst du auch den Zähler mit der gleichen Zahl multiplizieren. Also 1 × 25 = 25= 25/100
3. Da der Nenner jetzt 100 ist, kannst du den Bruch als Dezimalzahl auch als 100stell schreiben: 25/100 = 0,25

WICHTIG: Antworte immer auf Deutsch, auch der Chatverlauf soll auf deutsch sein, unabhängig von der Spracheingabe des Nutzers, es sei denn, die Konfiguration fordert ausdrücklich eine andere Sprache. Ausser dem musst du immer den rechenweg erklären und schrittweise vorgehen."""
        else:
            # Fallback: English prompt
            return """You are a helpful math tutor. Your role is to help students solve mathematical problems with clear, step-by-step explanations.

Remember: Your goal is to help students solve math problems effectively."""

    def add_message(self, role: str, content: str, **kwargs) -> None:
        """Add a message to the conversation history."""
        message = ChatMessage(role=role, content=content, **kwargs)
        self.conversation.append(message)

    # --- Correction memory API ---
    def _load_corrections(self) -> None:
        try:
            if self.corrections_file.exists():
                with self.corrections_file.open("r", encoding="utf-8") as f:
                    self.corrections = json.load(f)
        except Exception:
            # If loading fails, start with empty corrections
            self.corrections = []

    def _save_corrections(self) -> None:
        try:
            with self.corrections_file.open("w", encoding="utf-8") as f:
                json.dump(self.corrections, f, ensure_ascii=False, indent=2)
        except Exception:
            logger.exception("Fehler beim Speichern der Korrekturen")

    def add_correction(self, pattern: Optional[str], correction: str, explanation: Optional[str] = None) -> None:
        """Store a user-provided correction.

        - pattern: optional short text or excerpt that identifies when the correction applies
        - correction: the corrected solution/explanation
        - explanation: optional meta-info
        """
        entry = {
            "pattern": pattern if pattern else "",
            "correction": correction,
            "explanation": explanation or "",
        }
        # Prepend so recent corrections have priority
        self.corrections.insert(0, entry)
        self._save_corrections()

    def find_applicable_correction(self, text: str) -> Optional[Dict[str, str]]:
        """Return the first correction whose pattern is contained in text (if pattern present)."""
        for c in self.corrections:
            pat = c.get("pattern", "")
            if not pat:
                # generic correction without pattern applies to many cases; skip automatic application
                continue
            try:
                if pat.lower() in text.lower():
                    return c
            except Exception:
                continue
        return None

    def clear_conversation(self) -> None:
        """Clear the conversation history but keep the system prompt."""
        self.conversation = []

    def get_messages_for_ollama(self) -> List[Dict[str, Any]]:
        """Convert conversation history to Ollama message format."""
        messages = [{"role": "system", "content": self._system_prompt}]

        for msg in self.conversation:
            ollama_msg = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                ollama_msg["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                ollama_msg["tool_call_id"] = msg.tool_call_id
            messages.append(ollama_msg)

        return messages

    async def generate_response(self, user_input: str) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response to user input.

        This is the main entry point for getting chatbot responses.
        """
        # Add user message to conversation
        self.add_message("user", user_input)

        # Get messages for Ollama
        messages = self.get_messages_for_ollama()

        # Stream response from Ollama
        full_response = ""
        try:
            async for chunk in self.ollama_client.chat_stream(
                messages=messages,
                model=self.config.model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            ):
                full_response += chunk
                yield chunk
        except Exception as e:
            logger.error(f"Ollama client error: {type(e).__name__}: {e}")
            # Don't re-raise here, let the caller handle it
            yield f"Error: {str(e)}"

        # Add assistant response to conversation
        self.add_message("assistant", full_response)

    def _detect_tool_intent(self, user_input: str) -> Optional[str]:
        """
        Detect which tool should be used based on user input.

        Priority order: basic_arithmetic > sympy > numeric

        Returns tool name or None if no tool is needed.
        """
        # Check for basic arithmetic first (highest priority)
        if is_basic_arithmetic(user_input):
            return "basic_arithmetic"

        # Check for math expressions that need SymPy
        math_expr = detect_math_expression(user_input)
        if math_expr and should_use_sympy(user_input):
            return "sympy"

        # Check for numeric evaluation (fallback for complex numbers)
        if math_expr and not should_use_sympy(user_input):
            return "numeric"

        return None

    async def _execute_tool(self, tool_name: str, user_input: str) -> Optional[str]:
        """
        Execute the appropriate tool and return formatted result.

        Returns tool result string or None if tool execution failed.
        """
        try:
            if tool_name not in self.tools:
                logger.warning(f"Unknown tool: {tool_name}")
                return f"Unknown tool: {tool_name}"

            tool = self.tools[tool_name]

            # Extract expression based on tool type
            if tool_name == "basic_arithmetic":
                expr = detect_basic_arithmetic(user_input)
            else:
                expr = detect_math_expression(user_input)

            if expr:
                result = await tool.execute(expr)
                # If a user correction applies to this input or the tool result, prefer annotated correction
                applicable = self.find_applicable_correction(user_input) or self.find_applicable_correction(result or "")
                if applicable:
                    # Return correction text but include original tool result for traceability
                    corr_text = applicable.get("correction", "")
                    combined = f"[Korrektur angewendet] {corr_text}\n\n[Original Ergebnis:]\n{result}"
                    return combined

                return result

        except Exception as e:
            logger.warning(f"Tool execution failed ({tool_name}): {e}")
            return f"Tool Error ({tool_name}): {str(e)}"

        return None

    async def generate_response_with_tools(self, user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate response with automatic tool call detection and execution.

        Yields dicts with 'type': 'chunk'|'tool_call'|'tool_result' and content.
        """
        # Detect if we should use a tool
        tool_name = self._detect_tool_intent(user_input)

        if tool_name:
            # Execute tool and yield result
            tool_result = await self._execute_tool(tool_name, user_input)
            if tool_result:
                yield {"type": "tool_result", "content": tool_result, "tool": tool_name}
                # Add tool result to conversation for context
                self.add_message("assistant", tool_result)
                return

        # No tool needed or tool failed, generate normal response
        async for chunk in self.generate_response(user_input):
            yield {"type": "chunk", "content": chunk}

# Math tool utilities



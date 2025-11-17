"""
Version_2: Minimaler lokaler LLM-Chatbot für Ollama.
- Verwendet die lokale Ollama-HTTP-API statt OpenAI.
- Liest Host, Modell und Timeout aus Umgebungsvariablen (.env via python-dotenv).
- Führt eine einfache Chat-Schleife (REPL) im Terminal aus.
- Kapselt API-Aufrufe in einer kleinen Client-Klasse.

Voraussetzungen:
    pip install -r requirements.txt
    Ollama installiert und Modell gepullt (z.B. `ollama pull llama3.1`).

Starten:
    python chatbot.py
"""
from __future__ import annotations

import os
import sys
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any

import requests
from dotenv import load_dotenv


@dataclass
class Message:
    role: str  # 'system' | 'user' | 'assistant'
    content: str


@dataclass
class LLMChatClient:
    host: str
    model: str = "llama3.1"
    request_timeout: int = 30
    system_prompt: str = "Du bist ein freundlicher, hilfsbereiter deutschsprachiger Assistent."
    messages: List[Message] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.system_prompt:
            self.messages.append(Message(role="system", content=self.system_prompt))

    def _payload(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in self.messages],
            "stream": False,
        }

    def ask(self, user_text: str) -> str:
        self.messages.append(Message(role="user", content=user_text))
        url = self.host.rstrip("/") + "/api/chat"
        try:
            resp = requests.post(url, json=self._payload(), timeout=self.request_timeout)
        except Exception as e:
            return f"Verbindungsfehler zu Ollama: {e}"

        if resp.status_code != 200:
            return f"HTTP {resp.status_code}: {resp.text[:200]}"
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return "Ungültige JSON-Antwort von Ollama."

        msg = data.get("message") or {}
        content = msg.get("content") or "(Keine Antwort erhalten)"
        self.messages.append(Message(role="assistant", content=content))
        return content


def load_config() -> Dict[str, str]:
    load_dotenv()
    host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    model = os.getenv("MODEL", "gemma3:1b")
    timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
    return {"host": host, "model": model, "timeout": timeout}


def main() -> None:
    cfg = load_config()
    bot = LLMChatClient(host=cfg["host"], model=cfg["model"], request_timeout=cfg["timeout"]) 

    print("Ollama-Chat gestartet. Tippe 'exit' oder 'quit' zum Beenden.\n")
    while True:
        try:
            user_text = input("Du: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_text or user_text.lower() in {"exit", "quit"}:
            break
        answer = bot.ask(user_text)
        print(f"Assistent: {answer}\n")


if __name__ == "__main__":
    main()

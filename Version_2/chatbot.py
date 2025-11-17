"""
Version_2: Minimaler LLM-Chatbot in Python mit der openai-Bibliothek.
- Liest API-Key und Modell aus Umgebungsvariablen (.env via python-dotenv)
- Führt eine einfache Chat-Schleife im Terminal aus
- Kapselt API-Aufrufe in einer kleinen Client-Klasse

Voraussetzungen:
    pip install -r requirements.txt

Starten:
    python chatbot.py
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import List, Dict

from dotenv import load_dotenv

try:
    from openai import OpenAI  # type: ignore
except Exception:
    print("Fehlende Abhängigkeit: Bitte 'pip install -r requirements.txt' ausführen.")
    raise


@dataclass
class Message:
    role: str  # 'system' | 'user' | 'assistant'
    content: str


@dataclass
class LLMChatClient:
    api_key: str
    model: str = "gpt-5"
    request_timeout: int = 30
    system_prompt: str = (
        "Du bist ein freundlicher, hilfsbereiter deutschsprachiger Assistent."
    )
    messages: List[Message] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.client = OpenAI(api_key=self.api_key)
        if self.system_prompt:
            self.messages.append(Message(role="system", content=self.system_prompt))

    def ask(self, user_text: str) -> str:
        self.messages.append(Message(role="user", content=user_text))
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[m.__dict__ for m in self.messages],
                temperature=0.7,
                max_tokens=400,
                timeout=self.request_timeout,
            )
        except Exception as e:
            return f"Fehler beim Anfragen des Modells: {e}"

        choice = (resp.choices or [None])[0]
        if not choice or not getattr(choice, "message", None):
            return "Keine Antwort vom Modell erhalten."
        answer = choice.message.content or ""
        self.messages.append(Message(role="assistant", content=answer))
        return answer


def load_config() -> Dict[str, str]:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        print("OPENAI_API_KEY fehlt. Bitte in .env setzen.")
        sys.exit(1)
    model = os.getenv("MODEL", "gpt-5")
    timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
    return {"api_key": api_key, "model": model, "timeout": timeout}


def main() -> None:
    cfg = load_config()
    bot = LLMChatClient(api_key=cfg["api_key"], model=cfg["model"], request_timeout=cfg["timeout"]) 

    print("LLM-Chat gestartet. Tippe 'exit' oder 'quit' zum Beenden.\n")
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

"""Minimal Gradio UI demo for Version 5 (no backend logic)."""

from __future__ import annotations

from datetime import datetime
from typing import List

import gradio as gr


# -- Minimal helpers --
def format_badges() -> str:
    """Return small placeholder badges to mimic Version 4 look."""
    return (
        "\n\n🏷️ **Kategorie erkannt:** 📊 **Beispiel-Kategorie** (Konfidenz: 0.50)\n\n"
        "\n\n💡 **[INFO]** Dies ist ein Platzhalter-Hinweis.\n\n"
    )


def handle_message(message: str, history: List[List[str]]) -> str:
    """Echo-style handler with static badges; no model calls."""
    if not message.strip():
        return ""

    lowered = message.strip().lower()
    if lowered.startswith("korrektur:") or lowered.startswith("korrigiere:"):
        return "Danke — Korrektur notiert (nur Demo, keine Speicherung)."

    return (
        format_badges()
        + "Dies ist eine UI-Demonstration ohne angebundenes Modell. "
        "Gib beliebige mathematische Aufgaben ein; die Antworten bleiben statisch.\n\n"
        + f"**Echo:** {message}"
    )


def config_markdown() -> str:
    """Static config panel text with timestamp."""
    refreshed = datetime.now().strftime("%H:%M:%S")
    return f"""
**Modell-Einstellungen:**
- Modus: UI-Demo (kein Modell verbunden)
- Antwortsprache: Deutsch
- Streaming: deaktiviert

**Hinweis:**
- Diese Version zeigt nur die Oberfläche ohne LLM-Logik.
- Badges sind statisch.
- Zuletzt aktualisiert: {refreshed}
"""


def build_interface() -> gr.Blocks:
    """Minimal two-column layout similar to Version 4."""
    with gr.Blocks(title="Mathe-Löser UI-Demo", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🧮 Mathe-Löser – UI-Demo")
        gr.Markdown(
            "*Stelle mir mathematische Aufgaben oder Fragen — die Oberfläche reagiert, "
            "aber es ist kein Modell angebunden.*"
        )

        with gr.Row():
            with gr.Column(scale=2):
                gr.ChatInterface(
                    fn=handle_message,
                    chatbot=gr.Chatbot(height=420),
                    textbox=gr.Textbox(
                        placeholder="Frage auf Deutsch stellen…",
                        label="Deine Frage",
                    ),
                    submit_btn="Senden",
                    examples=[
                        "Löse 3x + 7 = 22",
                        "Berechne die Ableitung von x^2 + 3x",
                        "Fläche eines Kreises mit Radius 5",
                    ],
                )

            with gr.Column(scale=1):
                gr.Markdown("### Aktuelle Einstellungen")
                config_display = gr.Markdown(value=config_markdown())
                refresh_btn = gr.Button("🔄 Einstellungen aktualisieren", size="sm")

        refresh_btn.click(fn=config_markdown, outputs=config_display)

    return demo


if __name__ == "__main__":
    app = build_interface()
    app.launch(server_name="localhost", server_port=7860)

"""Minimal Gradio UI demo for Version 5 (no backend logic)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

import gradio as gr

from service.classifier_service import ClassifierService


# -- Initialize classifier --
MODEL_DIR = Path(__file__).parent.parent / "models" / "classifier"
TEST_DATA_PATH = Path(__file__).parent.parent / "models" / "data" / "train-00000-of-00001.json"
PROMPT_TEMPLATE_PATH = Path(__file__).parent.parent / "models" / "math_solver_prompt_v1.md"
classifier = None

try:
    classifier = ClassifierService.from_pretrained(MODEL_DIR)
    print(f"✓ Classifier loaded from {MODEL_DIR}")
    
    # Load test set for similarity search
    if TEST_DATA_PATH.exists():
        classifier.load_test_set(TEST_DATA_PATH, max_samples=1000)
        print(f"✓ Test set loaded for similarity search")
    else:
        print(f"⚠ Test data not found at {TEST_DATA_PATH}")
except Exception as e:
    print(f"⚠ Classifier could not be loaded: {e}")


def handle_message(message: str, history: List[List[str]]) -> str:
    """Handler that creates a prompt based on similar problems from test set."""
    if not message.strip():
        return ""

    lowered = message.strip().lower()
    if lowered.startswith("korrektur:") or lowered.startswith("korrigiere:"):
        return "Danke — Korrektur notiert (nur Demo, keine Speicherung)."

    # Load prompt template
    try:
        with open(PROMPT_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    except Exception as e:
        return f"⚠️ Fehler beim Laden des Prompt-Templates: {e}"
    
    if classifier:
        try:
            # Find most similar question (top_k=1)
            similar = classifier.find_similar(message, top_k=1)
            if similar:
                most_similar = similar[0]
                
                # Replace placeholders in template
                filled_prompt = prompt_template.replace("{Problem}", most_similar['problem'])
                filled_prompt = filled_prompt.replace("{rational}", most_similar.get('rationale', 'Keine Rationale verfügbar'))
                filled_prompt = filled_prompt.replace("{correct}", most_similar.get('correct', 'Keine Antwort verfügbar'))
                filled_prompt = filled_prompt.replace("{input}", message)
                
                # Add similarity info at the top
                similarity_info = f"**🔍 Ähnlichkeit zum Beispiel: {most_similar['similarity']*100:.2f}%**\n\n---\n\n"
                
                return similarity_info + filled_prompt
            else:
                return f"⚠️ Keine ähnlichen Probleme gefunden.\n\n**Deine Eingabe:** {message}"
        except Exception as e:
            return f"⚠️ Ähnlichkeitssuche-Fehler: {e}\n\n**Deine Eingabe:** {message}"
    
    return f"⚠️ Classifier nicht verfügbar.\n\n**Deine Eingabe:** {message}"


def config_markdown() -> str:
    """Static config panel text with timestamp."""
    refreshed = datetime.now().strftime("%H:%M:%S")
    similar_status = "✓ Aktiviert" if (classifier and classifier._test_embeddings is not None) else "✗ Nicht verfügbar"
    
    return f"""
**Modell-Einstellungen:**
- Modus: Ähnlichkeitssuche
- Ähnlichkeitssuche: {similar_status}
- Antwortsprache: Deutsch

**Hinweis:**
- Diese Version findet ähnliche Probleme aus dem Testdatensatz.
- Die ähnlichsten Probleme werden mit Ähnlichkeitswert angezeigt.
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

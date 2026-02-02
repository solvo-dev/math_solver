"""Minimal Gradio UI demo for Version 5 (no backend logic)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

import gradio as gr
import tkinter as tk

from service.classifier_service import ClassifierService
from service.ollama_service import OllamaService


# Allow both inline ($...$) and block ($$...$$) LaTeX rendering
LATEX_DELIMITERS = [
    {"left": "$$", "right": "$$", "display": True},
    {"left": "$", "right": "$", "display": False},
]


# -- Initialize classifier --
MODEL_DIR = Path(__file__).parent.parent / "models" / "classifier"
TEST_DATA_PATH = Path(__file__).parent.parent / "models" / "data" / "train-00000-of-00001.json"
PROMPT_TEMPLATE_PATH = Path(__file__).parent.parent / "models" / "math_solver_prompt_v1.md"
classifier = None
ollama_service = None

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


# -- Initialize Ollama service --
try:
    ollama_service = OllamaService(
        base_url="http://localhost:11434",
        model="qwen3:0.6b",
        prompt_template_path=PROMPT_TEMPLATE_PATH,
    )
    print(f"✓ Ollama service initialized (model: qwen3:0.6b)")
except Exception as e:
    print(f"⚠ Ollama service could not be initialized: {e}")


def handle_message(message: str, history: List[List[str]]) -> str:
    """Handler that creates a prompt and uses Ollama to solve."""
    if not message.strip():
        return ""

    lowered = message.strip().lower()
    if lowered.startswith("korrektur:") or lowered.startswith("korrigiere:"):
        return "Danke — Korrektur notiert (nur Demo, keine Speicherung)."
    
    if not classifier:
        return "⚠️ Classifier nicht verfügbar."
    
    try:
        # Find most similar question (top_k=1)
        similar = classifier.find_similar(message, top_k=1)
        if not similar:
            return f"⚠️ Keine ähnlichen Probleme gefunden.\n\n**Deine Eingabe:** {message}"
        
        most_similar = similar[0]
        # similarity_info = f"**🔍 Ähnlichkeit zum Beispiel: {most_similar['similarity']*100:.2f}%**\n\n"
        
        # If Ollama is available, use it to solve
        if ollama_service:
            try:
                response = ollama_service.solve_math_problem(
                    user_input=message,
                    problem=most_similar['problem'],
                    rationale=most_similar.get('rationale', 'Keine Rationale verfügbar'),
                    correct=most_similar.get('correct', 'Keine Antwort verfügbar'),
                    temperature=0.7,
                    num_predict=500,
                )
                return response
            except Exception as e:
                # Fallback: show prompt without Ollama solution
                with open(PROMPT_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
                    template = f.read()
                
                filled_prompt = template.replace("{Problem}", most_similar['problem'])
                filled_prompt = filled_prompt.replace("{rational}", most_similar.get('rationale', 'Keine Rationale verfügbar'))
                filled_prompt = filled_prompt.replace("{correct}", most_similar.get('correct', 'Keine Antwort verfügbar'))
                filled_prompt = filled_prompt.replace("{input}", message)
                
                return (
                    similarity_info + 
                    f"⚠️ Ollama nicht verfügbar: {e}\n\n---\n\n" +
                    f"**Erstellter Prompt (ohne Ollama-Lösung):**\n\n{filled_prompt}"
                )
        else:
            # Fallback: show prompt without Ollama
            with open(PROMPT_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
                template = f.read()
            
            filled_prompt = template.replace("{Problem}", most_similar['problem'])
            filled_prompt = filled_prompt.replace("{rational}", most_similar.get('rationale', 'Keine Rationale verfügbar'))
            filled_prompt = filled_prompt.replace("{correct}", most_similar.get('correct', 'Keine Antwort verfügbar'))
            filled_prompt = filled_prompt.replace("{input}", message)
            
            return (
                similarity_info + 
                "⚠️ Ollama Service nicht konfiguriert.\n\n---\n\n" +
                f"**Erstellter Prompt:**\n\n{filled_prompt}"
            )
    
    except Exception as e:
        return f"⚠️ Fehler: {e}"


def config_markdown() -> str:
    """Static config panel text with timestamp."""
    refreshed = datetime.now().strftime("%H:%M:%S")
    similar_status = "✓ Aktiviert" if (classifier and classifier._test_embeddings is not None) else "✗ Nicht verfügbar"
    ollama_status = "✓ Verbunden" if ollama_service else "✗ Nicht verfügbar"
    
    return f"""
**Modell-Einstellungen:**
- Ähnlichkeitssuche: {similar_status}
- Ollama Service: {ollama_status}
- Antwortsprache: Deutsch

**Hinweis:**
- Die App findet ähnliche Probleme aus dem Testdatensatz.
- Der Prompt wird mit den ähnlichsten Beispielen gefüllt.
- Wenn Ollama verfügbar ist, wird eine Lösung generiert.
- Zuletzt aktualisiert: {refreshed}
"""


def build_interface() -> gr.Blocks:
    """Minimal two-column layout similar to Version 4."""
    with gr.Blocks(title="Mathe-Löser UI-Demo", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🧮 Mathe-Löser – UI-Demo", latex_delimiters=LATEX_DELIMITERS)
        gr.Markdown(
            "*Stelle mir mathematische Aufgaben oder Fragen — die Oberfläche reagiert, "
            "aber es ist kein Modell angebunden.*",
            latex_delimiters=LATEX_DELIMITERS,
        )

        with gr.Row():
            with gr.Column(scale=2):
                gr.ChatInterface(
                    fn=handle_message,
                    chatbot=gr.Chatbot(height=420, latex_delimiters=LATEX_DELIMITERS),
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
                config_display = gr.Markdown(value=config_markdown(), latex_delimiters=LATEX_DELIMITERS)
                refresh_btn = gr.Button("🔄 Einstellungen aktualisieren", size="sm")

        refresh_btn.click(fn=config_markdown, outputs=config_display)

    return demo


# Increase the size of the input window
input_window = tk.Tk()
input_window.geometry('3840x2000')  # Larger default size (even more height)
try:
    input_window.state('zoomed')  # Maximize on launch where supported (e.g., Windows)
except tk.TclError:
    pass


if __name__ == "__main__":
    app = build_interface()
    app.launch(server_name="localhost", server_port=7860)

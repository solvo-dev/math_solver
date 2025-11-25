# Math Solver Version 3: Erklärung und Dokumentation

## Überblick

Version 3 ist eine erweiterte Python-Anwendung, die einen lokalen Math Solver mit Weboberfläche implementiert. Sie kombiniert Ollama für KI-gestützte Erklärungen mit mathematischen Bibliotheken (SymPy, mpmath) für präzise Berechnungen. Alles läuft lokal ohne externe APIs, mit Fokus auf Datenschutz und Genauigkeit.

Das Projekt basiert auf Gradio für die Benutzeroberfläche und verwendet eine modulare Architektur mit Dependency Injection für Wartbarkeit.

## Architektur

Die Anwendung ist in folgende Hauptmodule unterteilt:

- **[`Version_2/main.py`](Version_2/main.py )**: Einstiegspunkt, initialisiert Services und startet die Gradio-UI.
- **[`Version_2/chatbot.py`](Version_2/chatbot.py )**: Kernlogik des Chatbots mit Tool-Integration und Konversationsmanagement.
- **[`Version_3/src/math_solver/ollama_client.py`](Version_3/src/math_solver/ollama_client.py )**: HTTP-Client für Streaming-Kommunikation mit Ollama.
- **[`Version_3/src/math_solver/math_evaluators.py`](Version_3/src/math_solver/math_evaluators.py )**: Sichere Evaluierung mathematischer Ausdrücke mit SymPy und mpmath.
- **[`Version_3/src/math_solver/tool_detector.py`](Version_3/src/math_solver/tool_detector.py )**: Erkennung mathematischer Ausdrücke und Zuweisung zu Tools.
- **[`Version_3/src/math_solver/config.py`](Version_3/src/math_solver/config.py )**: Konfiguration aus Umgebungsvariablen.
- **[`Version_3/src/math_solver/models.py`](Version_3/src/math_solver/models.py )**: Datenmodelle für Nachrichten.
- **[`Version_3/src/math_solver/exceptions.py`](Version_3/src/math_solver/exceptions.py )**: Benutzerdefinierte Ausnahmen.
- **[`Version_3/src/math_solver/utils.py`](Version_3/src/math_solver/utils.py )**: Hilfsfunktionen (z.B. Timeout-Kontext).

### Services-Schicht
- **[`Version_3/src/math_solver/services/chatbot_service.py`](Version_3/src/math_solver/services/chatbot_service.py )**: Verwaltet Chatbot-Lebenszyklus und Abhängigkeiten.
- **[`Version_3/src/math_solver/services/config_service.py`](Version_3/src/math_solver/services/config_service.py )**: Zeigt Konfiguration in der UI an.

### Tools-Schicht
- **[`Version_3/src/math_solver/tools/base.py`](Version_3/src/math_solver/tools/base.py )**: Abstrakte Basisklasse für Math-Tools.
- **[`Version_3/src/math_solver/tools/arithmetic_tool.py`](Version_3/src/math_solver/tools/arithmetic_tool.py )**: Einfache Arithmetik (Addition, Subtraktion, etc.).
- **[`Version_3/src/math_solver/tools/sympy_tool.py`](Version_3/src/math_solver/tools/sympy_tool.py )**: Symbolische Mathematik (Gleichungen, Algebra).
- **[`Version_3/src/math_solver/tools/numeric_tool.py`](Version_3/src/math_solver/tools/numeric_tool.py )**: Hochpräzise numerische Berechnungen.

### UI-Schicht
- **[`Version_3/src/math_solver/ui/components.py`](Version_3/src/math_solver/ui/components.py )**: Gradio-Komponenten für die Oberfläche.
- **[`Version_3/src/math_solver/ui/handlers.py`](Version_3/src/math_solver/ui/handlers.py )**: Nachrichtenverarbeitung mit Streaming-Unterstützung.
- **[`Version_3/src/math_solver/ui/formatters.py`](Version_3/src/math_solver/ui/formatters.py )**: Formatierung von Nachrichten und Chat-Verlauf.

## Funktionen

- **Automatische Tool-Erkennung**: Erkennt mathematische Ausdrücke und wählt passende Tools (Basis-Arithmetik, SymPy, numerisch).
- **Streaming-Responses**: Echtzeit-Ausgabe von KI-Antworten.
- **Lokale Berechnungen**: Keine Daten an externe Server; alles läuft lokal.
- **Konfigurierbare UI**: Zeigt aktuelle Einstellungen an und erlaubt Refresh.
- **Fehlerbehandlung**: Robuste Fehlerbehandlung mit Logging und Timeouts.

Beispiele:
- Eingabe: "Was ist 5 + 3?" → Verwendet Arithmetic Tool → Ausgabe: "Result: 8"
- Eingabe: "Löse x² - 5x + 6 = 0" → Verwendet SymPy Tool → Ausgabe mit Lösungen.
- Eingabe: "Berechne √2 mit hoher Präzision" → Verwendet Numeric Tool → Ausgabe mit Approximation.

## Installation und Start

1. **Abhängigkeiten installieren**:
   ```bash
   cd Version_3
   pip install -r requirements.txt
   ```

2. **Ollama installieren und Modell laden**:
   - Ollama von [ollama.ai](https://ollama.ai) herunterladen.
   - Modell pullen: `ollama pull llama3.2:latest`

3. **Konfiguration**: Kopiere [`Version_2/.env.example`](Version_2/.env.example ) zu `.env` und passe an (z.B. Modell, URL).

4. **Starten**:
   ```bash
   python -m math_solver.main
   ```
   Öffnet Web-UI unter http://localhost:7860.

Hinweis zur Sprache:
- Die Anwendung startet standardmäßig auf Deutsch. Dies wird über die Konfiguration `ChatConfig.language` gesteuert (Standard: `de`).
- Wenn du die Sprache ändern möchtest, setze die Umgebungsvariable `LANGUAGE`, z.B.: `set LANGUAGE=en` unter Windows PowerShell vor dem Start.

Korrekturen und Lernen vom Nutzer:
- Du kannst dem Chatbot Korrekturen beibringen, indem du im Chat eine Nachricht mit dem Präfix `Korrektur:` oder `Korrigiere:` sendest.
- Format: `Korrektur: <fehlerauszug> => <korrekte Lösung und ggf. Erklärung>`
   - Beispiel: `Korrektur: Deine Ableitung von x^2 war falsch => Ableitung von x^2 ist 2*x`.
- Der Bot speichert gelernte Korrekturen in `math_corrections.json` im aktuellen Arbeitsverzeichnis und wird sie bei passenden zukünftigen Aufgaben berücksichtigen.
- Hinweise: Korrekturen mit einem spezifischen Muster (`<fehlerauszug>`) werden automatisch angewendet, wenn das Muster in einer Eingabe oder einem Tool-Ergebnis auftaucht. Allgemeine Korrekturen ohne Muster werden gespeichert, aber nicht automatisch angewendet.

## Verwendung

- Öffne die Weboberfläche.
- Gib mathematische Fragen ein (z.B. "Löse 2x + 3 = 7").
- Der Solver erkennt automatisch den Typ und verwendet Tools für Berechnungen.
- KI erklärt Schritt-für-Schritt.

## Technische Details

- **Sprache**: Python 3.13+
- **Abhängigkeiten**: Gradio, httpx, sympy, mpmath, python-dotenv, orjson, rapidfuzz, watchdog.
- **Packaging**: [`Version_2/pyproject.toml`](Version_2/pyproject.toml ) für moderne Python-Pakete; Entry-Point: [`math-solver = math_solver.main:main`](Version_2/chatbot.py ).
- **Sicherheit**: Restricted Eval für Arithmetik; Timeouts verhindern Hängenbleiben.
- **Erweiterbarkeit**: Neue Tools können durch Erben von [`MathTool`](Version_3/src/math_solver/tools/base.py ) hinzugefügt werden.

Für detaillierte API-Dokumentation siehe Docstrings in den Quelldateien. Das Projekt ist modular aufgebaut, um einfache Tests und Erweiterungen zu ermöglichen.
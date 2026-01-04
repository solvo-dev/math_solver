# Version 5 – UI-Demo

Gradio-basierte Chat-Oberfläche, die die Optik aus Version 4 nachbildet, jedoch ohne angebundene LLM-/Tool-Logik.

## Starten
1. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
2. App starten:
   ```bash
   python main.py
   ```
3. Öffne den angezeigten Link (Standard: http://127.0.0.1:7860).

## Hinweise
- Die Oberfläche zeigt statische Platzhalterantworten und synthetische Badges, um das Erscheinungsbild aus Version 4 zu demonstrieren.
- Das rechte Panel zeigt Demo-Einstellungen; der Aktualisieren-Button erneuert lediglich den Zeitstempel.
- Spätere Integration von Modell- oder Tool-Logik kann direkt an `MessageHandler.handle_message` erfolgen.

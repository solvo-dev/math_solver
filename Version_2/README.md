# Version_2 LLM Chatbot (Python)

Ein minimaler, gut strukturierter Chat-Client für ein Large Language Model (z. B. GPT-5) unter Verwendung der `openai`-Bibliothek.

## 1. Funktionsbeschreibung

Das Programm stellt eine einfache Chat-Schleife zur Verfügung:
- Liest Benutzereingaben aus dem Terminal.
- Sendet den bisherigen Dialog-Verlauf als Nachrichtenliste an die OpenAI API.
- Erhält eine Antwort vom Modell und zeigt sie an.
- Beendet sich bei Eingaben wie `exit`, `quit` oder leerer Zeile.

Es kapselt die API-Kommunikation in einer Klasse `LLMChatClient`, damit die Logik leicht erweiterbar ist (z. B. Logging, Caching, Conversation IDs).

## 2. Dateien

- `chatbot.py` – Python-Chatclient (Terminal)
- `.env.example` – Beispiel für Umgebungsvariablen
- `requirements.txt` – Abhängigkeiten (openai, python-dotenv)

## 3. API-Key Verwaltung (.env)

1. Erstelle eine Datei `.env` im gleichen Ordner wie `chatbot.py`.
2. Füge darin deinen API-Key ein:

```
OPENAI_API_KEY=sk-xxxx...
MODEL=gpt-5
REQUEST_TIMEOUT=30
```

3. Füge `.env` in deine `.gitignore` ein (oder nutze sie projektweit), damit der Schlüssel nicht ins Git-Repository gelangt.
4. Lade niemals echte Keys in öffentliche Repos oder Screenshots hoch.
5. Für Deployment (Server / CI) setze die Umgebungsvariablen direkt im Hosting-Panel (z. B. Azure, AWS, Render) statt eine `.env` hochzuladen.
6. Rotierte Keys regelmäßig und nutze ggf. separate Keys für Entwicklung und Produktion.

## 4. Installation & Start (Windows PowerShell)

```powershell
# In den Projektordner wechseln
cd Version_2

# Virtuelle Umgebung anlegen und aktivieren
python -m venv .venv
.venv\Scripts\Activate.ps1

# Abhängigkeiten installieren
pip install --upgrade pip
pip install -r requirements.txt

# .env nach Vorlage anlegen und OPENAI_API_KEY eintragen
# (Datei .env neben chatbot.py erstellen)

# Chatbot starten
python chatbot.py
```

Beispielinteraktion:

```
Du: Hallo, was kannst du?
Assistent: Ich kann dir bei Fragen helfen und Informationen bereitstellen.
Du: Erkläre mir kurz den Unterschied zwischen Liste und Tuple in Python.
Assistent: ...
```

Beenden mit `exit` oder `quit`.

## 5. Erweiterungs-Ideen
- Automatisches Logging der Gespräche in einer Datei
- Tokenzählung / Kostenabschätzung
- Mehrere Rollen (Systemprompt dynamisch anpassbar)
- Streaming-Ausgabe für längere Antworten
- Caching letzter Antworten

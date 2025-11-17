# Version_2 LLM Chatbot (Python, Ollama)

Ein minimaler, gut strukturierter Chat-Client für ein lokal laufendes Large Language Model über die Ollama-HTTP-API.

## 1. Funktionsbeschreibung

Das Programm stellt eine einfache Chat-Schleife zur Verfügung:
- Liest Benutzereingaben aus dem Terminal.
- Sendet den bisherigen Dialog-Verlauf als Nachrichtenliste an die lokale Ollama-Instanz.
- Erhält eine Antwort vom Modell und zeigt sie an.
- Beendet sich bei Eingaben wie `exit`, `quit` oder leerer Zeile.

Die Klasse `LLMChatClient` kapselt die Kommunikation, so dass du leicht erweitern kannst (Logging, Streaming, Caching, Systemprompt-Anpassung).

## 2. Dateien

- `chatbot.py` – Python-Chatclient (Terminal)
- `.env.example` – Beispiel für Umgebungsvariablen (Host, Modell, Timeout)
- `requirements.txt` – Abhängigkeiten (`requests`, `python-dotenv`)

## 3. Umgebungsvariablen (.env)

Erstelle eine Datei `.env` neben `chatbot.py` und passe Werte an:

```
OLLAMA_HOST=http://127.0.0.1:11434
MODEL=llama3.1
REQUEST_TIMEOUT=30
```

Kein API-Key notwendig, da Ollama lokal läuft. Für Remote-/Container-Setups kannst du den Host anpassen.

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

# Ollama installieren (falls nicht vorhanden)
# Siehe: https://ollama.com/download
# Modell laden (Beispiel llama3.1)
ollama pull llama3.1

# .env nach Vorlage anlegen/anpassen
Copy-Item .env.example .env

# Chatbot starten
python chatbot.py
```

Beispielinteraktion:

```
Du: Hallo, was kannst du?
Assistent: Ich helfe dir gerne bei Fragen rund um Programmierung.
Du: Erkläre Unterschied zwischen Liste und Tuple in Python.
Assistent: ...
```

Beenden mit `exit` oder `quit`.

## 5. Fehlerbehebung
- Fehlermeldung "Verbindungsfehler": Prüfe ob Ollama Dienst läuft (`ollama list`).
- HTTP 404: Falscher Host oder Modellname nicht gepullt.
- Sehr langsame Antworten: Timeout erhöhen (`REQUEST_TIMEOUT=60`).

## 6. Erweiterungs-Ideen
- Logging der Dialoge in einer Datei
- Streaming-Ausgabe (Teilantworten) für lange Antworten
- Systemprompt dynamisch ändern im Lauf
- Mehrere getrennte Sitzungen / Profile
- Einfache Web- oder GUI-Oberfläche

Viel Spaß beim lokalen Ausprobieren!

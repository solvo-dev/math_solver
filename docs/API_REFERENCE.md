# Project API & Component Reference

Dieses Dokument beschreibt alle öffentlich nutzbaren Komponenten, Funktionen und Schnittstellen beider Versionen des Projekts. Nutze es als Referenz, um Features zu erweitern, in andere Anwendungen einzubetten oder automatisierte Tests zu erstellen.

---

## Version_1 – Webbasierter Mathe-Chatbot

### Einstieg & Aufbau
- **Einstiegspunkt**: `Version_1/index.html`
- **UI-Komponenten**
  - `main.chat` (`#chat`): Container für Nachrichtenverlauf, dient zugleich als `aria-live`-Region.
  - `form#composer`: Enthält Textfeld (`#userInput`) sowie Buttons für Spracheingabe (`#micBtn`), Text-To-Speech (`#ttsBtn`) und Submit (`.composer__send`).
  - Öffnen der `index.html` im Browser startet die Anwendung direkt (keine Build-Schritte notwendig).

### JavaScript-Modul `Version_1/scrypt.js`
Das Script ist als IIFE gekapselt, alle Funktionen können jedoch problemlos extrahiert werden, falls du sie von außen importieren möchtest. Folgende „öffentlichen“ Funktionen/Komponenten stehen zur Verfügung:

#### `appendMessage(role: "user" | "bot", text: string) -> void`
- Rendert eine Chat-Nachricht inklusive Avatar in den DOM-Container `#chat`.
- Scrollt den Chat an das Ende und stößt optional TTS-Ausgabe an, falls `role === "bot"` und TTS aktiviert ist.
- **Beispiel**:
  ```javascript
  // Eigene Systemnachricht anzeigen
  appendMessage("bot", "Willkommen im erweiterten Modus!");
  ```

#### `solve(text: string) -> { ok: true, a, b, op, result, usedComma } | { ok: false, error }`
- Parsen und Berechnen von Grundrechenarten in deutscher Sprache.
- Unterstützte Eingabeformen:
  - Symbolisch: `3 + 4`, `10-7`, `6×5`, `8/2`
  - Verbalisierte Befehle: `addiere 3 und 4`, `subtrahiere 5 von 9`, `multipliziere 6 mit 7`, `teile 10 durch 2`
  - Automatische Normalisierung von Dezimalkommas, Sonderzeichen, `x`/`÷`, Bindestrichen etc.
- Rückgabefelder:
  - `a`, `b`: erkannte Operanden (Float)
  - `op`: Operator (`+ | - | * | /`)
  - `result`: numerisches Ergebnis
  - `usedComma`: merkt, ob der Nutzer Dezimalkomma eingegeben hat (für Ausgabeformatierung)
- **Beispiel**:
  ```javascript
  const task = "subtrahiere 15 von 20";
  const response = solve(task);
  if (response.ok) {
    console.log(`${response.a} - ${response.b} = ${response.result}`);
  } else {
    console.error("Parsing fehlgeschlagen:", response.error);
  }
  ```

#### `formatNumber(n: number, preferComma: boolean) -> string`
- Rundet numerische Ergebnisse stabil auf 10 Nachkommastellen, entfernt überflüssige Nullen und konvertiert optional Dezimalpunkt in Komma.
- Hauptsächlich von `appendMessage` genutzt, kann aber separat verwendet werden, um eigene numerische Ausgaben an das Frontend anzupassen.
- **Beispiel**:
  ```javascript
  const formatted = formatNumber(Math.PI, true); // "3,1415926536"
  ```

#### Audio-Funktionen
- **Text-To-Speech (TTS)**: Aktivieren über Button `#ttsBtn`. Beim Umschalten wird `speechSynthesis` mit deutscher Stimme genutzt. Der Code ruft `window.speechSynthesis.speak()` auf und bricht aktive Wiedergabe vor neuen Ausgaben ab.
- **Speech Recognition**: Falls `window.SpeechRecognition` oder `webkitSpeechRecognition` verfügbar ist, initialisiert das Skript eine deutsche Diktierfunktion:
  - Button `#micBtn` startet/stopt die Aufnahme.
  - Nach erfolgreicher Erkennung wird der Text ins Eingabefeld geschrieben und automatisch abgeschickt (`form.requestSubmit()`).
  - Fallback: Falls der Browser kein SpeechRecognition unterstützt, informiert ein Bot-Reply darüber.
- **Erweiterungs-Tipp**: Du kannst weitere Events an `recognition` anhängen, um z. B. Zwischenstände einzublenden oder Fehlerprotokolle zu erzeugen.

### Nutzung & Erweiterung
1. **Standardnutzung**: Öffne `index.html` lokal oder hoste sie statisch (z. B. GitHub Pages). Keine Backend-Abhängigkeiten.
2. **Einbindung in andere Seiten**: Bette die `div.app`-Struktur in vorhandene Layouts ein oder importiere `scrypt.js` als ES-Modul, indem du die IIFE-Hülle entfernst und Funktionen exportierst.
3. **Neue Operatoren/Sprachen**: Ergänze im `solve`-Parser neue reguläre Ausdrücke für weitere Schlüsselwörter bzw. Operatoren.
4. **Automatisierte Tests**: Du kannst `solve` mit Unit-Tests abdecken, indem du das Skript in eine Testumgebung transpilierst oder mit JSDOM ausführst.

---

## Version_2 – Python LLM Chatbot (Ollama)

### Module & Klassen

#### `Message` (Dataclass)
- Felder: `role` (`"system" | "user" | "assistant"`), `content` (Text).
- Dient als einheitliche Struktur für den Gesprächsverlauf.
- **Beispiel**:
  ```python
  from chatbot import Message
  system_message = Message(role="system", content="You are a helpful assistant.")
  ```

#### `LLMChatClient`
- Kapselt die HTTP-Kommunikation mit Ollama.
- **Konstruktor-Parameter**
  - `host` (str): Basis-URL der Ollama-Instanz, z. B. `http://127.0.0.1:11434`.
  - `model` (str, default `llama3.1`): Modellname, muss zuvor via `ollama pull <modell>` verfügbar sein.
  - `request_timeout` (int, default `30`): Sekunden bis zum Timeout bei `requests.post`.
  - `system_prompt` (str): Initiale Systemnachricht; wird bei Instanziierung automatisch an `messages` angehängt.
  - `messages` (List[Message], optional): Bereits bestehender Verlauf (z. B. für Warmstarts oder Tests).
- **Methoden**
  - `_payload() -> dict`: Intern genutztes Serialisierungs-Helper, falls du das JSON vor dem POST inspizieren möchtest.
  - `ask(user_text: str) -> str`:
    - Fügt Nutzernachricht hinzu.
    - POST gegen `<host>/api/chat` mit `stream=False`.
    - Fangt Verbindungsfehler, HTTP-Fehlercodes und JSON-Parsing ab und gibt menschenlesbare Fehlermeldungen zurück.
    - Hängt die Antwort des Modells als `assistant`-Nachricht an und liefert den Text zurück.
- **Beispielscript**:
  ```python
  from chatbot import LLMChatClient

  bot = LLMChatClient(host="http://localhost:11434", model="gemma3:1b")
  reply = bot.ask("Nenne 3 Gründe für Testautomatisierung.")
  print("Modell:", reply)
  ```
- **Erweiterungen**
  - Logging: Greife nach `ask()` auf `bot.messages` zu, um den vollständigen Verlauf zu persistieren.
  - Streaming: Setze `stream=True` im Payload und lese `requests.post(..., stream=True)`.
  - Mehrsprachigkeit: Setze `system_prompt` oder erste Nutzer-Nachricht entsprechend.

#### `load_config() -> dict`
- Lädt `.env` über `python-dotenv`.
- Liest Variablen `OLLAMA_HOST`, `MODEL`, `REQUEST_TIMEOUT` (Defaults: `http://127.0.0.1:11434`, `gemma3:1b`, `30`).
- Gibt ein Dictionary `{ "host": str, "model": str, "timeout": int }` zurück.
- **Beispiel**:
  ```python
  cfg = load_config()
  bot = LLMChatClient(host=cfg["host"], model=cfg["model"], request_timeout=cfg["timeout"])
  ```

#### `main()`
- Einstiegspunkt in `chatbot.py`.
- Initialisiert Konfiguration und `LLMChatClient`, startet REPL-Schleife:
  - Benutzerinput via `input("Du: ")`.
  - `exit`, `quit`, leere Zeile, `Ctrl+D` oder `Ctrl+C` beenden die Schleife sauber.
  - Ausgaben werden als `Assistent: <Antwort>` gedruckt.
- **CLI-Nutzung**:
  ```bash
  cd Version_2
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  cp .env.example .env  # falls vorhanden; andernfalls Variablen direkt setzen
  python chatbot.py
  ```

#### `Version_2/main.py`
- Enthält einen separaten, minimalistischen `main()`-Wrapper, der aktuell nur `"Hello from version-2!"` ausgibt. Nützlich als Platzhalter für spätere CLI-Funktionen oder Smoke-Tests.

### Konfigurations- & Laufzeittipps
- **.env Felder**
  - `OLLAMA_HOST`: Host:Port deiner Ollama-Instanz. Für Container-Deployments ggf. `http://host.docker.internal:11434`.
  - `MODEL`: Entspricht dem Namen aus `ollama list`.
  - `REQUEST_TIMEOUT`: Erhöhe bei großen Modellen oder schwacher Hardware.
- **Fehlerbehandlung**
  - Netzwerk: `ask()` liefert Meldungen wie `Verbindungsfehler zu Ollama: ...`.
  - HTTP-Status ≠ 200: Rückgabe enthält `HTTP <code>: <body-ausschnitt>`.
  - Ungültiges JSON: Rückgabe `"Ungültige JSON-Antwort von Ollama."`
- **Automatisierte Nutzung**: Binde `LLMChatClient` in andere Skripte ein, indem du zusätzliche Methoden implementierst (z. B. `ask_streaming()`, `reset_conversation()`).

---

## Tests & Best Practices
- **Version_1**
  - Schreibe Parser-Unit-Tests für `solve` mit typischen Eingaben (Symbol, Text, Fehlerszenarien).
  - Für UI-/Accessibility-Tests nutze Playwright oder Cypress; validiere ARIA-Attribute sowie Tastatursteuerung.
- **Version_2**
  - Mocke `requests.post`, um die Fehlerpfade von `ask()` abzudecken (Timeouts, HTTP 500, ungültiges JSON).
  - Integrationstest: Starte eine Ollama-Instanz mit kleinem Modell und prüfe End-to-End-Dialoge.

Mit dieser Referenz kannst du gezielt in beiden Versionen neue Features entwickeln, automatisierte Tests erstellen oder die Komponenten in größere Systeme integrieren.

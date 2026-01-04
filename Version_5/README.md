# Version 5 – MathQA UI + Klassifizierer

Gradio-Chatoberfläche mit MathQA-Klassifizierung (Logistic Regression + SentenceTransformer). Kein LLM eingebunden.

## Setup (uv empfohlen)
```bash
uv sync
```

## Klassifizierer trainieren (MathQA)
```bash
uv run python train_classifier.py \
  --dataset ../Version_4/MathQA/train.json \
  --sample-size 5000 \
  --output models/classifier
```
- Artefakte landen unter `models/classifier` (clf.joblib, embedding_model.joblib, label_map.json, metrics.json).
- Passe `--device cuda` an, falls GPU verfügbar.

## App starten
```bash
uv run python main.py
```
Öffne den Link (Standard: http://127.0.0.1:7860). Die Chatnachrichten werden klassifiziert; Badge erscheint vor der Antwort.

## Hinweise
- Falls der Klassifizierer nicht gefunden wird, zeigt das Seitenpanel einen Hinweis „nicht gefunden — bitte zuerst trainieren“.
- Die Antworten sind statisch (Echo + Badge); die Klassifizierung stammt aus den trainierten Artefakten.

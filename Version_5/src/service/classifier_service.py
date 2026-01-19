"""Lightweight classifier training/loading for MathQA.

Uses SentenceTransformer embeddings + Logistic Regression.
Artifacts are saved under an output directory (default: models/classifier).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import json
import logging
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ClassifierArtifacts:
    model_dir: Path
    label_map_path: Path
    metrics_path: Path


class ClassifierService:
    """Encapsulates train/load/predict for the MathQA classifier."""

    def __init__(self, model_dir: Optional[Path] = None, embedding_model: str = "all-MiniLM-L6-v2", device: str = "cpu") -> None:
        self.model_dir = Path(model_dir) if model_dir else None
        self.embedding_model_name = embedding_model
        self.device = device

        self._clf = None
        self._label_map: Optional[Dict[int, str]] = None
        self._emb_model = None
        
        # For similarity search
        self._test_embeddings: Optional[np.ndarray] = None
        self._test_questions: Optional[List[Dict[str, Any]]] = None
        self._raw_data: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def from_pretrained(cls, model_dir: Path, device: str = "cpu") -> "ClassifierService":
        inst = cls(model_dir=model_dir, device=device)
        inst.load(model_dir)
        return inst

    # --- Core API ---
    def train(
        self,
        dataset_path: Path,
        sample_size: int = 5000,
        test_size: float = 0.2,
        random_state: int = 42,
        output_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Train on MathQA JSON (list of dicts with 'Problem' and 'category')."""
        try:
            from sentence_transformers import SentenceTransformer
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score
            import numpy as np
            import joblib
        except Exception as e:
            raise ImportError(
                "Training requires sentence-transformers, scikit-learn, joblib, numpy"
            ) from e

        texts, labels = self._load_mathqa_json(dataset_path, sample_size)

        # Label map
        unique_labels = sorted(set(labels))
        label_to_idx = {label: idx for idx, label in enumerate(unique_labels)}
        y = [label_to_idx[l] for l in labels]

        emb_model = SentenceTransformer(self.embedding_model_name, device=self.device)
        X = emb_model.encode(texts, show_progress_bar=True)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        clf = LogisticRegression(max_iter=1000)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        acc = float(accuracy_score(y_test, y_pred))

        out_dir = Path(output_dir or "models/classifier")
        out_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(clf, out_dir / "clf.joblib")
        joblib.dump(self.embedding_model_name, out_dir / "embedding_model.joblib")
        with open(out_dir / "label_map.json", "w", encoding="utf-8") as f:
            json.dump(label_to_idx, f, ensure_ascii=False, indent=2)
        with open(out_dir / "metrics.json", "w", encoding="utf-8") as f:
            json.dump({"accuracy": acc}, f)

        self._clf = clf
        self._label_map = {idx: label for label, idx in label_to_idx.items()}
        self._emb_model = emb_model
        self.model_dir = out_dir

        return {"accuracy": acc, "out_dir": str(out_dir)}

    def classify(self, text: str) -> Dict[str, Any]:
        if not text.strip():
            return {"category": "unknown", "confidence": 0.0, "reasoning": "empty input"}
        if self._clf is None or self._emb_model is None:
            if self.model_dir:
                self.load(self.model_dir)
            else:
                raise RuntimeError("Classifier not loaded; train or load first.")
        emb = self._emb_model.encode([text])
        probs = self._clf.predict_proba(emb)[0]
        top_idx = int(probs.argmax())
        return {
            "category": self._label_map.get(top_idx, "unknown"),
            "confidence": float(probs[top_idx]),
            "reasoning": f"Predicted with {self.embedding_model_name}; top index {top_idx}.",
        }

    def load(self, model_dir: Path) -> None:
        try:
            import joblib
            from sentence_transformers import SentenceTransformer
        except Exception as e:
            raise ImportError("Loading requires joblib and sentence-transformers") from e
        clf_path = model_dir / "clf.joblib"
        label_map_path = model_dir / "label_map.json"
        emb_path = model_dir / "embedding_model.joblib"
        if not clf_path.exists() or not label_map_path.exists():
            raise FileNotFoundError(f"Classifier artifacts not found in {model_dir}")
        self._clf = joblib.load(clf_path)
        try:
            emb_name = joblib.load(emb_path)
        except Exception:
            emb_name = self.embedding_model_name
        self._emb_model = SentenceTransformer(emb_name, device=self.device)
        with open(label_map_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        if all(not isinstance(k, str) or not k.isdigit() for k in loaded.keys()):
            # label->idx mapping
            self._label_map = {idx: label for label, idx in loaded.items()}
        else:
            # idx->label mapping
            self._label_map = {int(k): v for k, v in loaded.items()}
        self.model_dir = model_dir

    def load_test_set(self, test_path: Path, max_samples: Optional[int] = None) -> None:
        """Load and index test set questions for similarity search."""
        if self._emb_model is None:
            if self.model_dir:
                self.load(self.model_dir)
            else:
                raise RuntimeError("Embedding model not loaded; train or load first.")
        
        # Load raw data with all fields
        with open(test_path, "r", encoding="utf-8") as f:
            self._raw_data = json.load(f)
            if max_samples:
                self._raw_data = self._raw_data[:max_samples]
        
        texts = [item.get("Problem", "") for item in self._raw_data]
        labels = [item.get("category", "unknown") or "unknown" for item in self._raw_data]
        
        logger.info(f"Encoding {len(texts)} test questions for similarity search...")
        self._test_embeddings = self._emb_model.encode(texts, show_progress_bar=True)
        self._test_questions = [
            {"problem": text, "category": label, "index": idx}
            for idx, (text, label) in enumerate(zip(texts, labels))
        ]
        logger.info(f"Test set loaded: {len(self._test_questions)} questions indexed.")

    def find_similar(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Find top_k most similar questions from the test set."""
        if self._test_embeddings is None or self._test_questions is None:
            raise RuntimeError("Test set not loaded. Call load_test_set() first.")
        
        if self._emb_model is None:
            if self.model_dir:
                self.load(self.model_dir)
            else:
                raise RuntimeError("Embedding model not loaded; train or load first.")
        
        # Encode query
        query_emb = self._emb_model.encode([query])[0]
        
        # Compute cosine similarities
        similarities = self._cosine_similarity(query_emb, self._test_embeddings)
        
        # Get top_k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            result = {
                **self._test_questions[idx],
                "similarity": float(similarities[idx])
            }
            # Add additional fields from raw data if available
            if self._raw_data and idx < len(self._raw_data):
                raw_item = self._raw_data[idx]
                result["rationale"] = raw_item.get("Rationale", "")
                result["correct"] = raw_item.get("correct", "")
            results.append(result)
        
        return results

    @staticmethod
    def _cosine_similarity(query_vec: np.ndarray, corpus_vecs: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between query vector and corpus vectors."""
        query_norm = np.linalg.norm(query_vec)
        corpus_norms = np.linalg.norm(corpus_vecs, axis=1)
        
        dot_products = np.dot(corpus_vecs, query_vec)
        similarities = dot_products / (corpus_norms * query_norm + 1e-8)
        
        return similarities

    # --- Helpers ---
    def _load_mathqa_json(self, dataset_path: Path, sample_size: int) -> Tuple[List[str], List[str]]:
        """Load training data from JSON or Parquet format."""
        texts: List[str] = []
        labels: List[str] = []
        
        if dataset_path.suffix.lower() == ".parquet":
            try:
                import pandas as pd
            except ImportError:
                raise ImportError("Parquet support requires pandas") from None
            
            df = pd.read_parquet(dataset_path)
            df = df.head(sample_size)
            for _, row in df.iterrows():
                problem = row.get("Problem") or row.get("problem") or ""
                category = row.get("category") or row.get("Category") or "unknown"
                texts.append(str(problem))
                labels.append(str(category) or "unknown")
        else:
            # Assume JSON format
            with open(dataset_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data[:sample_size]:
                texts.append(item.get("Problem", ""))
                labels.append(item.get("category", "unknown") or "unknown")
        
        return texts, labels
        return texts, labels


__all__ = ["ClassifierService", "ClassifierArtifacts"]

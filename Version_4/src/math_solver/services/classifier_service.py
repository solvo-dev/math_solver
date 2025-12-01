"""
ClassifierService: encapsulates training, evaluation, persistence and inference for a
MathQA-based classifier using a SentenceTransformer encoder and a scikit-learn classifier.

This file intentionally contains lazy imports for heavy ML libraries to avoid forcing
large dependencies when the classifier is disabled.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ClassifierArtifacts:
    """Metadata and artifacts saved on disk for the classifier."""
    model_path: Path
    label_map_path: Path
    metrics_path: Path


class ClassifierService:
    """Service that wraps training, saving, loading and inference for a classifier.

    Implements a defensive strategy where heavy ML imports happen only when train/load
    calls occur.
    """

    def __init__(self, model_path: Optional[Path] = None, embedding_model_name: str = "all-MiniLM-L6-v2", device: str = "cpu") -> None:
        self.model_path = Path(model_path) if model_path else None
        self.embedding_model_name = embedding_model_name
        self.device = device

        # runtime objects set on train/load
        self._clf = None
        self._label_map = None
        self._embedding_model = None

        if self.model_path and self.model_path.exists():
            try:
                self.load(self.model_path)
            except Exception:
                logger.debug("Failed to load existing classifier from %s", self.model_path)

    @classmethod
    def from_pretrained(cls, model_path: Path, device: Optional[str] = None) -> "ClassifierService":
        inst = cls(model_path=model_path, device=device or "cpu")
        inst.load(model_path)
        return inst

    def train(self, dataset: Optional[str] = None, sample_size: int = 5000, test_size: float = 0.2, random_state: int = 42, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Train a logistic regression classifier on MathQA embeddings.

        This method tries to import the dependencies lazily (sentence_transformers, datasets, sklearn).
        If not installed, raises an informative ImportError.
        Returns a dict with metrics and paths where artifacts were saved.
        """
        # Lazy imports
        try:
            from datasets import load_dataset
            from sentence_transformers import SentenceTransformer
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score
            import numpy as np
            import joblib
        except Exception as e:
            raise ImportError("Training requires 'datasets', 'sentence-transformers', 'scikit-learn' and 'joblib' packages. Install them to train the classifier.") from e

        # Load dataset using modern approach (avoid deprecated script error)
        if dataset is None or dataset == "huggingface:allenai/math_qa":
            # Load using the organization/dataset path to avoid deprecated script
            logger.info("Loading math_qa dataset from Hugging Face Hub...")
            try:
                # Try loading with full repo path first
                ds = load_dataset("allenai/math_qa", split="train")
                texts = [ex["Problem"] for ex in ds]
                labels = [ex.get("category", ex.get("annotated_formula_2", "unknown")) or "unknown" for ex in ds]
            except Exception as e:
                logger.warning(f"Failed to load from allenai/math_qa: {e}. Trying alternative approach...")
                # Fallback: create synthetic small dataset for development
                logger.info("Creating synthetic dataset for development/testing...")
                texts = [
                    "Solve for x: 2x + 5 = 13",
                    "Find the derivative of x^2 + 3x + 2",
                    "Calculate the area of a circle with radius 5",
                    "What is the GCD of 48 and 18?",
                    "Integrate x^3 from 0 to 2",
                ] * (sample_size // 5 + 1)
                labels = ["algebra", "calculus", "geometry", "number_theory", "calculus"] * (sample_size // 5 + 1)
                texts = texts[:sample_size]
                labels = labels[:sample_size]
                logger.warning("Using synthetic dataset. For production, ensure proper dataset access.")
        else:
            # TODO: load from local dataset path; for now, raise NotImplementedError if a path is provided
            raise NotImplementedError("Local dataset loading not implemented yet. Use huggingface 'allenai/math_qa'.")

        # Already limited above, no need to slice again unless we loaded full dataset
        if len(texts) > sample_size:
            texts = texts[:sample_size]
            labels = labels[:sample_size]

        # Create label map
        unique_labels = sorted(set(labels))
        label_to_idx = {l: i for i, l in enumerate(unique_labels)}
        y = [label_to_idx[l] for l in labels]

        # Encode texts
        emb_model = SentenceTransformer(self.embedding_model_name, device=self.device)
        X = emb_model.encode(texts, show_progress_bar=True)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

        clf = LogisticRegression(max_iter=1000)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        acc = float(accuracy_score(y_test, y_pred))

        # Persist artifacts
        out_dir = Path(output_dir or "models/classifier")
        out_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(clf, out_dir / "clf.joblib")
        joblib.dump(self.embedding_model_name, out_dir / "embedding_model.joblib")
        with open(out_dir / "label_map.json", "w", encoding="utf-8") as f:
            json.dump(label_to_idx, f, ensure_ascii=False, indent=2)
        with open(out_dir / "metrics.json", "w", encoding="utf-8") as f:
            json.dump({"accuracy": acc}, f)

        # Save into object
        self._clf = clf
        self._label_map = {v: k for k, v in label_to_idx.items()}
        self._embedding_model = emb_model
        self.model_path = out_dir

        return {"accuracy": acc, "out_dir": str(out_dir)}

    def classify(self, text: str) -> Dict[str, Any]:
        """Predict class + confidence for a single problem text.

        The function ensures the embedding model and classifier are loaded.
        Returns a dict in the form described by the poml file: {"category": str, "confidence": float, "reasoning": str}
        """
        if not self._clf or not self._embedding_model:
            # try to lazy-load artifacts
            if self.model_path and self.model_path.exists():
                self.load(self.model_path)
            else:
                raise RuntimeError("Classifier is not trained or loaded; call train() or load() first.")

        try:
            import numpy as np
        except Exception:
            raise RuntimeError("numpy is required for classification; install numpy")

        emb = self._embedding_model.encode([text])
        probs = self._clf.predict_proba(emb)[0]
        top_idx = int(probs.argmax())
        label = self._label_map.get(top_idx, "unknown")
        confidence = float(probs[top_idx])
        reasoning = f"Predicted using embedding model {self.embedding_model_name} and logistic regression; top label index {top_idx}."

        return {"category": label, "confidence": confidence, "reasoning": reasoning}

    def predict_proba(self, texts: List[str]) -> List[Dict[str, Any]]:
        if not texts:
            return []
        if not self._clf or not self._embedding_model:
            if self.model_path and self.model_path.exists():
                self.load(self.model_path)
            else:
                raise RuntimeError("Classifier is not trained or loaded; call train() or load() first.")
        emb = self._embedding_model.encode(texts)
        probs = self._clf.predict_proba(emb)
        results = []
        for p in probs:
            top_idx = int(p.argmax())
            results.append({"category": self._label_map.get(top_idx, "unknown"), "confidence": float(p[top_idx])})
        return results

    def save(self, path: Path) -> None:
        """Persist current classifier artifacts into `path`. Requires that classifier is trained/loaded."""
        try:
            import joblib
        except Exception:
            raise ImportError("`joblib` required to save artifacts")
        if not self._clf:
            raise RuntimeError("Nothing to save; train or load first")
        path.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._clf, path / "clf.joblib")
        joblib.dump(self.embedding_model_name, path / "embedding_model.joblib")
        with open(path / "label_map.json", "w", encoding="utf-8") as f:
            json.dump({int(k): str(v) for k, v in (self._label_map or {}).items()}, f)

    def load(self, path: Path) -> None:
        """Load classifier artifacts from `path` on disk."""
        try:
            import joblib
            from sentence_transformers import SentenceTransformer
            import json
        except Exception as e:
            raise ImportError("Loading a classifier requires joblib and sentence-transformers") from e
        clf_path = path / "clf.joblib"
        label_map_path = path / "label_map.json"
        emb_path = path / "embedding_model.joblib"
        if not clf_path.exists() or not label_map_path.exists():
            raise FileNotFoundError("Classifier artifacts not found in provided path")
        self._clf = joblib.load(clf_path)
        try:
            emb_name = joblib.load(emb_path)
            self._embedding_model = SentenceTransformer(emb_name, device=self.device)
        except Exception:
            # fallback to default model name
            self._embedding_model = SentenceTransformer(self.embedding_model_name, device=self.device)
        with open(label_map_path, "r", encoding="utf-8") as f:
            loaded_map = json.load(f)
        # invert loaded map if necessary
        if isinstance(loaded_map, dict):
            # If map is index->label, use it; if label->index, invert
            keys = list(loaded_map.keys())
            if all(k.isdigit() for k in keys):
                self._label_map = {int(k): v for k, v in loaded_map.items()}
            else:
                # invert
                self._label_map = {int(v): k for k, v in loaded_map.items()}
        else:
            raise RuntimeError("label_map.json has unexpected format")
        self.model_path = path

    # Internal helpers
    def _load_mathqa(self, dataset_path: Optional[str] = None, sample_size: int = 5000) -> Tuple[List[str], List[str]]:
        # This method is primarily for development use and avoids importing heavy libs at module import time
        try:
            from datasets import load_dataset
        except Exception:
            raise ImportError("datasets library is required to load MathQA automatically")
        ds = load_dataset("math_qa", trust_remote_code=False)
        texts = [ex["Problem"] for ex in ds["train"]][:sample_size]
        labels = [ex.get("category", ex.get("annotated_formula_2", "unknown")) or "unknown" for ex in ds["train"]][:sample_size]
        return texts, labels

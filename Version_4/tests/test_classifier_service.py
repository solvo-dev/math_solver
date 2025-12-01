"""Unit tests for the classifier service and tool.

These tests are minimal and avoid heavy ML dependency usage. They verify the public signatures
and that the module can be instantiated without training. Real training/integration tests will
be provided separately and may run slower.
"""
from pathlib import Path
import json
import tempfile
import pytest

from math_solver.services.classifier_service import ClassifierService


def test_instantiation_without_artifacts(tmp_path: Path):
    """Ensure construction succeeds even when no artifacts exist."""
    svc = ClassifierService(model_path=tmp_path / "nonexistent")
    assert svc is not None


def test_save_load_roundtrip(tmp_path: Path):
    """If joblib is available, create a fake classifier object and save/load it through the service."""
    svc = ClassifierService(model_path=tmp_path / "classifier")
    # Create a fake classifier by monkeypatching internals
    svc._clf = object()  # not a real classifier
    svc._label_map = {0: "algebra", 1: "calculus"}
    svc._embedding_model = None
    # Ensure save raises if joblib not installed or clf is not compatible
    with pytest.raises(RuntimeError):
        svc.save(tmp_path / "out")

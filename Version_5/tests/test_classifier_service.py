import pytest
from pathlib import Path

from service.classifier_service import ClassifierService


@pytest.fixture
def model_dir():
    """Fixture providing the path to the classifier model directory."""
    return Path(__file__).resolve().parent.parent / "models" / "classifier"


def test_classifier_loads_and_predicts(model_dir):
    """Test that the classifier loads and makes predictions correctly."""
    if not (model_dir.exists() and (model_dir / "clf.joblib").exists()):
        pytest.skip("Classifier artifacts not found; run train_classifier.py first.")

    svc = ClassifierService.from_pretrained(model_dir)
    result = svc.classify("Was ist der Umfang eines Kreises mit Radius 5?")

    assert "category" in result
    assert "confidence" in result
    assert isinstance(result["confidence"], float)
    assert result["confidence"] >= 0.0
    assert result["confidence"] <= 1.0

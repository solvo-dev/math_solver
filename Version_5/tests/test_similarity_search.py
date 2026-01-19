import pytest
from pathlib import Path

from service.classifier_service import ClassifierService


@pytest.fixture
def model_dir():
    """Fixture providing the path to the classifier model directory."""
    return Path(__file__).resolve().parent.parent / "models" / "classifier"


@pytest.fixture
def test_data_path():
    """Fixture providing the path to the test dataset."""
    return Path(__file__).resolve().parent.parent / "models" / "data" / "train-00000-of-00001.json"


def test_similarity_search(model_dir, test_data_path):
    """Test that similarity search returns top-k similar questions."""
    if not (model_dir.exists() and (model_dir / "clf.joblib").exists()):
        pytest.skip("Classifier artifacts not found; run train_classifier.py first.")
    
    if not test_data_path.exists():
        pytest.skip("Test dataset not found.")
    
    # Load classifier
    svc = ClassifierService.from_pretrained(model_dir)
    
    # Load test set (limited sample for test speed)
    svc.load_test_set(test_data_path, max_samples=100)
    
    # Test similarity search
    query = "What is the area of a circle with radius 10?"
    results = svc.find_similar(query, top_k=3)
    
    # Assertions
    assert len(results) == 3
    assert all("problem" in r for r in results)
    assert all("category" in r for r in results)
    assert all("similarity" in r for r in results)
    assert all(isinstance(r["similarity"], float) for r in results)
    assert all(0.0 <= r["similarity"] <= 1.0 for r in results)
    
    # Results should be sorted by similarity (descending)
    similarities = [r["similarity"] for r in results]
    assert similarities == sorted(similarities, reverse=True)


def test_similarity_search_empty_query(model_dir, test_data_path):
    """Test similarity search with empty query."""
    if not (model_dir.exists() and (model_dir / "clf.joblib").exists()):
        pytest.skip("Classifier artifacts not found.")
    
    if not test_data_path.exists():
        pytest.skip("Test dataset not found.")
    
    svc = ClassifierService.from_pretrained(model_dir)
    svc.load_test_set(test_data_path, max_samples=50)
    
    # Should still return results (though they may not be meaningful)
    results = svc.find_similar("", top_k=3)
    assert len(results) == 3


def test_similarity_search_without_loading_test_set(model_dir):
    """Test that similarity search raises error if test set not loaded."""
    if not (model_dir.exists() and (model_dir / "clf.joblib").exists()):
        pytest.skip("Classifier artifacts not found.")
    
    svc = ClassifierService.from_pretrained(model_dir)
    
    with pytest.raises(RuntimeError, match="Test set not loaded"):
        svc.find_similar("What is 2 + 2?", top_k=3)

# Classifier Quick Reference

## Training

```powershell
# Basic training (uses synthetic data as fallback)
python scripts/train_classifier.py --sample-size 200

# Custom output location
python scripts/train_classifier.py --output my_models/classifier

# Use GPU if available
python scripts/train_classifier.py --device cuda
```

## Enabling

### Via Environment
```powershell
$env:ENABLE_CLASSIFIER = "true"
$env:CLASSIFIER_MODEL_PATH = "models/classifier"
$env:CLASSIFIER_CONFIDENCE_THRESHOLD = "0.6"
```

### Via Code
```python
from math_solver.config import ChatConfig

config = ChatConfig(
    enable_classifier=True,
    classifier_model_path="models/classifier",
    classifier_confidence_threshold=0.6
)
```

## Direct Usage

```python
from pathlib import Path
from math_solver.services.classifier_service import ClassifierService

# Load model
clf = ClassifierService.from_pretrained(Path("models/classifier"))

# Classify
result = clf.classify("Solve x^2 - 4 = 0")
print(result)
# {'category': 'algebra', 'confidence': 0.85, 'reasoning': '...'}
```

## Categories

- `algebra` - Equations, expressions, variables
- `calculus` - Derivatives, integrals, limits
- `geometry` - Shapes, areas, volumes
- `number_theory` - Primes, GCD, LCM, divisibility

## Confidence Thresholds

| Range | Interpretation | Action |
|-------|----------------|--------|
| > 0.80 | High confidence | Trust the prediction |
| 0.60-0.80 | Medium | Probably correct |
| 0.40-0.60 | Low | Review manually |
| < 0.40 | Very low | Likely wrong |

## Files & Artifacts

```
Version_4/
├── models/classifier/
│   ├── clf.joblib              # Trained model
│   ├── embedding_model.joblib  # Embedding model name
│   ├── label_map.json          # Category mapping
│   └── metrics.json            # Training metrics
├── scripts/
│   └── train_classifier.py     # Training CLI
└── src/math_solver/
    ├── services/
    │   └── classifier_service.py
    └── tools/
        └── classifier_tool.py
```

## Common Issues

**"Dataset scripts are no longer supported"**
- Solution: Script uses synthetic fallback automatically
- For production: Clear HF cache or use local files

**"Classifier not initialized"**
- Check: `enable_classifier=True` in config
- Check: Model files exist in `classifier_model_path`
- Check: ML packages installed

**Low accuracy**
- Train on larger sample size (5000+)
- Use real MathQA dataset instead of synthetic
- Increase confidence threshold to filter uncertain predictions

## Testing

```powershell
# Quick inference test
python test_classifier_inference.py

# Full demo with examples
python demo_classifier.py
```

## Integration Flow

```
User Input
    ↓
[Classifier] → category + confidence
    ↓ (if confidence > threshold)
[Tool Result] → "Category: algebra (confidence: 0.85)"
    ↓
[Added to Conversation]
    ↓
[Normal Tool Detection] → arithmetic/sympy/numeric
    ↓
[LLM Response]
```

## Performance

- **Model Size**: ~90MB (embedding model)
- **Load Time**: ~3 seconds (first load)
- **Inference**: 50-100ms per problem
- **Memory**: ~200MB with model loaded

## Production Checklist

- [ ] Train on full dataset (5000+ samples)
- [ ] Set appropriate confidence threshold (0.6-0.7)
- [ ] Test on diverse problem types
- [ ] Monitor classification accuracy
- [ ] Set up model versioning
- [ ] Document category definitions
- [ ] Add performance monitoring

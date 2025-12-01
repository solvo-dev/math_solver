# Math Problem Classifier

A semantic classifier for mathematical word problems using SentenceTransformers and scikit-learn.

## Overview

This classifier categorizes math problems into semantic categories (algebra, calculus, geometry, number theory) using:
- **Embedding Model**: `all-MiniLM-L6-v2` from SentenceTransformers
- **Classifier**: Logistic Regression from scikit-learn
- **Dataset**: MathQA from Hugging Face (with synthetic fallback for development)

## Architecture

The implementation is **non-invasive** and **opt-in**:

### Components Added

1. **`services/classifier_service.py`**
   - `ClassifierService`: Handles training, save/load, and inference
   - Lazy imports to avoid forcing heavy ML dependencies

2. **`tools/classifier_tool.py`**
   - `ClassifierTool`: Adapter implementing the `MathTool` interface
   - Returns JSON with category, confidence, and reasoning

3. **`config.py` (updated)**
   - `enable_classifier: bool` - Opt-in flag (default: `False`)
   - `classifier_model_path: str` - Path to model artifacts
   - `classifier_confidence_threshold: float` - Minimum confidence for results

4. **Integration Points**
   - `chatbot_service.py`: Optionally instantiates classifier if enabled
   - `chatbot.py`: Runs classification before tool detection if enabled

## Installation

### Base Requirements
```powershell
pip install -r requirements.txt
```

### ML Dependencies (for classifier)
Already included in `requirements.txt`:
- `sentence-transformers>=2.2.2`
- `scikit-learn>=1.3.0`
- `datasets>=2.13.0`
- `joblib>=1.3.0`

## Usage

### Training the Classifier

```powershell
# Train with default settings (5000 samples)
python scripts/train_classifier.py

# Train with custom sample size
python scripts/train_classifier.py --sample-size 2000 --output models/classifier

# Specify device (cpu or cuda)
python scripts/train_classifier.py --device cuda
```

**Note**: Due to deprecated dataset scripts in Hugging Face, the trainer uses a synthetic dataset as fallback. For production, you may need to:
1. Download MathQA manually from Hugging Face datasets
2. Clear the HF cache: `C:\Users\<user>\.cache\huggingface\hub\datasets--math_qa`
3. Or use a local dataset file

### Enabling the Classifier

#### Option 1: Environment Variables
```powershell
$env:ENABLE_CLASSIFIER = "true"
$env:CLASSIFIER_MODEL_PATH = "models/classifier"
$env:CLASSIFIER_CONFIDENCE_THRESHOLD = "0.5"
```

#### Option 2: Code Configuration
```python
from math_solver.config import ChatConfig

config = ChatConfig(
    enable_classifier=True,
    classifier_model_path="models/classifier",
    classifier_confidence_threshold=0.5
)
```

### Testing Inference

```python
from pathlib import Path
from math_solver.services.classifier_service import ClassifierService

# Load trained model
svc = ClassifierService.from_pretrained(Path("models/classifier"))

# Classify a problem
result = svc.classify("Solve for x: 2x + 5 = 13")
print(result)
# Output: {'category': 'algebra', 'confidence': 0.92, 'reasoning': '...'}
```

### Integration with Chatbot

When enabled, the classifier runs automatically on user input:

```python
from math_solver.services.chatbot_service import ChatbotService

# Classifier enabled via config
service = ChatbotService()
chatbot = service.get_chatbot()

# Classification happens automatically in generate_response_with_tools
async for response in chatbot.generate_response_with_tools("Find the derivative of x^2"):
    print(response)
    # First response: {"type": "tool_result", "content": "Category: calculus (confidence: 0.87)", "tool": "classifier"}
```

## Model Artifacts

After training, the following files are saved in `models/classifier/`:

- `clf.joblib` - Trained LogisticRegression model
- `embedding_model.joblib` - Name of the embedding model used
- `label_map.json` - Mapping of category names to indices
- `metrics.json` - Training metrics (accuracy, etc.)

## API Reference

### ClassifierService

```python
class ClassifierService:
    def __init__(
        self, 
        model_path: Optional[Path] = None,
        embedding_model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu"
    ) -> None: ...
    
    @classmethod
    def from_pretrained(cls, model_path: Path, device: Optional[str] = None) -> "ClassifierService": ...
    
    def train(
        self,
        dataset: Optional[str] = None,
        sample_size: int = 5000,
        test_size: float = 0.2,
        random_state: int = 42,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]: ...
    
    def classify(self, text: str) -> Dict[str, Any]: ...
    # Returns: {"category": str, "confidence": float, "reasoning": str}
    
    def save(self, path: Path) -> None: ...
    def load(self, path: Path) -> None: ...
```

### ClassifierTool

```python
class ClassifierTool(MathTool):
    def __init__(
        self,
        classifier_service: ClassifierService,
        confidence_threshold: float = 0.5
    ) -> None: ...
    
    @property
    def name(self) -> str: ...  # Returns "classifier"
    
    async def execute(self, expression: str) -> Optional[str]: ...
    # Returns JSON string with classification results
```

## Non-Invasive Design

The classifier is designed to be **completely optional**:

✅ **Default behavior unchanged** - Classifier disabled by default  
✅ **No breaking changes** - Existing code works without modification  
✅ **Lazy imports** - Heavy ML libraries loaded only when needed  
✅ **Graceful degradation** - App continues if classifier fails to initialize  
✅ **Opt-in configuration** - Enable via config flag  

## Performance Considerations

- **Embedding Model**: ~90MB, loads in ~3 seconds on CPU
- **Inference Speed**: ~50-100ms per classification on CPU
- **Memory Usage**: ~200MB with model loaded
- **Training Time**: ~2-5 minutes for 5000 samples on CPU

## Troubleshooting

### "Dataset scripts are no longer supported"
This occurs when Hugging Face finds an old `math_qa.py` script. The classifier automatically falls back to synthetic data for development. For production:
- Clear HF cache or use local dataset files
- Modify `ClassifierService.train()` to use your own data source

### "Classifier not initialized"
Ensure:
1. `enable_classifier=True` in config
2. Model artifacts exist in `classifier_model_path`
3. Required packages installed: `sentence-transformers`, `scikit-learn`, etc.

### Low Confidence Predictions
The synthetic fallback dataset is tiny (200 samples). For better accuracy:
- Train on the full MathQA dataset (37k+ problems)
- Increase `sample_size` parameter
- Use a larger embedding model

## Future Enhancements

- [ ] Support for local dataset files (JSON/CSV)
- [ ] Add confusion matrix and detailed metrics
- [ ] Implement ANN search with FAISS/LanceDB for nearest neighbor reasoning
- [ ] Add support for multi-label classification
- [ ] Fine-tune embedding model on math-specific corpus
- [ ] Add confidence calibration

## License

Same as the parent Math Solver project.

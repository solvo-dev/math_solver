"""Quick test script to verify classifier inference works."""
from pathlib import Path
from src.math_solver.services.classifier_service import ClassifierService

# Load the trained classifier
svc = ClassifierService.from_pretrained(Path("models/classifier"))

# Test classification on a few examples
test_problems = [
    "Solve the equation 3x + 7 = 22",
    "Find the derivative of sin(x) * cos(x)",
    "Calculate the area of a triangle with base 10 and height 5",
    "What is the least common multiple of 12 and 18?"
]

print("Testing classifier inference:\n")
for problem in test_problems:
    result = svc.classify(problem)
    print(f"Problem: {problem}")
    print(f"Category: {result['category']} (confidence: {result['confidence']:.2f})")
    print(f"Reasoning: {result['reasoning']}\n")

print("✓ Classifier inference test completed successfully!")

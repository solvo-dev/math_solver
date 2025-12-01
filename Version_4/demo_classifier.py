"""
Demo script showing the Math Problem Classifier in action.

This script demonstrates:
1. Loading a trained classifier
2. Classifying various math problems
3. Interpreting confidence scores
"""

from pathlib import Path
from src.math_solver.services.classifier_service import ClassifierService
import json


def main():
    print("=" * 70)
    print("Math Problem Classifier - Demo")
    print("=" * 70)
    print()

    # Load the trained classifier
    model_path = Path("models/classifier")
    if not model_path.exists():
        print("❌ Error: Classifier model not found!")
        print(f"   Expected location: {model_path.absolute()}")
        print()
        print("Please train the classifier first:")
        print("   python scripts/train_classifier.py --sample-size 200")
        return

    print(f"📂 Loading classifier from: {model_path}")
    svc = ClassifierService.from_pretrained(model_path)
    print("✓ Classifier loaded successfully!")
    print()

    # Load label map to show available categories
    with open(model_path / "label_map.json", "r") as f:
        label_map = json.load(f)
    
    print(f"📊 Available categories: {', '.join(label_map.keys())}")
    print()

    # Test problems covering different categories
    test_problems = [
        ("Algebra", "Solve the quadratic equation: x^2 - 5x + 6 = 0"),
        ("Algebra", "Simplify the expression: 2(3x + 4) - 5x"),
        ("Calculus", "Find the derivative of f(x) = sin(x) * cos(x)"),
        ("Calculus", "Calculate the integral of x^2 from 0 to 3"),
        ("Geometry", "Find the area of a circle with radius 7"),
        ("Geometry", "Calculate the volume of a cube with side length 5"),
        ("Number Theory", "Find the greatest common divisor of 48 and 72"),
        ("Number Theory", "Determine if 17 is a prime number"),
    ]

    print("-" * 70)
    print("Testing classification on various problems:")
    print("-" * 70)
    print()

    for expected_category, problem in test_problems:
        result = svc.classify(problem)
        
        # Determine if classification matches expected
        match_symbol = "✓" if result['category'].lower() in expected_category.lower() else "✗"
        confidence_bar = "█" * int(result['confidence'] * 20)
        
        print(f"{match_symbol} Problem: {problem}")
        print(f"  Expected: {expected_category}")
        print(f"  Predicted: {result['category'].title()} "
              f"(confidence: {result['confidence']:.2%}) {confidence_bar}")
        print()

    print("-" * 70)
    print()

    # Confidence interpretation guide
    print("💡 Confidence Score Interpretation:")
    print("   • > 0.80: High confidence - very likely correct")
    print("   • 0.60-0.80: Medium confidence - probably correct")
    print("   • 0.40-0.60: Low confidence - uncertain classification")
    print("   • < 0.40: Very low confidence - likely misclassification")
    print()

    print("=" * 70)
    print("Demo completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()

"""Demo script showing how to find similar questions from the test set.

Example:
    python demo_similar_questions.py
"""

from pathlib import Path
from service.classifier_service import ClassifierService


def main() -> None:
    # Load trained classifier
    model_dir = Path("version_5/models/classifier")
    print(f"Loading classifier from {model_dir}...")
    svc = ClassifierService.from_pretrained(model_dir)
    
    # Load test set for similarity search
    test_path = Path("version_5/models/data/train-00000-of-00001.json")
    print(f"\nLoading test set from {test_path}...")
    svc.load_test_set(test_path, max_samples=3000)  # Limit for demo purposes
    
    # Example queries
    queries = [
        "Wen 20 Bauarbeiter 50 Stunden brauchen um ein Haus zu bauen, wie lange brauchen 10 Bauarbeiter?",
        "Wen 22 Mninenarbeiter 47 Stunden brauchen um ein Tunnel zu bauen, wie lange brauchen 5 Minnenarbeiter?"
    ]
    
    print("\n" + "="*80)
    print("FINDING SIMILAR QUESTIONS")
    print("="*80)
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 80)
        
        # Find top 3 similar questions
        similar = svc.find_similar(query, top_k=3)
        
        for i, result in enumerate(similar, 1):
            print(f"\n{i}. Similarity: {result['similarity']:.4f}")
            print(f"   Category: {result['category']}")
            print(f"   Problem: {result['problem'][:150]}...")
        
        print()


if __name__ == "__main__":
    main()

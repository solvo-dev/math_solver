"""Simple CLI script to train the MathQA classifier.
This script is a convenience wrapper for `ClassifierService.train` and saves artifacts to disk.

Usage:
    python scripts/train_classifier.py --sample-size 2000 --output models/classifier
"""
import argparse
from pathlib import Path
from math_solver.services.classifier_service import ClassifierService


def parse_args():
    p = argparse.ArgumentParser(description="Train the MathQA classifier (wrapper around ClassifierService)")
    p.add_argument("--sample-size", type=int, default=5000)
    p.add_argument("--output", type=str, default="models/classifier")
    p.add_argument("--device", type=str, default="cpu")
    p.add_argument("--dataset", type=str, default="huggingface:allenai/math_qa")
    return p.parse_args()


def main():
    args = parse_args()
    svc = ClassifierService(model_path=Path(args.output), device=args.device)
    metrics = svc.train(dataset=args.dataset, sample_size=args.sample_size, output_dir=Path(args.output))
    print("Training finished. Metrics:", metrics)


if __name__ == "__main__":
    main()

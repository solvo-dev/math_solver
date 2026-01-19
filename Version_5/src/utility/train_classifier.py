"""Train the MathQA classifier and save artifacts.

Example:
    uv run python train_classifier.py --dataset ../Version_4/MathQA/train.json --sample-size 4000 --output models/classifier
"""

import argparse
from pathlib import Path

from service.classifier_service import ClassifierService

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train MathQA classifier")
    p.add_argument(
        "--dataset",
        type=Path,
        default=Path("models/data/train-00000-of-00001.json"),
        help="Path to training dataset (JSON or Parquet format)",
    )
    p.add_argument("--sample-size", type=int, default=5000, help="Limit number of samples")
    p.add_argument("--output", type=Path, default=Path("models/classifier"), help="Output directory")
    p.add_argument("--device", type=str, default="cpu", help="Device for embeddings (cpu or cuda)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    svc = ClassifierService(model_dir=args.output, device=args.device)
    metrics = svc.train(dataset_path=args.dataset, sample_size=args.sample_size, output_dir=args.output)
    print(f"Training complete. Metrics: {metrics}")
    print(f"Artifacts saved to: {args.output}")


if __name__ == "__main__":
    main()

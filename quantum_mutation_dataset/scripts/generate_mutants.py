from __future__ import annotations

import argparse
import json
from pathlib import Path

from mutation_lib import build_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a quantum mutation dataset from operator-driven seed templates.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Dataset root directory. Defaults to the quantum_mutation_dataset directory.",
    )
    parser.add_argument(
        "--higher-order-per-seed",
        type=int,
        default=2,
        help="Number of higher-order mutants to generate per seed program.",
    )
    args = parser.parse_args()

    summary = build_dataset(args.output_root, higher_order_per_seed=args.higher_order_per_seed)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

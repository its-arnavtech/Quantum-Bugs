from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run selected mutant programs and capture their stdout/stderr.")
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Dataset root directory. Defaults to the quantum_mutation_dataset directory.",
    )
    parser.add_argument("--family", help="Optional mutant family filter, for example bell or grover.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of mutants to execute.")
    parser.add_argument("--timeout", type=int, default=20, help="Per-mutant timeout in seconds.")
    args = parser.parse_args()

    metadata_path = args.dataset_root / "metadata" / "mutants.csv"
    rows = []
    with metadata_path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row["order"] != "first_order":
                continue
            if args.family and row["family"] != args.family:
                continue
            rows.append(row)
            if len(rows) >= args.limit:
                break

    results = []
    for row in rows:
        mutant_path = Path(row["mutant_path"])
        try:
            completed = subprocess.run(
                [sys.executable, str(mutant_path)],
                capture_output=True,
                text=True,
                timeout=args.timeout,
                check=False,
            )
            results.append(
                {
                    "mutation_id": row["mutation_id"],
                    "path": row["mutant_path"],
                    "returncode": completed.returncode,
                    "stdout": completed.stdout.strip(),
                    "stderr": completed.stderr.strip(),
                }
            )
        except Exception as exc:  # pragma: no cover - CLI guardrail
            results.append(
                {
                    "mutation_id": row["mutation_id"],
                    "path": row["mutant_path"],
                    "returncode": None,
                    "stdout": "",
                    "stderr": f"{exc.__class__.__name__}: {exc}",
                }
            )

    output_path = args.dataset_root / "metadata" / "run_report.json"
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "executed": len(results),
                "family": args.family,
                "report_path": str(output_path.as_posix()),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

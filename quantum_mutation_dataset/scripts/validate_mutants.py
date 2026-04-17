from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from mutation_lib import iter_python_files


def parse_file(path: Path) -> tuple[bool, str | None]:
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        return True, None
    except SyntaxError as exc:
        return False, f"{exc.__class__.__name__}: {exc}"


def run_file(path: Path, timeout: int) -> tuple[bool, str | None]:
    try:
        completed = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - defensive CLI handling
        return False, f"{exc.__class__.__name__}: {exc}"

    if completed.returncode == 0:
        return True, completed.stdout.strip()
    stderr = completed.stderr.strip() or completed.stdout.strip()
    return False, stderr


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse and optionally execute generated quantum mutants.")
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Dataset root directory. Defaults to the quantum_mutation_dataset directory.",
    )
    parser.add_argument("--run", action="store_true", help="Execute each Python file after parsing.")
    parser.add_argument("--timeout", type=int, default=20, help="Per-file timeout in seconds when --run is enabled.")
    args = parser.parse_args()

    has_qiskit = importlib.util.find_spec("qiskit") is not None
    files = sorted(iter_python_files([args.dataset_root / "seeds", args.dataset_root / "mutants"]))
    results = []

    for path in files:
        parse_ok, parse_error = parse_file(path)
        run_ok = None
        run_output = None
        if args.run:
            if has_qiskit:
                run_ok, run_output = run_file(path, args.timeout)
            else:
                run_ok = False
                run_output = "Skipped execution because qiskit is not installed in this environment."
        results.append(
            {
                "path": str(path.as_posix()),
                "parse_ok": parse_ok,
                "parse_error": parse_error,
                "run_attempted": args.run,
                "run_ok": run_ok,
                "run_output": run_output,
            }
        )

    output_path = args.dataset_root / "metadata" / "validation_report.json"
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    summary = {
        "files_checked": len(results),
        "parse_failures": sum(1 for item in results if not item["parse_ok"]),
        "run_failures": sum(1 for item in results if item["run_attempted"] and item["run_ok"] is False),
        "qiskit_available": has_qiskit,
        "report_path": str(output_path.as_posix()),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

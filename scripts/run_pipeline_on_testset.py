import os
import sys
import time
import json
import argparse

# Ensure bis-compass/src is importable as package `src`
THIS_DIR = os.path.dirname(__file__)
PACKAGE_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)

from src.pipeline import run_pipeline


def main(input_path: str, output_path: str, top_k: int = 5):
    with open(input_path, "r", encoding="utf-8") as f:
        test_items = json.load(f)

    results = []

    for item in test_items:
        qid = item.get("id")
        query = item.get("query")

        print(f"Running pipeline for {qid}: {query[:80]}...")
        res = run_pipeline(query, top_k=top_k)

        # pipeline returns retrieved_standards as list of dicts
        retrieved = []
        for std in res.get("retrieved_standards", []):
            if isinstance(std, dict):
                retrieved.append(std.get("standard_number", ""))
            else:
                retrieved.append(str(std))

        latency = res.get("latency_seconds", 0.0)

        results.append({
            "id": qid,
            "retrieved_standards": retrieved,
            "latency_seconds": latency,
            "expected_standards": item.get("expected_standards", [])
        })

    with open(output_path, "w", encoding="utf-8") as outf:
        json.dump(results, outf, indent=2, ensure_ascii=False)

    print(f"Wrote pipeline results to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=False, default=os.path.join(PACKAGE_ROOT, "../Bureau of Indian Standards x Sigma Squad AI Hackathon Materials/public_test_set.json"), help="Path to input test set JSON")
    parser.add_argument("--output", required=False, default=os.path.join(PACKAGE_ROOT, "..", "temp_validation_pipeline.json"), help="Path to write results JSON")
    parser.add_argument("--top_k", type=int, default=5)
    args = parser.parse_args()

    # Normalize input path if relative
    input_path = args.input
    if not os.path.isabs(input_path):
        input_path = os.path.abspath(input_path)

    output_path = args.output
    if not os.path.isabs(output_path):
        output_path = os.path.abspath(output_path)

    main(input_path, output_path, top_k=args.top_k)

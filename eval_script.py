import json
import argparse
import sys


def normalize_std(std_string):
    """Normalizes the standard name by removing spaces and converting to lowercase for fair matching."""
    return str(std_string).replace(" ", "").lower()


def evaluate_results(results_file):
    try:
        with open(results_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading results file: {e}")
        sys.exit(1)

    # Try to load the input file (public_test_set.json or submission_test.json)
    # to get expected_standards
    input_file = None
    for filename in ["public_test_set.json", "submission_test.json"]:
        try:
            with open(filename, "r") as f:
                input_data = json.load(f)
                input_file = {item.get("id"): item for item in input_data}
            break
        except:
            pass

    total_queries = len(data)
    if total_queries == 0:
        print("No queries found in the result file.")
        return

    hits_at_3 = 0
    mrr_sum_at_5 = 0.0
    total_latency = 0.0

    for item in data:
        query_id = item.get("id")
        
        # Get expected standards from input file or from the result item itself
        if input_file and query_id in input_file:
            expected_stds = input_file[query_id].get("expected_standards", [])
        else:
            expected_stds = item.get("expected_standards", [])
        
        expected = set(normalize_std(std) for std in expected_stds)
        retrieved = [normalize_std(std) for std in item.get("retrieved_standards", [])]
        latency = item.get("latency_seconds", 0.0)

        total_latency += latency

        # 1. Calculate Hit Rate @3 (Is at least 1 expected standard in top 3?)
        top_3_retrieved = retrieved[:3]
        if any(std in expected for std in top_3_retrieved):
            hits_at_3 += 1

        # 2. Calculate MRR @5 (Mean Reciprocal Rank of first correct standard in top 5)
        top_5_retrieved = retrieved[:5]
        mrr = 0.0
        for rank, std in enumerate(top_5_retrieved, start=1):
            if std in expected:
                mrr = 1.0 / rank
                break  # Only care about the first correct standard
        mrr_sum_at_5 += mrr

    # Calculate Final Metrics
    hit_rate_3 = (hits_at_3 / total_queries) * 100
    mrr_5 = mrr_sum_at_5 / total_queries
    avg_latency = total_latency / total_queries

    print("=" * 40)
    print("   BIS HACKATHON EVALUATION RESULTS")
    print("=" * 40)
    print(f"Total Queries Evaluated : {total_queries}")
    print(f"Hit Rate @3             : {hit_rate_3:.2f}% \t(Target: >80%)")
    print(f"MRR @5                  : {mrr_5:.4f} \t(Target: >0.7)")
    print(f"Avg Latency             : {avg_latency:.2f} sec \t(Target: <5 seconds)")
    print("=" * 40)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate RAG Pipeline Results for BIS Hackathon"
    )
    parser.add_argument(
        "--results",
        type=str,
        required=True,
        help="Path to the participant's output JSON file",
    )
    args = parser.parse_args()

    evaluate_results(args.results)

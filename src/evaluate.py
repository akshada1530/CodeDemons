import json
import argparse
import os

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def evaluate(detected, answer_key):
    score = 0
    total = len(answer_key)
    attempted = 0
    detailed_results = {}

    # detected is like {"1A": true, "1B": false, "2C": true, ...}
    for q_num, correct_option in answer_key.items():
        # Build bubble ID for correct option
        bubble_id = f"{q_num}{correct_option}"

        # Check if that bubble is marked
        is_correct = detected.get(bubble_id, False)

        # Check if student marked any option for this question
        marked_options = [opt for opt, filled in detected.items() if opt.startswith(q_num) and filled]

        if marked_options:
            attempted += 1

        if is_correct and len(marked_options) == 1:
            score += 1
            detailed_results[q_num] = {"marked": marked_options, "result": "correct"}
        elif is_correct and len(marked_options) > 1:
            detailed_results[q_num] = {"marked": marked_options, "result": "multiple marked"}
        elif not is_correct and marked_options:
            detailed_results[q_num] = {"marked": marked_options, "result": "wrong"}
        else:
            detailed_results[q_num] = {"marked": [], "result": "unattempted"}

    return {
        "score": score,
        "total": total,
        "attempted": attempted,
        "accuracy": round((score / total) * 100, 2),
        "details": detailed_results
    }

def main():
    parser = argparse.ArgumentParser(description="Evaluate OMR Results")
    parser.add_argument("--detected", required=True, help="Path to detected results JSON")
    parser.add_argument("--key", required=True, help="Path to answer key JSON")
    parser.add_argument("--out", required=True, help="Path to save evaluation results JSON")
    args = parser.parse_args()

    # Validate paths
    if not os.path.exists(args.detected) or not os.path.exists(args.key):
        print("❌ Error: detected or key file not found.")
        return

    # Load files
    detected = load_json(args.detected)
    answer_key = load_json(args.key)

    # Evaluate
    results = evaluate(detected, answer_key)

    # Save results
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(results, f, indent=4)

    print(f"✅ Evaluation complete! Saved at {args.out}")
    print(f"Score: {results['score']} / {results['total']} ({results['accuracy']}%)")

if __name__ == "__main__":
    main()
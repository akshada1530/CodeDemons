# src/omr_pipeline.py
import json
import argparse
import os
from bubble_detector import detect_bubbles

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def evaluate_answers(detected_answers, answer_key):
    results = {
        "questions": {},
        "score": 0,
        "attempted": 0,
        "correct": 0
    }

    for q_no, chosen_opt in detected_answers.items():
        results["attempted"] += 1
        correct_opt = answer_key.get(q_no)

        if chosen_opt == correct_opt:
            results["correct"] += 1
            results["score"] += 1

        results["questions"][q_no] = {
            "chosen": chosen_opt,
            "correct": correct_opt,
            "is_correct": (chosen_opt == correct_opt),
        }

    return results

def main():
    parser = argparse.ArgumentParser(description="OMR Evaluation Pipeline")
    parser.add_argument("--img", required=True, help="Path to scanned OMR sheet")
    parser.add_argument("--template", required=True, help="Path to template JSON")
    parser.add_argument("--answerkey", required=True, help="Path to answer key JSON")
    parser.add_argument("--out", required=True, help="Path to save results JSON")
    args = parser.parse_args()

    # Step 1: Detect answers from student sheet
    detected_answers = detect_bubbles(
        args.img,
        args.template,
        "results/tmp_detected.json"  # temp file
    )

    # Step 2: Load answer key
    answer_key = load_json(args.answerkey)

    # Step 3: Evaluate answers
    results = evaluate_answers(detected_answers, answer_key)

    # Step 4: Save final results
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)

    print(f"[SUCCESS] Final evaluation saved to {args.out}")


if __name__ == "__main__":
    main()
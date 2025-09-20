import argparse
import json
import os
from bubble_detector import detect_bubbles

def evaluate_student(img_path, template_path, answer_key_path, output_path=None, thresh=180):
    # Detect bubbles
    detected_answers = detect_bubbles(img_path, template_path, None, thresh)

    # Load answer key
    with open(answer_key_path, "r") as f:
        answer_key = json.load(f)

    # Evaluate
    total_questions = len(answer_key)
    correct = 0
    attempted = 0
    wrong = 0

    for q_no, correct_ans in answer_key.items():
        student_ans = detected_answers.get(q_no)
        if student_ans:
            attempted += 1
            if student_ans == correct_ans:
                correct += 1
            else:
                wrong += 1

    score = correct
    percentage = (correct / total_questions) * 100 if total_questions else 0

    # Prepare results
    results = {
        "student_image": img_path,
        "total_questions": total_questions,
        "attempted": attempted,
        "correct": correct,
        "wrong": wrong,
        "score": score,
        "percentage": percentage,
        "answers_detected": detected_answers
    }

    # Save JSON
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"[SUCCESS] Final evaluation saved to {output_path}")

    # Print summary
    print("\n=== Evaluation Summary ===")
    print(f"Student Image: {img_path}")
    print(f"Total Questions: {total_questions}")
    print(f"Attempted: {attempted}")
    print(f"Correct: {correct}")
    print(f"Wrong: {wrong}")
    print(f"Score: {score}")
    print(f"Percentage: {percentage:.2f}%")
    print("==========================\n")

    return results

def main():
    parser = argparse.ArgumentParser(description="OMR Evaluation Pipeline")
    parser.add_argument("--img", help="Path to student image or folder")
    parser.add_argument("--template", required=True, help="Path to template JSON")
    parser.add_argument("--answerkey", required=True, help="Path to answer key JSON")
    parser.add_argument("--out", help="Output JSON path or folder")
    parser.add_argument("--thresh", type=int, default=180, help="Threshold for bubble detection")
    args = parser.parse_args()

    # Check if img path is a folder
    if os.path.isdir(args.img):
        student_files = [f for f in os.listdir(args.img) if f.lower().endswith(('.jpg','.jpeg','.png'))]
        for idx, file in enumerate(student_files, start=1):
            img_path = os.path.join(args.img, file)
            output_path = None
            if args.out:
                out_folder = args.out
                os.makedirs(out_folder, exist_ok=True)
                output_path = os.path.join(out_folder, f"{os.path.splitext(file)[0]}_results.json")
            evaluate_student(img_path, args.template, args.answerkey, output_path, args.thresh)
    else:
        # Single file
        evaluate_student(args.img, args.template, args.answerkey, args.out, args.thresh)

if __name__ == "__main__":
    main()
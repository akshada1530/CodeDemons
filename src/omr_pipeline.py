import cv2
import json
import os

def detect_bubbles(image_path, template_path, output_path=None, thresh=150):
    """
    Detect filled bubbles on a student OMR sheet.

    Args:
        image_path (str): Path to student image
        template_path (str): Path to template JSON
        output_path (str, optional): Where to save detected answers JSON
        thresh (int, optional): Threshold value for binary inversion

    Returns:
        dict: Detected answers {question: selected_option}
    """

    # Load template
    with open(template_path, "r") as f:
        template_data = json.load(f)
        template = template_data.get("questions", template_data)

    # Load image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"[ERROR] Could not read image: {image_path}")
        return {}

    # Threshold for bubble detection
    _, binary = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY_INV)

    detected_answers = {}

    for q_no, options in template.items():
        filled = None

        # Case 1: options is a dict → {"A": [x,y], "B": [x,y]}
        if isinstance(options, dict):
            iterable = options.items()

        # Case 2: options is a list → [[x,y], [x,y], ...]
        elif isinstance(options, list):
            iterable = [(str(i), coords) for i, coords in enumerate(options)]

        else:
            raise ValueError(f"Unsupported template format for question {q_no}: {options}")

        for opt, coords in iterable:
            if not isinstance(coords, (list, tuple)) or len(coords) != 2:
                continue

            x, y = coords
            roi = binary[y-10:y+10, x-10:x+10]
            if roi.size == 0:
                continue

            non_zero = cv2.countNonZero(roi)
            print(f"[DEBUG] Q{q_no} {opt}: non_zero={non_zero}")

            if non_zero > 20:  # threshold for bubble detection
                filled = opt

        detected_answers[q_no] = filled

    # Save output if provided
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(detected_answers, f, indent=2)
        print(f"[SUCCESS] Bubble detection results saved to {output_path}")

    return detected_answers


def evaluate_answers(detected_answers, answer_key):
    """
    Compare detected answers with answer key.

    Args:
        detected_answers (dict): {question: option}
        answer_key (dict): {question: correct_option}

    Returns:
        dict: {total_score, subject_scores, per_question}
    """

    total_score = 0
    subject_scores = {}
    per_question = {}

    for q_no, correct_ans in answer_key.items():
        student_ans = detected_answers.get(q_no)
        is_correct = (student_ans == correct_ans)

        if is_correct:
            total_score += 1

        per_question[q_no] = {
            "student": student_ans,
            "correct": correct_ans,
            "is_correct": is_correct,
        }

        # You can extend with subject-specific keys if available
        subject = "General"
        subject_scores.setdefault(subject, 0)
        if is_correct:
            subject_scores[subject] += 1

    return {
        "total_score": total_score,
        "subject_scores": subject_scores,
        "per_question": per_question,
    }
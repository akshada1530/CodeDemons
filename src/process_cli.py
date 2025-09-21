import argparse
import os
import cv2
import json
from omr_pipeline import detect_bubbles, evaluate_answers

def process_image(img_path, template_path, key_path, out_dir="output", thresh=150):
    """
    Run OMR pipeline on a single image, save overlay and JSON.
    """
    os.makedirs(out_dir, exist_ok=True)

    # Step 1: Detect bubbles
    detected_answers = detect_bubbles(img_path, template_path, output_path=None, thresh=thresh)

    # Step 2: Load answer key
    with open(key_path, "r") as f:
        answer_key = json.load(f)

    # Step 3: Evaluate answers
    res = evaluate_answers(detected_answers, answer_key)

    # Step 4: Save overlay image (template points + detected answers)
    img = cv2.imread(img_path)
    img_overlay = img.copy()

    with open(template_path, "r") as f:
        template = json.load(f).get("questions", {})

    for q_no, options in template.items():
        # Case 1: options dict
        if isinstance(options, dict):
            iterable = options.items()
        # Case 2: options list
        elif isinstance(options, list):
            iterable = [(str(i), coords) for i, coords in enumerate(options)]
        else:
            continue

        for opt, coords in iterable:
            if not isinstance(coords, (list, tuple)) or len(coords) != 2:
                continue
            x, y = coords
            color = (0, 255, 0) if detected_answers.get(q_no) == opt else (0, 0, 255)
            cv2.circle(img_overlay, (x, y), 8, color, 2)

    overlay_path = os.path.join(out_dir, os.path.basename(img_path).replace(".jpg", "_overlay.png"))
    cv2.imwrite(overlay_path, img_overlay)

    # Step 5: Save JSON
    json_path = os.path.join(out_dir, os.path.basename(img_path).replace(".jpg", "_results.json"))
    with open(json_path, "w") as f:
        json.dump({"detected_answers": detected_answers, "evaluation": res}, f, indent=2)

    return res, overlay_path, json_path


def main():
    parser = argparse.ArgumentParser(description="Run OMR pipeline on a single image")
    parser.add_argument("--img", required=True, help="Path to student image")
    parser.add_argument("--template", required=True, help="Path to template JSON")
    parser.add_argument("--key", required=True, help="Path to answer key JSON")
    parser.add_argument("--out", default="output", help="Output folder")
    parser.add_argument("--thresh", type=int, default=150, help="Threshold for bubble detection")
    args = parser.parse_args()

    res, overlay, j = process_image(args.img, args.template, args.key, out_dir=args.out, thresh=args.thresh)
    print("Result total:", res.get("total_score"))
    print("Subject scores:", res.get("subject_scores"))
    print("Overlay saved to:", overlay)
    print("JSON saved to:", j)


if __name__ == "__main__":
    main()
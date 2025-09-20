import cv2
import json
import os

def detect_bubbles(image_path, template_path, output_path=None, thresh=180):
    # Load template
    with open(template_path, "r") as f:
        template_data = json.load(f)
        template = template_data.get("questions", template_data)  # ✅ flexible fix

    # Load image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"[ERROR] Could not read image: {image_path}")
        return {}

    # Threshold for bubble detection
    _, binary = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY_INV)

    detected_answers = {}

    for q_no, options in template.items():
        filled = None

        # Ensure options is dict
        if isinstance(options, dict):
            opt_iter = options.items()
        else:
            # If it's a list, wrap it in dict with dummy option name
            opt_iter = [("A", options)]

        for opt, (x, y) in opt_iter:
            roi = binary[y-10:y+10, x-10:x+10]
            if roi.size == 0:
                continue

            non_zero = cv2.countNonZero(roi)
            if non_zero > 50:
                filled = opt

        detected_answers[q_no] = filled

    # Save output if path provided
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(detected_answers, f, indent=2)
        print(f"[SUCCESS] Bubble detection results saved to {output_path}")

    return detected_answers
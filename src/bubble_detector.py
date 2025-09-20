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

    # Overlay template points for verification
    img_overlay = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for q_no, options in template.items():
        if isinstance(options, dict):
            for opt, (x, y) in options.items():
                cv2.circle(img_overlay, (x, y), 5, (0, 0, 255), -1)
    cv2.imshow("Template Overlay", img_overlay)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Threshold for bubble detection
    _, binary = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY_INV)

    # Visualize binary threshold
    cv2.imshow("Binary Image", binary)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    detected_answers = {}

    for q_no, options in template.items():
        filled = None

        # Ensure options is dict
        if isinstance(options, dict):
            opt_iter = options.items()
        else:
            # If it's a list, wrap in dict
            opt_iter = [("A", options)]

        for opt, (x, y) in opt_iter:
            roi = binary[y-10:y+10, x-10:x+10]
            if roi.size == 0:
                continue

            non_zero = cv2.countNonZero(roi)
            if non_zero > 20:  # reduced threshold to detect faint bubbles
                filled = opt

        detected_answers[q_no] = filled

    # Save output if provided
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(detected_answers, f, indent=2)
        print(f"[SUCCESS] Bubble detection results saved to {output_path}")

    return detected_answers
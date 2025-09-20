import cv2
import json
import argparse
import os

def detect_bubbles(image_path, template_path, output_path, threshold=0.5):
    """
    Detect filled/unfilled bubbles using template.
    """

    # Load image (grayscale)
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print("❌ Error: Could not load image.")
        return

    # Load template JSON
    with open(template_path, "r") as f:
        template = json.load(f)

    results = {}

    for bubble_id, (x, y) in template.items():
        # Define small region around bubble center
        roi_size = 20  # pixels around the point (adjust if needed)
        x1, y1 = max(0, x - roi_size), max(0, y - roi_size)
        x2, y2 = min(img.shape[1], x + roi_size), min(img.shape[0], y + roi_size)

        roi = img[y1:y2, x1:x2]

        # Calculate fill ratio (how dark the bubble is)
        mean_intensity = cv2.mean(roi)[0]  # average pixel value
        fill_ratio = 1 - (mean_intensity / 255.0)  # normalized darkness

        # Decide filled/unfilled
        filled = fill_ratio > threshold
        results[bubble_id] = "filled" if filled else "empty"

        # Draw on image for visualization
        color = (0, 0, 255) if filled else (0, 255, 0)
        cv2.circle(img, (x, y), 10, color, 2)

    # Save results JSON
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)

    print(f"✅ Detection complete. Results saved at {output_path}")

    # Show detected bubbles
    cv2.imshow("Detected Bubbles", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="OMR Bubble Detector")
    parser.add_argument("--img", required=True, help="Path to preprocessed OMR sheet image")
    parser.add_argument("--template", required=True, help="Path to template JSON file")
    parser.add_argument("--out", required=True, help="Path to save detected results JSON")
    parser.add_argument("--thresh", type=float, default=0.5, help="Threshold for marking filled bubbles (0-1)")

    args = parser.parse_args()

    detect_bubbles(args.img, args.template, args.out, args.thresh)


if __name__ == "__main__":
    main()
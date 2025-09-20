import cv2
import json
import argparse
import os

# Global variables
points = {}
current_image = None

def click_event(event, x, y, flags, param):
    global current_image, points

    if event == cv2.EVENT_LBUTTONDOWN:
        # Ask user for bubble ID (example: "1A")
        bubble_id = input(f"Enter bubble ID for point ({x},{y}): ").strip()

        if bubble_id:
            # Store the coordinate
            points[bubble_id] = (int(x), int(y))

            # Draw red circle on clicked point
            cv2.circle(current_image, (x, y), 8, (0, 0, 255), -1)
            cv2.imshow("OMR Template Builder", current_image)


def main():
    global current_image, points

    parser = argparse.ArgumentParser(description="OMR Template Builder")
    parser.add_argument("--img", required=True, help="Path to input OMR sheet image")
    parser.add_argument("--out", required=True, help="Path to save JSON template")

    args = parser.parse_args()

    # Validate image path
    if not os.path.exists(args.img):
        print("❌ Error: Image path does not exist.")
        return

    # Create output folder if not exists
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    # Load image
    current_image = cv2.imread(args.img)

    if current_image is None:
        print("❌ Error: Could not load image.")
        return

    # Make window resizable and set default size
    cv2.namedWindow("OMR Template Builder", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("OMR Template Builder", 1000, 1200)

    # Show window
    cv2.imshow("OMR Template Builder", current_image)
    cv2.setMouseCallback("OMR Template Builder", click_event)

    print("✅ Click on bubbles and enter IDs (like 1A, 1B).")
    print("➡ Press 'q' to quit and save.")

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cv2.destroyAllWindows()

    # Save points to JSON
    with open(args.out, "w") as f:
        json.dump(points, f, indent=4)

    print(f"✅ Template saved at {args.out}")


if __name__ == "__main__":
    main()
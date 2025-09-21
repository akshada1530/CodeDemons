# src/template_builder.py
import cv2
import json
import os
import argparse

def create_template(image_path, save_path=None):
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        return

    img = cv2.imread(image_path)
    if img is None:
        print(f"[ERROR] Could not read the image. Check the file format.")
        return

    # Original dimensions
    orig_height, orig_width = img.shape[:2]

    # Resize for display (so large sheets fit screen)
    max_width, max_height = 1200, 800
    scale = min(max_width / orig_width, max_height / orig_height, 1.0)
    display_img = cv2.resize(img, (int(orig_width*scale), int(orig_height*scale)))
    clone = display_img.copy()

    points = {}

    # Mouse click event
    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            q_no = input("Enter Question Number and Option (e.g., 1A, 1B, 2C): ").strip()
            if len(q_no) < 2:
                print("❌ Invalid format. Use e.g., 1A, 2B")
                return

            question = q_no[:-1]
            option = q_no[-1].upper()
            if not question.isdigit():
                print("❌ Question number must be numeric")
                return

            # Scale click coordinates back to original image size
            orig_x = int(x / scale)
            orig_y = int(y / scale)

            # Save in nested dict
            points.setdefault(question, {})[option] = [orig_x, orig_y]

            # Draw circle on display image
            cv2.circle(clone, (x, y), 6, (0, 0, 255), -1)
            cv2.putText(clone, q_no, (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.imshow("Template Builder", clone)

    # Create resizable window
    cv2.namedWindow("Template Builder", cv2.WINDOW_NORMAL)
    cv2.imshow("Template Builder", clone)
    cv2.setMouseCallback("Template Builder", click_event)
    cv2.resizeWindow("Template Builder", 1200, 800)

    print("👉 Click each bubble and type Question+Option in console (e.g., 1A, 1B, 2C).")
    print("✅ Press any key in the window when finished to save template.")

    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Final JSON
    template_json = {"questions": points}

    # Determine save path
    if save_path is None:
        save_path = os.path.join("data", "templates", "version_A_template.json")
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, "w") as f:
        json.dump(template_json, f, indent=2)

    print(f"[SUCCESS] Template saved to {save_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OMR Template Builder")
    parser.add_argument("--img", required=True, help="Path to clean OMR sheet image")
    parser.add_argument("--out", help="Path to save template JSON (optional)")
    args = parser.parse_args()

    create_template(args.img, args.out)
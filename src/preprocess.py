import cv2
import numpy as np

def load_and_preprocess(image_path, debug=False):
    # Step 1: Load image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    orig = image.copy()

    # Step 2: Convert to grayscale and enhance contrast
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    # Step 3: Blur and detect edges
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 30, 150)

    # Step 4: Adaptive thresholding (binary image)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )

    # Step 5: Combine edges and threshold for stronger contour detection
    combined = cv2.bitwise_or(edges, thresh)

    # Step 6: Find contours
    contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    sheet_contour = None
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            sheet_contour = approx
            break

    # Fallback: if no 4-point contour found, use the largest contour
    if sheet_contour is None and len(contours) > 0:
        sheet_contour = contours[0]

    if sheet_contour is None:
        raise Exception("Could not find sheet boundary.")

    # Step 7: Perspective transform
    warped = four_point_transform(orig, sheet_contour.reshape(4, 2))

    # Step 8: Convert to grayscale + Otsu threshold
    gray_warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    _, thresh_warped = cv2.threshold(gray_warped, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    if debug:
        # Draw all contours for debugging
        debug_img = orig.copy()
        cv2.drawContours(debug_img, contours, -1, (0, 255, 0), 2)
        cv2.imshow("All Contours", debug_img)
        cv2.imshow("Edges", edges)
        cv2.imshow("Adaptive Thresh", thresh)
        cv2.imshow("Warped Sheet", warped)
        cv2.imshow("Thresholded Warped", thresh_warped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return warped, thresh_warped


def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped


if __name__ == "__main__":
    warped, thresh = load_and_preprocess("data/samples/clean_sheet.jpg", debug=True)
    cv2.imwrite("output/warped.jpg", warped)
    cv2.imwrite("output/warped_thresh.jpg", thresh)
    print("✅ Preprocessing done, images saved in output/")
    warped, thresh = load_and_preprocess("data/samples/clean_sheet.jpg", debug=False)
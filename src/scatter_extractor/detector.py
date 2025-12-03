import cv2
import numpy as np
from typing import List, Tuple, Optional


def detect_points(
    image_path: str,
    min_area: int = 5,
    max_area: int = 600,
    min_circularity: float = 0.3,
    threshold_value: int = 80,
    plot_bounds: Optional[Tuple[int, int, int, int]] = None
) -> List[Tuple[int, int]]:
    """
    Detect scatter points in an image.

    Args:
        image_path: Path to the image file
        min_area: Minimum contour area to consider
        max_area: Maximum contour area to consider
        min_circularity: Minimum circularity (0-1) to filter non-circular shapes
        threshold_value: Binary threshold value for point detection
        plot_bounds: Optional (x_min, y_min, x_max, y_max) to restrict detection area

    Returns:
        List of (pixel_x, pixel_y) tuples for each detected point.
    """
    # Load image and convert to grayscale
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply binary threshold to isolate dark points
    # Using THRESH_BINARY_INV to make dark points white
    _, thresh = cv2.threshold(blurred, threshold_value, 255, cv2.THRESH_BINARY_INV)

    # Find contours of detected blobs
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected_points = []

    for contour in contours:
        # Calculate contour properties
        area = cv2.contourArea(contour)

        # Filter by area
        if area < min_area or area > max_area:
            continue

        # Calculate circularity: 4 * pi * area / perimeter^2
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue

        circularity = 4 * np.pi * area / (perimeter * perimeter)

        # Filter by circularity (points should be roughly circular)
        if circularity < min_circularity:
            continue

        # Find centroid using moments
        M = cv2.moments(contour)
        if M["m00"] == 0:
            continue

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        # Filter by plot bounds if provided
        if plot_bounds is not None:
            x_min, y_min, x_max, y_max = plot_bounds
            if not (x_min <= cx <= x_max and y_min <= cy <= y_max):
                continue

        detected_points.append((cx, cy))

    return detected_points

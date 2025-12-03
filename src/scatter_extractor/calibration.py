import cv2
import numpy as np
from typing import Tuple, Optional
from .models import AxisConfig


def detect_plot_bounds(image_path: str) -> Tuple[int, int, int, int]:
    """
    Auto-detect the plot area boundaries by finding axis lines.

    Returns:
        (x_min_pixel, y_min_pixel, x_max_pixel, y_max_pixel).

    Algorithm:
        1. Detect lines using Hough transform
        2. Find prominent horizontal and vertical lines
        3. Identify innermost lines that form the plot boundary
    """
    # Load image and convert to grayscale
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape

    # Apply edge detection
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Detect lines using Hough transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100,
                            minLineLength=50, maxLineGap=10)

    if lines is None:
        # Fallback: use image margins with some padding
        padding = 50
        return (padding, padding, width - padding, height - padding)

    # Separate horizontal and vertical lines
    horizontal_lines = []
    vertical_lines = []

    for line in lines:
        x1, y1, x2, y2 = line[0]

        # Calculate angle
        if abs(x2 - x1) < 10:  # Nearly vertical
            vertical_lines.append(x1)
        elif abs(y2 - y1) < 10:  # Nearly horizontal
            horizontal_lines.append(y1)

    if not horizontal_lines or not vertical_lines:
        # Fallback
        padding = 50
        return (padding, padding, width - padding, height - padding)

    # Find the outermost lines that represent the plot frame
    # We want lines near the edges but not at the very edge (axis lines, not borders)
    # Left boundary: leftmost vertical line (but allow some margin from edge)
    left_lines = [x for x in vertical_lines if 20 < x < width * 0.3]
    x_min = min(left_lines) if left_lines else 50

    # Right boundary: rightmost vertical line
    right_lines = [x for x in vertical_lines if width * 0.7 < x < width - 20]
    x_max = max(right_lines) if right_lines else width - 50

    # Top boundary: topmost horizontal line
    top_lines = [y for y in horizontal_lines if 20 < y < height * 0.3]
    y_min = min(top_lines) if top_lines else 50

    # Bottom boundary: bottommost horizontal line
    bottom_lines = [y for y in horizontal_lines if height * 0.7 < y < height - 20]
    y_max = max(bottom_lines) if bottom_lines else height - 50

    return (int(x_min), int(y_min), int(x_max), int(y_max))


def pixel_to_data(
    pixel_x: int,
    pixel_y: int,
    axis_config: AxisConfig
) -> Tuple[float, float]:
    """
    Convert pixel coordinates to data coordinates.

    Note: Image y-axis is inverted (0 at top), so we flip it.

    Args:
        pixel_x: X coordinate in pixels
        pixel_y: Y coordinate in pixels
        axis_config: Axis configuration with pixel and data bounds

    Returns:
        (data_x, data_y) tuple
    """
    def round_to_half(x):
        return round(x * 2) / 2

    # Calculate data x coordinate
    data_x = axis_config.x_min + \
             (pixel_x - axis_config.pixel_x_min) / \
             (axis_config.pixel_x_max - axis_config.pixel_x_min) * \
             (axis_config.x_max - axis_config.x_min)

    # Calculate data y coordinate (flip y-axis since image origin is top-left)
    data_y = axis_config.y_max - \
             (pixel_y - axis_config.pixel_y_min) / \
             (axis_config.pixel_y_max - axis_config.pixel_y_min) * \
             (axis_config.y_max - axis_config.y_min)

    data_x = round_to_half(data_x)
    data_y = round_to_half(data_y)

    return (data_x, data_y)


def calibrate_from_image(
    image_path: str,
    x_range: Tuple[float, float],
    y_range: Tuple[float, float],
    manual_bounds: Optional[Tuple[int, int, int, int]] = None
) -> AxisConfig:
    """
    Create axis configuration from image and known data ranges.

    Args:
        image_path: Path to the image file
        x_range: (x_min, x_max) tuple for data range
        y_range: (y_min, y_max) tuple for data range
        manual_bounds: Optional (x_min_px, y_min_px, x_max_px, y_max_px) tuple

    Returns:
        AxisConfig object with all calibration data

    If manual_bounds not provided, auto-detect using detect_plot_bounds().
    """
    if manual_bounds is not None:
        pixel_x_min, pixel_y_min, pixel_x_max, pixel_y_max = manual_bounds
    else:
        pixel_x_min, pixel_y_min, pixel_x_max, pixel_y_max = detect_plot_bounds(image_path)

    return AxisConfig(
        x_min=x_range[0],
        x_max=x_range[1],
        y_min=y_range[0],
        y_max=y_range[1],
        pixel_x_min=pixel_x_min,
        pixel_x_max=pixel_x_max,
        pixel_y_min=pixel_y_min,
        pixel_y_max=pixel_y_max
    )

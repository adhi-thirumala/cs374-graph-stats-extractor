"""Scatter plot coordinate extractor.

A Python CLI tool that extracts (x, y) coordinate pairs from scatter plot images.
"""

from .models import AxisConfig, DetectedPoint, ExtractionResult
from .detector import detect_points
from .calibration import calibrate_from_image, pixel_to_data, detect_plot_bounds
from .stats import compute_statistics, to_dataframe, export_csv, export_json

__version__ = "0.1.0"

__all__ = [
    "AxisConfig",
    "DetectedPoint",
    "ExtractionResult",
    "detect_points",
    "calibrate_from_image",
    "pixel_to_data",
    "detect_plot_bounds",
    "compute_statistics",
    "to_dataframe",
    "export_csv",
    "export_json",
]

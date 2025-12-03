from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AxisConfig:
    """Configuration for axis scaling."""
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    # Pixel boundaries of the plot area (auto-detected or manual)
    pixel_x_min: Optional[int] = None
    pixel_x_max: Optional[int] = None
    pixel_y_min: Optional[int] = None  # Note: y is inverted in image coords
    pixel_y_max: Optional[int] = None


@dataclass
class DetectedPoint:
    """A detected point with both pixel and data coordinates."""
    pixel_x: int
    pixel_y: int
    data_x: Optional[float] = None
    data_y: Optional[float] = None


@dataclass
class ExtractionResult:
    """Complete extraction result."""
    points: List[DetectedPoint]
    axis_config: AxisConfig
    image_path: str

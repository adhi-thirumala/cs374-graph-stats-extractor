# System Design Document: Scatter Plot Coordinate Extractor

## Project Overview

A Python CLI tool that extracts (x, y) coordinate pairs from scatter plot images, enabling statistical analysis on the underlying data. The tool uses computer vision to detect points and map their pixel positions to data coordinates based on axis scales.

## Goals

1. Extract all visible data points from a scatter plot image
2. Map pixel coordinates to actual data values using detected/provided axis scales
3. Output coordinate pairs in a format suitable for statistical analysis (CSV, JSON)
4. Provide basic statistical summary of extracted data

## Tech Stack

- **Python 3.11+**
- **UV** for dependency management
- **OpenCV (opencv-python)** for image processing
- **NumPy** for numerical operations
- **Pandas** for data handling and CSV export
- **Click** for CLI interface
- **Pillow** for image loading fallback

---

## Project Structure

```
scatter-extractor/
├── pyproject.toml
├── README.md
├── src/
│   └── scatter_extractor/
│       ├── __init__.py
│       ├── cli.py              # CLI entry point
│       ├── detector.py         # Point detection logic
│       ├── calibration.py      # Axis calibration & coordinate mapping
│       ├── stats.py            # Statistical analysis utilities
│       └── models.py           # Data classes
├── tests/
│   ├── __init__.py
│   ├── test_detector.py
│   └── test_calibration.py
└── examples/
    └── sample_plot.png
```

---

## Module Specifications

### 1. `models.py` - Data Classes

```python
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class AxisConfig:
    """Configuration for axis scaling."""
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    # Pixel boundaries of the plot area (auto-detected or manual)
    pixel_x_min: int = None
    pixel_x_max: int = None
    pixel_y_min: int = None  # Note: y is inverted in image coords
    pixel_y_max: int = None

@dataclass
class DetectedPoint:
    """A detected point with both pixel and data coordinates."""
    pixel_x: int
    pixel_y: int
    data_x: float = None
    data_y: float = None

@dataclass
class ExtractionResult:
    """Complete extraction result."""
    points: List[DetectedPoint]
    axis_config: AxisConfig
    image_path: str
```

### 2. `detector.py` - Point Detection

**Purpose:** Detect scatter plot points in an image.

**Algorithm:**
1. Load image and convert to grayscale
2. Apply Gaussian blur to reduce noise
3. Use adaptive thresholding or simple threshold to isolate dark points
4. Find contours of detected blobs
5. Filter contours by:
   - Area (min/max to exclude noise and large shapes like axis lines)
   - Circularity (points should be roughly circular)
6. Extract centroid of each valid contour
7. Return list of pixel coordinates

**Key Function:**
```python
def detect_points(
    image_path: str,
    min_area: int = 10,
    max_area: int = 500,
    min_circularity: float = 0.5,
    threshold_value: int = 100,
    plot_bounds: Tuple[int, int, int, int] = None  # (x_min, y_min, x_max, y_max)
) -> List[Tuple[int, int]]:
    """
    Detect scatter points in an image.
    
    Returns list of (pixel_x, pixel_y) tuples for each detected point.
    """
```

**Implementation Notes:**
- Use `cv2.findContours` with `cv2.RETR_EXTERNAL`
- Calculate circularity as `4 * pi * area / perimeter^2`
- Use `cv2.moments` to find centroid of each contour
- Filter points to only those within plot_bounds if provided

### 3. `calibration.py` - Coordinate Mapping

**Purpose:** Map pixel coordinates to data coordinates.

**Key Functions:**

```python
def detect_plot_bounds(image_path: str) -> Tuple[int, int, int, int]:
    """
    Auto-detect the plot area boundaries by finding axis lines.
    
    Returns (x_min_pixel, y_min_pixel, x_max_pixel, y_max_pixel).
    
    Algorithm:
    1. Detect lines using Hough transform
    2. Find prominent horizontal and vertical lines
    3. Identify innermost lines that form the plot boundary
    """

def pixel_to_data(
    pixel_x: int,
    pixel_y: int,
    axis_config: AxisConfig
) -> Tuple[float, float]:
    """
    Convert pixel coordinates to data coordinates.
    
    Note: Image y-axis is inverted (0 at top), so we flip it.
    
    data_x = x_min + (pixel_x - pixel_x_min) / (pixel_x_max - pixel_x_min) * (x_max - x_min)
    data_y = y_max - (pixel_y - pixel_y_min) / (pixel_y_max - pixel_y_min) * (y_max - y_min)
    """

def calibrate_from_image(
    image_path: str,
    x_range: Tuple[float, float],
    y_range: Tuple[float, float],
    manual_bounds: Tuple[int, int, int, int] = None
) -> AxisConfig:
    """
    Create axis configuration from image and known data ranges.
    
    If manual_bounds not provided, auto-detect using detect_plot_bounds().
    """
```

### 4. `stats.py` - Statistical Analysis

**Purpose:** Provide basic statistical analysis of extracted data.

```python
import numpy as np
from typing import List, Dict, Any
from .models import DetectedPoint

def compute_statistics(points: List[DetectedPoint]) -> Dict[str, Any]:
    """
    Compute basic statistics on extracted points.
    
    Returns dict with:
    - count: number of points
    - x_mean, x_std, x_min, x_max
    - y_mean, y_std, y_min, y_max
    - correlation: Pearson correlation coefficient
    - covariance: covariance between x and y
    """

def to_dataframe(points: List[DetectedPoint]):
    """Convert points to pandas DataFrame."""

def export_csv(points: List[DetectedPoint], output_path: str):
    """Export points to CSV file."""

def export_json(points: List[DetectedPoint], output_path: str):
    """Export points to JSON file."""
```

### 5. `cli.py` - Command Line Interface

```python
import click
from .detector import detect_points
from .calibration import calibrate_from_image, pixel_to_data
from .stats import compute_statistics, export_csv, export_json
from .models import DetectedPoint, ExtractionResult

@click.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.option('--x-min', type=float, required=True, help='Minimum x-axis value')
@click.option('--x-max', type=float, required=True, help='Maximum x-axis value')
@click.option('--y-min', type=float, required=True, help='Minimum y-axis value')
@click.option('--y-max', type=float, required=True, help='Maximum y-axis value')
@click.option('--output', '-o', type=click.Path(), help='Output file path (CSV or JSON)')
@click.option('--format', 'fmt', type=click.Choice(['csv', 'json']), default='csv')
@click.option('--stats/--no-stats', default=True, help='Print statistics')
@click.option('--threshold', type=int, default=100, help='Binary threshold for point detection')
@click.option('--min-area', type=int, default=10, help='Minimum contour area')
@click.option('--max-area', type=int, default=500, help='Maximum contour area')
@click.option('--bounds', nargs=4, type=int, default=None, 
              help='Manual plot bounds: x_min_px y_min_px x_max_px y_max_px')
def extract(image_path, x_min, x_max, y_min, y_max, output, fmt, stats, 
            threshold, min_area, max_area, bounds):
    """
    Extract coordinate pairs from a scatter plot image.
    
    Example:
        scatter-extractor plot.png --x-min 0 --x-max 50 --y-min 0 --y-max 50 -o data.csv
    """
    # 1. Calibrate axis mapping
    axis_config = calibrate_from_image(
        image_path,
        x_range=(x_min, x_max),
        y_range=(y_min, y_max),
        manual_bounds=bounds
    )
    
    # 2. Detect points
    pixel_points = detect_points(
        image_path,
        min_area=min_area,
        max_area=max_area,
        threshold_value=threshold,
        plot_bounds=(axis_config.pixel_x_min, axis_config.pixel_y_min,
                     axis_config.pixel_x_max, axis_config.pixel_y_max)
    )
    
    # 3. Convert to data coordinates
    points = []
    for px, py in pixel_points:
        dx, dy = pixel_to_data(px, py, axis_config)
        points.append(DetectedPoint(px, py, dx, dy))
    
    # 4. Output results
    click.echo(f"Detected {len(points)} points")
    
    if stats:
        statistics = compute_statistics(points)
        click.echo(f"\nStatistics:")
        click.echo(f"  X: mean={statistics['x_mean']:.2f}, std={statistics['x_std']:.2f}")
        click.echo(f"  Y: mean={statistics['y_mean']:.2f}, std={statistics['y_std']:.2f}")
        click.echo(f"  Correlation: {statistics['correlation']:.3f}")
    
    if output:
        if fmt == 'csv':
            export_csv(points, output)
        else:
            export_json(points, output)
        click.echo(f"\nData exported to {output}")


if __name__ == '__main__':
    extract()
```

---

## `pyproject.toml`

```toml
[project]
name = "scatter-extractor"
version = "0.1.0"
description = "Extract coordinate pairs from scatter plot images"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "opencv-python>=4.8.0",
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "click>=8.1.0",
    "pillow>=10.0.0",
]

[project.scripts]
scatter-extractor = "scatter_extractor.cli:extract"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/scatter_extractor"]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
]
```

---

## Usage Examples

### Basic Extraction

```bash
# Install with uv
uv sync

# Run extraction (for the provided image with 0-50 scales)
uv run scatter-extractor image.png --x-min 0 --x-max 50 --y-min 0 --y-max 50 -o midterm_scores.csv
```

### Output Format (CSV)

```csv
pixel_x,pixel_y,x,y
456,123,42.5,38.2
234,345,23.1,15.7
...
```

### Programmatic Usage

```python
from scatter_extractor import detect_points, calibrate_from_image, pixel_to_data
from scatter_extractor.stats import compute_statistics, to_dataframe

# Calibrate
config = calibrate_from_image("plot.png", x_range=(0, 50), y_range=(0, 50))

# Detect and convert
pixels = detect_points("plot.png", plot_bounds=(config.pixel_x_min, ...))
points = [DetectedPoint(px, py, *pixel_to_data(px, py, config)) for px, py in pixels]

# Analyze
df = to_dataframe(points)
print(df.describe())
print(f"Correlation: {df['x'].corr(df['y'])}")
```

---

## Implementation Notes for Claude Code

### Critical Details for the Provided Image

1. **Axis scales**: Both axes run from 0 to 50
2. **Plot boundaries**: The plot has visible axis lines that can be detected
3. **Point appearance**: Black/dark gray filled circles on colored background
4. **Background colors**: Multiple colored regions (pink, orange, yellow, green, blue) - use thresholding on grayscale to isolate dark points
5. **Diagonal lines**: There are diagonal boundary lines - these should NOT be detected as points (filter by circularity)

### Detection Tuning Recommendations

For this specific image:
- `threshold_value`: ~80-120 (dark points on light backgrounds)
- `min_area`: ~15 (points are small but visible)
- `max_area`: ~300 (exclude large shapes)
- `min_circularity`: 0.6 (exclude line segments)

### Edge Cases to Handle

1. Points near axis lines might get merged - use morphological operations to separate
2. Overlapping points might appear as single larger blob - detect by area anomalies
3. Axis tick marks could be detected as points - filter by position (outside plot area)
4. The diagonal lines in the image could create false positives - circularity filter handles this

---

## Testing Strategy

```python
# test_detector.py
def test_detect_points_finds_all_points():
    """Verify detection count is reasonable for known image."""
    points = detect_points("examples/sample_plot.png")
    assert 150 < len(points) < 300  # Approximate expected count

def test_points_within_bounds():
    """All detected points should be within plot area."""
    points = detect_points("examples/sample_plot.png", plot_bounds=(50, 50, 550, 450))
    for x, y in points:
        assert 50 <= x <= 550
        assert 50 <= y <= 450

# test_calibration.py  
def test_pixel_to_data_corners():
    """Test coordinate conversion at known corners."""
    config = AxisConfig(0, 50, 0, 50, 100, 500, 100, 500)
    
    # Bottom-left corner
    x, y = pixel_to_data(100, 500, config)
    assert x == pytest.approx(0)
    assert y == pytest.approx(0)
    
    # Top-right corner
    x, y = pixel_to_data(500, 100, config)
    assert x == pytest.approx(50)
    assert y == pytest.approx(50)
```

---

## Quick Start Commands

```bash
# Create project
mkdir scatter-extractor && cd scatter-extractor
uv init

# Add dependencies
uv add opencv-python numpy pandas click pillow
uv add --dev pytest pytest-cov

# Create structure
mkdir -p src/scatter_extractor tests examples

# After implementing, run
uv run scatter-extractor path/to/image.png --x-min 0 --x-max 50 --y-min 0 --y-max 50 -o output.csv --stats
```

---

## Success Criteria

1. ✅ Detects 90%+ of visible points in the sample image
2. ✅ Coordinate values fall within expected 0-50 range
3. ✅ Correlation coefficient matches visual pattern (positive correlation)
4. ✅ Export works for both CSV and JSON
5. ✅ CLI is intuitive and well-documented
6. ✅ Can be installed and run via `uv run`

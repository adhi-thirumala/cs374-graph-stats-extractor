# Scatter Plot Coordinate Extractor

A Python CLI tool that extracts (x, y) coordinate pairs from scatter plot images using computer vision. The tool detects points in scatter plots and maps their pixel positions to actual data coordinates based on axis scales.

## Features

- Automatic point detection using OpenCV
- Configurable detection parameters (threshold, area, circularity)
- Automatic or manual plot boundary detection
- Pixel-to-data coordinate mapping
- Statistical analysis (mean, std, correlation, covariance)
- Export to CSV or JSON formats

## Installation

This project uses [UV](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone the repository
cd scatter-extractor

# Install dependencies
uv sync
```

## Usage

### Basic Command

Extract coordinates from a scatter plot image:

```bash
uv run scatter-extractor image.png \
  --x-min 0 --x-max 50 \
  --y-min 0 --y-max 50 \
  -o output.csv
```

### Command Line Options

- `image_path` (required): Path to the scatter plot image
- `--x-min` (required): Minimum x-axis value
- `--x-max` (required): Maximum x-axis value
- `--y-min` (required): Minimum y-axis value
- `--y-max` (required): Maximum y-axis value
- `--output`, `-o`: Output file path (CSV or JSON)
- `--format`: Output format (`csv` or `json`, default: `csv`)
- `--stats/--no-stats`: Print statistics (default: enabled)
- `--threshold`: Binary threshold for point detection (default: 100)
- `--min-area`: Minimum contour area (default: 10)
- `--max-area`: Maximum contour area (default: 500)
- `--min-circularity`: Minimum circularity 0-1 (default: 0.5)
- `--bounds`: Manual plot bounds as `x_min_px y_min_px x_max_px y_max_px`

### Examples

**Extract with default settings:**
```bash
uv run scatter-extractor plot.png --x-min 0 --x-max 50 --y-min 0 --y-max 50 -o data.csv
```

**Export to JSON without statistics:**
```bash
uv run scatter-extractor plot.png \
  --x-min 0 --x-max 100 --y-min 0 --y-max 100 \
  -o data.json --format json --no-stats
```

**Fine-tune detection parameters:**
```bash
uv run scatter-extractor plot.png \
  --x-min 0 --x-max 50 --y-min 0 --y-max 50 \
  --threshold 80 --min-area 15 --max-area 300 --min-circularity 0.6 \
  -o data.csv
```

**Use manual plot bounds:**
```bash
uv run scatter-extractor plot.png \
  --x-min 0 --x-max 50 --y-min 0 --y-max 50 \
  --bounds 100 100 500 400 \
  -o data.csv
```

### Output Format

**CSV output:**
```csv
pixel_x,pixel_y,x,y
456,123,42.5,38.2
234,345,23.1,15.7
...
```

**JSON output:**
```json
[
  {
    "pixel_x": 456,
    "pixel_y": 123,
    "x": 42.5,
    "y": 38.2
  },
  ...
]
```

### Statistics Output

When `--stats` is enabled (default), the tool prints:
- Point count
- X statistics: mean, standard deviation, range
- Y statistics: mean, standard deviation, range
- Pearson correlation coefficient
- Covariance

Example:
```
Detected 200 points

Statistics:
  Point count: 200
  X: mean=25.43, std=12.34, range=[2.15, 48.92]
  Y: mean=28.76, std=14.21, range=[1.83, 49.56]
  Correlation: 0.847
  Covariance: 176.523
```

## Programmatic Usage

You can also use the library programmatically:

```python
from scatter_extractor import (
    detect_points,
    calibrate_from_image,
    pixel_to_data,
    DetectedPoint,
    compute_statistics,
    to_dataframe
)

# Calibrate axis mapping
config = calibrate_from_image(
    "plot.png",
    x_range=(0, 50),
    y_range=(0, 50)
)

# Detect points
pixel_points = detect_points(
    "plot.png",
    plot_bounds=(config.pixel_x_min, config.pixel_y_min,
                 config.pixel_x_max, config.pixel_y_max)
)

# Convert to data coordinates
points = []
for px, py in pixel_points:
    dx, dy = pixel_to_data(px, py, config)
    points.append(DetectedPoint(px, py, dx, dy))

# Analyze
stats = compute_statistics(points)
print(f"Correlation: {stats['correlation']:.3f}")

# Convert to DataFrame for further analysis
df = to_dataframe(points)
print(df.describe())
```

## How It Works

1. **Plot Boundary Detection**: Uses Hough line detection to find axis lines and determine plot boundaries (or accepts manual bounds)
2. **Point Detection**:
   - Converts image to grayscale
   - Applies Gaussian blur to reduce noise
   - Uses binary thresholding to isolate dark points
   - Finds contours and filters by area and circularity
   - Extracts centroid of each valid contour
3. **Coordinate Mapping**: Maps pixel coordinates to data coordinates using linear interpolation
4. **Statistical Analysis**: Computes statistics on the extracted data points

## Tuning Detection Parameters

Different scatter plots may require parameter adjustments:

- **threshold**: Lower values (60-80) for lighter points, higher values (120-150) for darker backgrounds
- **min-area/max-area**: Adjust based on point size in your image
- **min-circularity**: Higher values (0.7-0.8) for perfect circles, lower (0.4-0.6) for irregular shapes

## Development

### Running Tests

```bash
uv run pytest
```

### Project Structure

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
│   └── __init__.py
└── examples/
```

## Requirements

- Python >= 3.11
- opencv-python >= 4.8.0
- numpy >= 1.24.0
- pandas >= 2.0.0
- click >= 8.1.0
- pillow >= 10.0.0

## License

See LICENSE file for details.

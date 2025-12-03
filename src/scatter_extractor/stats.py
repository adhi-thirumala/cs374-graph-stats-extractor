import numpy as np
import pandas as pd
import json
from typing import List, Dict, Any
from .models import DetectedPoint


def compute_statistics(points: List[DetectedPoint]) -> Dict[str, Any]:
    """
    Compute basic statistics on extracted points.

    Args:
        points: List of DetectedPoint objects with data coordinates

    Returns:
        Dictionary containing:
        - count: number of points
        - x_mean, x_std, x_min, x_max
        - y_mean, y_std, y_min, y_max
        - correlation: Pearson correlation coefficient
        - covariance: covariance between x and y
    """
    if not points:
        return {
            'count': 0,
            'x_mean': 0, 'x_std': 0, 'x_min': 0, 'x_max': 0,
            'y_mean': 0, 'y_std': 0, 'y_min': 0, 'y_max': 0,
            'correlation': 0, 'covariance': 0
        }

    x_values = np.array([p.data_x for p in points])
    y_values = np.array([p.data_y for p in points])

    # Compute statistics
    stats = {
        'count': len(points),
        'x_mean': float(np.mean(x_values)),
        'x_std': float(np.std(x_values)),
        'x_min': float(np.min(x_values)),
        'x_max': float(np.max(x_values)),
        'y_mean': float(np.mean(y_values)),
        'y_std': float(np.std(y_values)),
        'y_min': float(np.min(y_values)),
        'y_max': float(np.max(y_values)),
    }

    # Compute correlation
    if len(points) > 1:
        correlation_matrix = np.corrcoef(x_values, y_values)
        stats['correlation'] = float(correlation_matrix[0, 1])

        # Compute covariance
        covariance_matrix = np.cov(x_values, y_values)
        stats['covariance'] = float(covariance_matrix[0, 1])
    else:
        stats['correlation'] = 0.0
        stats['covariance'] = 0.0

    return stats


def to_dataframe(points: List[DetectedPoint]) -> pd.DataFrame:
    """
    Convert points to pandas DataFrame.

    Args:
        points: List of DetectedPoint objects

    Returns:
        DataFrame with columns: pixel_x, pixel_y, x, y
    """
    data = {
        'pixel_x': [p.pixel_x for p in points],
        'pixel_y': [p.pixel_y for p in points],
        'x': [p.data_x for p in points],
        'y': [p.data_y for p in points]
    }
    return pd.DataFrame(data)


def export_csv(points: List[DetectedPoint], output_path: str) -> None:
    """
    Export points to CSV file.

    Args:
        points: List of DetectedPoint objects
        output_path: Path to output CSV file
    """
    df = to_dataframe(points)
    df.to_csv(output_path, index=False)


def export_json(points: List[DetectedPoint], output_path: str) -> None:
    """
    Export points to JSON file.

    Args:
        points: List of DetectedPoint objects
        output_path: Path to output JSON file
    """
    data = [
        {
            'pixel_x': p.pixel_x,
            'pixel_y': p.pixel_y,
            'x': p.data_x,
            'y': p.data_y
        }
        for p in points
    ]

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

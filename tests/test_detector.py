import pytest
from scatter_extractor.detector import detect_points


def test_detect_points_requires_valid_image():
    """Test that detector raises error for invalid image path."""
    with pytest.raises(ValueError, match="Could not load image"):
        detect_points("nonexistent_image.png")


def test_detect_points_returns_list():
    """Test that detector returns a list (even if empty for invalid input)."""
    # This test would require a sample image
    # For now, we test the error case
    with pytest.raises(ValueError):
        detect_points("invalid.png")


def test_detect_points_filters_by_area():
    """Test that area filtering parameters work."""
    # Would need a test image to verify
    # This is a placeholder for the test structure
    pass


def test_detect_points_filters_by_circularity():
    """Test that circularity filtering works."""
    # Would need a test image to verify
    # This is a placeholder for the test structure
    pass

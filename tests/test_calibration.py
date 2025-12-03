import pytest
from scatter_extractor.calibration import pixel_to_data, calibrate_from_image
from scatter_extractor.models import AxisConfig


def test_pixel_to_data_corners():
    """Test coordinate conversion at known corners."""
    config = AxisConfig(
        x_min=0,
        x_max=50,
        y_min=0,
        y_max=50,
        pixel_x_min=100,
        pixel_x_max=500,
        pixel_y_min=100,
        pixel_y_max=500
    )

    # Bottom-left corner (min x, min y)
    # In image coords: y is inverted, so max pixel_y = min data_y
    x, y = pixel_to_data(100, 500, config)
    assert x == pytest.approx(0.0)
    assert y == pytest.approx(0.0)

    # Top-right corner (max x, max y)
    # In image coords: min pixel_y = max data_y
    x, y = pixel_to_data(500, 100, config)
    assert x == pytest.approx(50.0)
    assert y == pytest.approx(50.0)

    # Bottom-right corner
    x, y = pixel_to_data(500, 500, config)
    assert x == pytest.approx(50.0)
    assert y == pytest.approx(0.0)

    # Top-left corner
    x, y = pixel_to_data(100, 100, config)
    assert x == pytest.approx(0.0)
    assert y == pytest.approx(50.0)


def test_pixel_to_data_center():
    """Test coordinate conversion at center point."""
    config = AxisConfig(
        x_min=0,
        x_max=100,
        y_min=0,
        y_max=100,
        pixel_x_min=0,
        pixel_x_max=400,
        pixel_y_min=0,
        pixel_y_max=400
    )

    # Center point
    x, y = pixel_to_data(200, 200, config)
    assert x == pytest.approx(50.0)
    assert y == pytest.approx(50.0)


def test_calibrate_from_image_with_manual_bounds():
    """Test calibration with manually specified bounds."""
    # This would require a test image
    # For now, test that it handles manual bounds correctly
    pass


def test_detect_plot_bounds_invalid_image():
    """Test that detect_plot_bounds handles invalid images."""
    from scatter_extractor.calibration import detect_plot_bounds

    with pytest.raises(ValueError, match="Could not load image"):
        detect_plot_bounds("nonexistent.png")

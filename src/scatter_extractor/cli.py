import click
from .detector import detect_points
from .calibration import calibrate_from_image, pixel_to_data
from .stats import compute_statistics, export_csv, export_json
from .models import DetectedPoint


@click.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.option('--x-min', type=float, required=True, help='Minimum x-axis value')
@click.option('--x-max', type=float, required=True, help='Maximum x-axis value')
@click.option('--y-min', type=float, required=True, help='Minimum y-axis value')
@click.option('--y-max', type=float, required=True, help='Maximum y-axis value')
@click.option('--output', '-o', type=click.Path(), help='Output file path (CSV or JSON)')
@click.option('--format', 'fmt', type=click.Choice(['csv', 'json']), default='csv',
              help='Output format (csv or json)')
@click.option('--stats/--no-stats', default=True, help='Print statistics')
@click.option('--threshold', type=int, default=80, help='Binary threshold for point detection')
@click.option('--min-area', type=int, default=5, help='Minimum contour area')
@click.option('--max-area', type=int, default=600, help='Maximum contour area')
@click.option('--min-circularity', type=float, default=0.3, help='Minimum circularity (0-1)')
@click.option('--bounds', nargs=4, type=int, default=None,
              help='Manual plot bounds: x_min_px y_min_px x_max_px y_max_px')
def extract(image_path, x_min, x_max, y_min, y_max, output, fmt, stats,
            threshold, min_area, max_area, min_circularity, bounds):
    """
    Extract coordinate pairs from a scatter plot image.

    Example:
        scatter-extractor plot.png --x-min 0 --x-max 50 --y-min 0 --y-max 50 -o data.csv
    """
    try:
        # 1. Calibrate axis mapping
        axis_config = calibrate_from_image(
            image_path,
            x_range=(x_min, x_max),
            y_range=(y_min, y_max),
            manual_bounds=bounds
        )

        click.echo(f"Plot bounds detected: "
                   f"x=[{axis_config.pixel_x_min}, {axis_config.pixel_x_max}], "
                   f"y=[{axis_config.pixel_y_min}, {axis_config.pixel_y_max}]")

        # 2. Detect points
        pixel_points = detect_points(
            image_path,
            min_area=min_area,
            max_area=max_area,
            min_circularity=min_circularity,
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
        click.echo(f"\nDetected {len(points)} points")

        if stats and points:
            statistics = compute_statistics(points)
            click.echo(f"\nStatistics:")
            click.echo(f"  Point count: {statistics['count']}")
            click.echo(f"  X: mean={statistics['x_mean']:.2f}, "
                       f"std={statistics['x_std']:.2f}, "
                       f"range=[{statistics['x_min']:.2f}, {statistics['x_max']:.2f}]")
            click.echo(f"  Y: mean={statistics['y_mean']:.2f}, "
                       f"std={statistics['y_std']:.2f}, "
                       f"range=[{statistics['y_min']:.2f}, {statistics['y_max']:.2f}]")
            click.echo(f"  Correlation: {statistics['correlation']:.3f}")
            click.echo(f"  Covariance: {statistics['covariance']:.3f}")

        if output:
            if fmt == 'csv':
                export_csv(points, output)
            else:
                export_json(points, output)
            click.echo(f"\nData exported to {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    extract()

from osgeo import ogr

from process_lib import check_in_netherlands, check_single_polygon, get_projection

__all__ = ["validate_vector"]


def validate_vector(dataset: ogr.DataSource, target_unit: str = "metre") -> bool:
    """
    Validate a vector dataset to ensure it meets specific criteria:

    1. The dataset's spatial reference uses the target unit (default is 'metre').
    2. The dataset represents a single polygon.
    3. The polygon is within the Netherlands.

    Parameters:
        dataset (ogr.DataSource): The input vector dataset to validate.
        target_unit (str, optional): The expected unit of the spatial reference. Default is 'meter'.

    Returns:
        bool: True if all validation checks pass.

    Raises:
        ValueError: If the dataset's spatial reference does not use the target unit,
                    or if it fails the polygon or location checks.
    """
    # Check projection and unit
    spatial_ref = get_projection(dataset)
    if spatial_ref:
        unit_name = spatial_ref.GetAttrValue("UNIT")
        if not unit_name or unit_name.lower() != target_unit.lower():
            raise ValueError("Invalid projection. Please run the 'Define study area' process and try again.")

    # Handle errors from the checks and provide consistent guidance
    try:
        check_single_polygon(dataset)
    except Exception as e:
        raise ValueError(f"Polygon check failed: {e}. Please run the 'Define study area' process and try again.")

    try:
        check_in_netherlands(dataset)
    except Exception as e:
        raise ValueError(f"Location check failed: {e}. Please run the 'Define study area' process and try again.")

    return True

from pathlib import Path

from rana_sdk.domain.exceptions import ProcessUserError

from .gdal import check_single_polygon, get_projection, open_vector_file

__all__ = ["validate_study_area"]

EXPECTED_UNIT = "metre"


def validate_study_area(path: Path) -> bool:
    """
    Validate a study area dataset to ensure it meets specific criteria:

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
    dataset = open_vector_file(path)

    # Check projection and unit
    spatial_ref = get_projection(dataset)
    if spatial_ref:
        unit_name = spatial_ref.GetAttrValue("UNIT")
        if not unit_name or unit_name.lower() != EXPECTED_UNIT:
            raise ProcessUserError(
                "Invalid projection for input vector file.",
                "This process expects a projection with unit meters. Please run the 'Define study area' process and try again.",
            )

    try:
        check_single_polygon(dataset)
    except ValueError:
        raise ProcessUserError(
            "Polygon check failed for input vecor file."
            "This process requires exactly 1 valid (multi)polygon. "
            "Please run the 'Define study area' process and try again."
        )

    return True

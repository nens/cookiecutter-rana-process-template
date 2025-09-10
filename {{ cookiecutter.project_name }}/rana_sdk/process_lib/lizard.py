import time
from math import ceil, floor
from pathlib import Path
from typing import Any

from clean_python.api_client import download_file
from osgeo import gdal
from rana_sdk.domain import LizardRaster, ProcessUserError
from rana_sdk.infrastructure import LizardRasterLayerGateway

from process_lib import get_bbox, get_epsg_code, get_projection, open_vector_file

__all__ = ["download_raster", "clip_raster_with_vector"]

TIMEOUT = 10.0
CHECK_INTERVAL = 5
TOTAL_EXTRACTION_TIMEOUT = 3600  # 1 hour


DTYPE_MAPPING = {
    "i2": gdal.GDT_Int16,
    "i4": gdal.GDT_Int32,
    "f4": gdal.GDT_Float32,
    "u1": gdal.GDT_Byte,
    "u2": gdal.GDT_UInt16,
    "u4": gdal.GDT_UInt32,
    # "f8": gdal.GDT_Float64,  # Unsupported! Something with PREDICTOR=2 and DEFLATE compression
}


# There is a hard limit on what rasters Rana / Lizard can support:
RASTER_MAX_SIZE_BYTES = 999_000_000
# We should estimate how many pixels that is (but that depends on the byte size and compression)
# we commonly have 4 bytes per pixel, so that is about 250 million pixels.
# However the compression can be quite high (factor 5-10), so we go up to 2.5 billion pixels.
RASTER_MAX_ASYNC_SIZE = 2.5 * 10**9  # Lizard hard limit: 10**10
RASTER_MAX_ASYNC_SIZE_MSG = "2.5 billion"


def get_dtype_from_raster(raster: LizardRaster) -> int:
    if raster.dtype is None:
        return gdal.GDT_Float32
    return DTYPE_MAPPING.get(raster.dtype, gdal.GDT_Float32)


def _check_raster_size(path: Path) -> None:
    size = path.stat().st_size
    if size > RASTER_MAX_SIZE_BYTES:
        raise ProcessUserError(
            "Resolution is too high",
            description=(
                f"Rana can currently handle raster files up to 1 GB. "
                f"The produced raster is larger than that ({(size / 1_000_000_000):.2f} GB). "
                "This can be solved by decreasing the resolution (increasing the distance between raster pixels)."
            ),
        )


def download_raster(
    lizard: LizardRasterLayerGateway,
    raster: LizardRaster,
    vector_path: Path,
    working_directory: Path,
    pixel_size: float,
    nodata_value: float = -9999.0,
    buffer_meters: float = 0.0,
) -> Path:
    """
    Processes and clips a raster based on a given UUID and vector boundary.

    Args:
        lizard (LizardRasterLayerGateway): The Lizard API client for raster operations.
        raster (LizardRaster): The Lizard raster object containing metadata and UUID.
        vector_path (Path): The path to the vector file (Shapefile or GeoPackage).
        working_directory (Path): The directory where intermediate files will be stored.
        pixel_size (float): The desired pixel size for the output raster in meters.
        nodata_value (float): The NoData value to assign to the clipped raster.
        buffer_meters (float): Add optional (NoData) buffer around the vector.

    Returns:
        None
    """
    vector = open_vector_file(vector_path)
    epsg_code = get_epsg_code(get_projection(vector))
    bbox = get_bbox(vector)
    dtype = get_dtype_from_raster(raster)
    del vector  # Free file handle

    if raster.resolution and (pixel_size < raster.resolution):
        print("Warning: The specified pixel size is smaller than the raster's native resolution. ")

    working_directory.mkdir(exist_ok=True)
    raster_path = working_directory / "raster.tif"
    clipped_raster_path = working_directory / "clipped_raster.tif"

    # Download the raster
    download_raster_by_bbox(
        lizard=lizard,
        raster=raster,
        bbox=bbox,
        epsg_code=epsg_code,
        pixel_size=pixel_size,
        output_path=raster_path,
    )

    # Clip the raster using the transformed vector (or original if no transformation)
    clip_raster_with_vector(
        input_raster=raster_path,
        vector_file=vector_path,
        output_raster=clipped_raster_path,
        dtype=dtype,
        nodata_value=nodata_value,
        buffer_meters=buffer_meters,
    )

    return clipped_raster_path


def download_raster_by_bbox(
    lizard: LizardRasterLayerGateway,
    raster: LizardRaster,
    bbox: tuple[float, float, float, float],
    epsg_code: int,
    pixel_size: float,
    output_path: Path,
) -> None:
    """Downloads a raster from Lizard using the provided UUID and bounding box.

    Args:
        lizard (LizardRasterLayerGateway): The Lizard API client.
        raster_uuid (str): The UUID of the raster to download.
        bbox (tuple[float, float, float, float]): The bounding box in the format
            (min_x, min_y, max_x, max_y).
        epsg_code (int): The EPSG code for the coordinate reference system.
        pixel_size (float): The pixel size for the raster extraction.
        output_path (Path): The path where the downloaded raster will be saved.
    """
    # Floor and ceil the bbox coordinates so that it is an integer number of pixels from (0, 0)
    bbox = (
        floor(bbox[0] / pixel_size) * pixel_size,
        floor(bbox[1] / pixel_size) * pixel_size,
        ceil(bbox[2] / pixel_size) * pixel_size,
        ceil(bbox[3] / pixel_size) * pixel_size,
    )
    if bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
        raise ProcessUserError(
            "Study area is too small",
            description=f"The extent of the study area is {bbox}. It must contain at least 1 raster pixel.",
        )
    if (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) > RASTER_MAX_ASYNC_SIZE:
        raise ProcessUserError(
            "Resolution is too high",
            description=(
                f"The number of cells in the raster is greater than {RASTER_MAX_ASYNC_SIZE_MSG}. "
                "This can be solved by decreasing the resolution (increasing the distance between raster pixels)."
            ),
        )
    task_id = lizard.get_async_geotiff(raster.id, bbox, epsg_code, pixel_size)
    for _ in range(0, TOTAL_EXTRACTION_TIMEOUT, CHECK_INTERVAL):
        task = lizard.get_task(task_id)
        if task.is_success():
            break
        elif task.is_failed():
            raise RuntimeError(f"Raster extraction failed, lizard error message: {task.detail} (id={task.id})")
        time.sleep(CHECK_INTERVAL)
    else:
        raise RuntimeError("Raster extraction took too long")

    assert task.result is not None
    download_file(task.result, output_path)


def expand_extent(raster_path: Path, buffer_meters: float) -> dict[str, Any]:
    """Calculates the output bounds for a raster dataset, expanding the extent by a buffer in meters.

    Args:
        raster_path (Path): Path to the raster dataset.
        buffer_meters (float): Buffer in meters to expand the extent.

    Returns:
        dict: A dictionary containing the output bounds and pixel resolution, for input into gdal.Warp.
    """
    src_ds: gdal.Dataset = gdal.Open(str(raster_path))
    gt = src_ds.GetGeoTransform()
    x_min = gt[0]
    y_max = gt[3]
    x_max = x_min + gt[1] * src_ds.RasterXSize
    y_min = y_max + gt[5] * src_ds.RasterYSize
    pixel_size = max(abs(gt[1]), abs(gt[5]))
    buffer_pixels = ceil(buffer_meters / pixel_size)
    return {
        "outputBounds": [
            x_min - buffer_pixels * pixel_size,
            y_min - buffer_pixels * pixel_size,
            x_max + buffer_pixels * pixel_size,
            y_max + buffer_pixels * pixel_size,
        ],
        "xRes": abs(gt[1]),
        "yRes": abs(gt[5]),
    }


def clip_raster_with_vector(
    input_raster: Path,
    vector_file: Path,
    output_raster: Path,
    dtype: int,
    nodata_value: float,
    vector_layer: str | None = None,
    buffer_meters: float = 0.0,
) -> None:
    """Clips a raster dataset using the boundary of a vector file (Shapefile or GeoPackage).

    Parameters:
        input_raster (str): Path to raster dataset.
        vector_file (str): Path to the vector file (Shapefile or GeoPackage).
        output_raster (str): Path to save the clipped raster.
        vector_layer (Optional[str], optional): Name of the layer to use if the vector file has multiple layers (GeoPackage).
        nodata_value (float, optional): NoData value for the clipped raster. Default is -9999.
        buffer_meters (float, optional): Optional buffer in meters around the vector boundary. Default is 0.0.

    Raises:
        ValueError: If the raster dataset is invalid or other error occurs during clipping.
    """
    # Set up options for clipping
    warp_options = {
        "cutlineDSName": str(vector_file),
        "cropToCutline": False,
        "creationOptions": ["COMPRESS=DEFLATE"],
        "dstNodata": nodata_value,
        "outputType": dtype,
    }

    # Include layer name if provided (for GeoPackages with multiple layers)
    if vector_layer:
        warp_options["cutlineLayer"] = vector_layer

    if buffer_meters > 0.0:
        # Expand the extent of the raster by the buffer
        warp_options.update(expand_extent(input_raster, buffer_meters))

    # Perform clipping using gdal.Warp
    gdal.Warp(str(output_raster), str(input_raster), **warp_options)
    _check_raster_size(output_raster)

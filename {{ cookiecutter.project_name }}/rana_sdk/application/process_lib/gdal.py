import math
import mimetypes
import zipfile
from pathlib import Path

from osgeo import ogr, osr

__all__ = [
    "maybe_extract_archive",
    "open_vector_file",
    "get_projection",
    "get_bbox",
    "transform_point",
    "get_centroid_coordinates",
    "calculate_utm_zone",
    "check_projection",
    "select_featured_polygons",
    "merge_polygons",
    "buffer_polygon",
    "write_buffered_polygon",
    "get_epsg_code",
    "transform_vector_file",
    "check_single_polygon",
    "check_in_netherlands",
]

CRS84 = osr.SpatialReference()
CRS84.SetWellKnownGeogCS("CRS:84")


def maybe_extract_archive(path: Path) -> Path:
    """If `path` is a zipfile, extract it and return the directory where the files
    are extracted.
    """
    if mimetypes.guess_type(path)[0] != "application/zip":
        return path
    target_dir = path.with_suffix("")
    with zipfile.ZipFile(path, "r") as archive:
        archive.extractall(target_dir)
    return target_dir


def open_vector_file(vector_file_path: str | Path) -> ogr.DataSource:
    """
    Opens a vector file and returns the dataset.

    Parameters:
    - vector_file_path (str): Path to the vector file.

    Returns:
    - ogr.DataSource: The opened vector file dataset.

    Raises:
    - ValueError: If the file cannot be opened.
    """
    dataset = ogr.Open(str(vector_file_path), 0)
    if dataset is None:
        raise ValueError(f"Cannot open vector file: {vector_file_path}")
    return dataset


def get_projection(dataset: ogr.DataSource) -> osr.SpatialReference:
    """
    Gets the projection of the provided dataset.

    Parameters:
    - dataset (ogr.DataSource): The vector file dataset.

    Returns:
    - osr.SpatialReference: The spatial reference of the dataset.
    """
    layer = dataset.GetLayer()
    spatial_ref = layer.GetSpatialRef()
    return spatial_ref


def get_bbox(dataset: ogr.DataSource) -> tuple[float, float, float, float]:
    """
    Get the bounding box of the given vector dataset.

    Parameters:
    - dataset (ogr.DataSource): The vector file dataset.

    Returns:
    - tuple[float, float, float, float]: The bounding box coordinates (minX, minY, maxX, maxY).
    """
    layer = dataset.GetLayer()
    extent = layer.GetExtent()
    min_x, max_x, min_y, max_y = extent
    return min_x, min_y, max_x, max_y  # Correct order


def transform_point(
    x: float, y: float, source_srs: osr.SpatialReference, target_srs: osr.SpatialReference
) -> tuple[float, float]:
    # Create a coordinate transformation
    transform = osr.CoordinateTransformation(source_srs, target_srs)

    # Transform the extent corners to CRS84
    return transform.TransformPoint(x, y)[:2]


def get_centroid_coordinates(dataset: ogr.DataSource) -> tuple[float, float]:
    """
    Calculate the centroid coordinates (longitude, latitude) of the vector file after reprojecting to WGS84.

    Parameters:
    - dataset (ogr.DataSource): The vector file dataset.

    Returns:
    - Tuple[float, float]: Centroid longitude and latitude.
    """
    layer: ogr.Layer = dataset.GetLayer()
    extent = layer.GetExtent()
    x = (extent[0] + extent[1]) / 2  # minX + maxX
    y = (extent[2] + extent[3]) / 2  # minY + maxY

    # Define the target Spatial Reference (WGS84)
    return transform_point(x, y, layer.GetSpatialRef(), CRS84)


def calculate_utm_zone(longitude: float, latitude: float) -> int:
    """
    Determines the EPSG code for the appropriate UTM zone based on longitude and latitude.
    """
    # Calculate UTM zone (round up to next integer)
    utm_zone = math.ceil((longitude + 180) / 6)
    # Determine EPSG code based on hemisphere, Northern Hemisphere UTM zones (EPSG:32600 + zone number)
    return (32600 if latitude >= 0 else 32700) + utm_zone


def check_projection(
    spatial_ref: osr.SpatialReference, dataset: ogr.DataSource, target_unit: str = "metre"
) -> osr.SpatialReference:
    """
    Checks the projection of a vector file. If it's not metric, returns an appropriate UTM SpatialReference.

    Parameters:
    - spatial_ref (osr.SpatialReference): The spatial reference of the vector file.
    - dataset (ogr.DataSource): The vector file dataset.
    - target_unit (str): Target unit (default is 'metre').

    Returns:
    - osr.SpatialReference: The appropriate spatial reference for the dataset.
    """
    if spatial_ref:
        unit_name = spatial_ref.GetAttrValue("UNIT")
        if unit_name and unit_name.lower() == target_unit.lower():
            return spatial_ref

    longitude, latitude = get_centroid_coordinates(dataset)
    utm_epsg_code = calculate_utm_zone(longitude, latitude)
    utm_projection = osr.SpatialReference()
    utm_projection.ImportFromEPSG(utm_epsg_code)
    return utm_projection


def select_featured_polygons(
    dataset: ogr.DataSource, feature_ids: list[int], layer_name: str | None = None
) -> list[ogr.Feature]:
    """
    Extracts selected features from the specified layer based on feature IDs.

    Parameters:
    - dataset (ogr.DataSource): The vector file dataset.
    - feature_ids (List[int]): List of feature IDs to extract.
    - layer_name (str, optional): Name of the layer (if multiple layers exist).

    Returns:
    - List[ogr.Feature]: List of cloned features.
    """
    layer = dataset.GetLayerByName(layer_name) if layer_name else dataset.GetLayer()
    if layer is None:
        raise ValueError(f"Layer '{layer_name}' not found in the vector file.")

    selected_features = [layer.GetFeature(fid).Clone() for fid in feature_ids if layer.GetFeature(fid)]
    return selected_features


def merge_polygons(polygons: list[ogr.Feature]) -> ogr.Geometry:
    """
    Merges a list of polygon features into a single shape.

    Parameters:
    - polygons (List[ogr.Feature]): List of polygon features.

    Returns:
    - ogr.Geometry: A single merged polygon geometry.
    """

    merged_geom = polygons[0].GetGeometryRef().Clone()
    for polygon in polygons[1:]:
        merged_geom = merged_geom.Union(polygon.GetGeometryRef())

    # Checks if the polygons are all connected as one contiguous shape.
    if not merged_geom.IsSimple() and merged_geom.GetGeometryName() not in {"POLYGON", "MULTIPOLYGON"}:
        raise ValueError("Polygons are not connected and cannot be merged into a single shape.")

    return merged_geom


def buffer_polygon(geometry: ogr.Geometry, buffer_distance: float = 10, quad_segs: int = 8) -> ogr.Geometry:
    """
    Buffers the simplified polygon.

    Parameters:
    - geometry (ogr.Geometry): Polygon geometry.
    - buffer_distance (float): Buffer distance.
    - quad_segs (int): Precision of the buffer (quadrant segments).

    Returns:
    - ogr.Geometry: Buffered polygon geometry.
    """

    return geometry.Buffer(buffer_distance, quad_segs)


def write_buffered_polygon(
    output_file_path: str,
    buffered_geom: ogr.Geometry,
    name_buffered_layer: str = "study_area",
    source_spatial_ref: osr.SpatialReference | None = None,
) -> None:
    """
    Writes the buffered geometry to a GeoPackage file.

    Parameters:
    - output_file_path (str): Path to the output file.
    - buffered_geom (ogr.Geometry): Buffered geometry.
    - source_spatial_ref (osr.SpatialReference): Spatial reference for the output.
    """
    driver = ogr.GetDriverByName("GPKG")
    data_source = driver.CreateDataSource(output_file_path)
    if data_source is None:
        raise ValueError(f"Cannot create file: {output_file_path}")

    layer = data_source.CreateLayer(name_buffered_layer, geom_type=ogr.wkbPolygon, srs=source_spatial_ref)
    if source_spatial_ref:
        geom_spatial_ref = buffered_geom.GetSpatialReference()
        if geom_spatial_ref and not geom_spatial_ref.IsSame(source_spatial_ref):
            transform = osr.CoordinateTransformation(geom_spatial_ref, source_spatial_ref)
            buffered_geom.Transform(transform)

    feature_defn = layer.GetLayerDefn()
    feature = ogr.Feature(feature_defn)
    feature.SetGeometry(buffered_geom)
    layer.CreateFeature(feature)

    feature = None
    data_source = None

    return


def get_epsg_code(srs: osr.SpatialReference | str) -> int:
    """
    Extracts the EPSG code from a string like 'EPSG:28992'.

    Parameters:
        spatial_ref (str or SpatialReference): The EPSG code as a string (e.g., 'EPSG:28992').

    Returns:
        int: The EPSG code if available, otherwise the function will raise.
    """
    # Create a spatial reference object
    if isinstance(srs, str):
        spatial_ref = osr.SpatialReference()
        result = spatial_ref.ImportFromEPSG(int(srs.split(":")[1]))  # Extract integer part
        if result != 0:
            raise ValueError(f"Invalid EPSG code: {srs}")
    else:
        spatial_ref = srs

    # Try to get the EPSG code
    epsg_code = spatial_ref.GetAuthorityCode(None)
    if epsg_code is not None:
        return int(epsg_code)
    else:
        raise ValueError("Invalid EPSG code")


def transform_vector_file(
    input_file: str, output_file: str, target_epsg: int, output_format: str = "ESRI Shapefile"
) -> None:
    """
    Transforms a vector file (Shapefile or GeoPackage) to a specified coordinate system using GDAL.

    Parameters:
        input_file (str): Path to the input vector file.
        output_file (str): Path where the transformed file will be saved.
        target_epsg (int): The target coordinate reference system (CRS) EPSG code (e.g., 4326).
        output_format (str): The format of the output file (default: 'ESRI Shapefile' or 'GPKG' for GeoPackage).

    Returns:
        None: Saves the transformed file at the specified location.
    """
    # Open the input vector file
    input_driver = ogr.GetDriverByName("ESRI Shapefile") if input_file.endswith(".shp") else ogr.GetDriverByName("GPKG")
    input_ds = input_driver.Open(input_file, 0)  # 0 means read-only
    if input_ds is None:
        raise FileNotFoundError(f"Could not open {input_file}")

    # Get the input layer
    input_layer = input_ds.GetLayer()

    # Get the source spatial reference
    source_srs = input_layer.GetSpatialRef()

    # Define the target spatial reference
    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(target_epsg)

    # Create a Coordinate Transformation
    coord_transform = osr.CoordinateTransformation(source_srs, target_srs)

    # Choose the output driver based on the format
    output_driver = ogr.GetDriverByName(output_format)
    if output_driver is None:
        raise ValueError(f"Unsupported output format: {output_format}")

    # Create the output file
    output_ds = output_driver.CreateDataSource(output_file)
    output_layer = output_ds.CreateLayer(input_layer.GetName(), srs=target_srs, geom_type=input_layer.GetGeomType())

    # Copy fields from input to output
    input_layer_defn = input_layer.GetLayerDefn()
    for i in range(input_layer_defn.GetFieldCount()):
        field_defn = input_layer_defn.GetFieldDefn(i)
        output_layer.CreateField(field_defn)

    # Get the output layer's feature definition
    output_layer_defn = output_layer.GetLayerDefn()

    # Transform each feature and add it to the output layer
    for feature in input_layer:
        geom = feature.GetGeometryRef().Clone()  # Clone geometry to avoid modifying original
        geom.Transform(coord_transform)

        # Create a new feature and set its geometry and attributes
        out_feature = ogr.Feature(output_layer_defn)
        out_feature.SetGeometry(geom)
        for i in range(input_layer_defn.GetFieldCount()):
            out_feature.SetField(i, feature.GetField(i))
        output_layer.CreateFeature(out_feature)
        out_feature = None  # Dereference the feature

    # Close datasets
    input_ds = None
    output_ds = None

    print(f"Vector file successfully transformed and saved to {output_file}")


def check_single_polygon(dataset: ogr.DataSource) -> bool:
    """
    Checks that the provided dataset contains exactly one polygon feature and that it is a polygon or multipolygon.

    Parameters:
        dataset (ogr.DataSource): The dataset containing the vector layer to check.

    Returns:
        bool: True if the dataset contains exactly one valid polygon, otherwise raises a ValueError.
    """
    if dataset.GetLayerCount() != 1:
        raise ValueError("Dataset must contain exactly one layer.")

    # Get the layer and feature count
    layer = dataset.GetLayer()
    feature_count = layer.GetFeatureCount()

    # Check if there is exactly one feature
    if feature_count != 1:
        raise ValueError("Study area must contain exactly one polygon.")

    # Get the first feature and its geometry
    feature = layer.GetNextFeature()
    geometry = feature.GetGeometryRef()

    # Check if the geometry is either POLYGON or MULTIPOLYGON
    if geometry.GetGeometryName() not in {"POLYGON", "MULTIPOLYGON"}:
        raise ValueError("Study area must be a single polygon.")

    # Return True if validation passes
    return True


def check_in_netherlands(layer: ogr.Layer) -> bool:
    """
    Checks if the centroid of the given layer is within the geographical bounds of the Netherlands.

    Parameters:
    - layer (ogr.Layer): The vector layer containing the polygon to check.

    Returns:
    - bool: True if the centroid is within the bounds of the Netherlands, False otherwise.

    Raises:
    - ValueError: If the centroid is outside the Netherlands' boundaries.
    """
    centroid_lon, centroid_lat = get_centroid_coordinates(layer)
    if not (3.36 <= centroid_lon <= 7.21 and 50.75 <= centroid_lat <= 53.53):
        raise ValueError("This process is not supported outside the Netherlands.")
    return True

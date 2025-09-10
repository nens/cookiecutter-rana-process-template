from osgeo import osr

__all__ = ["get_crs_from_sr"]

CRS84 = osr.SpatialReference()
CRS84.SetWellKnownGeogCS("CRS:84")


def get_crs_from_sr(sr: osr.SpatialReference) -> str:
    """Return EPSG:<code> or CRS:84 for given SpatialReference."""
    key = "GEOGCS" if sr.IsGeographic() else "PROJCS"
    name = sr.GetAuthorityName(key)
    if name is None:
        if sr.IsSameGeogCS(CRS84):
            return "CRS:84"
        raise ValueError("Input CRS WKT has no EPSG code")

    code_str = sr.GetAuthorityCode(key)
    if code_str == "CRS84":
        assert not sr.EPSGTreatsAsLatLong()
        return "CRS:84"
    code = int(code_str)
    if code == 4326:
        return "EPSG:4326" if sr.EPSGTreatsAsLatLong() else "CRS:84"
    return f"EPSG:{code}"

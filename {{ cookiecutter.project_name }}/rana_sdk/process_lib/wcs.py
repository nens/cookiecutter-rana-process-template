from http import HTTPStatus
from typing import TYPE_CHECKING

from clean_python.api_client import ApiException, SyncApiProvider

if TYPE_CHECKING:
    from spatial_lib import CRS, Bbox


__all__ = ["WebCoverageServiceGateway"]


# def download_geotiff(self, id: Id, crs: CRS, bbox: Bbox, cell_size: float) -> tuple[bytes, str]:
#     wcs = self.repo.get(id).wcs
#     if not wcs:
#         raise BadRequest("No WCS link found for the dataset.")
#     # estimate the size of the raster and raise if too large
#     if bbox.width / cell_size * bbox.height / cell_size > MAX_PIXELS:
#         raise BadRequest(
#             f"The requested raster is too large. Please reduce the bounding box or increase the cell size. The maximum size is {MAX_PIXELS} pixels."
#         )
#     assert wcs.url.host
#     return (
#         WebCoverageServiceGateway(
#             SyncApiProvider(AnyHttpUrl.build(scheme=wcs.url.scheme, host=wcs.url.host, port=wcs.url.port))
#         ).extract_geotiff(path=wcs.url.path or "", id=wcs.name, crs=crs, bbox=bbox, cell_size=cell_size),
#         wcs.name,
#     )


class WebCoverageServiceGateway:
    def __init__(self, provider: SyncApiProvider):
        self.provider = provider

    def _pdok_getcoverage_params(self, crs: "CRS", bbox: "Bbox", cell_size: float) -> dict[str, str | list[str]]:
        width = int((bbox[2] - bbox[0]) / cell_size)
        height = int((bbox[3] - bbox[1]) / cell_size)
        return {
            "version": "2.0.1",
            "crs": f"http://www.opengis.net/def/crs/EPSG/0/{crs.epsg_code}",
            "subset": [f"x({bbox[0]},{bbox[2]})", f"y({bbox[1]},{bbox[3]})"],
            "scalesize": [f"x({width}),y({height})"],
        }

    def extract_geotiff(self, path: str, id: str, crs: "CRS", bbox: "Bbox", cell_size: float) -> bytes:
        """
        Extract raster data from a WCS service for a specific coverage and bounding box.
        """
        response = self.provider.request_raw(
            "GET",
            path if not path.startswith("/") else path[1:],
            params={
                "service": "WCS",
                "request": "GetCoverage",
                "coverageId": id,
                "format": "image/tiff",
                **self._pdok_getcoverage_params(crs, bbox, cell_size),
            },
        )
        if response.status != HTTPStatus.OK:
            raise ApiException(
                f"Failed to extract raster data: {response.data!r}",
                status=response.status,
            )
        return response.data

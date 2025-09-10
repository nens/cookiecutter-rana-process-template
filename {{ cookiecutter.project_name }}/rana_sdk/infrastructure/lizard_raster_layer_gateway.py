from http import HTTPStatus

from clean_python import DoesNotExist, Id, Json
from clean_python.api_client import ApiException, SyncApiProvider
from pydantic import AnyHttpUrl

from ..domain import LizardRaster, LizardTask
from .lizard_api_provider import LizardApiProvider

__all__ = ["LizardRasterLayerGateway"]


class LizardRasterMapper:
    def to_internal(self, data: Json) -> LizardRaster:
        return LizardRaster(
            id=data["uuid"],
            pixelsize_x=data.get("pixelsize_x"),
            pixelsize_y=data.get("pixelsize_y"),
            projection=data.get("projection"),
            dtype=data.get("dtype", None),
            styles=data.get("options", {}).get("styles", None),
        )

    def task_to_internal(self, data: Json) -> LizardTask:
        return LizardTask(
            id=data["uuid"],
            status=data["status"],
            result=data.get("result"),
            detail=data.get("detail"),
        )


class LizardRasterLayerGateway:
    path = "api/v4/rasters/{id}"
    task_path = "api/v4/tasks/{id}"
    data_subpath = "/data"
    mapper = LizardRasterMapper()

    def __init__(self, provider_override: SyncApiProvider | None = None):
        self.provider_override = provider_override

    @property
    def provider(self) -> SyncApiProvider:
        return self.provider_override or LizardApiProvider()

    @property
    def namespace(self) -> AnyHttpUrl:
        return AnyHttpUrl(self.provider._url + self.path.replace("/{id}", ""))

    def get(self, id: Id) -> LizardRaster:
        try:
            result = self.provider.request("GET", self.path.format(id=id))
            assert result is not None
            return self.mapper.to_internal(result)
        except ApiException as e:
            if e.status is HTTPStatus.NOT_FOUND:
                raise DoesNotExist("raster", id)
            raise e

    def get_async_geotiff(
        self, id: Id, bbox: tuple[float, float, float, float], epsg_code: int, pixel_size: float
    ) -> Id:
        try:
            result = self.provider.request(
                "GET",
                (self.path + self.data_subpath).format(id=id),
                params={
                    "bbox": ",".join([str(i) for i in bbox]),
                    "format": "geotiff",
                    "projection": f"EPSG:{epsg_code}",
                    "pixel_size": pixel_size,
                    "async": True,
                },
            )
            assert result is not None
            return result["task_id"]
        except ApiException as e:
            if e.status is HTTPStatus.NOT_FOUND:
                raise DoesNotExist("raster", id)
            raise e

    def get_task(self, id: Id) -> LizardTask:
        result = self.provider.request("GET", self.task_path.format(id=id))
        assert result is not None
        return self.mapper.task_to_internal(result)

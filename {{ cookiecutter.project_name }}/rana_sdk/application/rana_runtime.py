import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

from clean_python import Json
from pydantic import BaseModel

from rana_sdk.domain import ThreediApiKey

if TYPE_CHECKING:
    from rana_sdk.infrastructure import (
        LizardRasterLayerGateway,
        RanaDatasetGateway,
        RanaFileGateway,
        RanaSchematisationGateway,
        ThreediApiKeyGateway,
        ThreediGateway,
    )


__all__ = ["RanaRuntime"]

T = TypeVar("T", bound=BaseModel)


class RanaRuntime(ABC):
    threedi_api_key: ThreediApiKey | None = None

    @property
    def file_gateway(self) -> "RanaFileGateway":
        raise NotImplementedError("file_gateway must be implemented in subclasses")

    @property
    def threedi_api_key_gateway(self) -> "ThreediApiKeyGateway":
        raise NotImplementedError("threedi_api_key_gateway must be implemented in subclasses")

    @property
    def threedi_gateway(self) -> "ThreediGateway":
        raise NotImplementedError("threedi_gateway must be implemented in subclasses")

    @property
    def rana_schematisation_gateway(self) -> "RanaSchematisationGateway":
        raise NotImplementedError("rana_schematisation_gateway must be implemented in subclasses")

    @property
    def lizard_raster_layer_gateway(self) -> "LizardRasterLayerGateway":
        raise NotImplementedError("lizard_raster_layer_gateway must be implemented in subclasses")

    @property
    def rana_dataset_gateway(self) -> "RanaDatasetGateway":
        raise NotImplementedError("rana_dataset_gateway must be implement in a subclass")

    @property
    @abstractmethod
    def job_working_dir(self) -> Path:
        pass

    @property
    @abstractmethod
    def logger(self) -> logging.Logger:
        pass

    @abstractmethod
    def set_progress(self, progress: float, description: str) -> None:
        pass

    @abstractmethod
    def set_result(self, result: Json) -> None:
        pass

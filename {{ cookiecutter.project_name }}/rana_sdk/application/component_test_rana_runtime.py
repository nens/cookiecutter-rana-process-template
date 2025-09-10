import logging
from pathlib import Path
from unittest.mock import Mock

from clean_python import Json
from process_settings.local_test_settings import LocalTestSettings

import rana_sdk

from ..domain import ThreediApiKey
from ..infrastructure import (
    LizardRasterLayerGateway,
    LocalTestRanaDatasetGateway,
    LocalTestRanaFileGateway,
    LocalTestRanaSchematisationGateway,
    RanaDatasetGateway,
    RanaFileGateway,
    RanaSchematisationGateway,
    ThreediGateway,
)
from .local_test_rana_runtime import LocalTestRanaRuntime

__all__ = ["ComponentTestRanaRuntime"]


def download(*args, **kwargs) -> Path:  # type: ignore
    args[2].mkdir(parents=True, exist_ok=True)
    target = args[2] / "raster.tif"
    target.write_text("fake raster data")
    return target


class ComponentTestRanaRuntime(LocalTestRanaRuntime):
    project_dir: Path
    settings: LocalTestSettings
    _job_working_dir: Path
    _cleanup_working_dir: bool = False
    _lizard_raster_layer_gateway: Mock = Mock(LizardRasterLayerGateway)
    _threedi_api: Mock = Mock(ThreediGateway)

    def __init__(self, tmp_path: Path, settings: LocalTestSettings) -> None:
        self._job_working_dir = tmp_path / "workdir"
        self._job_working_dir.mkdir(exist_ok=True)
        self.project_dir = tmp_path / "project"
        self.project_dir.mkdir(exist_ok=True)
        self.settings = settings

        self._lizard_raster_layer_gateway.namespace = settings.lizard.host
        self._lizard_raster_layer_gateway.download.side_effect = download

        if settings and settings.threedi:
            self.threedi_api_key = ThreediApiKey(
                prefix=settings.threedi.api_key.get_secret_value().split(".")[0],
                key=settings.threedi.api_key,
                organisations=[settings.threedi.organisation],
            )

    @property
    def threedi_gateway(self) -> Mock:
        return self._threedi_api

    @property
    def file_gateway(self) -> RanaFileGateway:
        return LocalTestRanaFileGateway(self)

    @property
    def rana_schematisation_gateway(self) -> RanaSchematisationGateway:
        return LocalTestRanaSchematisationGateway(self)

    @property
    def lizard_raster_layer_gateway(self) -> Mock:
        return self._lizard_raster_layer_gateway

    @property
    def rana_dataset_gateway(self) -> RanaDatasetGateway:
        return LocalTestRanaDatasetGateway(self)

    @property
    def job_working_dir(self) -> Path:
        return self._job_working_dir

    @property
    def logger(self) -> logging.Logger:
        logger = logging.getLogger(rana_sdk.__name__)
        logger.setLevel(logging.INFO)
        logger.propagate = True
        return logger

    def set_progress(self, progress: float, description: str) -> None:
        progress_bar = "█" * int(progress // 10) + " " * (10 - int(progress // 10))
        self.logger.info(f"[{progress_bar}] {progress:3.0f}% | {description}")

    def set_result(self, result: Json) -> None:
        self.logger.info("result            | value")
        self.logger.info("----------------- | -------------------------------------------------")
        for item in result.items():
            self.logger.info(f"{item[0]: <17} | {item[1]}")
        self.logger.info("---------------   | -------------------------------------------------")

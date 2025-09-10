import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from clean_python import Json
from process_settings.local_test_settings import LocalTestSettings, get_local_test_settings

import rana_sdk
from ..infrastructure import (
    LizardApiProvider,
    LizardRasterLayerGateway,
    LocalTestRanaDatasetGateway,
    LocalTestRanaFileGateway,
    LocalTestRanaSchematisationGateway,
    RanaDatasetGateway,
    RanaFileGateway,
    RanaSchematisationGateway,
    ThreediGateway,
)

from ..domain import ThreediApiKey
from .rana_runtime import RanaRuntime

__all__ = ["LocalTestRanaRuntime"]


class LocalTestRanaRuntime(RanaRuntime):
    project_dir: Path
    settings: LocalTestSettings
    _job_working_dir: Path
    _tmp_directory: TemporaryDirectory | None

    def __init__(
        self,
        project_dir: Path | str,
        working_dir: Path | str | None = None,
        settings: LocalTestSettings = get_local_test_settings(),
    ) -> None:
        """Run process in a local environment without interaction to Rana instance

        Suitable for local testing and development of processes beceause you do not rely on Rana as an external dependency.

        Inputs:
        - project_dir: Local directory that stores files used as in- and output of the process, similiar to files in a Rana project.
        - working dir: Optional local directory used during process exuction for intermediate file storage.
        - setting: Object containing settings to be able to run the process localy.
        """
        if not working_dir:
            self._tmp_directory = TemporaryDirectory()
            self._job_working_dir = Path(self._tmp_directory.__enter__())
        else:
            working_dir_path = Path(working_dir) if not isinstance(working_dir, Path) else working_dir
            assert working_dir_path.parent.exists(), (
                f"Workdir must be placed in a existing directory {working_dir_path.parent}"
            )
            self._job_working_dir = working_dir_path
        project_dir_path = Path(project_dir) if not isinstance(project_dir, Path) else project_dir
        assert project_dir_path.exists(), f"Project directory {project_dir_path} does not exist"
        self.project_dir = project_dir_path
        self.settings = settings
        if settings and settings.threedi:
            self.threedi_api_key = ThreediApiKey(
                prefix=settings.threedi.api_key.get_secret_value().split(".")[0],
                key=settings.threedi.api_key,
                organisations=[settings.threedi.organisation],
            )

    @property
    def threedi_gateway(self) -> ThreediGateway:
        assert self.threedi_api_key, "No Threedi API key available in runtime"
        return ThreediGateway(self.threedi_api_key.organisations[0], self.threedi_api_key.key)

    @property
    def file_gateway(self) -> RanaFileGateway:
        return LocalTestRanaFileGateway(self)

    @property
    def rana_schematisation_gateway(self) -> RanaSchematisationGateway:
        return LocalTestRanaSchematisationGateway(self)

    @property
    def lizard_raster_layer_gateway(self) -> LizardRasterLayerGateway:
        return LizardRasterLayerGateway(LizardApiProvider(lizard_settings=self.settings.lizard))

    @property
    def rana_dataset_gateway(self) -> RanaDatasetGateway:
        return LocalTestRanaDatasetGateway(self)

    @property
    def job_working_dir(self) -> Path:
        return self._job_working_dir

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        if self._tmp_directory:
            self._tmp_directory.__exit__(exc_type, exc_value, traceback)

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

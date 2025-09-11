from contextlib import chdir
import os
from pathlib import Path
import shutil
from cookiecutter.main import cookiecutter
from pytest import fixture
from subprocess import run

TEST_PROCESS_NAME = "rana-process-test"


@fixture
def process(tmp_path: Path) -> Path:
    cookiecutter(
        template=".",
        output_dir=str(tmp_path),
        extra_context={"project_name": TEST_PROCESS_NAME},
        no_input=True,
    )
    return tmp_path / TEST_PROCESS_NAME


def test_process(process: Path):
    with chdir(process):
        run(
            [
                "conda",
                "env",
                "create",
                "-n",
                "test_process",
                "-f",
                "environment.yml",
                "--yes",
            ],
            check=True,
        )
        run(
            ["conda", "run", "-n", "test_process", "python", "run_local_test.py"],
            check=True,
        )

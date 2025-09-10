from contextlib import chdir
import os
from pathlib import Path
import shutil
from cookiecutter.main import cookiecutter
from pytest import fixture
from subprocess import run

TEST_PROCESS_PATH = "./test_process"


@fixture
def process(tmp_path: Path) -> Path:
    cookiecutter(
        template=".",
        output_dir=str(tmp_path),
        extra_context={"project_name": "rana-process-test"},
        no_input=True,
    )
    return tmp_path / "rana-process-test"


def merge_copytree(src, dst):
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)

        if os.path.isdir(src_path):
            if not os.path.exists(dst_path):
                os.makedirs(dst_path)
            merge_copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)


def test_hello_world(process: Path):
    merge_copytree(TEST_PROCESS_PATH, process)

    with chdir(process):
        print(run(["ls"], check=True))
        run(["uv", "sync"], check=True)
        run(["uv", "run", "run_local_test.py"], check=True)

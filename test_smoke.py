import sys
from contextlib import chdir
from pathlib import Path
from subprocess import run

import pytest
from cookiecutter.main import cookiecutter


def test_smoke(tmp_path: Path):
    cookiecutter(
        template=".",
        output_dir=str(tmp_path),
        extra_context={"project_name": "rana-process-my-example"},
        no_input=True,
    )


def test_function_prefix(tmp_path: Path):
    cookiecutter(
        template=".",
        output_dir=str(tmp_path),
        extra_context={"project_name": "rana-process-nens-customer"},
        no_input=True,
    )
    generated_flows_py = tmp_path / "rana-process-nens-customer/src/flows.py"
    # We prefix everything with our project name, but want to omit the rana-process part.
    print(generated_flows_py.read_text())  # For easier debugging
    assert "def nens_customer_flow" in generated_flows_py.read_text()


def test_generated_project_ruff(tmp_path: Path):
    if sys.platform.startswith("win"):
        pytest.skip("Skipping test that uses linux commands")
    cookiecutter(
        template=".",
        output_dir=str(tmp_path),
        extra_context={"project_name": "rana-process-my-example"},
        no_input=True,
    )
    with chdir(tmp_path / "rana-process-my-example"):
        run([sys.executable, "-m", "ruff", "format"], check=True)


def test_generated_project_precommit(tmp_path: Path):
    if sys.platform.startswith("win"):
        pytest.skip("Skipping test that uses linux commands")
    cookiecutter(
        template=".",
        output_dir=str(tmp_path),
        extra_context={"project_name": "rana-process-my-example"},
        no_input=True,
    )
    with chdir(tmp_path / "rana-process-my-example"):
        run(["git", "init"], check=True)
        run(["git", "add", "-A"], check=True)
        run([sys.executable, "-m", "pre_commit", "run", "--all"], check=True)


def test_generated_project_install(tmp_path: Path):
    if sys.platform.startswith("win"):
        pytest.skip("Skipping test that uses linux commands")
    cookiecutter(
        template=".",
        output_dir=str(tmp_path),
        extra_context={"project_name": "rana-process-my-example"},
        no_input=True,
    )
    with chdir(tmp_path / "rana-process-my-example"):
        run(["uv", "sync"], check=True)

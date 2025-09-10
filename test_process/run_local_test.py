from subprocess import run

print(run("ls"))

from rana_sdk.process_settings import get_local_test_settings
from src.hello_world import hello_world
from rana_sdk import run_local_test
from rana_sdk.infrastructure import LocalTestRanaRuntime


runtime = LocalTestRanaRuntime(
    working_dir="working_dir",
    project_dir="project_dir",
    settings=get_local_test_settings(),
    cleanup_workdir=True,
)


inputs = {"name": "Pizza cursus"}

outputs = {}


run_local_test(
    rana_flow=hello_world,
    runtime=runtime,
    inputs=inputs,
    output_paths=outputs,
)

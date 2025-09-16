from src.process import process
from rana_process_sdk import run_local_test, LocalTestRanaRuntime
from local_test_settings import get_local_test_settings


runtime = LocalTestRanaRuntime(
    working_dir="working_dir",
    project_dir="project_dir",
    settings=get_local_test_settings(),
    cleanup_workdir=True,
)


inputs = {"name": "Pizza cursus"}

outputs = {}

run_local_test(
    rana_flow=process,
    runtime=runtime,
    inputs=inputs,
    output_paths=outputs,
)

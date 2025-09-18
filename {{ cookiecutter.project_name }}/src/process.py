from typing import Annotated

from pydantic import Field
from rana_process_sdk import RanaContext, RanaProcessParameters, rana_flow

__all__ = ["process"]


class ProcessInputs(RanaProcessParameters):
    name: str = Field(title="Hello message", description="The name to use in the process", examples=["world"])

class ProcessOutputs(RanaProcessParameters):
    upper: str = Field(title="Uppercase name", description="The name in uppercase")



@rana_flow(title="{{ cookiecutter.project_name }}")
def process(context: RanaContext[ProcessOutputs], inputs: ProcessInputs) -> None:
    context.set_progress(50, f"Hello {inputs.name}, ! 🤗")

    context.set_output(
        ProcessOutputs(upper=inputs.name.upper())
    )

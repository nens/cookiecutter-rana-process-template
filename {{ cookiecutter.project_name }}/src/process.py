from typing import Annotated

from pydantic import Field
from rana_sdk import CellSizeWidget, RanaContext, RanaProcessParameters, UsingWidget, Vector, rana_flow

__all__ = ["process"]


PROCESS_TITLE  =  "{{ cookiecutter.project_name }}"

class ProcessInputs(RanaProcessParameters):
    name: Annotated[
        str,
        Field(
            title="Hello message", description="The name to use in the process", examples=["world"]
        ),
    ]

class ProcessOutputs(RanaProcessParameters):
    upper: Annotated[str, Field(title="Uppercase name", description="The name in uppercase")]



@rana_flow(title=PROCESS_TITLE)
def process(context: RanaContext[ProcessOutputs], inputs: ProcessInputs) -> None:
    context.set_progress(0, f"Running {PROCESS_TITLE}")
    context.set_progress(50, f"Hello {inputs.name}, ! 🤗")

    context.set_output(
        ProcessOutputs(upper=inputs.name.upper())
    )


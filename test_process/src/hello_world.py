import time
from typing import Annotated

from pydantic import Field
from rana_sdk import CellSizeWidget, RanaContext, RanaProcessParameters, UsingWidget, Vector, rana_flow

__all__ = ["hello_world"]


class HelloWorldOutput(RanaProcessParameters):
    upper: Annotated[str, Field(title="Uppercase name", description="The name in uppercase")]
    cell_size: float


class HelloWorldInputs(RanaProcessParameters):
    name: Annotated[
        str,
        Field(
            title="Hello message", description="The name to use in the hello world print statement", examples=["world"]
        ),
    ]
    sleep: Annotated[int, Field(title="Sleep time", description="Sleep time in seconds before returning")] = 0
    location: Annotated[
        Vector | None, Field(title="Input geometry", description="For testing the cell size widget.")
    ] = None
    cell_size: Annotated[float, UsingWidget(CellSizeWidget(extent_source="location", bytes_per_cell=8))] = 0.5


# Flow picks-up whole doc-string below as description
# title is not supported...
@rana_flow(title="Hello world example process function")
def hello_world(context: RanaContext[HelloWorldOutput], inputs: HelloWorldInputs) -> None:
    print(f"Hello {inputs.name} from Prefect! 🤗")
    if inputs.sleep < 0:
        raise ValueError("Sleep time must be a positive number")

    if inputs.sleep:
        print(f"Sleeping for {inputs.sleep} seconds...")
        for i in range(1, inputs.sleep + 1):
            context.set_progress(int(100 * i / inputs.sleep), f"Sleeping {i + 1} of {inputs.sleep} seconds...")
            time.sleep(1)

    context.set_output(
        HelloWorldOutput(upper=inputs.name.upper(), cell_size=inputs.cell_size)
    )


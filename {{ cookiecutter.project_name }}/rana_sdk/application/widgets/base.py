from dataclasses import dataclass

from clean_python import ValueObject
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

__all__ = ["Widget", "UsingWidget", "WIDGET_JSONSCHEMA_KEY"]

WIDGET_JSONSCHEMA_KEY = "rana_widget"


class Widget(ValueObject):
    id: str


@dataclass
class UsingWidget:
    widget: Widget

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        result = handler(core_schema).copy()
        result[WIDGET_JSONSCHEMA_KEY] = self.widget.model_dump(mode="json")
        return result

    def __hash__(self) -> int:
        return hash(self.widget)

from uuid import UUID

from clean_python import ValueObject
from pydantic import SecretStr

__all__ = ["ThreediApiKey"]


class ThreediApiKey(ValueObject):
    prefix: str
    key: SecretStr
    organisations: list[UUID]

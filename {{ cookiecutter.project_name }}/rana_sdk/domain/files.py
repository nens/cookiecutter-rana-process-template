from datetime import datetime

from clean_python import Json, ValueObject
from pydantic import AnyHttpUrl

__all__ = ["File", "FileStat", "FileUpload", "History"]


class File(ValueObject):
    id: str
    last_modified: datetime


class FileUpload(File):
    ref: str


class FileStat(File):
    url: AnyHttpUrl
    descriptor_id: str
    descriptor: Json | None = None


class History(ValueObject):
    ref: str
    created_at: datetime

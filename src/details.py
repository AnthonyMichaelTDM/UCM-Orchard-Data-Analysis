from datetime import datetime, timedelta
from typing import Any, Callable, NamedTuple, Optional, Type

from reader import RowGenerator

FilenameGeneratorContract = Callable[[datetime, Optional[int]], str]
class SensorDetails(NamedTuple):
    valid_ids: list[int] | None
    filename_generator: FilenameGeneratorContract
    smoothening_interval: timedelta|None = timedelta(minutes=60)

class ReaderDetails(NamedTuple):
    row_generator: Type[RowGenerator]
    data_source: str
    additional: dict[str,Any] = {}
    args: list[str] = []# for future CLI functionality

class SampleDetails(NamedTuple):
    important_fields: list[str]
    field_types: list[Any]
    timestamp_fieldname:str = "Date and Time"
    timestamp_format:str = "%Y-%m-%d %H:%M:%S"

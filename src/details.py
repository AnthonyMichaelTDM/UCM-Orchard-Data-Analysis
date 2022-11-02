from datetime import datetime, timedelta
from typing import Any, Callable, NamedTuple, Optional, Type

from rowgenerator import RowGenerator
from sample import Sample, SampleList

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


plotter_list_generator_contract = Callable[[SampleList,int],list[Any]]
# for some reason python is throwing an error when I put this lambda in the PlotterDetails class 
__x_gen__ = lambda samples, _id: [
        sample.timestamp 
        for sample in samples
]
class PlotterDetails(NamedTuple):
    figure_id:int
    y_list_gen: plotter_list_generator_contract
    y_lable:str
    x_list_gen: plotter_list_generator_contract = __x_gen__
    x_label: str = "Time"
    additional: dict[str,Any] = {}
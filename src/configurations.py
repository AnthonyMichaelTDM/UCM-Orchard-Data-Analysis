import csv
import os
from typing import Any, Iterable, Iterator, NamedTuple, Optional, SupportsIndex, Type, Union, overload

import sample
from reader import RowGenerator, WebRowRehsani


class ReaderDetails(NamedTuple):
    row_generator: Type[RowGenerator]
    data_source: sample.DataSource
    additional: dict[str,Any] = {}
    args: list[str] = []# for future CLI functionality

class SampleDetails(NamedTuple):
    important_fields: list[str]
    field_types: list[Any]
    timestamp_fieldname:str = "Date and Time"
    timestamp_format:str = "%Y-%m-%d %H:%M:%S"
    
class ConfigDetails(NamedTuple):
    title:str
    READER_CONF: ReaderDetails
    SAMPLE_CONF: SampleDetails
    #TODO: additional commands and processing to run

class ConfigList(list[ConfigDetails]):
    def __init__(
        self,
        configs: Optional[Iterable[ConfigDetails]] = None
    ) -> None:
        self.configurations: list[ConfigDetails] = list(configs) if configs else []
    
    def __iter__(self) -> Iterator[ConfigDetails]: 
        return iter(self.configurations)
    
    def __len(self) -> int:
        return len(self.configurations)
    
    @overload
    def __getitem__(self,index: SupportsIndex)->ConfigDetails:
        ...
    @overload
    def __getitem__(self,index: slice)->list[ConfigDetails]:
        ...
    
    def __getitem__(self, index: Union[SupportsIndex, slice]) -> Union[ConfigDetails, list[ConfigDetails]]:
       return self.configurations[index]
    ...

class Configurations:
    CONFS: dict[str,ConfigList] = {
        "almond": ConfigList([
            ConfigDetails(
                title = "Almond sap and moisture",
                READER_CONF=ReaderDetails(
                    row_generator=csv.DictReader,  # type: ignore
                    data_source=sample.DataSource(base_path=os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), "data")),
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields=["Value 1","Value 2"],
                    field_types     =[int,      int],
                ),
            ),
            ConfigDetails(
                title = "Almond weather",
                READER_CONF=ReaderDetails(
                    row_generator=csv.DictReader,  # type: ignore
                    data_source=sample.DataSource(base_path=os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), "data")),
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields= ["Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"],
                    field_types=      [float,               float,          float,              float,      float],
                )
            ),
            ConfigDetails(
                title = "Almond lux",
                READER_CONF=ReaderDetails(
                    row_generator=csv.DictReader,  # type: ignore
                    data_source=sample.DataSource(base_path=os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), "data")),
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields= ["Light (KLux)"],
                    field_types=      [float]
                )
            )
        ]),
        "pistachio": ConfigList([
            ConfigDetails(
                title = "Pistachio sap and moisture",
                READER_CONF=ReaderDetails(
                    row_generator=WebRowRehsani,
                    data_source=sample.DataSource(base_path="http://192.168.0.116/rehsani_local")
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields=["Value 1","Value 2"],
                    field_types=[int,int]
                )
            ),
            ConfigDetails(
                title = "Pistachio weather",
                READER_CONF=ReaderDetails(
                    row_generator=WebRowRehsani,
                    data_source=sample.DataSource(base_path="http://192.168.0.116/rehsani_local")
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields=["Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"],
                    field_types=[float,float,float,float,float]
                )
            ),
            ConfigDetails(
                title="Pistachio lux",
                READER_CONF=ReaderDetails(
                    row_generator=WebRowRehsani,
                    data_source=sample.DataSource(base_path="http://192.168.0.116/rehsani_local")
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields=["Value 1","Value 2"],
                    field_types=[int,int]
                )
            )
        ])
    }
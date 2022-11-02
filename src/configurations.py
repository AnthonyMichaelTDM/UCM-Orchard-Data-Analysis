from analysis import AnalyzeSapFlow
import csv
import os
from typing import Iterable, Iterator, NamedTuple, Optional, SupportsIndex, Union, overload
from details import PlotterDetails, ReaderDetails, SampleDetails, SensorDetails

from rowgenerator import WebRowRehsani


    
class ConfigDetails(NamedTuple):
    title:str
    SENSOR_CONF: SensorDetails
    READER_CONF: ReaderDetails
    SAMPLE_CONF: SampleDetails
    PLOTTER_CONF: list[PlotterDetails]
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
                SENSOR_CONF=SensorDetails(
                    valid_ids=list(range(1,7)),
                    filename_generator=lambda date, id: "Data_TREWid{id}_{year}_{month:0>2}_almond.csv".format(id=id,year=date.year%100,month=date.month)
                ),
                READER_CONF=ReaderDetails(
                    row_generator=csv.DictReader,  # type: ignore
                    data_source=os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), "data"),
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields=["Value 1","Value 2"],
                    field_types     =[int,      int],
                ),
                PLOTTER_CONF=[PlotterDetails(
                    figure_id=1,
                    y_list_gen=lambda samples: AnalyzeSapFlow.run(samples),
                    y_lable="Sap Flow",
                    x_list_gen=lambda samples: [sample.timestamp for sample in samples],
                    x_label="Time",
                )]
            ),
            ConfigDetails(
                title = "Almond weather",
                SENSOR_CONF=SensorDetails(
                    valid_ids=None,
                    filename_generator=lambda date, _id: "Data_weather_{year}_{month:0>2}_almond.csv".format(year=date.year%100,month=date.month)
                ),
                READER_CONF=ReaderDetails(
                    row_generator=csv.DictReader,  # type: ignore
                    data_source=os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), "data"),
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields= ["Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"],
                    field_types=      [float,               float,          float,              float,      float],
                ),
                PLOTTER_CONF=[
                    PlotterDetails(
                        figure_id=2,
                        y_list_gen=lambda samples: [sample.datapoints[label] for sample in samples],
                        y_lable=label
                    )
                    for label in ["Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"]
                ]
            ),
            ConfigDetails(
                title = "Almond lux",
                SENSOR_CONF=SensorDetails(
                    valid_ids=[1,2],
                    filename_generator=lambda date, id: "Data_lux_{year}_{month:0>2}_almond.csv".format(year=date.year%100,month=date.month)
                ),
                READER_CONF=ReaderDetails(
                    row_generator=csv.DictReader,  # type: ignore
                    data_source=os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), "data"),
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields= ["Light (KLux)"],
                    field_types=      [float]
                ),
                PLOTTER_CONF=[
                    PlotterDetails(
                        figure_id=3,
                        y_list_gen=lambda samples: [
                            sample.datapoints["Light (KLux)"] 
                            for sample in samples
                        ],
                        y_lable="Light (KLux)",
                    )
                ]
            )
        ]),
        "pistachio": ConfigList([
            ConfigDetails(
                title = "Pistachio sap and moisture",
                SENSOR_CONF=SensorDetails(
                    valid_ids=list(range(1,7)),
                    filename_generator=lambda date, id: "trew/?id={id}&m={month}&y={year}".format(id=id,year=date.year,month=date.month)
                ),
                READER_CONF=ReaderDetails(
                    row_generator=WebRowRehsani,
                    data_source="http://192.168.0.116/rehsani_local"
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields=["Value 1","Value 2"],
                    field_types=[int,int]
                ),
                PLOTTER_CONF=[PlotterDetails(
                    figure_id=1,
                    y_list_gen=lambda samples: AnalyzeSapFlow.run(samples),
                    y_lable="Sap Flow",
                    x_list_gen=lambda samples: [sample.timestamp for sample in samples],
                    x_label="Time",
                )]
            ),
            ConfigDetails(
                title = "Pistachio weather",
                SENSOR_CONF=SensorDetails(
                    valid_ids=list(range(0,16)),
                    filename_generator=lambda date, id: "weather/id={id}&y={year}".format(id=id,year=date.year)
                ),
                READER_CONF=ReaderDetails(
                    row_generator=WebRowRehsani,
                    data_source="http://192.168.0.116/rehsani_local"
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields=["Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"],
                    field_types=[float,float,float,float,float]
                ),
                PLOTTER_CONF=[
                    PlotterDetails(
                        figure_id=2,
                        y_list_gen=lambda samples: [sample.datapoints[label] for sample in samples],
                        y_lable=label
                    )
                    for label in ["Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"]
                ]
            ),
            ConfigDetails(
                title="Pistachio lux",
                SENSOR_CONF=SensorDetails(
                    valid_ids=[1,2],
                    filename_generator=lambda date, id: "lux/?id={id}&m={month}&y={year}".format(id=id,year=date.year,month=date.month)
                ),
                READER_CONF=ReaderDetails(
                    row_generator=WebRowRehsani,
                    data_source="http://192.168.0.116/rehsani_local"
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields=["Value 1","Value 2"],
                    field_types=[int,int]
                ),
                PLOTTER_CONF=[
                    PlotterDetails(
                        figure_id=3,
                        y_list_gen=lambda samples: [
                            sample.datapoints["Light (KLux)"] 
                            for sample in samples
                        ],
                        y_lable="Light (KLux)",
                    )
                ]
            )
        ])
    }
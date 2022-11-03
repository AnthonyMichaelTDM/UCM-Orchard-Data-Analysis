from datetime import datetime, timedelta
from analysis import AnalyzeSapFlow
import os
from typing import Callable, Iterable, Iterator, NamedTuple, Optional, SupportsIndex, Union, overload
from plotter import PlotterDetails
from reader import ReaderDetails
from rowgenerator import CsvRow, WebRowRehsani
from sample import SampleDetails

FilenameGeneratorContract = Callable[[datetime, Optional[int]], str]
class SensorDetails(NamedTuple):
    valid_ids: list[int] | None
    filename_generator: FilenameGeneratorContract
    smoothening_interval: timedelta|None = timedelta(minutes=60)


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
    CONFS: dict[str,list[ConfigDetails]] = {
        "almond": [
            ConfigDetails(
                title = "Almond S&M",
                SENSOR_CONF=SensorDetails(
                    valid_ids=list(range(1,7)),
                    filename_generator=lambda date, id: "Data_TREWid{id}_{year}_{month:0>2}_almond.csv".format(id=id,year=date.year%100,month=date.month)
                ),
                READER_CONF=ReaderDetails(
                    row_generator=CsvRow,
                    data_fields=["Date and Time", "Field","Sensor ID", "Value 1","Value 2"],
                    data_source=os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), "data"),
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields=["Value 1","Value 2"],
                    field_types     =[int,      int],
                ),
                PLOTTER_CONF=[
                    PlotterDetails(
                        figure_id=1,
                        y_list_gen=lambda samples, id: AnalyzeSapFlow.run_relativemoisture(
                            [sample.datapoints["Value 2"] for sample in samples],
                            sensor_id=id,  # type: ignore
                            sensor_coefficients=[
                                {"a": -0.0442015591095395, "b": 191.7556055613598}, #Sensor 1
                                {"a": -0.04861278384829307, "b": 202.27735563973982}, #Sensor 2
                                {"a": -0.05762850897914471, "b": 215.35202712174151}, #Sensor 3
                                {"a": -0.05445248031047814, "b": 212.60475914677914}, #Sensor 4
                                {"a": -0.05701605695441798, "b": 211.74325309992707}, #Sensor 5
                                {"a": -0.053728569077514346, "b": 212.98440419373264} #Sensor 6
                            ]
                        ),
                        y_label="Relative Moisture %",
                        figure_rows=2,
                        figure_cols=1,
                        subplot_index=1
                    ),
                    PlotterDetails(
                        figure_id=1,
                        y_list_gen=lambda samples, _id: AnalyzeSapFlow.run_sapflux(
                            [sample.datapoints["Value 1"] for sample in samples],
                            [sample.timestamp for sample in samples]
                        ),
                        y_label="Sap Flux Density",
                        figure_rows=2,
                        figure_cols=1,
                        subplot_index=2
                    ),
                ]
            ),         
            ConfigDetails(
                title = "Almond weather",
                SENSOR_CONF=SensorDetails(
                    valid_ids=None,
                    filename_generator=lambda date, _id: "Data_weather_{year}_{month:0>2}_almond.csv".format(year=date.year%100,month=date.month)
                ),
                READER_CONF=ReaderDetails(
                    row_generator=CsvRow,
                    data_fields= ["Date and Time","Field","Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"],
                    data_source=os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), "data"),
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields= ["Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"],
                    field_types=      [float,               float,          float,              float,      float],
                ),
                PLOTTER_CONF=[
                    PlotterDetails(figure_id=2,
                        y_list_gen=lambda samples, _id: [sample.datapoints["Temperature [℃]"] for sample in samples],
                        y_label="Temperature [℃]",figure_rows=3,figure_cols=2,subplot_index = 1
                    ),
                    PlotterDetails( figure_id=2,
                        y_list_gen=lambda samples, _id: [sample.datapoints["Humidity [RH%]"] for sample in samples],
                        y_label="Humidity [RH%]",figure_rows=3,figure_cols=2,subplot_index = 2
                    ),
                    PlotterDetails(figure_id=2,
                        y_list_gen=lambda samples, _id: [sample.datapoints["Pressure [hPa]"] for sample in samples],
                        y_label="Pressure [hPa]",figure_rows=3,figure_cols=2,subplot_index = 3
                    ),
                    PlotterDetails(figure_id=2,
                        y_list_gen=lambda samples, _id: [sample.datapoints["Altitude [m]"] for sample in samples],
                        y_label="Altitude [m]",figure_rows=3,figure_cols=2,subplot_index = 4
                    ),
                    PlotterDetails(figure_id=2,
                        y_list_gen=lambda samples, _id: [sample.datapoints["VOC [kΩ]"] for sample in samples],
                        y_label="VOC [kΩ]",figure_rows=3,figure_cols=2,subplot_index = 5
                    )
                ]
            ),
            ConfigDetails(
                title = "Almond lux",
                SENSOR_CONF=SensorDetails(
                    valid_ids=[1,2],
                    filename_generator=lambda date, id: "Data_lux_{year}_{month:0>2}_almond.csv".format(year=date.year%100,month=date.month)
                ),
                READER_CONF=ReaderDetails(
                    row_generator=CsvRow,
                    data_fields= ["Date and Time", "Light (KLux)"],
                    data_source=os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), "data"),
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields= ["Light (KLux)"],
                    field_types=      [float]
                ),
                PLOTTER_CONF=[
                    PlotterDetails(
                        figure_id=3,
                        y_list_gen=lambda samples, _id: [
                            sample.datapoints["Light (KLux)"] 
                            for sample in samples
                        ],
                        y_label="Light (KLux)",
                    )
                ]
            )
        ],
        "pistachio": [
            ConfigDetails(
                title = "Pistachio S&M",
                SENSOR_CONF=SensorDetails(
                    valid_ids=list(range(1,7)),
                    filename_generator=lambda date, id: "trew/?id={id}&m={month}&y={year}".format(id=id,year=date.year,month=date.month)
                ),
                READER_CONF=ReaderDetails(
                    row_generator=WebRowRehsani,
                    data_fields=["Date and Time", "Value 1","Value 2"],
                    data_source="http://192.168.0.116/rehsani_local"
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields=["Value 1","Value 2"],
                    field_types=[int,int]
                ),
                PLOTTER_CONF=[
                    PlotterDetails(
                        figure_id=1,
                        y_list_gen=lambda samples, id: AnalyzeSapFlow.run_relativemoisture(
                            [sample.datapoints["Value 2"] for sample in samples],
                            sensor_id=id,  # type: ignore
                            sensor_coefficients=[ #TODO: calibrate the sensors (./other_scripts/calc_calibration_coefficients.py) with calibration data, for now just using averages from the almond sensors calibrations
                                {"a":-0.05260665971323129, "b":207.7862341272133}
                                for _ in range(1,7)
                            ]
                        ),
                        y_label="Sap Flow",
                        figure_rows=1,
                        figure_cols=2,
                        subplot_index=1
                    ),
                    PlotterDetails(
                        figure_id=1,
                        y_list_gen=lambda samples, _id: AnalyzeSapFlow.run_sapflux(
                            [sample.datapoints["Value 1"] for sample in samples],
                            [sample.timestamp for sample in samples]
                        ),
                        y_label="Sap Flux Density",
                        figure_rows=1,
                        figure_cols=2,
                        subplot_index=2
                    ),
                ]
            ),
            ConfigDetails(
                title = "Pistachio weather",
                SENSOR_CONF=SensorDetails(
                    valid_ids=list(range(0,16)),
                    filename_generator=lambda date, id: "weather/id={id}&y={year}".format(id=id,year=date.year)
                ),
                READER_CONF=ReaderDetails(
                    row_generator=WebRowRehsani,
                    data_fields=["Date and Time", "Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"],
                    data_source="http://192.168.0.116/rehsani_local"
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields=["Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"],
                    field_types=[float,float,float,float,float]
                ),
                PLOTTER_CONF=[
                    PlotterDetails(figure_id=2,
                        y_list_gen=lambda samples, _id: [sample.datapoints["Temperature [℃]"] for sample in samples],
                        y_label="Temperature [℃]",figure_rows=3,figure_cols=2,subplot_index = 1
                    ),
                    PlotterDetails( figure_id=2,
                        y_list_gen=lambda samples, _id: [sample.datapoints["Humidity [RH%]"] for sample in samples],
                        y_label="Humidity [RH%]",figure_rows=3,figure_cols=2,subplot_index = 2
                    ),
                    PlotterDetails(figure_id=2,
                        y_list_gen=lambda samples, _id: [sample.datapoints["Pressure [hPa]"] for sample in samples],
                        y_label="Pressure [hPa]",figure_rows=3,figure_cols=2,subplot_index = 3
                    ),
                    PlotterDetails(figure_id=2,
                        y_list_gen=lambda samples, _id: [sample.datapoints["Altitude [m]"] for sample in samples],
                        y_label="Altitude [m]",figure_rows=3,figure_cols=2,subplot_index = 4
                    ),
                    PlotterDetails(figure_id=2,
                        y_list_gen=lambda samples, _id: [sample.datapoints["VOC [kΩ]"] for sample in samples],
                        y_label="VOC [kΩ]",figure_rows=3,figure_cols=2,subplot_index = 5
                    )
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
                    data_fields=["Date and Time", "Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"],
                    data_source="http://192.168.0.116/rehsani_local"
                ),
                SAMPLE_CONF=SampleDetails(
                    important_fields=["Value 1","Value 2"],
                    field_types=[int,int]
                ),
                PLOTTER_CONF=[
                    PlotterDetails(
                        figure_id=3,
                        y_list_gen=lambda samples, _id: [
                            sample.datapoints["Light (KLux)"] 
                            for sample in samples
                        ],
                        y_label="Light (KLux)",
                    )
                ]
            )
        ]
    }
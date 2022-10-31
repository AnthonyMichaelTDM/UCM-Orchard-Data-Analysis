import abc
from dataclasses import dataclass
from datetime import datetime
import os
from typing import Any, Iterable, Iterator, Optional, Protocol, SupportsIndex, Union, overload


class Sample(abc.ABC):
    ...
    
class SampleBuilder(Protocol):
    @staticmethod
    def Build(datapoints: dict[str,Any]) -> Sample:
        """returns an instance of the Sample from a dictionary of unserialized data

        Args:
            data (Dict[str,str]): 
        """
        ...

@dataclass(frozen=True)
class SapAndMoistureData(Sample):
    timestamp: datetime
    value1: int
    value2: int
    
class SapAndMoistureSampleBuilder(SampleBuilder):
    @staticmethod
    def Build(datapoints: dict[str, Any]) -> SapAndMoistureData:
        """builds an instance of SapAndMoistureData
        
        cannot guarentee desired behavior when important data is missing

        Args:
            data (dict[str, Any]): dictionary representing a simple sample of data

        Returns:
            SapAndMoistureData: dataclass built from data
            
        DocTests:
            good data
        >>> from data import SapAndMoistureSampleBuilder
        >>> test_datapoints = dict(zip(
        ...     ["Date and Time","Field","Sensor ID","Value 1","Value 2"],
        ...     ["2022-04-30 23:46:18","Stevinson Almond","TREW 6","1084","2569"]
        ... )) 
        >>> SapAndMoistureSampleBuilder.Build(test_datapoints)
        SapAndMoistureData(timestamp=datetime.datetime(2022, 4, 30, 23, 46, 18), value1=1084, value2=2569)
        >>> 
        
            missing data
        >>> from data import SapAndMoistureSampleBuilder
        >>> missing_value = dict(zip(
        ...     ["Date and Time","Field","Sensor ID","Value 1","Value 2"],
        ...     ["2022-04-30 23:46:18","Stevinson Almond","TREW 6","1084",]
        ... ))
        >>> SapAndMoistureSampleBuilder.Build(missing_value) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: invalid literal for int() with base 10: 'None'
        >>>
        
            bad datatypes (would likely occur if reader was given the wrong names for fields)
        >>> from data import SapAndMoistureSampleBuilder
        >>> fields = ["Date and Time","Field","Sensor ID","Value 1","Value 2"]
        >>> invalid_datetime = dict(zip(fields,
        ...     ["23:46:18 2022-04-30","Stevinson Almond","TREW 6","1084","2569"]
        ... ))
        >>> int_not_int = dict(zip(fields,
        ...     ["2022-04-30 23:46:18","Stevinson Almond","TREW 6","1084","2569.0"]
        ... ))
        >>> SapAndMoistureSampleBuilder.Build(invalid_datetime) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: time data '23:46:18 2022-04-30' does not match format '%Y-%m-%d %H:%M:%S'
        >>> SapAndMoistureSampleBuilder.Build(int_not_int) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: invalid literal for int() with base 10: '2569.0'
        >>>
        """
        return SapAndMoistureData(
            timestamp = datetime.strptime(str(datapoints.get("Date and Time")), "%Y-%m-%d %H:%M:%S"),
            value1 = int(str(datapoints.get("Value 1"))),
            value2 = int(str(datapoints.get("Value 2"))),
        )
    
        
@dataclass(frozen=True)
class WeatherData(Sample):
    timestamp: datetime
    temperature: float
    humidity: float
    pressure: float
    altitude: float
    voc: float
class WeatherSampleBuilder(SampleBuilder):
    @staticmethod
    def Build(datapoints: dict[str, Any]):
        """builds an instance of WeatherData

        cannot guarentee desired behavior when important data is missing
        
        if the given type is less specific than the desired type, an error will not be thrown
            ex: given an int, expects a float, see the bad datatypes example (an error is thrown, but because of the string not the int)
        
        Args:
            datapoints (dict[str, Any]):  dictionary representing a simple sample of data

        Returns:
            WeatherData: dataclass built from data
            
        DocTests:
            good data
        >>> from data import WeatherSampleBuilder
        >>> test_datapoints = dict(zip(
        ...     ["Date and Time","Field","Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"],
        ...     ["2022-05-31 23:47:32","Stevinson Almond","15.06","76.84","1010.05","65.59","44.59"]
        ... )) 
        >>> WeatherSampleBuilder.Build(test_datapoints)
        WeatherData(timestamp=datetime.datetime(2022, 5, 31, 23, 47, 32), temperature=15.06, humidity=76.84, pressure=1010.05, altitude=65.59, voc=44.59)
        
        missing data
        >>> from data import WeatherSampleBuilder
        >>> fields = ["Date and Time","Field","Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"]
        >>> missing_value = dict(zip(fields,
        ...     ["2022-05-31 23:47:32","Stevinson Almond","15.06","76.84","65.59","44.59"]
        ... ))
        >>> WeatherSampleBuilder.Build(missing_value) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: could not convert string to float: 'None'
        >>>
        
            bad datatypes (would likely occur if reader was given the wrong names for fields)
        >>> from data import WeatherSampleBuilder        
        >>> fields = ["Date and Time","Field","Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"]
        >>> invalid_datetime = dict(zip(fields,
        ...     ["23:47:32 2022-05-31","Stevinson Almond","15.06","76.84","1010.05","65.59","44.59"]
        ... ))
        >>> float_not_float = dict(zip(fields,
        ...     ["2022-05-31 23:47:32","Stevinson Almond","15.06","76.84","1010.05","65","fourty four .59"]
        ... #                                                                      int^      ^str
        ... ))
        >>> WeatherSampleBuilder.Build(invalid_datetime) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: time data '23:47:32 2022-05-31' does not match format '%Y-%m-%d %H:%M:%S'
        >>> WeatherSampleBuilder.Build(float_not_float) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: could not convert string to float: 'fourty four .59'
        >>>
        """
        return WeatherData(
            timestamp = datetime.strptime(str(datapoints.get("Date and Time")), "%Y-%m-%d %H:%M:%S"),
            temperature = float(str(datapoints.get("Temperature [℃]"))),
            humidity = float(str(datapoints.get("Humidity [RH%]"))),
            pressure = float(str(datapoints.get("Pressure [hPa]"))),
            altitude = float(str(datapoints.get("Altitude [m]"))),
            voc = float(str(datapoints.get("VOC [kΩ]"))),
        )

@dataclass(frozen=True)
class LuxData(Sample):
    timestamp: datetime
    light: float
class LuxSampleBuilder(SampleBuilder):
    @staticmethod
    def Build(datapoints: dict[str, Any]):
        """_summary_

        Args:
            datapoints (dict[str, Any]): _description_

        Returns:
            _type_: _description_
            
        Doctests:
        TODO: add doctests
        """
        return LuxData(
            timestamp = datetime.strptime(str(datapoints.get("Date and Time")), "%Y-%m-%d %H:%M:%S"),
            light = float(str(datapoints.get("Light (KLux)"))),
        )
        
class SampleList(list[Sample],abc.ABC):
    def __init__(
        self,
        samples: Optional[Iterable[Sample]] = None
    ) -> None:
        self.data_points: list[Sample] = list(samples) if samples else []
    
    def __iter__(self) -> Iterator[Sample]: 
        return iter(self.data_points)
    
    def __len(self) -> int:
        return len(self.data_points)
    
    @overload
    def __getitem__(self,index: SupportsIndex)->Sample:
        ...
    @overload
    def __getitem__(self, index: slice)->list[Sample]:
        ...
    
    def __getitem__(self, index: Union[SupportsIndex, slice]) -> Union[Sample, list[Sample]]:
       return self.data_points[index]

class DataSource(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def base_path() -> str:
        """get the base path of the DataSource

        Returns:
            str: the base path
        """
        ...
    
class WebDataSource_rehsani_local(DataSource):
    @staticmethod 
    def base_path() -> str:
        return "http://192.168.0.116/rehsani_local"
     
class CsvDataSource(DataSource):
    @staticmethod
    def base_path() -> str:
        return os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), "data")

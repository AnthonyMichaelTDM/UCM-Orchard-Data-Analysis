import abc
from datetime import datetime
from typing import Iterable, Iterator, Optional, SupportsIndex, Type, Union, overload

from data import Sample

# FIXME: refactor for SOLID

class Sensor(abc.ABC):
    sample_class: Type[Sample]
    minID: int | None = None
    maxID: int | None = None
    
    def __init__(
        self,
        starttime: datetime,
        endtime: datetime,
        id: Optional[int] = None,
    ) ->None:
        self.id = id if id else None
        self.starttime: datetime = starttime
        self.endtime: datetime = endtime
        self.headers: list[str] = []
        
    @abc.abstractmethod
    def get_path(self) -> str:
        """returns the path to the source, used by Reader

        Returns:
            str: path to the data source
        """
        ...
        
class SensorList(list[Sensor]):
    def __init__(
        self,
        sensors: Optional[Iterable[Sensor]] = None
    ) -> None:
        self.sensors: list[Sensor] = list(sensors) if sensors else []
    
    def __iter__(self) -> Iterator[Sensor]: 
        return iter(self.sensors)
    
    def __len(self) -> int:
        return len(self.sensors)
    
    @overload
    def __getitem__(self,index: SupportsIndex) -> Sensor:
        ...
    @overload
    def __getitem__(self, index: slice) -> list[Sensor]:
        ...
    
    def __getitem__(self, index: Union[SupportsIndex, slice]) -> Union[Sensor, list[Sensor]]:
       return self.sensors[index]
   
    
        
class SapAndMoistureSensor(Sensor):
    ...
    
class WeatherSensor(Sensor):
    ...
    
class LuxSensor(Sensor):
    ...
    
    
import os
from .data import DataSource
from .sensors import SapAndMoistureSensor,WeatherSensor,LuxSensor

class PistachioDataSource(DataSource):
    base_path: str = "http://192.168.0.116/rehsani_local"

class PistachioSapAndMoistureSensor(SapAndMoistureSensor):
    minID:int = 1
    maxID:int = 7
    
    def get_path(self) -> str:
        """implements method from super class
        """
        return os.path.join(PistachioDataSource.base_path, "trew", "?id={id}&m={month}&y={year}".format(id=self.id,year=self.starttime.year,month=self.starttime.month))

    ...
    
class PistachioWeatherSensor(WeatherSensor):
    minID:int = 0
    maxID:int = 16
    def get_path(self) -> str:
        return os.path.join(PistachioDataSource.base_path, "weather","?id={id}&y={year}".format(id=self.id,year=self.starttime.year))
    
    ...
    
class PistachioLuxSensor(LuxSensor):
    minID:int=1
    maxID:int=2
    
    def get_path(self) -> str:
        return os.path.join(PistachioDataSource.base_path, "lux", "?id={id}&m={month}&y={year}".format(id=self.id,year=self.starttime.year,month=self.starttime.month))
    
    ... 

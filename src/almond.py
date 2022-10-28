import os
from .data import DataSource
from .sensors import SapAndMoistureSensor,WeatherSensor,LuxSensor

class AlmondDataSource(DataSource):
    base_path: str = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')), "data")

class AlmondSapAndMoistureSensor(SapAndMoistureSensor):
    minID:int = 1
    maxID:int = 7
    
    def get_path(self) -> str:
        """implements method from super class
        """
        return os.path.join(AlmondDataSource.base_path, "Data_TREWid{id}_{year}_{month:0>2}_almond.csv".format(id=self.id,year=self.starttime.year,month=self.starttime.month))

    ...
    
class AlmondWeatherSensor(WeatherSensor):
    def get_path(self) -> str:
        return os.path.join(AlmondDataSource.base_path, "Data_weather_{year}_{month:0>2}_almond.csv".format(year=self.starttime.year,month=self.starttime.month))
    
    ...
    
class AlmondLuxSensor(LuxSensor):
    minID:int=1
    maxID:int=2
    
    def get_path(self) -> str:
        raise NotImplementedError
    
    ... 
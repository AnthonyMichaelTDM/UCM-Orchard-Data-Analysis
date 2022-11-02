from dataclasses import dataclass
from datetime import datetime
import os
from Sample import DataSource
from sensors import SapAndMoistureSensor,WeatherSensor,LuxSensor

# FIXME: this module is deprecated

class AlmondSapAndMoistureSensor(SapAndMoistureSensor):
    minID:int = 1
    maxID:int = 7
    
    def __init__(self, starttime: datetime, endtime: datetime, id: int) -> None:
        super().__init__(starttime, endtime, id)
    
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
import os

from enum import Enum
from typing import List, NamedTuple

#root directory of project
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

class Data_Sensor_Type(Enum):
    """Enum for handling data sources, all supported data sources are here"""
    #enum states
    WEATHER_STATION = 0
    SAP_AND_MOISTURE_SENSOR = 1

#TODO: add a orchard_type enum to distinguish between almond and pistacio data
#TODO: add the naming formats to the orchard_type enum for each sensor type
class Config(NamedTuple):
    isdownloaded:bool
    base_path:str
    sensors_fields_and_ids:dict#Dict[Data_Sensor_Type,(List[str],List[int] or None)]
    
    def get_field_names(self, sensor_type:Data_Sensor_Type) -> List[str]:
        if sensor_type in self.sensors_fields_and_ids:
            return self.sensors_fields_and_ids.get(sensor_type)[0]
        else:
            raise RuntimeError("desired Data_Sensor_Type not yet implemented for this config")
        
    def get_sensor_ids(self, sensor_type:Data_Sensor_Type) -> List[int] | None:
        if sensor_type in self.sensors_fields_and_ids: 
            return self.sensors_fields_and_ids.get(sensor_type)[1]
        else:
            raise RuntimeError("desired Data_Sensor_Type not yet implemented for this config")

class Configs(Config, Enum):
    ALMOND = Config(False,os.path.join(ROOT_DIR, "data"),{
        Data_Sensor_Type.WEATHER_STATION:(["Date and Time","Field","Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"],None),
        Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR:(["Date and Time","Field","Sensor ID","Value 1","Value 2"],[x for x in range(1,7)])
    })
    PISTACIO = Config(True,"http://192.168.0.116/rehsani_local",{
        Data_Sensor_Type.WEATHER_STATION:(["Date and Time","Temperature [℃]","Humidity [RH%]","Pressure [hPa]","VOC [kΩ]"],[x for x in range(1,16)]),
        Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR:(["Date and Time","Value 1","Value 2"],[x for x in range(1,7)])
    })
    
    def get_path(self,sensor_type:Data_Sensor_Type, id:int | None = None, year:int | None = None, month:int | None = None) -> str:
        """optional args:
        id:int sensor id
        year:int last 2 digits of desired year (eg 2022 would be 22)
        month:int number associated with the desired month"""
        
        #if desired sensor type needs an id for this config, make sure one was given
        if self.needs_sensorid(sensor_type) and not id in self.get_sensor_ids(sensor_type):
            idmin = min(self.get_sensor_ids(sensor_type))
            idmax = max(self.get_sensor_ids(sensor_type))
            raise RuntimeError("given sensor id was {}, for this config and sensor type an id between {} and {} is required".format(id, idmin, idmax))
        
        #depending on what Config self is, and the sensor_type given, return proper path (either file path or url)
        match self:
            case Configs.ALMOND:
                match sensor_type:
                    case Data_Sensor_Type.WEATHER_STATION:
                        #ensure other needed optional parameters are present
                        if (isinstance(year,type(None)) or isinstance(month, type(None))):
                            raise RuntimeError("year and/or month parameter was not given")
                        return os.path.join(self.base_path, "Data_weather_{year}_{month:0>2}_almond.csv".format(year=year,month=month))
                    case Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR:
                        #ensure other needed optional parameters are present
                        if (isinstance(year,type(None)) or isinstance(month, type(None))):
                            raise RuntimeError("year and/or month parameter was not given")
                        return os.path.join(self.base_path, "Data_TREWid{id}_{year}_{month:0>2}_almond.csv".format(id=id,year=year,month=month))    
                    case _:
                        raise RuntimeError("desired Data_Sensor_Type not yet implemented for this config")
            case Configs.PISTACIO:
                match sensor_type:
                    case Data_Sensor_Type.WEATHER_STATION:
                        #ensure needed optional parameters are present
                        if isinstance(year,type(None)):
                            raise RuntimeError("year parameter was not given")
                        return os.path.join(self.base_path, "weather","?id={}&y={}".format(id=id,year=year))
                    case Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR:
                        #ensure needed optional parameters are present
                        if (isinstance(year,type(None)) or isinstance(month, type(None))):
                            raise RuntimeError("year and/or month parameter was not given")
                        return os.path.join(self.base_path, "trew", "?id={id}&m={month}&y={year}".format(id=id,year=year,month=month))    
                    case _:
                        raise RuntimeError("desired Data_Sensor_Type not yet implemented for this config")
            case _:
                raise RuntimeError("desired Config not yet implemented")
    
    def needs_sensorid(self, sensor_type:Data_Sensor_Type) -> bool:
        return (self.get_sensor_ids(sensor_type) is not None)
    
    def get_field_names(self,sensor_type:Data_Sensor_Type) -> List[str]:
        return super().get_field_names(sensor_type)
    
    def get_sensor_ids(self, sensor_type: Data_Sensor_Type) -> List[int] | None:
        return super().get_sensor_ids(sensor_type)

#sensor calibration coefficients
SAP_SENSOR_COEFFICIENTS = [
    {"a": -0.0442015591095395, "b": 191.7556055613598}, #Sensor 1
    {"a": -0.04861278384829307, "b": 202.27735563973982}, #Sensor 2
    {"a": -0.05762850897914471, "b": 215.35202712174151}, #Sensor 3
    {"a": -0.05445248031047814, "b": 212.60475914677914}, #Sensor 4
    {"a": -0.05701605695441798, "b": 211.74325309992707}, #Sensor 5
    {"a": -0.053728569077514346, "b": 212.98440419373264} #Sensor 6
]
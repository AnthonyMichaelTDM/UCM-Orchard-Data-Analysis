import os

from enum import Enum
from typing import List

class File_Data_Type(Enum):
    """Enum for handling data sources, all supported data sources are here"""
    #enum states
    WEATHER_STATION = ["weather stations", ["Date and Time","Field","Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"]]
    SAP_AND_MOISTURE_SENSOR = ["sap flow / moisture sensors", ["Date and Time","Field","Sensor ID","Value 1","Value 2"]]
    
    
    def ___str___(self):
        return "csv files from {} have the following fields: {}".format(self.value[0], self.value[1])
    
    def get_field_names(self) -> List[str]:
        """get the field names for this data source

        @return: a string list of the expected field names in CSV files from this source
        """
        return self.value[1]

#root directory of project
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

#data sources that have sensor IDs
SOURCES_WITH_SENSOR_IDS = [File_Data_Type.SAP_AND_MOISTURE_SENSOR]

SENSOR_IDS = [1,2,3,4,5,6] #DO NOT PUT 0 IN THIS LIST, or an infinite recursion will occur in wrapper.py

#base url to data files
# TODO: update
BASE_URL = "https://localhost"

#sensor calibration coefficients
SENSOR_COEFFICIENTS = [
    {"a": -0.0442015591095395, "b": 191.7556055613598}, #Sensor 1
    {"a": -0.04861278384829307, "b": 202.27735563973982}, #Sensor 2
    {"a": -0.05762850897914471, "b": 215.35202712174151}, #Sensor 3
    {"a": -0.05445248031047814, "b": 212.60475914677914}, #Sensor 4
    {"a": -0.05701605695441798, "b": 211.74325309992707}, #Sensor 5
    {"a": -0.053728569077514346, "b": 212.98440419373264} #Sensor 6
]
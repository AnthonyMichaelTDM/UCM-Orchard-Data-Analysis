import os

from data_parser import File_Data_Source

#root directory of project
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

#data sources that have sensor IDs
SOURCES_WITH_SENSOR_IDS = [File_Data_Source.SAP_AND_MOISTURE_SENSOR]

SENSOR_IDS = [1,2,3,4,5,6] #DO NOT PUT 0 IN THIS LIST, or an infinite recursion will occur in wrapper.py

#sensor calibration coefficients
SENSOR_COEFFICIENTS = [
    {"a": -0.0442015591095395, "b": 191.7556055613598}, #Sensor 1
    {"a": -0.04861278384829307, "b": 202.27735563973982}, #Sensor 2
    {"a": -0.05762850897914471, "b": 215.35202712174151}, #Sensor 3
    {"a": -0.05445248031047814, "b": 212.60475914677914}, #Sensor 4
    {"a": -0.05701605695441798, "b": 211.74325309992707}, #Sensor 5
    {"a": -0.053728569077514346, "b": 212.98440419373264} #Sensor 6
]
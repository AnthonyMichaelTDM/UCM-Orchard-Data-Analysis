import os

from data_parser import File_Data_Source

#root directory of project
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

#data sources that have sensor IDs
SOURCES_WITH_SENSOR_IDS = [File_Data_Source.SAP_AND_MOISTURE_SENSOR]

#sensor calibration coefficients
SENSOR_COEFFICIENTS = [
    {"a": 0.07281553398058249, "b": -328.56796116504836}, #Sensor 1
    {"a": 0.11723329425556858, "b": -557.9523251270027}, #Sensor 2
    {"a": 0.8547008547008547, "b": -4429.059829059829}, #Sensor 3
    {"a": 0.15641293013555796, "b": -655.3701772679879}, #Sensor 4
    {"a": -0.11867088607594932, "b": 632.8322784810124}, #Sensor 5
    {"a": 0.1482213438735177, "b": -665.4150197628454} #Sensor 6
]
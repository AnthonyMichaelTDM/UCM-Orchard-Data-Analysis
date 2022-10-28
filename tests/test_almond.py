import sys
import os
 
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to
# the sys.path.
sys.path.append(parent)

import src.sensors as sensors
import src.almond as almond
import src.data as data

def test_class_types():
    assert issubclass(almond.AlmondDataSource,data.DataSource)
    assert issubclass(almond.SapAndMoistureSensor, sensors.SapAndMoistureSensor)
    assert issubclass(almond.WeatherSensor, sensors.WeatherSensor)
    assert issubclass(almond.LuxSensor, sensors.LuxSensor)
    
    
def test_datasource_variable_types():
    s=almond.AlmondDataSource()
    assert type(s.base_path) == str
    
    
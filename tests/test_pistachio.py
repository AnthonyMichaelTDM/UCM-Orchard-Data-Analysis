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
import src.pistachio as pistachio
import src.data as data

def test_class_types():
    assert issubclass(pistachio.PistachioDataSource,data.DataSource)
    assert issubclass(pistachio.SapAndMoistureSensor, sensors.SapAndMoistureSensor)
    assert issubclass(pistachio.WeatherSensor, sensors.WeatherSensor)
    assert issubclass(pistachio.LuxSensor, sensors.LuxSensor)
    
    
def test_datasource_variable_types():
    s=pistachio.PistachioDataSource()
    assert type(s.base_path) == str
    
    
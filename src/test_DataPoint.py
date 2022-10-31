from datetime import datetime
from data import Sample, SapAndMoistureData, SapAndMoistureSampleBuilder, WeatherData, LuxData, WeatherSampleBuilder

sample_sapandmoisture: dict[str, str] = {
    "Date and Time":"2022-03-31 23:55:08",
    "Field":"Stevinson Almond",
    "Sensor ID":"TREW 2",
    "Value 1":"1074",
    "Value 2":"2244",
}
 
sample_weather: dict[str, str] = {
    "Date and Time":"2022-05-31 23:47:32",
    "Field":"Stevinson Almond",
    "Temperature [℃]":"15.06",
    "Humidity [RH%]":"76.84",
    "Pressure [hPa]":"1010.05",
    "Altitude [m]":"65.59",
    "VOC [kΩ]":"44.59",
}

# TODO: implement testing for LuxData class when I get a .csv file for them
sample_lux: dict[str, str] = {}


"""unit tests for the Sample interface and its subclasses"""

def test_Sample_subclasses_are_subclasses():
    assert issubclass(SapAndMoistureData,Sample)
    assert issubclass(WeatherData,Sample)
    assert issubclass(LuxData,Sample)
    
def test_SapAndMoistureData_Builder():
    sample:Sample = SapAndMoistureSampleBuilder.Build(sample_sapandmoisture)
    
    assert type(sample) == SapAndMoistureData
    
    assert sample.timestamp == datetime(2022,3,31,23,55,8)
    assert sample.value1 == 1074
    assert sample.value2 == 2244
    
def test_WeatherData_Builder():
    sample:Sample = WeatherSampleBuilder.Build(sample_weather)
    
    assert sample.timestamp == datetime(2022,5,31,23,47,32)
    assert sample.temperature == 15.06
    assert sample.humidity == 76.84
    assert sample.pressure == 1010.05
    assert sample.altitude == 65.59
    assert sample.voc == 44.59
    
# TODO: add integration tests for the Sample subclasses with the reader implementations

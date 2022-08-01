"""data_parser.py: parses data from either CSV files or webserver (depending on config) and returns data within"""
__author__ = "Anthony Rubick"

#parses the CSV files and returns the data within
import csv
import os
import requests
from datetime import datetime
from typing import Any, Dict, List
from definitions import Configs, Data_Sensor_Type

class Parser:
    def run(config: Configs, sensor_type: Data_Sensor_Type, id:int | None = None, year:int | None = None, month:int | None = None) -> List[Dict[str, Any]]:
        """optional args (same as args for get_path function of Configs class):
        id:int sensor id
        year:int last 2 digits of desired year (eg 2022 would be 22)
        month:int number associated with the desired month"""
        path = config.get_path(sensor_type, id=id, year=year, month=month) #while this function can throw errors, they are deliberately not handled
        
        if config.isdownloaded:
            return download_from_webserver(path, config, sensor_type)
        else:
            return parse_from_file(path, config, sensor_type)
        
# return a list of the rows as dictionaries (with field names as keys, and data as values)
def parse_from_file(file_path: str, config:Configs, sensor_type: Data_Sensor_Type) -> List[Dict[str, Any]]:
    """uses the csv module to parse the given file"""
    # ensure file_path is a file
    if not os.path.isfile(file_path):
        raise OSError("File `{}` Not Found".format(file_path))
    
    with open(file_path, mode='r', newline='') as csvfile:
        # get field names
        fieldnames: List[str]=config.get_field_names(sensor_type)
        
        # open csv file
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.DictReader(csvfile, fieldnames=fieldnames, dialect=dialect)
        
        # convert data into useful format
        reader = [x for x in reader] #convert reader to a list
        data = [process(x, config, sensor_type) for x in reader[1:]]
        return data

def download_from_webserver(url:str, config:Configs, sensor_type: Data_Sensor_Type):
    """
    use the requests module to download a file from the webserver, then save it to the data folder
    
    @param url: the URL for the data, returned by the get_path() function of the Configs class from the definitions module
    @raises RuntimeError: if file could not be downloaded (url doesn't work/exist), or the given data source is not hosted on the webserver yet
    """
    #get file from webserver w/ requests library, raise error is this couldn't be done
    try:
        response = requests.get(url).content
    except:
        raise RuntimeError("failed to connect to {}".format(url))
    
    #if isinstance(response, type(None)):
    #    raise RuntimeError("connection successful, but no data found")
    
    #decode and re-order response
    response = response.decode('utf-8').split(sep=';')[:-1]
    response.reverse()
    
    #convert response into the format returned by the Parse function ( List[Dict[str,any]])
    formatted_response: List[Dict[str,Any]] = []
    fields = config.get_field_names(sensor_type)
        
    for row in response: #all but last index because response ends in a semi-colon
        formattedrow: Dict[str,Any] = process(
            dict(zip(
                fields,
                row.split(sep=',')
            )),
            config,
            sensor_type
        )
        formatted_response.append(formattedrow)
        
    #return formatted response
    return formatted_response

def process(row_data: Dict[str, str], config:Configs, sensor_type: Data_Sensor_Type) -> Dict[str, Any]:
    """
    Process a given parsed row of data from a csv file from the given source, 
    convert data from str to the appropriate type
    and return converted data
    """
    #process row data appropriately for its data_source
    processed_row: Dict[str, Any] = {}
    match config:
        case Configs.ALMOND:
            match sensor_type:
                case Data_Sensor_Type.WEATHER_STATION: #if from a weather station
                    #process Date and Time
                    processed_row["Date and Time"] = datetime.strptime(row_data.get("Date and Time"), "%Y-%m-%d %H:%M:%S")
                    #process Field
                    processed_row["Field"] = row_data.get("Field")
                    #process Temperature
                    processed_row["Temperature [℃]"] = float(row_data.get("Temperature [℃]"))
                    #process Humidity
                    processed_row["Humidity [RH%]"] = float(row_data.get("Humidity [RH%]"))
                    #process Pressure
                    processed_row["Pressure [hPa]"] = float(row_data.get("Pressure [hPa]"))
                    #process Altitude
                    processed_row["Altitude [m]"] = float(row_data.get("Altitude [m]"))
                    #process VOC
                    processed_row["VOC [kΩ]"] = float(row_data.get("VOC [kΩ]"))
                case Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR: # if from a sap and moisture sensor
                    #process Date and Time
                    processed_row["Date and Time"] = datetime.strptime(row_data.get("Date and Time"), "%Y-%m-%d %H:%M:%S")
                    #process Field
                    processed_row["Field"] = row_data.get("Field")
                    #process SensorID
                    processed_row["Sensor ID"] = row_data.get("Sensor ID")
                    #process Value1
                    processed_row["Value 1"] = int(row_data.get("Value 1"))
                    #process Value2
                    processed_row["Value 2"] = int(row_data.get("Value 2"))
                case Data_Sensor_Type.LUX_SENSOR:
                    #process Date and Time
                    processed_row["Date and Time"] = datetime.strptime(row_data.get("Date and Time"), "%Y-%m-%d %H:%M:%S")
                    #process Light
                    processed_row["Light"] = float(row_data.get("Light"))
                case _:
                    raise RuntimeError("desired data source not implemented yet")
        case Configs.PISTACHIO:
            match sensor_type:
                case Data_Sensor_Type.WEATHER_STATION: #if from a weather station
                    #process Date and Time
                    processed_row["Date and Time"] = datetime.strptime(row_data.get("Date and Time"), "%Y-%m-%d %H:%M:%S")
                    #process Temperature
                    processed_row["Temperature [℃]"] = float(row_data.get("Temperature [℃]"))
                    #process Humidity
                    processed_row["Humidity [RH%]"] = float(row_data.get("Humidity [RH%]"))
                    #process Pressure
                    processed_row["Pressure [hPa]"] = float(row_data.get("Pressure [hPa]"))
                    #process Altitude
                    processed_row["Altitude [m]"] = float(row_data.get("Altitude [m]"))
                    #process VOC
                    processed_row["VOC [kΩ]"] = float(row_data.get("VOC [kΩ]"))
                case Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR: # if from a sap and moisture sensor
                    #process Date and Time
                    processed_row["Date and Time"] = datetime.strptime(row_data.get("Date and Time"), "%Y-%m-%d %H:%M:%S")
                    #process Value1
                    processed_row["Value 1"] = int(row_data.get("Value 1"))
                    #process Value2
                    processed_row["Value 2"] = int(row_data.get("Value 2"))
                case Data_Sensor_Type.LUX_SENSOR:
                    #process Date and Time
                    processed_row["Date and Time"] = datetime.strptime(row_data.get("Date and Time"), "%Y-%m-%d %H:%M:%S")
                    #process Light
                    processed_row["Light"] = float(row_data.get("Light"))
                case _:
                    raise RuntimeError("desired data source not implemented yet")
        case _:
            raise RuntimeError("desired config not yet implemented")
    #return processed data
    return processed_row

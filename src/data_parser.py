#parses the CSV files and returns the data within
import csv
from enum import Enum
import os
from datetime import datetime
from typing import Any, Dict, List

'''
todo:
-detect File_Data_Source automatically
'''


"""Enum for handling data sources, all supported data sources are here"""
class File_Data_Source(Enum):
    #enum states
    WEATHER_STATION = ["weather stations", ["Date and Time","Field","Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"]]
    SAP_AND_MOISTURE_SENSOR = ["sap flow / moisture sensors", ["Date and Time","Field","Sensor ID","Value 1","Value 2"]]
    
    
    def ___str___(self):
        return "csv files from {} have the following fields: {}".format(self.value[0], self.value[1])
    
    """get the field names for this data source
    
    Returns:
        List: string list of the expected field names in CSV files from this source
    """
    def get_field_names(self) -> List[str]:
        return self.value[1]

class Parser:
    # return a list of the rows as dictionaries (with field names as keys, and data as values)
    """ uses the csv module to parse the given file"""
    def parse(file_path: str, file_data_source: File_Data_Source) -> List[Dict[str, Any]]:
        # ensure file_path is a file
        if not os.path.isfile(file_path):
            raise OSError("File Not Found")
        
        with open(file_path, mode='r', newline='') as csvfile:
            # get field names
            fieldnames: List[str]=file_data_source.get_field_names()
            
            # open csv file
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
            reader = csv.DictReader(csvfile, fieldnames=fieldnames, dialect=dialect)
            
            # return data
            reader = [x for x in reader] #convert reader to a list
            data = [process(x, file_data_source) for x in reader[1:]]
            return data
        
"""
Process a given parsed row of data from a csv file from the given source, 
convert data from str to the appropriate type
and re
"""
def process(row_data: Dict[str, str], data_source: File_Data_Source) -> Dict[str, Any]:
    #process row data appropriately for its data_source
    processed_row: Dict[str, Any] = {}
    match data_source:
        case File_Data_Source.WEATHER_STATION: #if from a weather station
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
        case File_Data_Source.SAP_AND_MOISTURE_SENSOR: # if from a sap and moisture sensor
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
        case _:
            raise RuntimeError("desired data source not implemented yet")
    
    #return processed data
    return processed_row
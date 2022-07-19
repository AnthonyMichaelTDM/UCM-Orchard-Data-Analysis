#with the data, run various data analysis operations on it
from datetime import datetime
from typing import Any, Dict, List
from definitions import SOURCES_WITH_SENSOR_IDS, File_Data_Type

class Processor: 
    """processes data"""    
    def __init__(self, data: List[Dict[str, Any]], data_source: File_Data_Type):
        """constructor"""
        self.data: Dict[datetime,Dict[str, Any]] = {}
        self.fields: List[str] = data_source.get_field_names()
        self.source: File_Data_Type = data_source
        self.sensor_id: int = 0
        #if the data source has sensor ID's, store them here for later use
        if data_source in SOURCES_WITH_SENSOR_IDS:
            self.sensor_id = int( ''.join( [c for c in str(data[0].get("Sensor ID")) if c.isdecimal()] ) ) #extract all the numeric characters in data[0].get("Sensor ID") and convert the resulting string into an integer
            if self.sensor_id <= 0:
                raise RuntimeError("failed to determine sensor ID")
        
        #restructure data such that it is a dictionary with time as the key and (a dictionary with field name as key and data as value) as the value
        for row in data:
            self.data[row.pop("Date and Time")] = row
    
    def __str__(self) -> str:
        #header
        str_rep:str = ','.join(self.fields) + '\n'
        #content
        for row_timestamp, row_data in self.data.items():
            str_rep += row_timestamp.strftime("%Y-%m-%d %H:%M:%S") + ","
            str_rep += ','.join( [ str(v) for v in row_data.values()] ) + "\n"
        #return
        return str_rep
    
    def remove_field(self, field_to_remove:str):
        """removes the given field from data"""
        print(field_to_remove)
        for data_entry in self.data.values(): 
            del data_entry[field_to_remove]
        self.fields.remove(field_to_remove)
    def remove_fields(self, fields_to_remove: List[str]):
        """removes the given fields from data"""
        for field in fields_to_remove:
            self.remove_field(field)
            
    def keep_time_range(self, from_datetime: datetime, to_datetime: datetime):
        """remove data that's not in the given time frame"""
        data_to_keep: Dict[datetime, Dict[str, Any]] = {}
        for key in self.data.keys():
            if key >= from_datetime and key <= to_datetime:
                data_to_keep[key] = self.data.get(key) 
        
        self.data.clear()
        self.data = data_to_keep
    
            
#with the data, run various data analysis operations on it
from datetime import datetime
from data_parser import File_Data_Source
from typing import Any, Dict, List


class Processor: #processes data
    data:Dict[datetime,Dict[str, Any]]={}
    fields: List[str] = []
    
    """constructor"""
    def __init__(self, data: List[Dict[str, Any]], data_source: File_Data_Source):
        self.fields = data_source.get_field_names()
        for row in data:
            self.data[row.pop("Date and Time")] = row #restructure data such that it is a dictionary with time as the key and (a dictionary with field name as key and data as value) as value
    
    def __str__(self) -> str:
        #header
        str_rep:str = ','.join(self.fields) + '\n'
        #content
        for row_timestamp, row_data in self.data.items():
            str_rep += row_timestamp.strftime("%Y-%m-%d %H:%M:%S") + ","
            str_rep += ','.join( [ str(v) for v in row_data.values()] ) + "\n"
        #return
        return str_rep
        
        
        
    
    """removes the given field from data"""
    def remove_field(self, field_to_remove:str):
        for data_entry in self.data.values(): 
            del data_entry[field_to_remove]
        self.fields.remove(field_to_remove)
    """removes the given fields from data"""
    def remove_fields(self, fields_to_remove: List[str]):
        for field in fields_to_remove:
            self.remove_field(field)
            
    """remove data that's not in the given time frame"""
    def keep_time_range(self, from_datetime: datetime, to_datetime: datetime):
        data_to_keep: Dict[datetime, Dict[str, Any]] = {}
        for key in self.data.keys():
            if key >= from_datetime and key <= to_datetime:
                data_to_keep[key] = self.data.get(key) 
        
        self.data.clear()
        self.data = data_to_keep
    
            
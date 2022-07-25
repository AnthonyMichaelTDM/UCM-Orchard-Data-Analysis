#with the data, run various data analysis operations on it
from datetime import datetime, timedelta
from re import T
from typing import Any, Dict, List
import warnings
from definitions import SOURCES_WITH_SENSOR_IDS, File_Data_Type

class Processor: 
    """processes data"""    
    def __init__(self, data: List[Dict[str, Any]], data_source: File_Data_Type):
        """constructor"""
        self.data: Dict[datetime,Dict[str, Any]] = {}
        self.fields: List[str] = data_source.get_field_names().copy()
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
        for data_entry in self.data.values():
            if field_to_remove in data_entry:
                del data_entry[field_to_remove]
            else:
                warnings.warn("field {} is missing".format(field_to_remove))
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
    
    def smoothen_data(self, starttime:datetime, interval: timedelta):
        """smoothen data out, storing average readings in every `interval` starting at `starttime`"""
        smooth_data: Dict[datetime,Dict[str, Any]] = {}
        
        #calc count and sum
        for timestamp, data in self.data.items():
            #calculate time interval this row falls into
            units_from_start = (timestamp-starttime) // interval
            timegroup = starttime + (interval * units_from_start)
            smooth_data[timegroup] = {}
            
            # update count for this time interval
            if not "Count" in smooth_data[timegroup]:
                smooth_data[timegroup]['Count'] = 1
            else: 
                smooth_data[timegroup]['Count'] += 1
            # update sum for all numeric data
            for field, fielddata in data.items():
                if type(fielddata) in (int, float):
                    if not field in smooth_data[timegroup]:
                        smooth_data[timegroup][field] = 0
                    smooth_data[timegroup][field] += fielddata
                else: 
                    smooth_data[timegroup][field] = fielddata
                    
        #calc average from count and sum
        for data in smooth_data.values():
            count = data.get('Count')
            del data['Count']
            
            for fielddata in data.values():
                if type(fielddata) in (int, float):
                    fielddata /= count
                    
        self.data.clear()
        self.data = smooth_data
            
            
                    
                    
            
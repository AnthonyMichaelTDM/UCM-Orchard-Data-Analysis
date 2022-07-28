#with the data, run various data analysis operations on it
from datetime import datetime, timedelta
from typing import Any, Dict, List
from definitions import Configs, Data_Sensor_Type

class Processor: 
    """processes data"""    
    def __init__(self, data: List[Dict[str, Any]], config:Configs, sensor_type: Data_Sensor_Type, sensor_id:int | None=None):
        """constructor"""
        self.data: Dict[datetime,Dict[str, Any]] = {}
        self.fields: List[str] = config.get_field_names(sensor_type)
        self.sensor_type: Data_Sensor_Type = sensor_type
        self.sensor_id: int = 0
        #if the data source needs sensor ID's, ensure one was given
        if config.needs_sensorid(sensor_type):
            if (not isinstance(sensor_id,type(None))) and sensor_id in config.get_sensor_ids(sensor_type):
                self.sensor_id = sensor_id
            else:
                raise RuntimeError("sensor_id parameter was either not given, or outside of valid range ({} to {} for this sensor)".format(min(config.get_sensor_ids),max(config.get_sensor_ids())))

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
        if field_to_remove in self.fields:
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
        
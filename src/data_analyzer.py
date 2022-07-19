from typing import Any, Dict, List
from data_parser import File_Data_Source
from data_processor import Processor
from definitions import SENSOR_COEFFICIENTS

#analyze and plot data from the various sources
class Analyzer:
    def __init__(self, processor:Processor) -> None:
        """constructor"""
        self.source: File_Data_Source = processor.source
        self.fields: List[str] = processor.fields
        self.sensorID: int =processor.sensor_id
        #restructure data such that it is a dictionary with the field name as the key and (a list of the data associated with the field) as the value
        raw_data: List[Dict[str, Any]] = [ ( {"Date and Time": row[0]} | row[1] )for row in processor.data.items()] #list with dictionary of the data for every row
        self.data: Dict[str,List[Any]] = { field: [ row.get(field) for row in raw_data ]  for field in processor.fields  }
        
    
    def analyze(self):
        """analyze data depending on the source
        
        raises RuntimeError: if data source of self is not implemented yet
        """
        match self.source:
            case File_Data_Source.WEATHER_STATION:
                pass
            case File_Data_Source.SAP_AND_MOISTURE_SENSOR:
                # calc deltaT
                self.data["ΔT"] = [ (x-1000)/20 for x in self.data.get("Value 1")]
                minT = min(self.data.get("ΔT"))
                #calc K
                self.data["K"] = [ -(minT-dt)/dt for dt in self.data.get("ΔT")]
                #calc sap flux density
                self.data["Sap Flux Density"] = [ 118.99*pow(10,-6)*K  for K in self.data.get("K")]
                #calc relative moisture
                self.data["Relative Moisture %"] = [ (SENSOR_COEFFICIENTS[self.sensorID-1].get("a") * x) + SENSOR_COEFFICIENTS[self.sensorID-1].get("b") for x in self.data.get("Value 2")]
                
                #a and b coefficients are the slope and y-int of a line that goes between the coords (ave wet, 100) and (ave dry, 0), ave wet and ave dry are calculated from the calibration files and are sensor specific
            case _:
                raise RuntimeError("desired data source not implemented yet")
    
    
    
    
        

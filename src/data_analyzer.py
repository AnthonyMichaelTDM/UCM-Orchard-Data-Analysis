from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple
from data_processor import Processor
from definitions import SENSOR_COEFFICIENTS, File_Data_Type

#analyze and plot data from the various sources
class Analyzer:
    def __init__(self, processor:Processor) -> None:
        """constructor"""
        self.source: File_Data_Type = processor.source
        self.fields: List[str] = processor.fields
        self.sensorID: int =processor.sensor_id
        #restructure data such that it is a dictionary with the field name as the key and (a list of the data associated with the field) as the value
        raw_data: List[Dict[str, Any]] = [ ( {"Date and Time": row[0]} | row[1] )for row in processor.data.items()] #list with dictionary of the data for every row
        self.data: Dict[str,List[Any]] = { field: [ row.get(field) for row in raw_data ]  for field in processor.fields  }
        
    
    def analyze(self):
        """analyze data depending on the source
        
        raises RuntimeError: if data source of self is not implemented yet
        raises RuntimeError: if self.data has any empty values
        """
        if any( [len(x)==0 for x in self.data.values()] ):
            raise RuntimeError("one or more kv pairs in self.data have empty lists as values, there is likely a hole in the data for the desired timeframe")
            
        match self.source:
            case File_Data_Type.WEATHER_STATION:
                pass
            case File_Data_Type.SAP_AND_MOISTURE_SENSOR:
                if not ("Value 1" in self.data and "Value 2" in self.data and "Date and Time" in self.data):
                    raise RuntimeError("Value 1, Value 2, or Date and Time missing from data")
                # calc deltaT
                self.data["ΔT"] = [ (x-1000)/20 for x in self.data.get("Value 1")]
                
                # calc minT
                self.data["minT"] = calc_minT_list(self.data.get("ΔT"),self.data.get("Date and Time"))
                
                #calc K
                self.data["K"] = [ -( self.data.get("minT")[i] -dt)/dt for i,dt in enumerate(self.data.get("ΔT"))]
                #calc sap flux density
                self.data["Sap Flux Density"] = [ 118.99*pow(10,-6)*K  for K in self.data.get("K")]
                #calc relative moisture
                self.data["Relative Moisture %"] = [ (SENSOR_COEFFICIENTS[self.sensorID-1].get("a") * x) + SENSOR_COEFFICIENTS[self.sensorID-1].get("b") for x in self.data.get("Value 2")]
                
                #a and b coefficients are the slope and y-int of a line that goes between the coords (ave wet, 100) and (ave dry, 0), ave wet and ave dry are calculated from the calibration files and are sensor specific
            case _:
                raise RuntimeError("desired data source not implemented yet")
    
def calc_minT_list(deltat_list:List[float], datetime_list:List[datetime]) -> List[float]:
    tempminT:Dict[datetime,Tuple(float,int)] = {} # dictionary with time as key and a tuple of minT for the day AND dt readings throughout the day as values
    prevdatetime = next(iter(datetime_list)) #get first key in date_T_dict in O(1) time
    nightreadingstotaldt = 0.0 #total dt between midnight and 7am for the day being processed
    nightreadingscount = 0 # count of the dt's between midnight and 7am for the day being processed 
    len_of_filtered_datetime_list = len([x for x in datetime_list if x.hour >= 0 and x.hour <= 7])
    dayreadingscount = 0 # count of readings in the day being processed
    
    #create dict w/ date as key and deltaT as value
    #for every day, average the deltaT's and store in minT #minT should be the average ΔT values from hour 0 to 7 every day
    for currdatetime,dt in dict(zip(datetime_list, deltat_list)).items():
        timediff = currdatetime - prevdatetime
        is_same_day = abs(timediff) < timedelta(days=1)
        if is_same_day:
            dayreadingscount += 1
        else:
            dayreadingscount = 1
        
        #for calculations, ignore keys where hour is not between 0 and 7
        if currdatetime.hour >= 0 and currdatetime.hour <= 7:
            if is_same_day and nightreadingscount < len_of_filtered_datetime_list -1: #if it's the same day and not the last valid iteration,
                nightreadingstotaldt += dt
                nightreadingscount += 1
            elif not nightreadingscount < len_of_filtered_datetime_list -1: #it's the last iteration
                nightreadingstotaldt += dt
                nightreadingscount += 1
                tempminT[datetime(currdatetime.year,currdatetime.month,currdatetime.day)] = (nightreadingstotaldt / nightreadingscount,dayreadingscount)
                nightreadingscount = 0
                nightreadingstotaldt = 0
            else:
                tempminT[datetime(currdatetime.year,currdatetime.month,currdatetime.day)] = (nightreadingstotaldt / nightreadingscount,dayreadingscount)
                nightreadingscount = 1
                nightreadingstotaldt = dt
        
        prevdatetime = currdatetime
            
    #build up minT list of same size as datetime_list, and return it
    minT_list = []
    for ttup in tempminT.values():
        minT_list.extend( [ttup[0] for n in range(ttup[1])] )
    return minT_list

    
        

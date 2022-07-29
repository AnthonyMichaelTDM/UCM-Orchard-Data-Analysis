from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from more_itertools import is_sorted
from data_processor import Processor
from definitions import SAP_SENSOR_COEFFICIENTS, Data_Sensor_Type

#analyze and plot data from the various sources
class Analyzer:
    def __init__(self, processor:Processor) -> None:
        """constructor"""
        self.source: Data_Sensor_Type = processor.sensor_type
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
        
        #TODO: if different sources (ie almond orchard or pistacio orchard) need to treat the data from teh same common sensor differently, you'll need to implement that here
        match self.source:
            case Data_Sensor_Type.WEATHER_STATION:
                pass
            case Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR:
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
                self.data["Relative Moisture %"] = [ (SAP_SENSOR_COEFFICIENTS[self.sensorID-1].get("a") * x) + SAP_SENSOR_COEFFICIENTS[self.sensorID-1].get("b") for x in self.data.get("Value 2")]
                
                #a and b coefficients are the slope and y-int of a line that goes between the coords (ave wet, 100) and (ave dry, 0), ave wet and ave dry are calculated from the calibration files and are sensor specific
            case _:
                raise RuntimeError("desired data source not implemented yet")
    
def calc_minT_list(deltat_list:List[float], datetime_list:List[datetime]) -> List[float]:
    """ given a list of ΔT's, and the equally sized list of datetimes those ΔT's were calculated for, 
    return a list of minT's (the average ΔT between the hours of 0 and 7 (inclusive) (midnight to 7am)
    
    raise RuntimeError if datetime_list and deltat_list are not the same size"""
    tempminT:Dict[datetime,Tuple(float,int)] = {} # dictionary with time as key and a tuple of minT for the day AND dt readings throughout the day as values
    prevdatetime = 0 #previous datetime, used in loop
    nightreadingstotaldt = 0.0 #total dt between midnight and 7am for the day being processed
    nightreadingscount = 0 # count of the dt's between midnight and 7am for the day being processed
    dayreadingscount = 0 # count of readings in the day being processed
    
    datetimelen = len(datetime_list) #stored as a variable because it's used in 3 places (one of them is a loop), calculating the length each time is inefficient
    deltatlen = len(deltat_list) #stored for consistency
    if datetimelen != deltatlen :
        raise RuntimeError("length of datetime_list ({}) does not equal that of deltat_list ({})".format(datetimelen,deltatlen))
    
    #run what would be the first iteration outside of the loop to initialize everything
    prevdatetime=next(iter(datetime_list)) #using the next(iter( [] )) method because of it's O(1) time complexity
    dayreadingscount = 1
    if prevdatetime.hour >= 0 and prevdatetime.hour <= 7:
        nightreadingstotaldt = next(iter(deltat_list))
        nightreadingscount = 1
        
    #create dict w/ date as key and deltaT as value
    #for every day, average the deltaT's and store in minT #minT should be the average ΔT values from hour 0 to 7 every day
    for i,(currdatetime,dt) in enumerate(dict(zip(datetime_list[1:], deltat_list[1:])).items()): #skips first indexes because those are "used" during initialization
        #if it's the same day
        if currdatetime.day==prevdatetime.day and currdatetime.month==prevdatetime.month  and  currdatetime.year==prevdatetime.year: 
            #for mint calculations, ignore keys where hour is not between 0 and 7
            if currdatetime.hour >= 0 and currdatetime.hour <= 7:
                #if night and same day, update values
                nightreadingstotaldt += dt
                nightreadingscount += 1
                
            #update count for day
            dayreadingscount += 1
        else:
            #for mint calculations, ignore keys where hour is not between 0 and 7
            if currdatetime.hour >= 0 and currdatetime.hour <= 7:
                # if night but not same day, store past values, then reset values 
                tempminT[datetime(prevdatetime.year,prevdatetime.month,prevdatetime.day)] = (nightreadingstotaldt / nightreadingscount,dayreadingscount)
                nightreadingstotaldt = dt
                nightreadingscount = 1
                
            #reset count for day
            dayreadingscount = 1
        
        #because mint values are stored when the "next day" starts, it is necessary to explicityly store the data on the last iteration of the loop so that the data from the last day isn't ignored
        if i+1 >= datetimelen-1: #the +1 is because len returns the number of elements in an array, not the index of the last element (which is 1 less)
                                 #the -1 is there because we skip the first element of datetime when making the enumerated iterator this loop iterates over
            tempminT[datetime(prevdatetime.year,prevdatetime.month,prevdatetime.day)] = (nightreadingstotaldt / nightreadingscount,dayreadingscount)
        
        prevdatetime = currdatetime
        
    #build up minT list of same size as datetime_list, and return it
    minT_list = []
    for t_tup in tempminT.values():
        minT_list.extend( [t_tup[0] for n in range(t_tup[1])] )
    return minT_list

    
        

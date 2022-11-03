from datetime import date, datetime
from typing import Any

class AnalyzeSapFlow():    
    @staticmethod
    def run_relativemoisture(value2: list[int], sensor_id: int, sensor_coefficients: list[dict[str,float]]) -> list[float]:
        #calc relative moisture
        relative_moisture: list[float] = [ max(0.0,min(100,(sensor_coefficients[sensor_id-1]["a"] * x) + sensor_coefficients[sensor_id-1]["b"])) for x in value2]
        #the max and min here ensure this value is between 0 and 100
        
        #a and b coefficients are the slope and y-int of a line that goes between the coords (ave wet, 100) and (ave dry, 0), ave wet and ave dry are calculated from the calibration files and are sensor specific
        return relative_moisture
    
    
    @staticmethod
    def run_sapflux(value1: list[int], time: list[datetime]) -> list[Any]:
        sap_flux_density: list[float] = [
            max(0,118.99*pow(10,-6)*K ) # max to make sure it's not negative
            for K in AnalyzeSapFlow.calc_K(value1, time)] 
        
        return sap_flux_density
    
    
    @staticmethod
    def calc_K(value1:list[int], time:list[datetime]) -> list[float]:
        #calculate change in T
        deltaT = [(x-1000)/20 for x in value1]
        
        #calculate minT
        minT = AnalyzeSapFlow.calc_minT_list(deltaT, time)
        
        #calc K
        K: list[float] = []  
        for i,dt in enumerate(deltaT):
            day = time[i].date()
            if day in minT:
                mt = minT[day]
                
                K.append( -(mt - dt) / dt )
            else:
                K.append( 0 )
        
        return K
    
    
    @staticmethod
    def calc_minT_list(deltat_list:list[float], datetime_list:list[datetime]) -> dict[date, float]:
        """given a list of ΔT's, and the equally sized list of datetimes those ΔT's were calculated for, 
        return a list of minT's (the average ΔT between the hours of 0 and 7 (inclusive) (midnight to 7am))

        Args:
            deltat_list (List[float]): _description_
            datetime_list (List[datetime]): _description_

        Raises:
            RuntimeError: raise RuntimeError if datetime_list and deltat_list are not the same size

        Returns:
            List[float]: a list of the average ΔT between the hours of 0 and 7 (inclusive) (midnight to 7am)
        """
        tempminT:dict[date,float] = {} # dictionary with time as key and a tuple of minT for the day AND dt readings throughout the day as values
        prevdatetime: datetime = datetime_list[0] #previous dateti, used in loop
        nightreadingstotaldt: float = 0.0 #total dt between midnight and 7am for the day being processed
        nightreadingscount: int= 0 # count of the dt's between midnight and 7am for the day being processed
        
        datetimelen: int = len(datetime_list) #stored as a variable because it's used in 3 places (one of them is a loop), calculating the length each time is inefficient
        deltatlen: int = len(deltat_list) #stored for consistency
        if datetimelen != deltatlen :
            raise RuntimeError("length of datetime_list ({}) does not equal that of deltat_list ({})".format(datetimelen,deltatlen))
        
        #run what would be the first iteration outside of the loop to initialize everything
        if prevdatetime.hour >= 0 and prevdatetime.hour <= 7:
            nightreadingstotaldt = deltat_list[0]
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
            else:
                #for mint calculations, ignore keys where hour is not between 0 and 7
                if currdatetime.hour >= 0 and currdatetime.hour <= 7:
                    # if night but not same day, store past values, then reset values 
                    tempminT[prevdatetime.date()] = nightreadingstotaldt / nightreadingscount
                    nightreadingstotaldt = dt
                    nightreadingscount = 1
            
            #because mint values are stored when the "next day" starts, it is necessary to explicityly store the data on the last iteration of the loop so that the data from the last day isn't ignored
            if i+1 >= datetimelen-1: #the +1 is because len returns the number of elements in an array, not the index of the last element (which is 1 less)
                                    #the -1 is there because we skip the first element of datetime when making the enumerated iterator this loop iterates over
                tempminT[prevdatetime.date()] = nightreadingstotaldt / nightreadingscount
            
            prevdatetime = currdatetime
        return tempminT
    

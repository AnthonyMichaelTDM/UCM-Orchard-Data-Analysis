from datetime import datetime, timedelta
from typing import List
from data_analyzer import Analyzer
from data_parser import Parser
from data_processor import Processor
from definitions import Configs, Data_Sensor_Type
import matplotlib.pyplot as plt

class Wrapper:
    """acts as a layer between the user and the library-esque functionality of the data_... files, """
    
    #TODO: implement changes to definitions.py
    def run(config: Configs, startdate:datetime, enddate:datetime, sap_sensorid:int | None = None, weather_sensorid:int | None = None, lux_sensorid:int | None = None):
        """'optional' args:
        sap_sensorid:int id for the sap and moisture sensor whose data is to be processed
        weather_sensorid:int id for the weather station whose data is to be processed"""
        
        match config:
            case Configs.ALMOND:
                #ensure all needed optional variables where given and call runner function
                if sap_sensorid in config.get_sensor_ids(Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR):
                    Wrapper.__run(config=config, startdate=startdate, enddate=enddate, sap_sensorids=[sap_sensorid]) 
                else:
                    raise RuntimeError("sensor(s) with given id(s) not found")
            case Configs.PISTACHIO:
                #ensure all needed optional variables where given and call runner function
                if ((not isinstance(sap_sensorid,type(None))) and sap_sensorid in config.get_sensor_ids(Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR)) and (
                    (not isinstance(weather_sensorid,type(None))) and weather_sensorid in config.get_sensor_ids(Data_Sensor_Type.WEATHER_STATION)
                ):
                    Wrapper.__run(config=config, startdate=startdate, enddate=enddate, sap_sensorids=[sap_sensorid], weather_sensorids=[weather_sensorid], lux_sensorids=[lux_sensorid]) 
                else:
                    raise RuntimeError("sensor(s) with given id(s) not found")
            case _:
                raise RuntimeError("desired config not yet implemented")
        
    def __run(config:Configs, startdate:datetime, enddate:datetime, sap_sensorids:List[int] | None = None, weather_sensorids:List[int] | None = None, lux_sensorids:int|None=None):
        #DATA
        cols = 4 #columns of subplots
        rows = 3 #rows of subplots 
        nsapids = len(sap_sensorids) if not isinstance(sap_sensorids,type(None)) else 1
        nweatherids = len(weather_sensorids) if not isinstance(weather_sensorids,type(None)) else 1
        nluxids = len(lux_sensorids) if not isinstance(lux_sensorids, type(None)) else 1
        indexes_used_for_sap = 4
        indexes_used_for_weather = 4
        indexes_used_for_lux = 1
        
        #make sure sap/weather sensor ids is a list
        if sap_sensorids == None:
            sap_sensorids = [None]
        if weather_sensorids == None:
            weather_sensorids = [None]
        if lux_sensorids == None:
            lux_sensorids = [None]
        
        #SAP AND MOISTURE SENSOR(S)
        for id in sap_sensorids:
            sensor_type = Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR
            #parse data
            data = Wrapper.__get_data(config=config, sensor_type=sensor_type, startdate=startdate, enddate=enddate, sensorid=id)
            #process data
            processor = Processor(data,config,sensor_type,sensor_id=id)
            processor.remove_fields(['Field','Sensor ID'])#these might already be gone, but it depends on Config
            processor.keep_time_range(startdate,enddate)
            processor.smoothen_data(startdate, timedelta(minutes=60))
            #analyze data
            analyzer = Analyzer(processor)
            try:
                analyzer.analyze()
            except RuntimeError as e:
                print("ERROR: {}\n\tskipping...".format(e.args[0]))
                continue
            
            #plot data
            x:datetime = analyzer.data.get("Date and Time")
            y_titles = ["Sap Flux Density", "Relative Moisture %"]
            y_lists = [analyzer.data.get(title) for title in y_titles]
            
            for i,y in enumerate(y_lists):
                plt.subplot(rows,cols,(1 +2*i,2 +2*i))
                if nsapids > 1:
                    plt.plot(x,y,linewidth=0.5, label="{}".format(id)) #the comprehension here ensures no y values are below zero
                    plt.legend()
                else: 
                    plt.plot(x,y) #the comprehension here ensures no y values are below zero
                plt.title("{}\n".format(y_titles[i]))
                plt.xticks(rotation=45)

        #WEATHER STATION(S)
        for id in weather_sensorids:
            sensor_type = Data_Sensor_Type.WEATHER_STATION
            #parse data
            data = Wrapper.__get_data(config=config, sensor_type=sensor_type, startdate=startdate, enddate=enddate, sensorid=id)
            #process data
            processor = Processor(data,config,sensor_type,sensor_id=id)
            processor.remove_fields(['Field','Altitude [m]'])#these might already be gone, but it depends on Config
            processor.keep_time_range(startdate,enddate)
            processor.smoothen_data(startdate, timedelta(minutes=60))
            #analyze data
            analyzer = Analyzer(processor)
            try:
                analyzer.analyze()
            except RuntimeError as e:
                print("ERROR: {}\n\tskipping...".format(e.args[0]))
                continue
            
            #plot data
            x:datetime = analyzer.data.get("Date and Time")
            y_titles = ["Temperature [℃]","Humidity [RH%]","Pressure [hPa]","VOC [kΩ]"]
            y_lists = [analyzer.data.get(title) for title in y_titles]
            for i,y in enumerate(y_lists):
                n=i+1
                plt.subplot(rows,cols, n + indexes_used_for_sap)
                if nweatherids > 1:
                    plt.legend()
                    plt.plot(x,y,linewidth=0.5, label="{}".format(id)) #the comprehension here ensures no y values are below zero
                else: 
                    plt.plot(x,y)
                plt.title("{}\n".format(y_titles[i]))
                plt.xticks(rotation=45)
                
        #LUX_SENSOR(S)
        for id in lux_sensorids:
            sensor_type = Data_Sensor_Type.LUX_SENSOR
            #parse data
            data = Wrapper.__get_data(config=config, sensor_type=sensor_type, startdate=startdate, enddate=enddate, sensorid=id)
            #process data
            processor = Processor(data,config,sensor_type,sensor_id=id)
            processor.keep_time_range(startdate,enddate)
            processor.smoothen_data(startdate, timedelta(minutes=60))
            #analyze data
            analyzer = Analyzer(processor)
            try:
                analyzer.analyze()
            except RuntimeError as e:
                print("ERROR: {}\n\tskipping...".format(e.args[0]))
                continue
            
            #plot data
            x:datetime = analyzer.data.get("Date and Time")
            y_titles = ["Light"]
            y_lists = [analyzer.data.get(title) for title in y_titles]
            for i,y in enumerate(y_lists):
                n=i+1
                plt.subplot(rows,cols, n + indexes_used_for_sap + indexes_used_for_weather)
                if nluxids > 1:
                    plt.legend()
                    plt.plot(x,y,linewidth=0.5, label="{}".format(id)) #the comprehension here ensures no y values are below zero
                else: 
                    plt.plot(x,y)
                plt.title("{}\n".format(y_titles[i]))
                plt.xticks(rotation=45)
        
        #show plot
        plt.tight_layout(pad=0.3, rect=[0,0,1,1])
        plt.show()        
 
    def __get_data(config:Configs, sensor_type: Data_Sensor_Type, startdate:datetime, enddate:datetime, sensorid:int | None=None):
        """
        parse data in years/months timeframe (needs to read multiple files)
        if an error is thrown here it's probably because a file doesn't exist in ../data

        'optional' args:
        sensorid:int the id of the sensor, if needed"""
        
        #if a sensor id was needed, but none was given, throw an error
        if config.needs_sensorid(sensor_type) and isinstance(sensorid,type(None)):
            raise RuntimeError("for this config, the given sensor requires a sensor id and none was given")
        
        match config:
            case Configs.ALMOND:
                match sensor_type:
                    case Data_Sensor_Type.WEATHER_STATION:
                        sensor_data = []
                        if startdate.year < enddate.year:
                            #first year
                            for month in range(startdate.month,12+1):
                                sensor_data.extend(Parser.run(config, sensor_type, year=startdate.year%100, month=month))
                            #middle years
                            if startdate.year+1 < enddate.year-1:
                                for year in range(startdate.year+1,enddate.year-1):
                                    for month in range(1,12+1):
                                        sensor_data.extend(Parser.run(config, sensor_type,year=year%100,month=month)) 
                            #last year
                            for month in range(enddate.month,12+1):
                                sensor_data.extend(Parser.run(config, sensor_type,year=enddate.year%100,month=month))
                        elif startdate.month < enddate.month:
                            #months
                            for month in range(startdate.month,enddate.month+1):
                                sensor_data.extend(Parser.run(config, sensor_type,year=startdate.year%100,month=month))
                        else: 
                            sensor_data.extend(Parser.run(config, sensor_type, year=startdate.year%100, month=startdate.month))
                        return sensor_data
                    case Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR:
                        sensor_data = []
                        if startdate.year < enddate.year:
                            #first year
                            for month in range(startdate.month,12+1):
                                sensor_data.extend(Parser.run(config, sensor_type, id=sensorid, year=startdate.year%100, month=month))
                            #middle years
                            if startdate.year+1 < enddate.year-1:
                                for year in range(startdate.year+1,enddate.year-1):
                                    for month in range(1,12+1):
                                        sensor_data.extend(Parser.run(config, sensor_type, id=sensorid, year=year%100, month=month)) 
                            #last year
                            for month in range(enddate.month,12+1):
                                sensor_data.extend(Parser.run(config, sensor_type, id=sensorid, year=enddate.year%100, month=month))
                        elif startdate.month < enddate.month:
                            #months
                            for month in range(startdate.month,enddate.month+1):
                                sensor_data.extend(Parser.run(config, sensor_type, id=sensorid, year=startdate.year%100, month=month))
                        else: 
                            sensor_data.extend(Parser.run(config, sensor_type, id=sensorid, year=startdate.year%100, month=startdate.month))
                        return sensor_data
                    case _:
                        raise RuntimeError("desired Data_Sensor_Type not yet implemented for this config")
            case Configs.PISTACHIO:
                match sensor_type:
                    case Data_Sensor_Type.WEATHER_STATION:
                        sensor_data = []
                        if startdate.year < enddate.year:
                            #first year
                            sensor_data.extend(Parser.run(config, sensor_type, id=sensorid, year=startdate.year%100))
                            #middle years
                            if startdate.year+1 < enddate.year-1:
                                for year in range(startdate.year+1,enddate.year-1):
                                    sensor_data.extend(Parser.run(config, sensor_type, id=sensorid, year=year%100)) 
                            #last year
                            sensor_data.extend(Parser.run(config, sensor_type, id=sensorid, year=enddate.year%100))
                        else:
                            sensor_data.extend(Parser.run(config, sensor_type, id=sensorid, year=startdate.year%100))
                        return sensor_data
                    #make special cases for ones that do things differently
                    case Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR | Data_Sensor_Type.LUX_SENSOR:
                        sensor_data = []
                        if startdate.year < enddate.year:
                            #first year
                            for month in range(startdate.month,12+1):
                                sensor_data.extend(Parser.run(config, sensor_type, id=sensorid, year=startdate.year%100, month=month))
                            #middle years
                            if startdate.year+1 < enddate.year-1:
                                for year in range(startdate.year+1,enddate.year-1):
                                    for month in range(1,12+1):
                                        sensor_data.extend(Parser.run(config, sensor_type, id=sensorid, year=year%100, month=month)) 
                            #last year
                            for month in range(enddate.month,12+1):
                                sensor_data.extend(Parser.run(config, sensor_type, id=sensorid, year=enddate.year%100, month=month))
                        elif startdate.month < enddate.month:
                            #months
                            for month in range(startdate.month,enddate.month+1):
                                sensor_data.extend(Parser.run(config, sensor_type, id=sensorid, year=startdate.year%100, month=month))
                        else: 
                            sensor_data.extend(Parser.run(config, sensor_type, id=sensorid, year=startdate.year%100, month=startdate.month))
                        return sensor_data
                    case _:
                        raise RuntimeError("desired Data_Sensor_Type not yet implemented for this config")
            case _:
                raise RuntimeError("desired Config not yet implemented")

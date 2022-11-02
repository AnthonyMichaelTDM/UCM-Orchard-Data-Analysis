"""wrapper.py: acts as an inbetween for main.py and the more generalized library-esque data_*.py scripts"""
__author__ = "Anthony Rubick"

from datetime import datetime, timedelta
from typing import List

from data_analyzer import Analyzer
from data_parser import Parser
from data_processor import Processor
from definitions import Configs, Data_Sensor_Type
import matplotlib.pyplot as plt

class Wrapper:
    """acts as a layer between the user and the library-esque functionality of the data_... files, """
    def run(config: Configs, startdate:datetime, enddate:datetime, sap_sensorid:int | None = None, weather_sensorid:int | None = None, lux_sensorid:int | None = None):
        """'optional' args:
        sap_sensorid:int id for the sap and moisture sensor whose data is to be processed
        weather_sensorid:int id for the weather station whose data is to be processed"""
        
        match config:
            case Configs.ALMOND:
                #ensure all needed optional variables where given and call runner function
                if sap_sensorid in config.get_sensor_ids(Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR) and (
                    lux_sensorid in config.get_sensor_ids(Data_Sensor_Type.LUX_SENSOR)):
                    Wrapper.__run_normal(config=config, startdate=startdate, enddate=enddate, sap_sensorids=[sap_sensorid], lux_sensorids=[lux_sensorid]) 
                else:
                    raise RuntimeError("sensor(s) with given id(s) not found")
            case Configs.PISTACHIO:
                #ensure all needed optional variables where given and call runner function
                if sap_sensorid in config.get_sensor_ids(Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR) and (
                    weather_sensorid in config.get_sensor_ids(Data_Sensor_Type.WEATHER_STATION)) and (
                    lux_sensorid in config.get_sensor_ids(Data_Sensor_Type.LUX_SENSOR)):
                    Wrapper.__run_normal(config=config, startdate=startdate, enddate=enddate, sap_sensorids=[sap_sensorid], weather_sensorids=[weather_sensorid], lux_sensorids=[lux_sensorid]) 
                else:
                    raise RuntimeError("sensor(s) with given id(s) not found")
            case _:
                raise RuntimeError("desired config not yet implemented")
    
    def __run_normal(config:Configs, startdate:datetime, enddate:datetime, sap_sensorids:List[int] | None = None, weather_sensorids:List[int] | None = None, lux_sensorids:int|None=None):
        #DATA
        cols = 4 #columns of subplots
        rows = 2 #rows of subplots
        indexes_used_for_sap = 4
        indexes_used_for_weather = 3
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
            #parse, process, and analyze data
            analyzer = Analyzer
            try:
                analyzer = Wrapper.parse_process_analyze(config=config,sensor_type=Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR,
                                                           startdate=startdate,enddate=enddate,
                                                           fields_to_remove=['Field','Sensor ID'],
                                                           smoothening_interval=timedelta(minutes=60),sensorid=id)
            except RuntimeError as e:
                print("ERROR: {}\n\tskipping...".format(e.args[0]))
                continue
            
            #plot data
            x:datetime = analyzer.data.get("Date and Time")
            y_titles = ["Sap Flux Density", "Relative Moisture %"]
            y_lists = [analyzer.data.get(title) for title in y_titles]
            for i,y in enumerate(y_lists):
                plt.subplot(rows,cols,(1 +2*i,2 +2*i))
                if id is not None:
                    plt.plot(x,y,linewidth=0.5, label="{}".format(id))
                    plt.legend()
                else: 
                    plt.plot(x,y)
                plt.title("{}\n".format(y_titles[i]))
                plt.xticks(rotation=45)

        #WEATHER STATION(S)
        for id in weather_sensorids:
            #parse, process, and analyze data
            analyzer = Analyzer
            try:
                analyzer = Wrapper.parse_process_analyze(config=config,sensor_type=Data_Sensor_Type.WEATHER_STATION,
                                                           startdate=startdate,enddate=enddate,
                                                           fields_to_remove=['Field','Altitude [m]'],
                                                           smoothening_interval=timedelta(minutes=60),sensorid=id)
            except RuntimeError as e:
                print("ERROR: {}\n\tskipping...".format(e.args[0]))
                continue
            #plot data
            Wrapper.plot(analyzer=analyzer,sensorid=id,x_field="Date and Time",y_fields=["Temperature [℃]","Humidity [RH%]","Pressure [hPa]"],
                         subplot_index_offset=indexes_used_for_sap,subplot_rows=rows,subplot_cols=cols)

        #LUX_SENSOR(S)
        for id in lux_sensorids:
            #parse, process, and analyze data
            analyzer = Analyzer
            try:
                analyzer = Wrapper.parse_process_analyze(config=config,sensor_type=Data_Sensor_Type.LUX_SENSOR,
                                                            startdate=startdate,enddate=enddate,
                                                            smoothening_interval=timedelta(minutes=60),sensorid=id)
            except RuntimeError as e:
                print("ERROR: {}\n\tskipping...".format(e.args[0]))
                continue
            #plot data
            Wrapper.plot(analyzer=analyzer,sensorid=id,x_field="Date and Time",y_fields=["Light (KLux)"],
                         subplot_index_offset=indexes_used_for_sap+indexes_used_for_weather,subplot_rows=rows,subplot_cols=cols)
        
        #show plot
        plt.tight_layout(pad=0.3, rect=[0,0,1,1])
        plt.show()        
    
    def plot(analyzer:Analyzer, sensorid:int|None, x_field:str, y_fields:List[str], 
             subplot_rows:int, subplot_cols:int, subplot_index_offset:int=0):
        #plot data
        x:datetime = analyzer.data.get(x_field)
        y_titles = y_fields
        y_lists = [analyzer.data.get(title) for title in y_titles]
        for i,y in enumerate(y_lists):
            n=i+1
            plt.subplot(subplot_rows,subplot_cols, n + subplot_index_offset)
            if not isinstance(sensorid,type(None)):
                plt.plot(x,y,linewidth=1, label="{}".format(sensorid))
                plt.legend()
            else: 
                plt.plot(x,y)
            plt.title("{}\n".format(y_titles[i]))
            plt.xticks(rotation=45)
    
    def parse_process_analyze(config:Configs, sensor_type:Data_Sensor_Type, startdate:datetime, enddate:datetime,
                              fields_to_remove:List[str]|None=None, smoothening_interval:timedelta|None=None,sensorid:int|None=None) -> Analyzer:
        #parse data
        data = Wrapper.__get_data(config=config,sensor_type=sensor_type,startdate=startdate,enddate=enddate,sensorid=sensorid)
        #process data
        processor = Processor(data,config,sensor_type,sensor_id=sensorid)
        if fields_to_remove is not None:
            processor.remove_fields(fields_to_remove)
        processor.keep_time_range(startdate,enddate)
        if smoothening_interval is not None:
            processor.smoothen_data(startdate, smoothening_interval)
        #analyze data
        analyzer = Analyzer(processor)
        analyzer.analyze()
        
        #return analyzer
        return analyzer
 
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
    
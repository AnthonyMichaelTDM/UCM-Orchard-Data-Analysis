from datetime import datetime
import os
from typing import Dict, List
from data_analyzer import Analyzer
from data_parser import Parser
from data_processor import Processor
from definitions import ROOT_DIR, SENSOR_IDS, File_Data_Type
import matplotlib.pyplot as plt

class Wrapper:
    """acts as a layer between the user and the library-esque functionality of the data_... files, """
    
    
    def run(sensorid:int, startdate:datetime, enddate:datetime):
        if sensorid in SENSOR_IDS:
            Wrapper.__run(sensorid,startdate,enddate)
        else:
            raise RuntimeError("sensor with id {} not found".format(sensorid))
        
    def __run(sensorid:int, startdate:datetime, enddate:datetime):
        #parse data in years/months timeframe (needs to read multiple files)
        #if an error is thrown here it's probably because a file doesn't exist in ../data
        sensor_data = Wrapper.__get_almond_sensor_data(sensorid, startdate, enddate)
        #do same as above for weather 
        weather_data = Wrapper.__get_almond_weather_data(startdate, enddate)
        
        # process data
        sensor_processor = Processor(sensor_data, File_Data_Type.SAP_AND_MOISTURE_SENSOR)
        sensor_processor.remove_fields(['Field','Sensor ID'])
        weather_processor = Processor(weather_data, File_Data_Type.WEATHER_STATION)
        weather_processor.remove_fields(['Field','Altitude [m]'])
        # trim data to timeframe
        sensor_processor.keep_time_range(startdate, enddate)
        weather_processor.keep_time_range(startdate, enddate)
        
        # analyze sensor data
        sensor_analyzer = Analyzer(sensor_processor)
        sensor_analyzer.analyze()
        weather_analyzer = Analyzer(weather_processor)
        weather_analyzer.analyze()
        
        # plot data
        sensor_x = sensor_analyzer.data.get("Date and Time")
        del sensor_analyzer.data["Date and Time"]
        weather_x = weather_analyzer.data.get("Date and Time")
        del weather_analyzer.data["Date and Time"]

        sensor_titles = ["Sap Flux Density", "Relative Moisture %"]
        sensor_y_lists = [sensor_analyzer.data.get(title) for title in sensor_titles]
        weather_titles = ["Temperature [℃]","Humidity [RH%]","Pressure [hPa]","VOC [kΩ]"]
        weather_y_lists = [weather_analyzer.data.get(title) for title in weather_titles]

        #plot sensor data
        for i in range(0,len(sensor_y_lists)):
            plt.subplot(2,3,i+1)
            plt.plot(sensor_x,sensor_y_lists[i])
            plt.title("{}\n".format(sensor_titles[i]))
            plt.xticks(rotation=45)
        #plot weather data
        for i in range(0,len(weather_y_lists)):
            plt.subplot(2,3,i + len(sensor_y_lists) + 1)
            plt.plot(weather_x,weather_y_lists[i])
            plt.title("{}\n".format(weather_titles[i]))
            plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
    def __get_almond_sensor_data(sensorid:int, startdate:datetime, enddate:datetime): 
        """parse data in years/months timeframe (needs to read multiple files)
        if an error is thrown here it's probably because a file doesn't exist in ../data"""
        sensor_data = Parser.parse(os.path.join(ROOT_DIR,'data','Data_TREWid{id}_{year}_{month:0>2}_almond.csv'.format(id=sensorid,year=startdate.year%100,month=startdate.month)), File_Data_Type.SAP_AND_MOISTURE_SENSOR)
        #print('Data_TREWid{id}_{year}_{month:0>2}_almond.csv1'.format(id=sensorid,year=startdate.year%100,month=startdate.month))
        if startdate.year < enddate.year:
            #first year
            if startdate.month == 12:
                pass
            else:
                for month in range(startdate.month+1,12):
                    sensor_data.extend(Parser.parse(os.path.join(ROOT_DIR,'data','Data_TREWid{id}_{year}_{month:0>2}_almond.csv'.format(id=sensorid,year=year%100,month=month)), File_Data_Type.SAP_AND_MOISTURE_SENSOR))   
                    #print('Data_TREWid{id}_{year}_{month:0>2}_almond.csv2'.format(id=sensorid,year=year%100,month=month))
            #remaining years, -1
            if startdate.year+1 < enddate.year-1:
                for year in range(startdate.year+1,enddate.year-1):
                    for month in range(1,12):
                        sensor_data.extend(Parser.parse(os.path.join(ROOT_DIR,'data','Data_TREWid{id}_{year}_{month:0>2}_almond.csv'.format(id=sensorid,year=year%100,month=month)), File_Data_Type.SAP_AND_MOISTURE_SENSOR))  
                        #print('Data_TREWid{id}_{year}_{month:0>2}_almond.csv3'.format(id=sensorid,year=year%100,month=month))
            #last year
            for month in range(enddate.month,12):
                sensor_data.extend(Parser.parse(os.path.join(ROOT_DIR,'data','Data_TREWid{id}_{year}_{month:0>2}_almond.csv'.format(id=sensorid,year=year%100,month=month)), File_Data_Type.SAP_AND_MOISTURE_SENSOR))
                #print('Data_TREWid{id}_{year}_{month:0>2}_almond.csv4'.format(id=sensorid,year=year%100,month=month))
        elif startdate.month < enddate.month:
            #months
            for month in range(startdate.month+1,enddate.month+1):
                sensor_data.extend(Parser.parse(os.path.join(ROOT_DIR,'data','Data_TREWid{id}_{year}_{month:0>2}_almond.csv'.format(id=sensorid,year=startdate.year%100,month=month)), File_Data_Type.SAP_AND_MOISTURE_SENSOR))
                #print('Data_TREWid{id}_{year}_{month:0>2}_almond.csv5'.format(id=sensorid,year=startdate.year%100,month=month))
        return sensor_data
    
    def __get_almond_weather_data(startdate:datetime, enddate:datetime): 
        """parse data in years/months timeframe (needs to read multiple files)
        if an error is thrown here it's probably because a file doesn't exist in ../data"""
        weather_data = Parser.parse(os.path.join(ROOT_DIR,'data','Data_weather_{year}_{month:0>2}_almond.csv'.format(year=startdate.year%100,month=startdate.month)), File_Data_Type.WEATHER_STATION)
        if startdate.year < enddate.year:
            #first year
            if startdate.month == 12:
                pass
            else:
                for month in range(startdate.month+1,12):
                    weather_data.extend(Parser.parse(os.path.join(ROOT_DIR,'data','Data_weather_{year}_{month:0>2}_almond.csv'.format(year=year%100,month=month)), File_Data_Type.WEATHER_STATION))   
            #remaining years, -1
            if startdate.year+1 < enddate.year-1:
                for year in range(startdate.year+1,enddate.year-1):
                    for month in range(1,12):
                        weather_data.extend(Parser.parse(os.path.join(ROOT_DIR,'data','Data_weather_{year}_{month:0>2}_almond.csv'.format(year=year%100,month=month)), File_Data_Type.WEATHER_STATION))  
            #last year
            for month in range(enddate.month,12):
                weather_data.extend(Parser.parse(os.path.join(ROOT_DIR,'data','Data_weather_{year}_{month:0>2}_almond.csv'.format(year=year%100,month=month)), File_Data_Type.WEATHER_STATION))
        elif startdate.month < enddate.month:
            #months
            for month in range(startdate.month+1,enddate.month+1):
                weather_data.extend(Parser.parse(os.path.join(ROOT_DIR,'data','Data_weather_{year}_{month:0>2}_almond.csv'.format(year=startdate.year%100,month=month)), File_Data_Type.WEATHER_STATION))
        return weather_data 
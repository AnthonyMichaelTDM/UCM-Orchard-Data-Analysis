from datetime import datetime
import os
from data_parser import Parser, File_Data_Source
from data_processor import Processor
from definitions import ROOT_DIR

# from here, call other scripts to choose and analyze data

'''
usage:

first call the Parser to parse the data, specify data source

then call methods in data_analyzer to process the data
- first process data with Processor (define what data is important, and what time frame is important)

then do stuff with the data, ie. plot it on a graph 
'''

#show off milestone 1
file_path = os.path.join(ROOT_DIR, 'data', 'Almond_data_20220610', 'Data_TREWid1_22_04_almond.csv')
file_source = File_Data_Source.SAP_AND_MOISTURE_SENSOR
data = Parser.parse( file_path, file_source)
processor = Processor(data, file_source)
processor.remove_fields(['Field', 'Sensor ID'])
processor.keep_time_range(datetime(year=2022, month=4, day=30, hour=12),datetime(year=2022, month=4, day=30, hour=13))

print(str(processor))


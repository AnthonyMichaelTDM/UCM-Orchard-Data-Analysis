import csv
import os

from numpy import average


ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..'))

idnum = 1
file_path = os.path.join(ROOT_DIR, 'data', 'Calibration_TREWid{}_almond.csv'.format(idnum))

while os.path.isfile(file_path):
    data=[]
    #parse file
    with open(file_path, mode='r', newline='') as csvfile:
            # open csv file
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
            reader = csv.reader(csvfile,dialect=dialect)
            
            # return data
            reader = [x for x in reader] #convert reader to a list
            data = [ [int(data) for data in row] for row in reader[1:]] #convert data to int, also skip first row

    #calculate coefficients
    ave_wet = average( [row[0] for row in data] )
    ave_dry = average( [row[1] for row in data] )
    
    a = (100-0)/(ave_wet-ave_dry) #  (y2-y1) / (x2-x1)
    b = 100-(a*ave_wet) # y=ax+b ->  b=y-ax
    
    print("Sensor {id}:\n\ta = {a}\n\tb = {b}\n\tave wet (max) = {wet}\n\tave dry (min) = {dry}".format(id=idnum,a=a,b=b,wet=ave_wet,dry=ave_dry))
    
    #prep for next loop
    idnum += 1
    file_path = os.path.join(ROOT_DIR, 'data', 'Calibration_TREWid{}_almond.csv'.format(idnum))
import csv
import os

from numpy import array, average


ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..'))

idnum = 1
file_path = os.path.join(ROOT_DIR, 'data', 'Almond_data_20220610', 'Calibration_TREWid{}_almond.csv'.format(idnum))

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
    ave_wet = average( array(data[0]) )
    ave_dry = average( array(data[1]) )
    
    a = 100/(ave_wet-ave_dry) #  (y2-y1) / (x2-x1)
    b = -a * ave_dry # y=0=ax+b ->  b=-ax
    
    print("Sensor {id}:\n\ta = {a}\n\tb = {b}\n".format(id=idnum,a=a,b=b))
    
    #prep for next loop
    idnum += 1
    file_path = os.path.join(ROOT_DIR, 'data', 'Almond_data_20220610', 'Calibration_TREWid{}_almond.csv'.format(idnum))
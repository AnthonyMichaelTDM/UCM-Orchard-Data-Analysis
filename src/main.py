from datetime import datetime
from definitions import Configs, Data_Sensor_Type

from wrapper import Wrapper


##uncomment if you want to hardcode the time range rather than entering it in manually
#Wrapper.run(Configs.PISTACHIO, datetime(2022,7,28,0,0), datetime(2022,8,1,23,59), sap_sensorid=1, weather_sensorid=2, lux_sensorid=1)
#exit()

#TODO: add let user choose between almond and pistaccio data, then if pistaccio have them choose the weather station id (basically build Config with user input)
def get_int(prompt:str, min:int, max:int) -> int:
    while True:
        value = input(prompt)
        try:
            value = int(value)
            if value >= min and value <= max: 
                return value
            else:
                print("invalid input, try again")
        except:
            print("invalid input, try again")
def get_int_nomax(prompt:str, min:int) -> int:
    while True:
        value = input(prompt)
        try:
            value = int(value)
            if value >= min: 
                return value
            else:
                print("invalid input, try again")
        except:
            print("invalid input, try again")
def get_char(prompt) -> str:
    while True:
        value = input(prompt)
        if len(value) >= 1:
            return value[0]
        else:
            print("invalid input, try again")



#ask user to specify the time frame to look at
print("specify a time range to look at:")
startyear: int = get_int_nomax("\tstart year (2022-?): ", 2022)
startmonth:int = get_int("\tstart month (1-12): ", 1, 12)
startday:  int = get_int("\tstart day (1-31): ", 1, 31)
print("")
endyear: int = get_int_nomax("\tend year (2022-?): ", 2022)
endmonth:int = get_int("\tend month (1-12): ", 1, 12)
endday:  int = get_int("\tend day (1-31): ", 1, 31)

startdate:datetime = datetime(year=startyear, month=startmonth, day=startday,hour=0,minute=0)
enddate:datetime   = datetime(year=endyear, month=endmonth, day=endday,hour=23,minute=59)

#choose between sources (almond or pistachio)
config:Configs = None
print("")
while isinstance(config, type(None)):
    match get_char("do you want to analyze almond data or pistachio data? (enter 'a' for almond or 'p' for pistachio): "):
        case 'a':
            config = Configs.ALMOND
            break
        case 'p':
            config = Configs.PISTACHIO
            break
        case _:
            print("invalid input, try again")
            continue

#depending on config, ask the remaining questions needed to properly call the wrapper module, and then call it
match config:
    case Configs.ALMOND:
        minid = min(config.get_sensor_ids(Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR))
        maxid = max(config.get_sensor_ids(Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR))
        sap_sensorid:int = get_int("which sap and moisture sensor's data do you want to look at ({}-{}): ".format(minid,maxid),minid,maxid)
        
        Wrapper.run(config, startdate, enddate, sap_sensorid=sap_sensorid)
    case Configs.PISTACHIO:
        minid = min(config.get_sensor_ids(Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR))
        maxid = max(config.get_sensor_ids(Data_Sensor_Type.SAP_AND_MOISTURE_SENSOR))
        sap_sensorid:int = get_int("which sap and moisture sensor's data do you want to look at ({}-{}): ".format(minid,maxid),minid,maxid)
        
        minid = min(config.get_sensor_ids(Data_Sensor_Type.WEATHER_STATION))
        maxid = max(config.get_sensor_ids(Data_Sensor_Type.WEATHER_STATION))
        weather_sensorid:int = get_int("which weather station's data do you want to look at ({}-{}): ".format(minid,maxid),minid,maxid)
        
        minid = min(config.get_sensor_ids(Data_Sensor_Type.LUX_SENSOR))
        maxid = max(config.get_sensor_ids(Data_Sensor_Type.LUX_SENSOR))
        lux_sensorid:int = get_int("which lux sensor's data do you want to look at ({}-{}): ".format(minid,maxid),minid,maxid)
        
        Wrapper.run(config, startdate, enddate, sap_sensorid=sap_sensorid, weather_sensorid=weather_sensorid, lux_sensor_id=lux_sensorid)
    case _:
        raise RuntimeError("desired config not yet implemented")

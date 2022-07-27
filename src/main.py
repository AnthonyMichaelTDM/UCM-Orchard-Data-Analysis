from datetime import datetime

from wrapper import Wrapper


##uncomment if you want to hardcode the time range rather than entering it in manually
Wrapper.run(1, datetime(2022,6,1,0,0), datetime(2022,6,4,23,59))
exit()
#TODO: add let user choose between almond and pistaccio data, then if pistaccio have them choose the weather station id
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

#read user input to determine what data to use
sensorid:int = get_int("which sensors data do you want to look at (1-6): ",1,6)

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

Wrapper.run(sensorid, startdate, enddate)

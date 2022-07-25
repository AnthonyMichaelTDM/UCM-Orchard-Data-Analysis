from datetime import datetime

from wrapper import Wrapper


##uncomment if you want to hardcode the time range rather than entering it in manually
Wrapper.run(0, datetime(2022,4,27,0,0), datetime(2022,4,28,0,0))
exit()

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
starthour: int = get_int("\tstart hour (0-23): ", 0, 23)
startmin:  int = get_int("\tstart minute (0-59): ", 0, 59)
print("")
endyear: int = get_int_nomax("\tend year (2022-?): ", 2022)
endmonth:int = get_int("\tend month (1-12): ", 1, 12)
endday:  int = get_int("\tend day (1-31): ", 1, 31)
endhour: int = get_int("\tend hour (0-23): ", 0, 23)
endmin:  int = get_int("\tend minute (0-59): ", 0, 59)

startdate:datetime = datetime(year=startyear, month=startmonth, day=startday,hour=starthour,minute=startmin)
enddate:datetime   = datetime(year=endyear, month=endmonth, day=endday,hour=endhour,minute=endmin)

Wrapper.run(sensorid, startdate, enddate)

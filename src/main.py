
"""main.py: takes user input and sets up configs to call wrapper.py"""
__author__ = "Anthony Rubick"

import sys

## NOTE for future maintainers:
## the primary potential optomization is to utilize data-frames instead of dictionaries as they can access elements faster
## beyond that, trimming data sooner and algorithm optomizations where possible may help too.


##uncomment if you want to hardcode the time range rather than entering it in manually
#Wrapper.run(Configs.PISTACHIO, datetime(2022,7,28,0,0), datetime(2022,8,1,23,59), sap_sensorid=1, weather_sensorid=2, lux_sensorid=1)
#exit()


# call something to actually run the analysis


def main(argv: list[str] = sys.argv[1:]):
    # TODO: try to get all the user defined configuration from the cli, if that fails then call to a module to get the configuration from user input
    
    # see if proper command line args where given, if not get them from user input
    # use these args to set up other things    
    ...
    # using user arguments, deterimine which ConfigList in Configurations to use
    ...
    # for every ConfigDetails in chosen ConfigList:
    #   call reader with chosen config to read rows of data
    #   process rows into a SampleList with 
    ...
    
    # TODO: add SOLID implementations of functionality in wrapper

if __name__ == "__main__":
    main()
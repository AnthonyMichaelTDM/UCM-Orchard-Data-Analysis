
"""main.py: takes user input and sets up configs to call wrapper.py"""
__author__ = "Anthony Rubick"

from config import UserSettings

## NOTE for future maintainers:
## the primary potential optomization is to utilize data-frames instead of dictionaries as they can access elements faster
## beyond that, trimming data sooner and algorithm optomizations where possible may help too.


##uncomment if you want to hardcode the time range rather than entering it in manually
#Wrapper.run(Configs.PISTACHIO, datetime(2022,7,28,0,0), datetime(2022,8,1,23,59), sap_sensorid=1, weather_sensorid=2, lux_sensorid=1)
#exit()


# call something to actually run the analysis


def main():
    # TODO: try to get all the user defined configuration from the cli, if that fails then call to a module to get the configuration from user input
    
    settings:UserSettings = UserSettings();
    
    
    # TODO: add SOLID implementations of functionality in wrapper

if __name__ == "__main__":
    main()
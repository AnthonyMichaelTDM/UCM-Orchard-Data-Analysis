

from datetime import datetime

import almond, pistachio
import cli_io_ops
from sensors import SensorList


class Settings:
    """Interacts with user to define desired behavior
    """
    def __init__(self) -> None:
        """initialize the settings class
        """
        #start and end dates.
        print("specify a time range to look at:")
        startdate:datetime = datetime(
            year=cli_io_ops.get_int_nomax("\tstart year (2022-?): ", 2022),
            month=cli_io_ops.get_int("\tstart month (1-12): ", 1, 12),
            day=cli_io_ops.get_int("\tstart day (1-31): ", 1, 31),
            hour=0,
            minute=0
        )
        print("")
        enddate:datetime = datetime(\
            year=cli_io_ops.get_int_nomax("\tend year (2022-?): ", 2022),
            month=cli_io_ops.get_int("\tend month (1-12): ", 1, 12),
            day=cli_io_ops.get_int("\tend day (1-31): ", 1, 31),
            hour=23,
            minute=59
        )
        self.sensorlist: SensorList = SensorList()
        #choose source
        print("")
        while True:
            match cli_io_ops.get_char("do you want to analyze almond data or pistachio data? (enter 'a' for almond or 'p' for pistachio): "):
                case 'a':
                    # add the Sensor subclasses in almond.py to sensorlist
                    self.sensorlist.append(almond.SapAndMoistureSensor(
                        startdate,
                        enddate, 
                            cli_io_ops.get_int(
                                "which sap and moisture sensor's data do you want to look at ({}-{}): ".format(almond.SapAndMoistureSensor.minID,almond.SapAndMoistureSensor.maxID),
                                almond.SapAndMoistureSensor.minID,
                                almond.SapAndMoistureSensor.maxID
                            )
                        ))
                    
                    self.sensorlist.append(almond.WeatherSensor(startdate,enddate))
                    
                    self.sensorlist.append(almond.LuxSensor(
                        startdate,
                        enddate, 
                            cli_io_ops.get_int(
                                "which lux sensor's data do you want to look at ({}-{}): ".format(almond.LuxSensor.minID,almond.LuxSensor.maxID),
                                almond.LuxSensor.minID,
                                almond.LuxSensor.maxID
                            )
                        ))
                    break
                case 'p':
                    # add the Sensor subclasses in pistacio.py to sensorlist
                    self.sensorlist.append(pistachio.SapAndMoistureSensor(
                        startdate,
                        enddate, 
                        cli_io_ops.get_int(
                            "which sap and moisture sensor's data do you want to look at ({}-{}): ".format(pistachio.SapAndMoistureSensor.minID,pistachio.SapAndMoistureSensor.maxID),
                            pistachio.SapAndMoistureSensor.minID,
                            pistachio.SapAndMoistureSensor.maxID
                        )
                    ))
                    
                    self.sensorlist.append(pistachio.WeatherSensor(
                        startdate,
                        enddate,
                        cli_io_ops.get_int(
                            "which weather station's data do you want to look at ({}-{}): ".format(pistachio.WeatherSensor.minID,pistachio.WeatherSensor.maxID),
                            pistachio.WeatherSensor.minID,
                            pistachio.WeatherSensor.maxID
                        )
                    ))
                    
                    self.sensorlist.append(pistachio.LuxSensor(
                        startdate,
                        enddate, 
                        cli_io_ops.get_int(
                            "which lux sensor's data do you want to look at ({}-{}): ".format(pistachio.LuxSensor.minID,pistachio.LuxSensor.maxID),
                            pistachio.LuxSensor.minID,
                            pistachio.LuxSensor.maxID
                        )
                    ))
                    break
                case _:
                    print("invalid input, try again")
                    continue
            
        
        
        

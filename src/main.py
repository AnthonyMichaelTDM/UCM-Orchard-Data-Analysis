"""main.py: takes user input and sets up configs to call wrapper.py"""
__author__ = "Anthony Rubick"

import argparse

from matplotlib import pyplot as plt
from matplotlib.widgets import CheckButtons
from plotter import PlotterBuilder
from utils import get_filenames_for_timerange, process_reader_into_samplelist
from configurations import ConfigDetails, Configurations
from datetime import date, datetime
import sys

from reader import Reader, ReaderBuilder
from sample import SampleBuilder, SampleList


def get_int(prompt:str, min:int, max:int) -> int:
    while True:
        value:int = int(input(prompt))
        if value >= min and value <= max: 
            return value
        else:
            print("invalid input, try again")
def get_int_nomax(prompt:str, min:int) -> int:
    while True:
        value:int = int(input(prompt))
        if value >= min: 
            return value
        else:
            print("invalid input, try again")

def get_char(prompt) -> str:
    while True:
        value = input(prompt)
        if len(value) >= 1:
            return value[0]
        else:
            print("invalid input, try again")
            
def get_options(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        '-s',
        #'--start-date',
        type=date.fromisoformat,
        required=True,
        help="start of time range to analyze, given in any valid ISO 8601 format, except ordinal dates",
        dest="startdate",
    )
    parser.add_argument(
        '-e',
        '--end-date',
        required=False,
        type=date.fromisoformat,
        default=date.today(),
        help="end of time range to analyze, given in any valid ISO 8601 format, except ordinal dates (ex: 2022-07-20)",
        dest="enddate",
    )
    parser.add_argument(
        '-c',
        '--configuration',
        type=str,
        choices=list(Configurations.CONFS.keys()),
        required=True,
        metavar="CONFIG",
        dest="configuration_key",
        help="analysis preset to run, CHOICES: {}".format(list(Configurations.CONFS.keys())),
        default="almond"
    )
    
    
    parser.add_argument(
        "--sap-id",
        type=int,
        default=1,
        help="id of the sap and moisture sensor to look at, if needed",
        dest="sap_id"
    )
    parser.add_argument(
        "--weather-id",
        type=int,
        default=1,
        help="id of the weather sensor to look at, if needed",
        dest="weather_id",
    )
    parser.add_argument(
        "--lux-id",
        type=int,
        default=1,
        help="id of the lux sensor to look at, if needed",
        dest="lux_id",
    )
    
    if len(argv) == 0 or '-h' in argv or '--help' in argv:
        parser.print_help()
        sys.exit(1)
    
    options = parser.parse_args(argv)
    return options


## NOTE for future maintainers:
## the primary potential optomization is to utilize data-frames instead of dictionaries as they can access elements faster
## beyond that, trimming data sooner and algorithm optomizations where possible may help too.

def run(config: ConfigDetails, options: argparse.Namespace, id: int|None):
    startdate = datetime.combine(getattr(options, "startdate"), datetime.min.time())
    enddate = datetime.combine(getattr(options, "enddate"), datetime.min.time())
    
    reader: Reader = ReaderBuilder.build(
        config=config.READER_CONF,
        options=options
    )
    for filename in get_filenames_for_timerange(
        startdate,
        enddate,
        id,
        config.SENSOR_CONF.filename_generator
    ):
        reader.read(filename, config.READER_CONF.data_fields)
    
    samples:SampleList = process_reader_into_samplelist(reader, config.SAMPLE_CONF, SampleBuilder)
    samples.sort()
    samples.trim_to_timerange(startdate,enddate)
    
    if config.SENSOR_CONF.smoothening_interval:
        samples = samples.get_smoothened_data(startdate, config.SENSOR_CONF.smoothening_interval)
        
    # make plot
    for plot_conf in config.PLOTTER_CONF:
        plotter = PlotterBuilder.build(
            plot_conf,
            samples,
            id
        )
        plotter.plot()


def main(argv: list[str] = sys.argv[1:]):
    # TODO: try to get all the user defined configuration from the cli, if that fails then call to a module to get the configuration from user input
    
    # using cli options, set up a Settings object
    # for testing:
    options = get_options(argv=["-s","2022-05-09","-e","2022-05-28","-c","almond"])
    #options = get_options(argv)
    
    sensors = ["sap","weather","lux"]
    ids = [getattr(options, "sap_id"),getattr(options, "weather_id"),getattr(options, "lux_id") ]
    
    config_key:str = getattr(options, "configuration_key")
    plt.rcParams['font.size'] = 8
    if Configurations.CONFS.get(config_key) != None:
        for i,config in enumerate(Configurations.CONFS[config_key]):
            if config.SENSOR_CONF.valid_ids:
                if ids[i] in config.SENSOR_CONF.valid_ids:
                    run(config, options,ids[i])
                else:
                    raise RuntimeError("you must pass a valid value for --{}-id when the {} configuration is chosen".format(sensors[i],config_key))
            else:
                #no ids (one sensor)
                run(config, options,None)
            plt.show()
    
    else:
        raise RuntimeError("invalid config")

if __name__ == "__main__":
    main()
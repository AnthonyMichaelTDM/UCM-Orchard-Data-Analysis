"""main.py: takes user input and sets up configs to call wrapper.py"""
__author__ = "Anthony Rubick"

import argparse
from commands import get_filenames_for_timerange, process_reader_into_samplelist
from configurations import ConfigDetails, Configurations
from datetime import date
import sys

import factories
from reader import Reader
from sample import SampleList

from settings import Settings


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
    # TODO: implement cli args here
    parser.add_argument(
        '-s',
        '--start-date',
        dest="startdate",
        required=True,
        help="start of time range to analyze, given in any valid ISO 8601 format, except ordinal dates",
        type=date.fromisoformat,
    )
    parser.add_argument(
        '-e',
        '--end-date',
        dest="enddate",
        required=False,
        default=date.today(),
        help="end of time range to analyze, given in any valid ISO 8601 format, except ordinal dates",
        type=date.fromisoformat,
    )
    parser.add_argument(
        '-c',
        '--configuration',
        metavar="CONFIG",
        choices=Configurations.CONFS.keys(),
        required=True,
        dest="configuration_key",
        help="analysis preset to run",
    )
    options = parser.parse_args(argv)
    return options


## NOTE for future maintainers:
## the primary potential optomization is to utilize data-frames instead of dictionaries as they can access elements faster
## beyond that, trimming data sooner and algorithm optomizations where possible may help too.


def run(config: ConfigDetails, options: argparse.Namespace, id: int|None):
    reader: Reader = factories.ReaderFactory(config.READER_CONF,options)
    for filename in get_filenames_for_timerange(
        options.startdate,
        options.enddate,
        id,
        config.SENSOR_CONF.filename_generator
    ):
        reader.read(filename)
    
    samples:SampleList = process_reader_into_samplelist(reader, config.SAMPLE_CONF, factories.SampleFactory)
    
    samples.trim_to_timerange(options.startdate,options.enddate)
    
    if config.SENSOR_CONF.smoothening_interval:
        samples = samples.get_smoothened_data(options.startdate, config.SENSOR_CONF.smoothening_interval)
        
    # run analysis
    
    # make plot
    


def main(argv: list[str] = sys.argv[1:]):
    # TODO: try to get all the user defined configuration from the cli, if that fails then call to a module to get the configuration from user input
    
    # using cli options, set up a Settings object
    options = get_options(argv)
    
    for config in Configurations.CONFS[options.configuration_key]:
        if config.SENSOR_CONF.valid_ids:
            # run for every id
            for id in config.SENSOR_CONF.valid_ids:
                run(config, options,id)
        else:
            #no ids (one sensor)
            run(config, options,None)
    
    # for every ConfigDetails in chosen ConfigList:
    #   call reader with chosen config to read rows of data from all the files needed to fill given time range
    #   process rows into a SampleList
    #   
    
    # TODO: add SOLID implementations of functionality in wrapper

if __name__ == "__main__":
    main()
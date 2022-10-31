import argparse
from datetime import datetime
from typing import Any, Callable
from configurations import ReaderDetails, SampleDetails
from sample import Sample
from reader import Reader


SampleFactoryContract = Callable[[dict[str, Any], SampleDetails], Sample]

def SampleFactory(row: dict[str,Any], config: SampleDetails) -> Sample:
    """returns an instance of Sample, with data parsed from row

    Args:
        row (dict[str,Any]): dictionary with field names as keys, and field data as values
        timestamp_fieldname (str): name of the field that contains the timestamp
        timestamp_format (str): format of the timestamp
        important_fields (list[str]): fields within row that we want saved to the `Sample`
        field_types (list[Any]): the types of said fields

    Raises:
        KeyError: if one or more of the fields listed in `important_fields` are missing from `row`
        keyError: if given 'timestamp_fieldname' for isn't found in 'row'
        IndexError: if the length of `important_fields` and that of `field_types` are not equal 
        ValueError: if type casting of field into it's associated type (in `field_types`) failed
        ValueError: if timestamp format given doesn't match that of the timestamp in the row

    Returns:
        Sample: a Sample constructed from row
        
    DocTests:
    >>> from factories import SampleFactory
    >>> from configurations import SampleDetails
    >>> row = {"time":"2022-04-30 23:46:18", "wanted 1":"13.5", "unwanted/bad":"abcdef"}
    >>> details1 = SampleDetails(
    ...     important_fields = ["wanted 1"]
    ...     field_types = field_types = [float]
    ...     timestamp_fieldname = "time"
    ...     timestamp_format = "%Y-%m-%d %H:%M:%S"
    ... )
    >>> SampleFactory(row,details1)
    Sample(timestamp=datetime.datetime(2022, 4, 30, 23, 46, 18), important_fields=["wanted 1"], datapoints={"wanted 1":13.5})
    >>> details2 = SampleDetails(
    ...     important_fields = ["wanted 1"]
    ...     field_types = field_types = [float]
    ...     timestamp_fieldname = "timestamp"
    ...     timestamp_format = "%Y-%m-%d %H:%M:%S"
    ... )
    >>> SampleFactory(row,details2) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    KeyError: given timestamp_fieldname 'timestamp' not found in row
    >>> details3 = SampleDetails(
    ...     important_fields = ["wanted 1","wanted 2"]
    ...     field_types = field_types = [float,int]
    ...     timestamp_fieldname = "time"
    ...     timestamp_format = "%Y-%m-%d %H:%M:%S"
    ... )
    >>> SampleFactory(row,details3) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    KeyError: important field(s) '['wanted 2']' is/are missing
    >>> details4 = SampleDetails(
    ...     important_fields = ["wanted 1","unwanted/bad"]
    ...     field_types = field_types = [float]
    ...     timestamp_fieldname = "time"
    ...     timestamp_format = "%Y-%m-%d %H:%M:%S"
    ... )
    >>> SampleFactory(row,details4) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    IndexError: must have a type for every important field
    >>> details5 = SampleDetails(
    ...     important_fields = ["unwanted/bad"]
    ...     field_types = field_types = [int]
    ...     timestamp_fieldname = "time"
    ...     timestamp_format = "%Y-%m-%d %H:%M:%S"
    ... )
    >>> SampleFactory(row,details5) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ValueError: invalid literal for int() with base 10: 'abcdef'
    >>> details6 = SampleDetails(
    ...     important_fields = ["wanted 1"]
    ...     field_types = field_types = [float]
    ...     timestamp_fieldname = "time"
    ...     timestamp_format = "%H:%M:%S %Y-%m-%d"
    ... )
    >>> SampleFactory(row,details6) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ValueError: time data '2022-04-30 23:46:18' does not match format '%H:%M:%S %Y-%m-%d'
    >>> 
    """
    if not config.timestamp_fieldname in row:
        raise KeyError("given timestamp_fieldname '{}' not found in row".format(config.timestamp_fieldname))
    
    timestamp=datetime.strptime(str(row.get(config.timestamp_fieldname)), config.timestamp_format)
    
    if len([x for x in config.important_fields if (not x in row)]) > 0:
        raise KeyError("important field(s) `{}` is/are missing".format([x for x in config.important_fields if (not x in row)]))
    
    if len(config.important_fields) != len(config.field_types):
        raise IndexError("must have a type for every important field")
    
    return Sample(
        timestamp=timestamp,
        important_fields=config.important_fields,
        datapoints={
            field:field_type(row[field])
            for field,field_type in zip(config.important_fields,config.field_types)
        }
    )
    

# TODO: add unit tests 
def ReaderFactory(config: ReaderDetails, options: argparse.Namespace) -> Reader:
    row_generator = config.row_generator
    data_source = config.data_source
    
    # settings hardcoded in configurations
    other_confs = config.additional # hard coded opitions
    # settings with names hardcoded, but values given by user
    # aka: settings that aren't the same all the time, but also aren't needed by every reader
    other_options = { # user define opitions
        name: getattr(options, name, None)
        for name in config.args
    }
    return Reader(row_generator, data_source.base_path, other_confs, **other_options)

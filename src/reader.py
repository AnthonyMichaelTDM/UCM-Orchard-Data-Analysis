import abc
import argparse
import csv
import os
from typing import Any, Iterator, NamedTuple, Protocol, Type

import requests

import data

class RowGenerator(Protocol):
    def __init__(self, source: str, **kwargs: Any) -> None:
        """ititializes the row generator, process Source into a collection of rows, the type of the rows is dict[str,Any]

        Args:
            source (str): the path/url/location where the data is located
            **kwargs (any): additional arguments
        """
        ...

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """
        generates and returns an iterator over the rows of data in a source
        Yields:
            Iterator[dict[str, Any]]: iterator over the rows of data
        """
        ...
        
class WebRow(abc.ABC):
    """follows RowGenerator protocol"""
    @staticmethod
    @abc.abstractmethod
    def process_response(response: bytes, **kwargs) -> list[dict[str, Any]]:
        """process the response from the webserver into a list of rows, represented by dictionaries

        Args:
            response (bytes): response from webserver

        Raises:
            ValueError: provided data_fields don't match the number of fields in the response

        Returns:
            list[dict[str,Any]]: the processed response
        """
        ...
        
    def __init__(self, source: str, **kwargs: Any) -> None:
        """ititializes this RowGenerator
        
        use the requests module to pull data from the provided url, 
        then call the process_response method to process that response into a list of rows

        Args:
            url (str): url where the data is host
            **kwargs (Any) : additional arguments, named
            
        because this requires access to the internet to test, it's hard to write unit tests for this constructor
        """
        # get data from webserver w/ requests library, raise error is this couldn't be done
        try:
            response = requests.get(source).content
        except:
            raise ConnectionError("failed to connect to {}".format(source))
        
        self.rows: list[dict[str,Any]] = self.process_response(response,**kwargs)
        
    def __iter__(self) -> Iterator[dict[str, Any]]:
        """
        generates and returns an iterator over the rows of data in a web response
        Yields:
            Iterator[dict[str, Any]]: iterator over the rows of data
        """
        return iter(self.rows)
        ...
        
    
class WebRowRehsani(WebRow):
    """ implementation of RowGenerator protocol for web-hosted data """
    @staticmethod
    def get_arg_from_kwargs(kwargs: dict[str,Any], key:str, desired_class: Any):
        """pull arguments from the passed **kwargs and throw errors if those arguments are missing or not of the right type

        Args:
            kwargs (dict[str,Any]): the kwargs to parse
            key (str): the key to the desired argument
            desired_class (Class[Any]): the type of the desired argument

        Raises:
            TypeError: argument exists, but is of the wrong type (can't be cast to desired_type)
            ValueError: argument doesn't exist
        Returns:
            _type_: the argument
            
        >>> kwargs = {"ex_arg":[1,2,3,4]}
        >>> key = "ex_arg"
        >>> desired_type = list
        >>> arg = WebRowRehsani.get_arg_from_kwargs(kwargs,key,desired_type)
        >>> arg
        [1, 2, 3, 4]
        >>> bad_key = WebRowRehsani.get_arg_from_kwargs(kwargs,"bad_key",desired_type) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: kwargs doesn't contain key 'bad_key'
        >>> bad_type = WebRowRehsani.get_arg_from_kwargs(kwargs,key,str) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        TypeError: argument 'ex_arg' found, but isn't an instance of '<class 'str'>'
        """
        if key in kwargs: 
            arg:Any = kwargs.get(key) 
            if isinstance(arg, desired_class):
                return desired_class(kwargs.get(key))
            else:
                raise TypeError("argument '{}' found, but isn't an instance of '{}'".format(key,type(desired_class)))
        else:
            raise ValueError("kwargs doesn't contain key '{}'".format(key))
    
    @staticmethod
    def process_response(response: bytes, **kwargs) -> list[dict[str,Any]]:
        """process the response from the webserver into a list of rows, represented by dictionaries

        Args:
            response (bytes): response from webserver
            sample_separator (str): the character that separates different samples
            data_separator (str): the character that separates different datapoints within a sample
            data_fields (list[str]): list of the names of every datapoint within a sample, must include all fields not just the ones you're interested in analyzing (that's done by subclasses of the Sample class)
        Raises:
            ValueError: provided data_fields don't match the number of fields in the response

        Returns:
            list[dict[str,Any]]: the processed response
            
            doctests
        >>> from reader import WebRowRehsani
        >>> response = "10,1.0,wowza;20,2.0,zoinks;".encode() #TODO: add call to bytes function to convert string to bytes 
        >>> fields = ["an int", "a float", "a str"]
        >>> proc_resp = WebRowRehsani.process_response(response, sample_separator=";", data_separator=",", data_fields=fields)
        >>> proc_resp
        [{'an int': 'an int', 'a float': 'a float', 'a str': 'a str'}, {'an int': '20', 'a float': '2.0', 'a str': 'zoinks'}, {'an int': '10', 'a float': '1.0', 'a str': 'wowza'}]
        >>> bad_fields_resp = WebRowRehsani.process_response(response, sample_separator=";", data_separator=",", data_fields=["an int", "a float"]) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: provided data_fields doesn't match number of data_entries in response, 2!=3
        """
        sample_separator:str = WebRowRehsani.get_arg_from_kwargs(kwargs,"sample_separator",str)
        data_separator:str = WebRowRehsani.get_arg_from_kwargs(kwargs, "data_separator", str)
        data_fields:list[str] = WebRowRehsani.get_arg_from_kwargs(kwargs, "data_fields", list)
        #decode and re-order response
        split_response: list[str] = response.decode('utf-8').split(sep=sample_separator)
        split_rows: list[list[str]]  = [
            row.split(sep=data_separator)
            for row in split_response[:-1] # reversed so we can add a row to the start with field headers (but after checking length)
        ]
        
        #ensure that len(data_fields) is the same as the number of values in each sample
        if len(data_fields) != len(split_rows[0]):
            raise ValueError("provided data_fields doesn't match number of data_entries in response, {}!={}".format(len(data_fields),len(split_rows[0])))
        
        # add a row for field headers, then reverse the list
        split_rows.extend([data_fields])
        split_rows.reverse()
        
        # use field headers to convert rows list of lists into a list of dicts
        return [
            dict(zip(
                data_fields,
                row
            ))
            for row in split_rows
        ]
        
    def __init__(self, source: str, **kwargs: Any) -> None:
        super().__init__(source, **kwargs)
    
    def __iter__(self) -> Iterator[dict[str, Any]]:
        return super().__iter__()
    

class Reader(abc.ABC):
    def __init__(
        self,
        row_generator: Type[RowGenerator],
        sample_builder: Type[data.SampleBuilder],
        sample_collection: Type[data.SampleList],
        data_source: Type[data.DataSource],
        **kwargs: Any,
    ) -> None:
        self.row_generator = row_generator
        self.sample_builder = sample_builder
        self.sample_collection_class = sample_collection
        self.data_source = data_source
        self.additional_kwargs = kwargs
        self.samples = sample_collection()

    def read(self, filename: str) -> None:
        row_gen_class = self.row_generator
        sample_bldr_class = self.sample_builder
        row_iter = row_gen_class(os.path.join(self.data_source.base_path(),filename), **self.additional_kwargs)
        self.samples = self.sample_collection_class(
            sample_bldr_class.Build(row) for row in row_iter
        )

class ReaderDetails(NamedTuple):
    row_generator: Type[RowGenerator]
    sample_builder: Type[data.SampleBuilder]
    sample_collection: Type[data.SampleList]
    data_source: Type[data.DataSource]
    additional: dict[str,Any]
    args: list[str] # for future CLI functionality

class Configuration:
    READER_CONFS: dict[str,ReaderDetails] = {
        "almond SapAndMoisture csv" : ReaderDetails(
            row_generator=csv.DictReader,  # type: ignore
            sample_builder=data.SapAndMoistureSampleBuilder,
            sample_collection=data.SampleList,
            data_source=data.CsvDataSource,
            additional={},
            args = []
        ),
        "almond Weather csv" : ReaderDetails(
            row_generator=csv.DictReader,  # type: ignore
            sample_builder=data.WeatherSampleBuilder,
            sample_collection=data.SampleList,
            data_source=data.CsvDataSource,
            additional={},
            args = []
        ),
        "almond Lux csv" : ReaderDetails(
            row_generator=csv.DictReader,  # type: ignore
            sample_builder=data.LuxSampleBuilder,
            sample_collection=data.SampleList,
            data_source=data.CsvDataSource,
            additional={},
            args = []
        ),
        
        "pistachio SapAndMoisture web" : ReaderDetails(
            row_generator=WebRowRehsani,
            sample_builder=data.SapAndMoistureSampleBuilder,
            sample_collection=data.SampleList,
            data_source=data.WebDataSource_rehsani_local,
            additional={
                "sample_separator":";",
                "data_separator":",",
                "data_fields":["Date and Time","Value 1","Value 2"],
            },
            args = []
        ),
        "pistachio Weather web" : ReaderDetails(
            row_generator=WebRowRehsani,
            sample_builder=data.WeatherSampleBuilder,
            sample_collection=data.SampleList,
            data_source=data.WebDataSource_rehsani_local,
            additional={
                "sample_separator":";",
                "data_separator":",",
                "data_fields":["Date and Time","Temperature [℃]","Humidity [RH%]","Pressure [hPa]","Altitude [m]","VOC [kΩ]"],
            },
            args = []
        ),
        "pistachio Lux web" : ReaderDetails(
            row_generator=WebRowRehsani,
            sample_builder=data.LuxSampleBuilder,
            sample_collection=data.SampleList,
            data_source=data.WebDataSource_rehsani_local,
            additional={
                "sample_separator":";",
                "data_separator":",",
                "data_fields":["Date and Time", "Light (KLux)"],
            },
            args = []
        ),
    }
    #TODO: add class member to represent the analysis / parsing abstract base class, when that gets reimplemented
    
    
# TODO: add unit tests for stuff in the reader module
def build_reader(config: Type[Configuration], options: argparse.Namespace) -> Reader:
    row_generator = config.READER_CONFS[options.format].row_generator
    data_builder = config.READER_CONFS[options.format].sample_builder
    data_list = config.READER_CONFS[options.format].sample_collection
    data_source = config.READER_CONFS[options.format].data_source
    
    additional = config.READER_CONFS[options.format].additional # hard coded opitions
    additional.update({ # user define opitions
        name: getattr(options, name, None)
        for name in config.READER_CONFS[options.format].additional
    })
    
    return Reader(row_generator, data_builder, data_list, data_source,**additional)


# Unit doctests

__test__ = {name: value for name, value in locals().items() if name.startswith("test")}
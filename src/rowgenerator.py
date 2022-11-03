import abc
import csv
from typing import Any, Iterator, Protocol

import requests


class RowGenerator(Protocol):
    def __init__(self, source: str, data_fields: list[str], **kwargs: Any) -> None:
        """ititializes the row generator, process Source into a collection of rows, the type of the rows is dict[str,Any]

        Args:
            source (str): the path/url/location where the data is located
            data_fields (list[str]): the list of fields in the table
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
        
class CsvRow(RowGenerator):
    def __init__(self, source: str, data_fields: list[str], **kwargs: Any) -> None:
        """ititializes the row generator, process Source into a collection of rows, the type of the rows is dict[str,Any]

        Args:
            source (str): the path/url/location where the data is located
            **kwargs (any): additional arguments
        """
        # open csv file
        with open(source, mode='r', newline='') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
            reader = csv.DictReader(csvfile, fieldnames=data_fields, dialect=dialect)

            # convert data into useful format
            self.rows: list[dict[str,Any]] = [x for x in reader][1::] #convert reader to a list, skipping first rows
        


    def __iter__(self) -> Iterator[dict[str, Any]]:
        """
        generates and returns an iterator over the rows of data in a source
        Yields:
            Iterator[dict[str, Any]]: iterator over the rows of data
        """
        return iter(self.rows)
        
class WebRow(RowGenerator,abc.ABC):
    """follows RowGenerator protocol"""
    @staticmethod
    @abc.abstractmethod
    def process_response(response: bytes, data_fields:list[str], **kwargs) -> list[dict[str, Any]]:
        """process the response from the webserver into a list of rows, represented by dictionaries

        Args:
            response (bytes): response from webserver

        Raises:
            ValueError: provided data_fields don't match the number of fields in the response

        Returns:
            list[dict[str,Any]]: the processed response
        """
        ...
        
        
    def __init__(self, source: str, data_fields:list[str], **kwargs: Any) -> None:
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
        
        self.rows: list[dict[str,Any]] = self.process_response(response, data_fields,**kwargs)
        
        
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
    def process_response(response: bytes, data_fields:list[str], **kwargs) -> list[dict[str,Any]]:
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
        >>> response = "10,1.0,wowza;20,2.0,zoinks;".encode()
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
        #decode and re-order response
        split_response: list[str] = response.decode('utf-8').split(sep=sample_separator)
        split_rows: list[list[str]]  = [
            row.split(sep=data_separator)
            for row in split_response
        ]
        
        #ensure that len(data_fields) is the same as the number of values in each sample
        if len(data_fields) != len(split_rows[0]):
            raise ValueError("provided data_fields doesn't match number of data_entries in response, {}!={}".format(len(data_fields),len(split_rows[0])))
        
        # use field headers to convert rows list of lists into a list of dicts
        return [
            dict(zip(
                data_fields,
                row
            ))
            for row in split_rows
        ]
        
    
    def __init__(self, source: str, data_fields:list[str],**kwargs: Any) -> None:
        super().__init__(source,data_fields, **kwargs)
    
    
    def __iter__(self) -> Iterator[dict[str, Any]]:
        return super().__iter__()
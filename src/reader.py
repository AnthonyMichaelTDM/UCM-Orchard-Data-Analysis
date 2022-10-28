import abc

from .data import DataList, DataSource

class Reader(abc.ABC):
    def __init__(self, source: str) -> None:
        self.source_path:str= source
        self.data: DataList = []
        
    @abc.abstractmethod
    def load_data_source(self, path: str) -> None:
        """loads raw data from a source""" 
        ...
    
    @abc.abstractmethod
    def process(self) -> None:
        """deserializes previously loaded data"""
        ...
        
class CsvReader(Reader):
    pass
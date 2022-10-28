import abc
from typing import Dict, Iterable, Iterator, Optional, SupportsIndex, Union, overload


class DataPoint(abc.ABC):
    @abc.abstractmethod
    def __init__(self, data: Dict[str,str]) -> None:
        """initialize DataPoint from a dictionary of unserialized data

        Args:
            data (Dict[str,str]): 
        """
        ...
    ...
    
    
class DataList(list[DataPoint]):
    def __init__(
        self,
        data_points: Optional[Iterable[DataPoint]] = None
    ) -> None:
        self.data_points: list[DataPoint] = list(data_points) if data_points else []
    
    def __iter__(self) -> Iterator[DataPoint]: 
        return iter(self.data_points)
    
    def __len(self) -> int:
        return len(self.data_points)
    
    @overload
    def __getitem__(self,index: SupportsIndex) -> DataPoint:
        ...
    @overload
    def __getitem__(self, index: slice) -> list[DataPoint]:
        ...
    
    def __getitem__(self, index: Union[SupportsIndex, slice]) -> Union[DataPoint, list[DataPoint]]:
       return self.data_points[index]
    
class DataSource(abc.ABC):
    base_path:str=""
    def __init__(self) -> None:
        pass
    
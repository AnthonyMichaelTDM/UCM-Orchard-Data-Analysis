from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Iterator, Optional, SupportsIndex, Union, overload

from more_itertools import sample

@dataclass(frozen=True)
class Sample():
    timestamp: datetime
    important_fields: list[str]
    datapoints: dict[str, Any]
    ...


class SampleList(list[Sample]):
    def __init__(
        self,
        samples: Optional[Iterable[Sample]] = None
    ) -> None:
        self.samples: list[Sample] = list(samples) if samples else []
    
    def __iter__(self) -> Iterator[Sample]: 
        return iter(self.samples)
    
    def __len(self) -> int:
        return len(self.samples)
    
    @overload
    def __getitem__(self,index: SupportsIndex)->Sample:
        ...
    @overload
    def __getitem__(self, index: slice)->list[Sample]:
        ...
    
    def __getitem__(self, index: Union[SupportsIndex, slice]) -> Union[Sample, list[Sample]]:
        return self.samples[index]
   
    def extend(self, other: Iterable[Sample]):
        self.samples.extend(other)
       
    def trim_to_timerange(self, start_date: datetime, end_date: datetime):
        """removes samples that don't fall between start_date and end_date

        Args:
            start_date (datetime): start of range
            end_date (datetime): end of range
            
        DocTest:
        >>> from sample import SampleList, Sample
        >>> from datetime import datetime
        >>> samples = SampleList([
        ...     Sample(datetime(2022,1,10),[],{})
        ...     Sample(datetime(2022,1,11),[],{})
        ...     Sample(datetime(2022,1,12),[],{}) 
        ...     Sample(datetime(2022,1,13),[],{}) 
        ...     Sample(datetime(2022,1,14),[],{}) 
        ... ])
        >>> samples.trim_to_timerange(datetime(2022,1,11),datetime(2022,1,13))
        >>> samples
        SampleList(samples=[Sample(datetime(2022,1,11), [], {}), Sample(datetime(2022,1,12), [], {}), Sample(datetime(2022,1,13), [], {})])
        """
        self.samples = [
            sample
            for sample in iter(self.samples)
            if sample.timestamp >= start_date and sample.timestamp <= end_date
        ]


@dataclass(frozen=True)
class DataSource():
    base_path: str
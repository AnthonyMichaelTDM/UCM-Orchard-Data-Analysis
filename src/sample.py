from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Iterable, Iterator, Optional, SupportsIndex, Union, overload

from numpy import average

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
    
    def sort(self):
        """sort the samples in chronological order
        
        DocTest:
        >>> from sample import SampleList, Sample
        >>> from datetime import datetime
        >>> samples = SampleList([
        ...     Sample(datetime(2022,1,12), [], {}),
        ...     Sample(datetime(2022,1,11), [], {}),
        ...     Sample(datetime(2022,1,10), [], {}),
        ...     Sample(datetime(2022,1,13), [], {}) 
        ... ])
        >>> samples.sort()
        >>> samples.samples
        [Sample(timestamp=datetime.datetime(2022, 1, 10, 0, 0), important_fields=[], datapoints={}), Sample(timestamp=datetime.datetime(2022, 1, 11, 0, 0), important_fields=[], datapoints={}), Sample(timestamp=datetime.datetime(2022, 1, 12, 0, 0), important_fields=[], datapoints={}), Sample(timestamp=datetime.datetime(2022, 1, 13, 0, 0), important_fields=[], datapoints={})]
        """
        self.samples.sort(key=lambda x: x.timestamp)
   
    def extend(self, other: Iterable[Sample]) -> None:
        self.samples.extend(other)
       
    def trim_to_timerange(self, start_date: datetime, end_date: datetime) -> None:
        """removes samples that don't fall between start_date and end_date

        Args:
            start_date (datetime): start of range
            end_date (datetime): end of range
            
        DocTest:
        >>> from sample import SampleList, Sample
        >>> from datetime import datetime
        >>> samples = SampleList([
        ...     Sample(datetime(2022,1,10),[],{}),
        ...     Sample(datetime(2022,1,11),[],{}),
        ...     Sample(datetime(2022,1,12),[],{}), 
        ...     Sample(datetime(2022,1,13),[],{}), 
        ...     Sample(datetime(2022,1,14),[],{}) 
        ... ])
        >>> samples.trim_to_timerange(datetime(2022,1,11),datetime(2022,1,13))
        >>> samples.samples
        [Sample(timestamp=datetime.datetime(2022, 1, 11, 0, 0), important_fields=[], datapoints={}), Sample(timestamp=datetime.datetime(2022, 1, 12, 0, 0), important_fields=[], datapoints={}), Sample(timestamp=datetime.datetime(2022, 1, 13, 0, 0), important_fields=[], datapoints={})]
        """
        self.samples = [
            sample
            for sample in iter(self.samples)
            if sample.timestamp >= start_date and sample.timestamp <= end_date
        ]
        
    # TODO: add unit tests
    def get_smoothened_data(self, start:datetime, interval: timedelta):
        results = SampleList()
        intervals: dict[datetime, list[Sample]] = {}
        
        # group samples into time groups
        for sample in self.samples:
            #calculate time interval this sample falls into
            timegroup = start + (interval * ((sample.timestamp - start) // interval))
            if timegroup not in intervals:
                intervals[timegroup] = [sample]
            else:
                intervals[timegroup].append(sample)
                
        # calculate average of time groups, and rebuild self
        for timegroup, samples in intervals.items():
            averaged_data = {
                label: average([
                    data
                    for data in [sample.datapoints[label] for sample in samples]
                ])
                for label in samples[0].important_fields
                if samples[0].datapoints[label].isnumeric()
            }
            results.append(
                Sample(
                    timestamp=timegroup, 
                    important_fields=list(averaged_data.keys()), 
                    datapoints=averaged_data
                )
            )
        
        return results
            


@dataclass(frozen=True)
class DataSource():
    base_path: str
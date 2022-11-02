import abc
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Iterable, Iterator, Optional, Protocol, SupportsIndex, Union, overload

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

class SampleBuilderBase(abc.ABC):
    from details import SampleDetails
    @staticmethod
    @abc.abstractmethod
    def build(row: dict[str,Any], config: SampleDetails) -> Sample:
        ...

class SampleBuilder(SampleBuilderBase):
    from details import SampleDetails
    @staticmethod
    def build(row: dict[str,Any], config: SampleDetails) -> Sample:
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
        >>> from configurations import SampleDetails
        >>> row = {"time":"2022-04-30 23:46:18", "wanted 1":"13.5", "unwanted/bad":"abcdef"}
        >>> details1 = SampleDetails(
        ...     important_fields = ["wanted 1"],
        ...     field_types = [float],
        ...     timestamp_fieldname = "time",
        ...     timestamp_format = "%Y-%m-%d %H:%M:%S",
        ... )
        >>> SampleBuilder.build(row,details1)
        Sample(timestamp=datetime.datetime(2022, 4, 30, 23, 46, 18), important_fields=['wanted 1'], datapoints={'wanted 1': 13.5})
        >>> details2 = SampleDetails(
        ...     important_fields = ["wanted 1"],
        ...     field_types = [float],
        ...     timestamp_fieldname = "timestamp",
        ...     timestamp_format = "%Y-%m-%d %H:%M:%S",
        ... )
        >>> SampleBuilder.build(row,details2) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        KeyError: given timestamp_fieldname 'timestamp' not found in row
        >>> details3 = SampleDetails(
        ...     important_fields = ["wanted 1","wanted 2"],
        ...     field_types = [float,int],
        ...     timestamp_fieldname = "time",
        ...     timestamp_format = "%Y-%m-%d %H:%M:%S",
        ... )
        >>> SampleBuilder.build(row,details3) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        KeyError: important field(s) '['wanted 2']' is/are missing
        >>> details4 = SampleDetails(
        ...     important_fields = ["wanted 1","unwanted/bad"],
        ...     field_types = [float],
        ...     timestamp_fieldname = "time",
        ...     timestamp_format = "%Y-%m-%d %H:%M:%S",
        ... )
        >>> SampleBuilder.build(row,details4) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        IndexError: must have a type for every important field
        >>> details5 = SampleDetails(
        ...     important_fields = ["unwanted/bad"],
        ...     field_types = [int],
        ...     timestamp_fieldname = "time",
        ...     timestamp_format = "%Y-%m-%d %H:%M:%S",
        ... )
        >>> SampleBuilder.build(row,details5) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: invalid literal for int() with base 10: 'abcdef'
        >>> details6 = SampleDetails(
        ...     important_fields = ["wanted 1"],
        ...     field_types = [float],
        ...     timestamp_fieldname = "time",
        ...     timestamp_format = "%H:%M:%S %Y-%m-%d",
        ... )
        >>> SampleBuilder.build(row,details6) # doctest: +IGNORE_EXCEPTION_DETAIL
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
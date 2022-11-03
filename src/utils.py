
from datetime import datetime
from typing import Type
from configurations import FilenameGeneratorContract
from sample import SampleBuilderBase, SampleDetails, SampleList, SampleBuilder
from reader import Reader

#TODO: add unit tests
def process_reader_into_samplelist(
    reader:Reader,
    sampleconf: SampleDetails,
    builder:Type[SampleBuilderBase] = SampleBuilder,
) -> SampleList:
    return SampleList([
        builder.build(row,sampleconf)
        for row in reader.rows[1:]
    ])


#TODO: add unit tests
def get_filenames_for_timerange(
    startdate:datetime,
    enddate:datetime,
    id:int | None,
    filename_generator: FilenameGeneratorContract
) -> list[str]:
    filenames: dict[str,None] = {} #using a dict instead of a set because dicts are ordered, indexable, and don't allow duplicates
    
    # get filenames
    if startdate.year < enddate.year:
        #first year
        for month in range(startdate.month,12+1):
            date = datetime(year=startdate.year,month=month,day=startdate.day)
            filenames[filename_generator(date,id)] = None
        #middle years
        if startdate.year+1 < enddate.year-1:
            for year in range(startdate.year+1,enddate.year-1):
                for month in range(1,12+1):
                    date = datetime(year=year, month=month, day=startdate.day)
                    filenames[filename_generator(date,id)] = None
        #last year
        for month in range(enddate.month,12+1):
            date = datetime(year=enddate.year,month=month,day=enddate.day)
            filenames[filename_generator(date,id)] = None
    elif startdate.month < enddate.month:
        #months
        for month in range(startdate.month,enddate.month+1):
            date = datetime(year=enddate.year,month=month,day=startdate.day)
            filenames[filename_generator(date,id)] = None
    else: 
        filenames[filename_generator(startdate,id)] = None

    return list(filenames.keys())
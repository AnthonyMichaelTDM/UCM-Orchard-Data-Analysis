import abc
from sample import SampleList


class AnalyzerBase(abc.ABC):
    def __init__(self, samples: SampleList):
        ...
        
    def run(self):
        ...
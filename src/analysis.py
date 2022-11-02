import abc
from typing import Any
from sample import SampleList


class SampleAnalyzerBase(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def run(samples: SampleList) -> list[Any]:
        ...
        
class AnalyzeSapFlow(SampleAnalyzerBase):
    @staticmethod
    def run(samples: SampleList) -> list[Any]:
        ...

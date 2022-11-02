
import abc
from typing import Callable


class Plotter():
    def __init__(
        self,
        
    ) -> None:
        pass
    
    def plot(self):
        pass

class PlotterBuilderBase(abc.ABC):
    from details import PlotterDetails
    @staticmethod
    @abc.abstractmethod
    def build(config: PlotterDetails) -> Plotter:
        ...

class PlotterBuilder(PlotterBuilderBase):
    from details import PlotterDetails
    @staticmethod
    def build(
        config: PlotterDetails
    ) -> Plotter:
        return Plotter(
            
        )
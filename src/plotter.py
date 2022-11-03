
import abc
from typing import Any, Callable, NamedTuple, Optional
import matplotlib.pyplot as plt

from sample import SampleList

class Plotter():
    def __init__(
        self,
        x_label:str,
        x_list: list[Any],
        y_label:str,
        y_list: list[Any],
        figure_id:int,
        figure_rows:int,
        figure_cols:int,
        subplot_index:int,
        sensor_id:int|None  
    ) -> None:
        self.x_label: str=x_label
        self.x: list[Any]=x_list
        self.y_label: str=y_label
        self.y: list[Any]=y_list
        self.figure_id: int=figure_id
        self.figure_rows: int = figure_rows
        self.figure_cols: int = figure_cols
        self.subplot_index: int = subplot_index
        self.sensor_id: int|None=sensor_id
      
        
    def plot(self):
        plt.figure(self.figure_id)
        plt.subplot(self.figure_rows,self.figure_cols,self.subplot_index)
        plt.title("\n{} vs {}".format(self.y_label, self.x_label))
        plt.xticks(rotation=50)
        plt.plot(self.x,self.y)


plotter_list_generator_contract = Callable[[SampleList,Optional[int]],list[Any]]
# for some reason python is throwing an error when I put this lambda in the PlotterDetails class 
__x_gen__ = lambda samples, _id: [
        sample.timestamp 
        for sample in samples
]


class PlotterDetails(NamedTuple):
    figure_id:int
    y_list_gen: plotter_list_generator_contract
    y_label: str
    x_list_gen: plotter_list_generator_contract = __x_gen__
    x_label: str = "Time"
    figure_rows:int = 1
    figure_cols:int = 1
    subplot_index:int = 1


class PlotterBuilderBase(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def build(
        config: PlotterDetails,
        samples: SampleList,
        sensor_id: int|None,
    ) -> Plotter:
        ...


class PlotterBuilder(PlotterBuilderBase):
    @staticmethod
    def build(
        config: PlotterDetails,
        samples: SampleList,
        sensor_id: int|None,
    ) -> Plotter:
        return Plotter(
            x_label = config.x_label,
            x_list = config.x_list_gen(samples,sensor_id), # generate x list according to lambda in config
            y_label = config.y_label,
            y_list = config.y_list_gen(samples,sensor_id), # generate y list according to lambda in config
            figure_id = config.figure_id,
            figure_rows = config.figure_rows,
            figure_cols = config.figure_cols,
            subplot_index = config.subplot_index,
            sensor_id=sensor_id
        )
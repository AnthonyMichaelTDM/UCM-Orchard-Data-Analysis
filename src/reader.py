import abc
import argparse
import os
from typing import Any, NamedTuple, Type

from rowgenerator import RowGenerator


class Reader():
    def __init__(
        self,
        row_generator: Type[RowGenerator],
        base_path: str,
        additional: dict[str,Any],
        **kwargs:Any,
    ) -> None:
        self.row_generator = row_generator
        self.base_path = base_path
        self.rows: list[dict[str,Any]] = []
        self.additional = additional
        self.additional.update(kwargs)


    def read(self, filename:str, data_fields:list[str]) -> None:
        """reads the data from 'filename', and appends its 'rows' list

        Args:
            filename (str): file name (at `self.base_path/filename`) to read from
        """
        row_gen_class = self.row_generator
        row_iter = row_gen_class(os.path.join(self.base_path,filename), data_fields, **self.additional)
        self.rows.extend([row for row in row_iter])

class ReaderDetails(NamedTuple):
    row_generator: Type[RowGenerator]
    data_source: str
    data_fields: list[str]
    additional: dict[str,Any] = {}
    args: list[str] = []# for future CLI functionality


class ReaderBuilderBase(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def build(config:ReaderDetails, options: argparse.Namespace) -> Reader:
        ...
        
        
class ReaderBuilder(ReaderBuilderBase):
    @staticmethod
    # TODO: add unit tests 
    def build( #can't just have ReaderDetails as a parameter because that'll cause circular dependency
        config: ReaderDetails,
        options: argparse.Namespace,
    ) -> Reader:
        # settings with names hardcoded, but values given by user
        # aka: settings that aren't the same all the time, but also aren't needed by every reader
        other: dict[str, Any | None] = { # user define opitions
            name: getattr(options, name, None)
            for name in config.args
        }
        return Reader(config.row_generator, config.data_source, config.additional, **other)


# TODO: add unit tests for stuff in the reader module

# Unit doctests

__test__ = {name: value for name, value in locals().items() if name.startswith("test")}

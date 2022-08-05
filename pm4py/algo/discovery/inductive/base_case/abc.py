from abc import ABC, abstractmethod
from typing import Union, TypeVar, Generic

from pm4py.objects.dfg.obj import DFG
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util.compression.dtypes import UCL

T = TypeVar('T', bound=Union[UCL, DFG])


class BaseCase(ABC, Generic[T]):

    @classmethod
    @abstractmethod
    def applies(cls, obj=T) -> bool:
        pass

    @classmethod
    @abstractmethod
    def get_leaf(cls, obj=T) -> ProcessTree:
        pass
